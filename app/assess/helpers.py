import concurrent
import csv
import time
from io import StringIO
from typing import List

from app.assess.data import get_associated_tags_for_application
from app.assess.data import get_flags
from app.assess.data import get_fund
from app.assess.data import get_sub_criteria_banner_state
from app.assess.data import get_tag_types
from app.assess.data import submit_flag
from app.assess.display_value_mappings import assessment_statuses
from app.assess.models.flag_v2 import FlagTypeV2
from app.assess.models.flag_v2 import FlagV2
from app.assess.models.fund import Fund
from app.assess.models.ui.common import Option
from app.assess.models.ui.common import OptionGroup
from config import Config
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from fsd_utils.mapping.application.application_utils import simplify_title


def get_ttl_hash(seconds=3600) -> int:
    return round(time.time() / seconds)


def get_value_from_request(parameter_names) -> str | None:
    for parameter_name in parameter_names:
        value = request.view_args.get(parameter_name) or request.args.get(
            parameter_name
        )
        if value:
            return value


def determine_flag_status(Flags: List[FlagV2]) -> str:
    flag_status = ""
    flags_list = (
        [
            (FlagV2.from_dict(flag) if isinstance(flag, dict) else flag)
            for flag in Flags
        ]
        if Flags
        else []
    )
    all_latest_status = [flag.latest_status for flag in flags_list]

    if FlagTypeV2.STOPPED in all_latest_status:
        flag_status = "Stopped"
    elif all_latest_status.count(FlagTypeV2.RAISED) > 1:
        flag_status = "Multiple flags to resolve"
    elif all_latest_status.count(FlagTypeV2.RAISED) == 1:
        for flag in flags_list:
            if flag.latest_status == FlagTypeV2.RAISED:
                flag_status = (
                    ("Flagged for " + flag.latest_allocation)
                    if flag.latest_allocation
                    else "Flagged"
                )
    return flag_status


def determine_display_status(
    workflow_status: str, Flags: List[FlagV2], is_qa_complete: bool
) -> str:
    flag_status = determine_flag_status(Flags)
    if flag_status:
        display_status = flag_status
    elif is_qa_complete:
        display_status = "QA complete"
    else:
        display_status = assessment_statuses[workflow_status]

    return display_status


def determine_assessment_status(
    workflow_status: str, is_qa_complete: bool
) -> str:
    if is_qa_complete:
        assessment_status = "QA complete"
    else:
        assessment_status = assessment_statuses[workflow_status]

    return assessment_status


def is_flaggable(flag_status: str):
    return flag_status != "Stopped"


def is_qa_complete(Flags: List[FlagV2]) -> bool:
    # TODO: Rework on this when QA_COMPLETED is moved to assessment enum type
    flags_list = (
        [
            (FlagV2.from_dict(flag) if isinstance(flag, dict) else flag)
            for flag in Flags
        ]
        if Flags
        else []
    )
    all_latest_status = [flag.latest_status for flag in flags_list]
    return FlagTypeV2.QA_COMPLETED in all_latest_status or False


def set_application_status_in_overview(application_overviews):
    """Add the 'application_status' key and return the modified list of application overviews."""
    for overview in application_overviews:
        display_status = determine_display_status(
            overview["workflow_status"],
            overview["flags_v2"],
            overview["is_qa_complete"],
        )
        status = ""
        for key, val in assessment_statuses.items():
            if val == display_status:
                status = key
                break
        if not status:
            status = display_status
        overview["application_status"] = status

    return application_overviews


def resolve_application(
    form,
    application_id,
    flag,
    user_id,
    justification,
    section,
    page_to_render,
    state=None,
    reason_to_flag="",
    allocated_team="",
    flag_id="",
):
    """This function is used to resolve an application
      by submitting a flag, justification, and section for the application.

    Args:
        form (obj): Form object to be validated and submitted
        application_id (int): ID of the application
        flag (str): Flag submitted for the application
        justification (str): Justification for the flag submitted
        section (str): Section of the application the flag is submitted for
        page_to_render (str): Template name to be rendered

    Returns:
        redirect: Redirects to the application page if the request method is
                  "POST" and form is valid.
        render_template: Renders the specified template with the
                         application_id, fund_name, state, form, and referrer
                         as parameters.
    """
    if request.method == "POST" and form.validate_on_submit():
        submit_flag(
            application_id,
            flag,
            user_id,
            justification,
            section,
            allocated_team,
            flag_id,
        )
        return redirect(
            url_for(
                "assess_bp.application",
                application_id=application_id,
            )
        )
    sub_criteria_banner_state = get_sub_criteria_banner_state(application_id)
    flags_list = get_flags(application_id)
    assessment_status = determine_assessment_status(
        state.workflow_status
        if state
        else sub_criteria_banner_state.workflow_status,
        flags_list,
    )
    flag_status = determine_flag_status(flags_list)

    fund = get_fund(sub_criteria_banner_state.fund_id)
    return render_template(
        page_to_render,
        application_id=application_id,
        fund=fund,
        sub_criteria=sub_criteria_banner_state,
        form=form,
        referrer=request.referrer,
        assessment_status=assessment_status,
        flag_status=flag_status,
        state=state,
        sections_to_flag=section,
        reason_to_flag=reason_to_flag,
        allocated_team=allocated_team,
    )


def generate_csv_of_application(q_and_a: dict, fund: Fund, application_json):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fund", fund.name, fund.id])
    writer.writerow(
        [
            "Application",
            application_json["short_id"],
            application_json["application_id"],
        ]
    )
    writer.writerow(["Section", "Question", "Answer"])
    for section_name, values in q_and_a.items():
        section_title = simplify_title(section_name, remove_text=["cof", "ns"])
        section_title = " ".join(section_title).capitalize()
        for questions, answers in values.items():
            if (
                answers
                and isinstance(answers, str)
                and answers.startswith("- ")
            ):
                answers = f"'{answers}"

            if not answers:
                answers = "Not provided"

            writer.writerow([section_title, questions, answers])
    return output.getvalue()


def generate_applicant_info_csv(applicant_info: dict):
    for index, person_data in enumerate(applicant_info):
        output = StringIO()

        headers = list(person_data.keys())

        rows = list(person_data.values())

        csv_writer = csv.writer(output)

        csv_writer.writerow(headers)
        csv_writer.writerow(rows)
    return output.getvalue()


def get_tag_map_and_tag_options(fund_round_tags, post_processed_overviews):
    tag_types = get_tag_types()
    tag_option_groups = []
    for purposes in Config.TAGGING_FILTER_CONFIG:
        tag_type_ids = [
            tag_type.id
            for tag_type in tag_types
            if tag_type.purpose in purposes
        ]
        tag_option_groups.append(
            OptionGroup(
                label=", ".join(p.capitalize() for p in purposes),
                options=sorted(
                    [
                        Option(value=tag.id, text_content=tag.value)
                        for tag in fund_round_tags
                        if tag.type_id in tag_type_ids
                    ],
                    key=lambda option: option.text_content,
                ),
            )
        )

    def _get_tags_with_app_context(application_id):
        from app import app

        with app.app_context():
            return get_associated_tags_for_application(application_id)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        tag_map_futures = {
            overview["application_id"]: executor.submit(
                _get_tags_with_app_context, overview["application_id"]
            )
            for overview in post_processed_overviews
        }
        tag_map = {
            application_id: future.result()
            for application_id, future in tag_map_futures.items()
        }

    return tag_map, tag_option_groups
