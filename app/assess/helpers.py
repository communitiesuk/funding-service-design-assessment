import time
from typing import Optional

from app.assess.data import get_fund
from app.assess.data import get_latest_flag
from app.assess.data import get_sub_criteria_banner_state
from app.assess.data import submit_flag
from app.assess.models.flag import Flag
from app.assess.models.flag import FlagType
from app.assess.models.flag_v2 import FlagTypeV2
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for


def get_ttl_hash(seconds=3600) -> int:
    return round(time.time() / seconds)


def get_application_id_from_request() -> str | None:
    application_id = (
        request.view_args.get("application_id")
        or request.view_args.get("application")
        or request.args.get("application_id")
        or request.args.get("application")
    )
    return application_id


def get_fund_short_name_from_request() -> str | None:
    fund_short_name = (
        request.view_args.get("fund_short_name")
        or request.view_args.get("fund_short_name")
        or request.args.get("fund_short_name")
        or request.args.get("fund_short_name")
    )
    return fund_short_name


def determine_display_status(
    workflow_status: str,
    latest_flag: Optional[Flag] = None,
) -> str:
    """
    Deduce whether to override display_status with a
    flag.
    """
    if latest_flag:
        status = (
            FlagType(getattr(latest_flag, "flag_type")).name
            if getattr(latest_flag, "flag_type", None)
            else FlagTypeV2(getattr(latest_flag, "latest_status")).name
        )
        if status and status == "RESOLVED":
            return workflow_status
        return status
    else:
        return workflow_status


def is_flaggable(latest_flag: Optional[Flag]):
    return not latest_flag or (
        latest_flag.flag_type in [FlagType.RESOLVED, FlagType.QA_COMPLETED]
    )


def set_application_status_in_overview(application_overviews):
    """Add the 'application_status' key and return the modified list of application overviews."""
    for overview in application_overviews:
        if overview["is_qa_complete"] and not overview["flags"][-1][
            "flag_type"
        ] in ["FLAGGED", "STOPPED"]:
            status = "QA_COMPLETED"
        elif len(overview["flags"]) > 1:
            status = "MULTIPLE_FLAGS"
        elif (
            overview["flags"]
            and overview["flags"][-1]["flag_type"] == "STOPPED"
        ):
            status = overview["flags"][-1]["flag_type"]
        elif (
            overview["flags"]
            and overview["flags"][-1]["flag_type"] == "FLAGGED"
        ):
            status = overview["flags"][-1]["flag_type"]
        else:
            status = overview["workflow_status"]
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
        submit_flag(application_id, flag, user_id, justification, section)
        return redirect(
            url_for(
                "assess_bp.application",
                application_id=application_id,
            )
        )
    sub_criteria_banner_state = get_sub_criteria_banner_state(application_id)
    latest_flag = get_latest_flag(application_id)
    if latest_flag:
        display_status = determine_display_status(
            sub_criteria_banner_state.workflow_status, latest_flag
        )

    fund = get_fund(sub_criteria_banner_state.fund_id)
    return render_template(
        page_to_render,
        application_id=application_id,
        fund=fund,
        sub_criteria=sub_criteria_banner_state,
        form=form,
        referrer=request.referrer,
        display_status=display_status,
        state=state,
        sections_to_flag=section,
        reason_to_flag=reason_to_flag,
        allocated_team=allocated_team,
    )
