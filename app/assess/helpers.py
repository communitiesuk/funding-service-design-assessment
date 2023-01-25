from app.assess.data import get_banner_state
from app.assess.data import get_fund
from app.assess.data import get_latest_flag
from app.assess.data import submit_flag
from app.assess.models.flag import FlagType
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for


def determine_display_status(state, latest_flag=None):
    """
    Deduce whether to override display_status with a
    flag.
    """
    if not latest_flag:
        state.display_status = state.workflow_status
    elif latest_flag and latest_flag.flag_type == FlagType.RESOLVED:
        state.display_status = state.workflow_status
        state.flag_resolved = True
    else:
        state.display_status = latest_flag.flag_type.name


def resolve_application(
    form, application_id, flag, justification, section, page_to_render
):
    if request.method == "POST" and form.validate_on_submit():
        submit_flag(application_id, flag, justification, section)
        return redirect(
            url_for(
                "assess_bp.application",
                application_id=application_id,
            )
        )
    state = get_banner_state(application_id)
    latest_flag = get_latest_flag(application_id)
    if latest_flag:
        determine_display_status(state, latest_flag)

    fund = get_fund(state.fund_id)
    return render_template(
        page_to_render,
        application_id=application_id,
        fund_name=fund.name,
        state=state,
        form=form,
        referrer=request.referrer,
    )
