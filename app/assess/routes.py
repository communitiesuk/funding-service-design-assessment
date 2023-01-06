from app.assess.data import *
from app.assess.data import get_application_overviews
from app.assess.data import submit_score_and_justification
from app.assess.display_value_mappings import assessment_statuses
from app.assess.display_value_mappings import asset_types
from app.assess.forms.comments_form import CommentsForm
from app.assess.forms.flag_form import FlagApplicationForm
from app.assess.forms.scores_and_justifications import ScoreForm
from app.assess.models.ui import applicants_response
from app.assess.models.ui.assessor_task_list import AssessorTaskList
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
    is_flagged = any(get_flags(application_id))

    comments = get_comments(
        application_id=application_id,
        sub_criteria_id=sub_criteria_id,
        theme_id=theme_id,
        themes=sub_criteria.themes,
    )

    common_template_config = {
        "current_theme_id": theme_id,
        "sub_criteria": sub_criteria,
        "application_id": application_id,
        "fund": fund,
        "comments": comments,
        "is_flagged": is_flagged,
        "display_comment_box": add_comment_argument,
        "comment_form": comment_form,
    }

    if theme_id == "score":
        # SECURITY SECTION START ######
        # Prevent non-assessors from accessing
        # the scoring version of this page
        if g.user.highest_role not in [
            "LEAD_ASSESSOR",
            "ASSESSOR",
        ]:
            current_app.logger.info(
                "Non-assessor attempted to access scoring view"
                f" {request.path}."
            )
            abort(404)
        # SECURITY SECTION END ######

        form = ScoreForm()
        score_error = justification_error = scores_submitted = False
        if request.method == "POST":
            current_app.logger.info(f"Processing POST to {request.path}.")
            if form.validate_on_submit():
                score = int(form.score.data)
                justification = form.justification.data
                user_id = g.account_id
                submit_score_and_justification(
                    score=score,
                    justification=justification,
                    application_id=application_id,
                    user_id=user_id,
                    sub_criteria_id=sub_criteria_id,
                )
                scores_submitted = True

            else:
                score_error = True if not form.score.data else False
                justification_error = (
                    True if not form.justification.data else False
                )
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
            "sub_criteria.html",
            on_summary=True,
            score_list=score_list or None,
            latest_score=latest_score,
            COF_score_list=COF_score_list,
            scores_submitted=scores_submitted,
            score_error=score_error,
            justification_error=justification_error,
            form=form,
            **common_template_config,
        )

    theme_answers_response = get_sub_criteria_theme_answers(
        application_id, theme_id
    )
    answers_meta = applicants_response.create_ui_components(
        theme_answers_response, application_id
    )

    return render_template(
        "sub_criteria.html",
        on_summary=False,
        answers_meta=answers_meta,
        **common_template_config,
    )


@assess_bp.route(
    "/flag/<application_id>",
    methods=["GET", "POST"],
)
@login_required(roles_required=["ASSESSOR", "LEAD_ASSESSOR"])
def flag(application_id):
    # TODO: handle multiple flags.
    flags = get_flags(application_id)
    if any(flags):
        abort(400, "Application already flagged")

    form = FlagApplicationForm()

    if request.method == "POST" and form.validate_on_submit():
        submit_flag(application_id, form.reason.data, form.section.data)
        return redirect(
            url_for(
                "assess_bp.application",
                application_id=application_id,
            )
        )

    banner_state = get_banner_state(application_id)
    fund = get_fund(banner_state["fund_id"])

    return render_template(
        "flag_application.html",
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

    return render_template(
        "assessor_dashboard.html",
        user=g.user,
        application_overviews=application_overviews,
        assessment_deadline=assessment_deadline,
        query_params=search_params,
        asset_types=asset_types,
        assessment_statuses=assessment_statuses,
        show_clear_filters=show_clear_filters,
    )


@assess_bp.route("/application/<application_id>", methods=["GET"])
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
    current_app.logger.info(
        f"Fetching data from '{assessor_task_list_metadata}'."
    )

    flags = get_flags(application_id)
    flag = flags[0] if flags else None  # TODO: handle multiple flags?

    accounts = {}
    if flag:
        state.workflow_status = "FLAGGED"
        accounts = get_bulk_accounts_dict([flag.user_id])

    return render_template(
        "assessor_tasklist.html",
        state=state,
        application_id=application_id,
        flag=flag,
        flag_user_info=accounts.get(flag.user_id) if flag else None,
    )


@assess_bp.route("/comments/", methods=["GET", "POST"])
def comments():
    """
    example route to call macro for text area field
    """
    form = CommentsForm()

    if form.validate_on_submit():
        comment_data = form.comment.data
        return render_template(
            "macros/example_comments_template.html",
            form=form,
            comment_data=comment_data,
        )

    return render_template("macros/example_comments_template.html", form=form)


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
