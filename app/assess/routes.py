from app.assess.data import *
from app.assess.data import get_application_overviews
from app.assess.data import get_assessments_stats
from app.assess.data import submit_score_and_justification
from app.assess.display_value_mappings import assessment_statuses
from app.assess.display_value_mappings import asset_types
from app.assess.forms.assessment_form import AssessmentCompleteForm
from app.assess.forms.comments_form import CommentsForm
from app.assess.forms.continue_application_form import ContinueApplicationForm
from app.assess.forms.flag_form import FlagApplicationForm
from app.assess.forms.mark_qa_complete_form import MarkQaCompleteForm
from app.assess.forms.rescore_form import RescoreForm
from app.assess.forms.resolve_flag_form import ResolveFlagForm
from app.assess.forms.scores_and_justifications import ScoreForm
from app.assess.helpers import determine_display_status
from app.assess.helpers import resolve_application
from app.assess.models.flag import FlagType
from app.assess.models.theme import Theme
from app.assess.models.ui import applicants_response
from app.assess.models.ui.assessor_task_list import AssessorTaskList
from app.assess.status import all_status_completed
from app.assess.status import update_ar_status_to_completed
from config import Config
from flask import abort
from flask import Blueprint
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from fsd_utils.authentication.decorators import login_required


assess_bp = Blueprint(
    "assess_bp",
    __name__,
    url_prefix=Config.ASSESSMENT_HUB_ROUTE,
    template_folder="templates",
)


@assess_bp.route(
    "/application_id/<application_id>/sub_criteria_id/<sub_criteria_id>",
    methods=["POST", "GET"],
)
def display_sub_criteria(
    application_id,
    sub_criteria_id,
):
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
                "assess_bp.display_sub_criteria",
                application_id=application_id,
                sub_criteria_id=sub_criteria_id,
                theme_id=theme_id,
                _anchor="comments",
            )
        )

    fund = get_fund(Config.COF_FUND_ID)
    flag = get_latest_flag(application_id)
    comments = get_comments(
        application_id=application_id,
        sub_criteria_id=sub_criteria_id,
        theme_id=theme_id,
        themes=sub_criteria.themes,
    )

    determine_display_status(sub_criteria, flag)
    common_template_config = {
        "current_theme_id": theme_id,
        "sub_criteria": sub_criteria,
        "application_id": application_id,
        "fund": fund,
        "comments": comments,
        "is_flagged": bool(flag),
        "display_comment_box": add_comment_argument,
        "comment_form": comment_form,
        "current_theme": current_theme,
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
        **common_template_config,
    )


@assess_bp.route(
    "/application_id/<application_id>/sub_criteria_id/<sub_criteria_id>/score",
    methods=["POST", "GET"],
)
@login_required(roles_required=["LEAD_ASSESSOR", "ASSESSOR"])
def score(
    application_id,
    sub_criteria_id,
):
    sub_criteria: SubCriteria = get_sub_criteria(
        application_id, sub_criteria_id
    )

    if not sub_criteria.is_scored:
        abort(404)
    fund = get_fund(Config.COF_FUND_ID)
    flag = get_latest_flag(application_id)
    comments = get_comments(
        application_id=application_id,
        sub_criteria_id=sub_criteria_id,
        theme_id=None,
        themes=sub_criteria.themes,
    )
    # TODO: Refactor this function so it doesn't rely on side-effects
    # and mutating SubCriteria model
    determine_display_status(sub_criteria, flag)
    score_form = ScoreForm()
    rescore_form = RescoreForm()
    is_rescore = rescore_form.validate_on_submit()
    if not is_rescore and request.method == "POST":
        if score_form.validate_on_submit():
            current_app.logger.info(f"Processing POST to {request.path}.")
            score = int(score_form.score.data)
            user_id = g.account_id
            justification = score_form.justification.data
            submit_score_and_justification(
                score=score,
                justification=justification,
                application_id=application_id,
                user_id=user_id,
                sub_criteria_id=sub_criteria_id,
            )
        else:
            is_rescore = True

    # call to assessment store to get latest score
    score_list = get_score_and_justification(
        application_id, sub_criteria_id, score_history=True
    )
    latest_score = (
        score_list.pop(0)
        if (score_list is not None and len(score_list) > 0)
        else None
    )
    # TODO make COF_score_list extendable to other funds
    COF_score_list = [
        (5, "Strong"),
        (4, "Good"),
        (3, "Satisfactory"),
        (2, "Partial"),
        (1, "Poor"),
    ]
    return render_template(
        "score.html",
        application_id=application_id,
        score_list=score_list or None,
        latest_score=latest_score,
        COF_score_list=COF_score_list,
        score_form=score_form,
        rescore_form=rescore_form,
        is_rescore=is_rescore,
        sub_criteria=sub_criteria,
        fund=fund,
        comments=comments,
    )


@assess_bp.route(
    "/flag/<application_id>",
    methods=["GET", "POST"],
)
@login_required(roles_required=["ASSESSOR"])
def flag(application_id):

    form = FlagApplicationForm()

    if request.method == "POST" and form.validate_on_submit():
        submit_flag(
            application_id,
            FlagType.FLAGGED.name,
            g.account_id,
            form.justification.data,
            form.section.data,
        )
        return redirect(
            url_for(
                "assess_bp.application",
                application_id=application_id,
            )
        )

    flag = get_latest_flag(application_id)
    if flag and flag.flag_type not in (
        FlagType.RESOLVED,
        FlagType.QA_COMPLETED,
    ):
        abort(400, "Application already flagged")
    banner_state = get_banner_state(application_id)
    fund = get_fund(banner_state.fund_id)

    return render_template(
        "flag_application.html",
        application_id=application_id,
        fund_name=fund.name,
        banner_state=banner_state,
        form=form,
        referrer=request.referrer,
    )


@assess_bp.route("/qa_complete/<application_id>", methods=["GET", "POST"])
@login_required(roles_required=["LEAD_ASSESSOR"])
def qa_complete(application_id):
    """
    QA complete form html page:
    Allows you to mark an application as QA_completed by submitting the form.
    Once submitted, a call is made to the application store endpoint to save
    the QA_COMPLETED flag in the database for the given application_id
    """

    form = MarkQaCompleteForm()

    if form.validate_on_submit():
        submit_flag(
            application_id=application_id,
            flag_type=FlagType.QA_COMPLETED.name,
            user_id=g.account_id,
        )
        return redirect(
            url_for(
                "assess_bp.application",
                application_id=application_id,
            )
        )

    banner_state = get_banner_state(application_id)
    fund = get_fund(banner_state.fund_id)

    return render_template(
        "mark_qa_complete.html",
        application_id=application_id,
        fund_name=fund.name,
        banner_state=banner_state,
        form=form,
        referrer=request.referrer,
    )


@assess_bp.route("/assessor_dashboard/", methods=["GET"])
def landing():
    """
    Landing page for assessors
    Provides a summary of available applications
    with a keyword searchable and filterable list
    of applications and their statuses
    """

    search_params = {
        "search_term": "",
        "search_in": "project_name,short_id",
        "asset_type": "ALL",
        "status": "ALL",
    }

    show_clear_filters = False
    if "clear_filters" not in request.args:
        # Add request arg search params to dict
        for key, value in request.args.items():
            if key in search_params:
                search_params.update({key: value})
                show_clear_filters = True

    application_overviews = get_application_overviews(
        Config.COF_FUND_ID, Config.COF_ROUND2_ID, search_params
    )
    assessment_deadline = get_round(
        Config.COF_FUND_ID, Config.COF_ROUND2_ID
    ).assessment_deadline

    stats = get_assessments_stats(Config.COF_FUND_ID, Config.COF_ROUND2_ID)

    post_processed_overviews = (
        (
            get_assessment_progress(application_overviews)
            if application_overviews
            else []
        )
        # TODO: remove this when we have local data for post requests.
        if not Config.USE_LOCAL_DATA
        else application_overviews
    )

    return render_template(
        "assessor_dashboard.html",
        user=g.user,
        application_overviews=post_processed_overviews,
        assessment_deadline=assessment_deadline,
        query_params=search_params,
        asset_types=asset_types,
        assessment_statuses=assessment_statuses,
        show_clear_filters=show_clear_filters,
        stats=stats,
    )


@assess_bp.route("/application/<application_id>", methods=["GET", "POST"])
def application(application_id):
    """
    Application summary page
    Shows information about the fund, application ID
    and all the application questions and their assessment status
    :param application_id:
    :return:
    """
    assessor_task_list_metadata = get_assessor_task_list_state(application_id)
    if not assessor_task_list_metadata:
        abort(404)

    # maybe there's a better way to do this?..
    fund = get_fund(assessor_task_list_metadata["fund_id"])
    if not fund:
        abort(404)
    assessor_task_list_metadata["fund_name"] = fund.name

    state = AssessorTaskList.from_json(assessor_task_list_metadata)
    flag = get_latest_flag(application_id)
    if flag:
        accounts = get_bulk_accounts_dict([flag.user_id])

    sub_criteria_status_completed = all_status_completed(state)
    form = AssessmentCompleteForm()

    if request.method == "POST":
        update_ar_status_to_completed(application_id)
        assessor_task_list_metadata = get_assessor_task_list_state(
            application_id
        )
        if not assessor_task_list_metadata:
            abort(404)
        fund = get_fund(assessor_task_list_metadata["fund_id"])
        if not fund:
            abort(404)
        assessor_task_list_metadata["fund_name"] = fund.name
        state = AssessorTaskList.from_json(assessor_task_list_metadata)

    determine_display_status(state, flag)
    return render_template(
        "assessor_tasklist.html",
        sub_criteria_status_completed=sub_criteria_status_completed,
        form=form,
        state=state,
        application_id=application_id,
        flag=flag,
        current_user_role=g.user.highest_role,
        flag_user_info=accounts.get(flag.user_id) if flag else None,
    )


@assess_bp.route("/fragments/sub_criteria_scoring", methods=["POST", "GET"])
def sub_crit_scoring():
    form = ScoreForm()

    if form.validate_on_submit():

        score = int(form.score.data)
        just = form.justification.data

        assessment_id = "test_assess_id"
        person_id = "test_person_id"
        sub_crit_id = "test_sub_crit_id"

        submit_score_and_justification(
            score=score,
            assessment_id=assessment_id,
            person_id=person_id,
            justification=just,
            sub_crit_id=sub_crit_id,
        )
        scores_submitted = True
    else:
        scores_submitted = False

    return render_template(
        "scores_justification.html",
        scores_submitted=scores_submitted,
        form=form,
    )


@assess_bp.route("/file/<application_id>/<file_name>", methods=["GET"])
def get_file(application_id: str, file_name: str):

    response = get_file_response(
        application_id=application_id, file_name=file_name
    )

    return response


@assess_bp.route("/resolve_flag/<application_id>", methods=["GET", "POST"])
@login_required(roles_required=["LEAD_ASSESSOR"])
def resolve_flag(application_id):
    form = ResolveFlagForm()
    section = request.args.get("section_id", "section not specified")
    return resolve_application(
        form=form,
        application_id=application_id,
        flag=form.resolution_flag.data,
        user_id=g.account_id,
        justification=form.justification.data,
        section=section,
        page_to_render="resolve_flag.html",
    )


@assess_bp.route(
    "/continue_assessment/<application_id>", methods=["GET", "POST"]
)
@login_required(roles_required=["LEAD_ASSESSOR"])
def continue_assessment(application_id):
    form = ContinueApplicationForm()
    return resolve_application(
        form=form,
        application_id=application_id,
        flag=FlagType.RESOLVED.name,
        user_id=g.account_id,
        justification=form.reason.data,
        section="NA",
        page_to_render="continue_assessment.html",
    )


@assess_bp.route("/generate_docs", methods=["POST"])
@login_required(roles_required=["LEAD_ASSESSOR", "ASSESSOR"])
def generate_docs_for_download():
    application_id = request.form.get("application_id")
    current_app.logger.info(
        f"Generating docs for application id {application_id}"
    )
    state = get_banner_state(application_id)
    latest_flag = get_latest_flag(application_id)
    if latest_flag:
        determine_display_status(state, latest_flag)

    fund = get_fund(state.fund_id)
    return render_template(
        "contract_downloads.html",
        application_id=application_id,
        fund_name=fund.name,
        state=state,
    )
