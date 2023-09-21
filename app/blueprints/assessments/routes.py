import io
import zipfile
from collections import OrderedDict
from datetime import datetime
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

from app.blueprints.assessments.forms.assessment_form import (
    AssessmentCompleteForm,
)
from app.blueprints.assessments.forms.comments_form import CommentsForm
from app.blueprints.assessments.forms.mark_qa_complete_form import (
    MarkQaCompleteForm,
)
from app.blueprints.assessments.helpers import download_file
from app.blueprints.assessments.helpers import generate_assessment_info_csv
from app.blueprints.assessments.helpers import generate_assessment_info_excel
from app.blueprints.assessments.helpers import generate_maps_from_form_names
from app.blueprints.assessments.helpers import (
    get_files_for_application_upload_fields,
)
from app.blueprints.assessments.helpers import get_tag_map_and_tag_options
from app.blueprints.assessments.helpers import get_team_flag_stats
from app.blueprints.assessments.helpers import (
    set_application_status_in_overview,
)
from app.blueprints.assessments.models import applicants_response
from app.blueprints.assessments.models.file_factory import (
    ApplicationFileRepresentationArgs,
)
from app.blueprints.assessments.models.file_factory import FILE_GENERATORS
from app.blueprints.assessments.models.file_factory import (
    generate_file_content,
)
from app.blueprints.assessments.models.flag_teams import TeamsFlagData
from app.blueprints.assessments.models.fund_summary import (
    create_round_summaries,
)
from app.blueprints.assessments.models.fund_summary import is_after_today
from app.blueprints.assessments.models.location_data import LocationData
from app.blueprints.assessments.status import all_status_completed
from app.blueprints.assessments.status import update_ar_status_to_completed
from app.blueprints.assessments.status import update_ar_status_to_qa_completed
from app.blueprints.authentication.validation import (
    check_access_application_id,
)
from app.blueprints.authentication.validation import (
    check_access_fund_short_name,
)
from app.blueprints.authentication.validation import get_countries_from_roles
from app.blueprints.authentication.validation import has_access_to_fund
from app.blueprints.authentication.validation import (
    has_devolved_authority_validation,
)
from app.blueprints.services.aws import get_file_for_download_from_aws
from app.blueprints.services.data_services import (
    get_all_uploaded_documents_theme_answers,
)
from app.blueprints.services.data_services import get_applicant_export
from app.blueprints.services.data_services import (
    get_applicant_feedback_and_survey,
)
from app.blueprints.services.data_services import get_application_json
from app.blueprints.services.data_services import get_application_overviews
from app.blueprints.services.data_services import (
    get_application_sections_display_config,
)
from app.blueprints.services.data_services import get_assessment_progress
from app.blueprints.services.data_services import (
    get_associated_tags_for_application,
)
from app.blueprints.services.data_services import get_bulk_accounts_dict
from app.blueprints.services.data_services import get_comments
from app.blueprints.services.data_services import get_flags
from app.blueprints.services.data_services import get_fund
from app.blueprints.services.data_services import get_funds
from app.blueprints.services.data_services import get_qa_complete
from app.blueprints.services.data_services import get_round
from app.blueprints.services.data_services import get_sub_criteria
from app.blueprints.services.data_services import (
    get_sub_criteria_theme_answers,
)
from app.blueprints.services.data_services import get_tags_for_fund_round
from app.blueprints.services.data_services import match_comment_to_theme
from app.blueprints.services.data_services import submit_comment
from app.blueprints.services.models.theme import Theme
from app.blueprints.services.shared_data_helpers import (
    get_state_for_tasklist_banner,
)
from app.blueprints.shared.filters import utc_to_bst
from app.blueprints.shared.helpers import determine_assessment_status
from app.blueprints.shared.helpers import determine_flag_status
from app.blueprints.shared.helpers import fund_matches_filters
from app.blueprints.shared.helpers import get_ttl_hash
from app.blueprints.shared.helpers import is_flaggable
from app.blueprints.shared.helpers import match_search_params
from app.blueprints.shared.helpers import process_assessments_stats
from config import Config
from config.display_value_mappings import assessment_statuses
from config.display_value_mappings import asset_types
from config.display_value_mappings import funding_types
from config.display_value_mappings import landing_filters
from config.display_value_mappings import search_params_cof
from config.display_value_mappings import search_params_nstf
from flask import abort
from flask import Blueprint
from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import Response
from flask import url_for
from fsd_utils import extract_questions_and_answers

assessment_bp = Blueprint(
    "assessment_bp",
    __name__,
    url_prefix=Config.ASSESSMENT_HUB_ROUTE,
    template_folder="templates",
)


def _handle_all_uploaded_documents(application_id):
    flags_list = get_flags(application_id)
    flag_status = determine_flag_status(flags_list)

    theme_answers_response = get_all_uploaded_documents_theme_answers(
        application_id
    )
    answers_meta = applicants_response.create_ui_components(
        theme_answers_response, application_id
    )

    state = get_state_for_tasklist_banner(application_id)
    assessment_status = determine_assessment_status(
        state.workflow_status, state.is_qa_complete
    )
    return render_template(
        "all_uploaded_documents.html",
        state=state,
        application_id=application_id,
        is_flaggable=is_flaggable(flag_status),
        answers_meta=answers_meta,
        assessment_status=assessment_status,
    )


@assessment_bp.route("/assessor_dashboard/", methods=["GET"])
def old_landing():
    return redirect("/assess/assessor_tool_dashboard/")


@assessment_bp.route("/assessor_tool_dashboard/", methods=["GET"])
def landing():
    filters = landing_filters._replace(
        **{
            k: v
            for k, v in request.args.items()
            if k in landing_filters._fields
        }
    )  # noqa
    funds = [
        f
        for f in get_funds(get_ttl_hash(seconds=300))
        if has_access_to_fund(f.short_name)
        and fund_matches_filters(f, filters)
    ]
    sorted_funds_map = OrderedDict(
        (fund.id, fund) for fund in sorted(funds, key=lambda f: f.name)
    )
    round_summaries = {
        fund.id: create_round_summaries(fund, filters) for fund in funds
    }
    return render_template(
        "assessor_tool_dashboard.html",
        fund_summaries=round_summaries,
        funds=sorted_funds_map,
        todays_date=utc_to_bst(datetime.now().strftime("%Y-%m-%dT%H:%M:%S")),
        landing_filters=filters,
        has_any_assessor_role=any(
            rs.access_controller.has_any_assessor_role
            for rsl in round_summaries.values()
            for rs in rsl
        ),
        show_assessments_live_rounds=Config.SHOW_ASSESSMENTS_LIVE_ROUNDS,
    )


@assessment_bp.route(
    "/assessor_dashboard/<fund_short_name>/<round_short_name>/",
    methods=["GET"],
)
@check_access_fund_short_name
def fund_dashboard(fund_short_name: str, round_short_name: str):
    if fund_short_name.upper() == "NSTF":
        search_params = {**search_params_nstf}
    else:
        search_params = {**search_params_cof}

    fund = get_fund(fund_short_name, use_short_name=True)
    if not fund:
        return redirect("/assess/assessor_tool_dashboard/")
    _round = get_round(fund_short_name, round_short_name, use_short_name=True)
    if not _round:
        return redirect("/assess/assessor_tool_dashboard/")
    fund_id, round_id = fund.id, _round.id

    countries = {"ALL"}
    if has_devolved_authority_validation(fund_id=fund_id):
        countries = get_countries_from_roles(fund.short_name)

    # This call is to get the location data such as country, region and local_authority
    # from all the existing applications.
    applications_metadata = get_application_overviews(
        fund_id, round_id, search_params=""
    )
    locations = LocationData.from_json_blob(applications_metadata)

    search_params = {
        **search_params,
        "countries": ",".join(countries),
    }

    search_params, show_clear_filters = match_search_params(
        search_params, request.args
    )

    application_overviews = get_application_overviews(
        fund_id, round_id, search_params
    )

    # note, we are not sending search parameters here as we don't want to filter
    # the stats at all.  see https://dluhcdigital.atlassian.net/browse/FS-3249
    stats = process_assessments_stats(applications_metadata)

    teams_flag_stats = get_team_flag_stats(application_overviews)

    # this is only used for querying applications, so remove it from the search params,
    # so it's not reflected on the user interface
    del search_params["countries"]

    round_details = {
        "assessment_deadline": _round.assessment_deadline,
        "round_title": _round.title,
        "fund_name": fund.name,
        "fund_short_name": fund_short_name,
        "round_short_name": round_short_name,
    }

    is_active_status = is_after_today(_round.assessment_deadline)
    post_processed_overviews = (
        get_assessment_progress(application_overviews, fund_id, round_id)
        if application_overviews
        else []
    )

    # get and set application status
    post_processed_overviews = set_application_status_in_overview(
        post_processed_overviews
    )

    active_fund_round_tags = get_tags_for_fund_round(
        fund_id, round_id, {"tag_status": "True"}
    )
    tag_map, tag_option_groups = get_tag_map_and_tag_options(
        active_fund_round_tags, post_processed_overviews
    )

    def get_sorted_application_overviews(
        application_overviews, column, reverse=False
    ):
        """Sorts application_overviews list based on the specified column."""

        sort_field_to_lambda = {
            "location": lambda x: x["location_json_blob"]["country"],
            "funding_requested": lambda x: x["funding_amount_requested"],
            "local_authority": lambda x: x["local_authority"],
            "project_name": lambda x: x["project_name"],
            "asset_type": lambda x: x["asset_type"],
            "organisation_name": lambda x: x["organisation_name"],
            "funding_type": lambda x: x["funding_type"],
            "status": lambda x: x["application_status"],
            "tags": lambda x: len(tag_map.get(x["application_id"]) or []),
        }

        # Define the sorting function based on the specified column
        if sort_key := sort_field_to_lambda.get(column, None):
            return sorted(application_overviews, key=sort_key, reverse=reverse)
        else:
            return application_overviews

    # Get the sort column and order from query parameters
    sort_column = request.args.get("sort_column", "")
    sort_order = request.args.get("sort_order", "")
    if sort_column:
        post_processed_overviews = get_sorted_application_overviews(
            post_processed_overviews,
            sort_column,
            reverse=sort_order != "asc",
        )

    return render_template(
        "assessor_dashboard.html",
        user=g.user,
        application_overviews=post_processed_overviews,
        round_details=round_details,
        query_params=search_params,
        asset_types=asset_types,
        funding_types=funding_types,
        assessment_statuses=assessment_statuses,
        show_clear_filters=show_clear_filters,
        stats=stats,
        team_flag_stats=teams_flag_stats,
        is_active_status=is_active_status,
        sort_column=sort_column,
        sort_order=sort_order,
        tag_option_groups=tag_option_groups,
        tags=tag_map,
        tagging_purpose_config=Config.TAGGING_PURPOSE_CONFIG,
        countries=locations.countries,
        regions=locations.regions,
        local_authorities=locations._local_authorities,
    )


@assessment_bp.route(
    "/application_id/<application_id>/sub_criteria_id/<sub_criteria_id>",
    methods=["POST", "GET"],
)
@check_access_application_id
def display_sub_criteria(
    application_id,
    sub_criteria_id,
):
    if sub_criteria_id == "all_uploaded_documents":
        return _handle_all_uploaded_documents(application_id)

    """
    Page showing sub criteria and themes for an application
    """
    current_app.logger.info(f"Processing GET to {request.path}.")
    sub_criteria = get_sub_criteria(application_id, sub_criteria_id)
    theme_id = request.args.get("theme_id", sub_criteria.themes[0].id)
    comment_form = CommentsForm()
    try:
        current_theme: Theme = next(
            iter(t for t in sub_criteria.themes if t.id == theme_id)
        )
    except StopIteration:
        current_app.logger.warn("Unknown theme ID requested: " + theme_id)
        abort(404)
    add_comment_argument = request.args.get("add_comment") == "1"
    if add_comment_argument and comment_form.validate_on_submit():
        comment = comment_form.comment.data
        submit_comment(
            comment=comment,
            application_id=application_id,
            sub_criteria_id=sub_criteria_id,
            user_id=g.account_id,
            theme_id=theme_id,
        )

        return redirect(
            url_for(
                "assessment_bp.display_sub_criteria",
                application_id=application_id,
                sub_criteria_id=sub_criteria_id,
                theme_id=theme_id,
                _anchor="comments",
            )
        )

    state = get_state_for_tasklist_banner(application_id)
    flags_list = get_flags(application_id)

    comment_response = get_comments(
        application_id=application_id,
        sub_criteria_id=sub_criteria_id,
        theme_id=theme_id,
    )

    # TODO add test for this function in data_operations
    theme_matched_comments = (
        match_comment_to_theme(
            comment_response, sub_criteria.themes, state.fund_short_name
        )
        if comment_response
        else None
    )

    assessment_status = determine_assessment_status(
        sub_criteria.workflow_status, state.is_qa_complete
    )
    flag_status = determine_flag_status(flags_list)

    common_template_config = {
        "sub_criteria": sub_criteria,
        "application_id": application_id,
        "comments": theme_matched_comments,
        "is_flaggable": False,  # Flag button is disabled in sub-criteria page,
        "display_comment_box": add_comment_argument,
        "comment_form": comment_form,
        "current_theme": current_theme,
        "flag_status": flag_status,
        "assessment_status": assessment_status,
    }

    theme_answers_response = get_sub_criteria_theme_answers(
        application_id, theme_id
    )

    answers_meta = applicants_response.create_ui_components(
        theme_answers_response, application_id
    )

    return render_template(
        "sub_criteria.html",
        answers_meta=answers_meta,
        state=state,
        **common_template_config,
    )


@assessment_bp.route("/application/<application_id>/export", methods=["GET"])
@check_access_application_id(roles_required=["LEAD_ASSESSOR"])
def generate_doc_list_for_download(application_id):
    current_app.logger.info(
        f"Generating docs for application id {application_id}"
    )
    state = get_state_for_tasklist_banner(application_id)
    short_id = state.short_id[-6:]
    flags_list = get_flags(application_id)
    assessment_status = determine_assessment_status(
        state.workflow_status, flags_list
    )
    flag_status = determine_flag_status(flags_list)

    application_json = get_application_json(application_id)
    supporting_evidence = get_files_for_application_upload_fields(
        application_id=application_id,
        short_id=short_id,
        application_json=application_json,
    )

    file_links = [
        (
            f"Download applicant answers as {file_type.upper()} file",
            url_for(
                "assessment_bp.download_application_answers",
                application_id=application_id,
                short_id=short_id,
                file_type=file_type,
            ),
        )
        for file_type in FILE_GENERATORS.keys()
    ]

    return render_template(
        "contract_downloads.html",
        application_id=application_id,
        state=state,
        file_links=file_links,
        supporting_evidence=supporting_evidence,
        assessment_status=assessment_status,
        flag_status=flag_status,
    )


@assessment_bp.route(
    "/application/<application_id>/export/<short_id>/answers.<file_type>"
)
@check_access_application_id(roles_required=["LEAD_ASSESSOR"])
def download_application_answers(
    application_id: str, short_id: str, file_type: str
):
    current_app.logger.info(
        "Generating application Q+A download for application"
        f" {application_id} in {file_type} format"
    )
    application_json = get_application_json(application_id)
    application_json_blob = application_json["jsonb_blob"]

    fund = get_fund(application_json["jsonb_blob"]["fund_id"])
    round_ = get_round(
        fund.id, application_json["round_id"], use_short_name=False
    )

    qanda_dict = extract_questions_and_answers(application_json_blob["forms"])
    application_sections_display_config = (
        get_application_sections_display_config(
            fund.id, round_.id, application_json["language"]
        )
    )

    (
        form_name_to_title_map,
        form_name_to_path_map,
    ) = generate_maps_from_form_names(application_sections_display_config)

    qanda_dict = {
        key: qanda_dict[key]
        for key in form_name_to_title_map
        if key in qanda_dict
    }

    all_uploaded_documents = []
    if file_type == "pdf":
        all_uploaded_documents = get_all_uploaded_documents_theme_answers(
            application_id
        )

    args = ApplicationFileRepresentationArgs(
        fund=fund,
        round=round_,
        question_to_answer=qanda_dict,
        application_json=application_json,
        form_name_to_title_map=form_name_to_title_map,
        short_id=short_id,
        all_uploaded_documents=all_uploaded_documents,
    )

    return generate_file_content(args, file_type)


@assessment_bp.route(
    "/application/<application_id>/export/<file_name>",
    methods=["GET"],
)
def get_file(application_id: str, file_name: str):
    if request.args.get("quoted"):
        file_name = unquote_plus(file_name)
    short_id = request.args.get("short_id")
    data, mimetype = get_file_for_download_from_aws(
        application_id=application_id, file_name=file_name
    )
    if short_id:
        return download_file(data, mimetype, f"{short_id}_{file_name}")

    return download_file(data, mimetype, file_name)


def download_multiple_files(files, folder_name):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_archive:
        for file_name, file_data in files:
            zip_archive.writestr(file_name, file_data)

    zip_buffer.seek(0)

    return Response(
        zip_buffer.read(),
        mimetype="application/zip",
        headers={
            "Content-Disposition": (
                f"attachment;filename={quote_plus(f'{folder_name}.zip')}"
            )
        },
    )


@assessment_bp.route("/application/<application_id>", methods=["GET", "POST"])
@check_access_application_id
def application(application_id):
    """
    Application summary page
    Shows information about the fund, application ID
    and all the application questions and their assessment status
    :param application_id:
    :return:
    """

    if request.method == "POST":
        update_ar_status_to_completed(application_id)

    state = get_state_for_tasklist_banner(application_id)
    fund_round = get_round(state.fund_id, state.round_id)

    user_id_list = []
    flags_list = get_flags(application_id)
    qa_complete = get_qa_complete(application_id)
    if qa_complete:
        user_id_list.append(qa_complete["user_id"])

    assessment_status = determine_assessment_status(
        state.workflow_status, state.is_qa_complete
    )
    flag_status = determine_flag_status(flags_list)

    if flags_list:
        for flag_data in flags_list:
            for flag_item in flag_data.updates:
                if flag_item["user_id"] not in user_id_list:
                    user_id_list.append(flag_item["user_id"])

    accounts_list = get_bulk_accounts_dict(user_id_list, state.fund_short_name)

    teams_flag_stats = TeamsFlagData.from_flags(flags_list).teams_stats

    sub_criteria_status_completed = all_status_completed(state)
    form = AssessmentCompleteForm()
    associated_tags = get_associated_tags_for_application(application_id)

    return render_template(
        "assessor_tasklist.html",
        sub_criteria_status_completed=sub_criteria_status_completed,
        tags=associated_tags,
        tag_config=Config.TAGGING_PURPOSE_CONFIG,
        form=form,
        state=state,
        application_id=application_id,
        accounts_list=accounts_list,
        teams_flag_stats=teams_flag_stats,
        flags_list=flags_list,
        is_flaggable=is_flaggable(flag_status),
        is_qa_complete=state.is_qa_complete,
        qa_complete=qa_complete,
        flag_status=flag_status,
        assessment_status=assessment_status,
        all_uploaded_documents_section_available=fund_round.all_uploaded_documents_section_available,
    )


@assessment_bp.route(
    "/assessor_export/<fund_short_name>/<round_short_name>/<report_type>",
    methods=["GET"],
)
@check_access_fund_short_name(roles_required=["LEAD_ASSESSOR"])
def assessor_export(
    fund_short_name: str, round_short_name: str, report_type: str
):
    _round = get_round(fund_short_name, round_short_name, use_short_name=True)
    export = get_applicant_export(_round.fund_id, _round.id, report_type)

    en_export_data = generate_assessment_info_csv(export["en_list"])
    cy_export_data = generate_assessment_info_csv(export["cy_list"])

    files_to_download = [
        ("en_export_data.csv", en_export_data),
        ("cy_export_data.csv", cy_export_data),
    ]

    return download_multiple_files(files_to_download, report_type)


@assessment_bp.route(
    "/feedback_export/<fund_short_name>/<round_short_name>/",
    methods=["GET"],
)
@check_access_fund_short_name(roles_required=["LEAD_ASSESSOR"])
def feedback_export(
    fund_short_name: str, round_short_name: str, report_type: str
):
    _round = get_round(fund_short_name, round_short_name, use_short_name=True)
    fund_id = _round.fund_id
    round_id = _round.id
    status_only = "SUBMITTED"

    export = get_applicant_feedback_and_survey(fund_id, round_id, status_only)
    en_export_data = generate_assessment_info_excel(export)
    short_name = fund_short_name + round_short_name

    return download_file(
        en_export_data, "application/zip", f"FSD_Feedback_{short_name}.xlsx"
    )


@assessment_bp.route("/qa_complete/<application_id>", methods=["GET", "POST"])
@check_access_application_id(roles_required=["LEAD_ASSESSOR"])
def qa_complete(application_id):
    """
    QA complete form html page:
    Allows you to mark an application as QA_completed by submitting the form.
    Once submitted, a call is made to the application store endpoint to save
    the QA_COMPLETED flag in the database for the given application_id
    """

    form = MarkQaCompleteForm()

    if form.validate_on_submit():
        update_ar_status_to_qa_completed(application_id, g.account_id)
        return redirect(
            url_for(
                "assessment_bp.application",
                application_id=application_id,
            )
        )
    state = get_state_for_tasklist_banner(application_id)

    return render_template(
        "mark_qa_complete.html",
        application_id=application_id,
        state=state,
        form=form,
        referrer=request.referrer,
        assessment_status=assessment_statuses[state.workflow_status],
    )
