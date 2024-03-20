from flask import Blueprint
from flask import abort
from flask import current_app
from flask import g
from flask import render_template
from flask import request

from app.blueprints.authentication.validation import check_access_application_id
from app.blueprints.flagging.helpers import get_flags
from app.blueprints.scoring.forms.rescore_form import RescoreForm
from app.blueprints.scoring.helpers import get_scoring_class
from app.blueprints.services.data_services import get_comments
from app.blueprints.services.data_services import get_score_and_justification
from app.blueprints.services.data_services import get_sub_criteria
from app.blueprints.services.data_services import match_comment_to_theme
from app.blueprints.services.data_services import match_score_to_user_account
from app.blueprints.services.data_services import submit_score_and_justification
from app.blueprints.services.models.sub_criteria import SubCriteria
from app.blueprints.services.shared_data_helpers import get_state_for_tasklist_banner
from app.blueprints.shared.helpers import determine_assessment_status
from app.blueprints.shared.helpers import determine_flag_status
from config import Config

scoring_bp = Blueprint(
    "scoring_bp",
    __name__,
    url_prefix=Config.ASSESSMENT_HUB_ROUTE,
    template_folder="templates",
)


@scoring_bp.route(
    "/application_id/<application_id>/sub_criteria_id/<sub_criteria_id>/score",
    methods=["POST", "GET"],
)
@check_access_application_id(roles_required=["LEAD_ASSESSOR", "ASSESSOR"])
def score(
    application_id,
    sub_criteria_id,
):
    sub_criteria: SubCriteria = get_sub_criteria(application_id, sub_criteria_id)

    if not sub_criteria.is_scored:
        abort(404)

    state = get_state_for_tasklist_banner(application_id)
    flags_list = get_flags(application_id)

    score_form = get_scoring_class(state.round_id)()
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
            # re-get sub_criteria to have updated status.
            sub_criteria: SubCriteria = get_sub_criteria(
                application_id, sub_criteria_id
            )
        else:
            is_rescore = True

    comment_response = get_comments(
        application_id=application_id,
        sub_criteria_id=sub_criteria_id,
        theme_id=None,
    )

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

    # call to assessment store to get latest score.
    score_list = get_score_and_justification(
        application_id, sub_criteria_id, score_history=True
    )
    # TODO add test for this function in data_operations
    scores_with_account_details = match_score_to_user_account(
        score_list, state.fund_short_name
    )
    latest_score = (
        scores_with_account_details.pop(0)
        if (score_list is not None and len(scores_with_account_details) > 0)
        else None
    )
    # TODO make COF_score_list extendable to other funds.

    return render_template(
        "score.html",
        application_id=application_id,
        score_list=scores_with_account_details or None,
        latest_score=latest_score,
        score_form=score_form,
        rescore_form=rescore_form,
        is_rescore=is_rescore,
        sub_criteria=sub_criteria,
        state=state,
        comments=theme_matched_comments,
        flag_status=flag_status,
        assessment_status=assessment_status,
        is_flaggable=False,  # Flag button is disabled in sub-criteria page
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
    )
