from app.assess.data import get_application
from app.assess.data import get_fund
from app.assess.data import get_funds
from app.assess.data import get_questions
from app.assess.data import get_round
from app.assess.data import get_rounds
from app.assess.status import get_status
from app.config import ASSESSMENT_HUB_ROUTE
from flask import abort
from flask import Blueprint
from flask import render_template

assess_bp = Blueprint(
    "assess_bp",
    __name__,
    url_prefix=ASSESSMENT_HUB_ROUTE,
    template_folder="templates",
)


@assess_bp.route("/", methods=["GET"])
def funds():

    funds = get_funds()

    return render_template("funds.html", funds=funds)


@assess_bp.route("/<fund_id>/", methods=["GET"])
def fund(fund_id: str):

    fund = get_fund(fund_id)
    if not fund:
        abort(404)

    rounds = get_rounds(fund_id)

    return render_template("fund.html", fund=fund, rounds=rounds)


@assess_bp.route("/<fund_id>/<round_id>/", methods=["GET"])
def fund_round(fund_id: str, round_id: str):

    fund = get_fund(fund_id)
    if not fund:
        abort(404)

    fund_round = get_round(fund_id=fund_id, round_id=round_id)
    if not fund_round:
        abort(404)

    return render_template("round.html", fund=fund, round=fund_round)


@assess_bp.route(
    "/<fund_id>/<round_id>/application/<application_id>", methods=["GET"]
)
def application(fund_id: str, round_id: str, application_id: str):
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
        "application.html",
        fund=fund,
        round=fund_round,
        application=application,
    )


@assess_bp.route(
    "/view_application/<fund_id>/<round_id>/<application_id>", methods=["GET"]
)
def view_application(application_id, fund_id, round_id):
    """_summary_:
    GIVEN route is a front end for General assessment of the
    applications, questions & its statuses

    Args:
        application_id: Takes an application ID.
        fund_id: Takes a fund ID.
        round_id: Takes a round ID.

    Returns:
        Returns question name, its status & number of questions are
        completed & not completed.
    """
    fund_data = get_fund(fund_id)
    if not fund_data:
        abort(404)

    round_data = get_round(fund_id=fund_id, round_id=round_id)
    if not round_data:
        abort(404)

    application_data = get_application(
        fund_id=fund_id, identifier=application_id
    )
    if not application_data:
        abort(404)

    questions_data = get_questions(application_id)
    status_data = get_status(questions_data)
    print(status_data)

    return render_template(
        "project_summary.html",
        application_data=application_data,
        fund_data=fund_data,
        round_data=round_data,
        questions_data=questions_data,
        status_data=status_data,
    )
