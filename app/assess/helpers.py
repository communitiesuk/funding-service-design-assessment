from enum import Flag
from typing import Optional

from app.assess.data import get_banner_state
from app.assess.data import get_fund
from app.assess.data import get_latest_flag
from app.assess.data import submit_flag
from app.assess.models.flag import FlagType
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for


def determine_display_status(
    workflow_status: str,
    latest_flag: Optional[Flag] = None,
) -> str:
    """
    Deduce whether to override display_status with a
    flag.
    """
    if not latest_flag or (
        latest_flag and latest_flag.flag_type == FlagType.RESOLVED
    ):
        return workflow_status
    else:
        return latest_flag.flag_type.name


def resolve_application(
    form, application_id, flag, user_id, justification, section, page_to_render
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
        redirect: Redirects to the application page if the request method is "POST" and form is valid. # noqa: E501
        render_template: Renders the specified template with the application_id, fund_name, state, form, and referrer as parameters. # noqa: E501
    """
    if request.method == "POST" and form.validate_on_submit():
        submit_flag(application_id, flag, user_id, justification, section)
        return redirect(
            url_for(
                "assess_bp.application",
                application_id=application_id,
            )
        )
    state = get_banner_state(application_id)
    latest_flag = get_latest_flag(application_id)
    if latest_flag:
        display_status = determine_display_status(
            state.workflow_status, latest_flag
        )

    fund = get_fund(state.fund_id)
    return render_template(
        page_to_render,
        application_id=application_id,
        fund_name=fund.name,
        state=state,
        form=form,
        referrer=request.referrer,
        display_status=display_status,
    )
