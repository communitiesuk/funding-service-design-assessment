from app.assess.data import APPLICATION_SEARCH_ENDPOINT
from app.assess.data import get_application
from app.assess.data import get_applications
from app.assess.data import get_fund
from app.assess.data import get_funds
from app.assess.data import get_questions
from app.assess.data import get_round
from app.assess.data import get_rounds
from app.assess.data import get_todo_summary
from app.assess.status import get_status
from app.config import APPLICATION_STORE_API_HOST_PUBLIC
from app.config import ASSESSMENT_HUB_ROUTE
from flask import abort
from flask import Blueprint
from flask import render_template
from flask import request

assess_bp = Blueprint(
    "assess_bp",
    __name__,
    url_prefix=ASSESSMENT_HUB_ROUTE,
    template_folder="templates",
)


@assess_bp.route("/", methods=["GET"])
def funds():
    """
    Page showing available funds
    from fund store
    :return:
    """

    funds = get_funds()

    return render_template("funds.html", funds=funds)


@assess_bp.route("/landing/", methods=["GET"])
def landing():
    """
    Landing page for assessors
    Provides a summary of available applications
    with a keyword searchable and filterable list
    of applications and their statuses
    """

    # Initialise empty search params
    search_params = {
        "id_contains": "",
        "order_by": "",
        "order_rev": "",
        "status_only": "",
    }

    # Add request arg search params to dict
    for key, value in request.args.items():
        if key in search_params:
            search_params.update({key: value})

    # Get from application store
    applications = get_applications(params=search_params)

    todo_summary = get_todo_summary()

    return render_template(
        "landing.html",
        applications=applications,
        search_params=search_params,
        todo_summary=todo_summary,
        application_search_endpoint="".join(
            [
                APPLICATION_STORE_API_HOST_PUBLIC,
                APPLICATION_SEARCH_ENDPOINT.replace("{params}", ""),
            ]
        ),
    )


@assess_bp.route("/<fund_id>/", methods=["GET"])
def fund(fund_id: str):
    """
    Page showing available rounds for a given fund
    from round store
    :param fund_id:
    :return:
    """

    fund = get_fund(fund_id)
    if not fund:
        abort(404)

    rounds = get_rounds(fund_id)

    return render_template("fund.html", fund=fund, rounds=rounds)


@assess_bp.route("/<fund_id>/<round_id>/", methods=["GET"])
def fund_round(fund_id: str, round_id: str):
    """
    Page showing available applications
    from a given fund_id and round_id
    from the application store
    :param fund_id:
    :param round_id:
    :return:
    """

    fund = get_fund(fund_id)
    if not fund:
        abort(404)

    fund_round = get_round(fund_id=fund_id, round_id=round_id)
    if not fund_round:
        abort(404)

    return render_template("round.html", fund=fund, round=fund_round)


@assess_bp.route("/application/<fund_id>/<application_id>", methods=["GET"])
def application(application_id, fund_id):

    """
    Application summary page
    Shows information about the fund, application ID
    and all the application questions and their assessment status
    :param application_id:
    :param fund_id:
    :return:
    """
    fund_data = get_fund(fund_id)
    if not fund_data:
        abort(404)

    application_data = get_application(
        fund_id=fund_id, identifier=application_id
    )
    if not application_data:
        abort(404)

    questions_data = get_questions(application_id, fund_id)
    status_data = get_status(questions_data)

    return render_template(
        "application.html",
        application_data=application_data,
        fund_data=fund_data,
        questions_data=questions_data,
        status_data=status_data,
    )


@assess_bp.route(
    "/<fund_id>/<round_id>/application/<application_id>", methods=["GET"]
)
def application_deprecated(fund_id: str, round_id: str, application_id: str):
    """
    DEPRECATED summary page for an application
    :param fund_id:
    :param round_id:
    :param application_id:
    :return:
    """
    fund = get_fund(fund_id)
    if not fund:
        abort(404)

    fund_round = get_round(fund_id=fund_id, round_id=round_id)
    if not fund_round:
        abort(404)

    application = get_application(fund_id=fund_id, identifier=application_id)
    if not application:
        abort(404)

    return render_template(
        "application_deprecated.html",
        fund=fund,
        round=fund_round,
        application=application,
    )
