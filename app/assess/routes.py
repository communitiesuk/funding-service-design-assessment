from app.assess.data import get_application
from app.assess.data import get_fund
from app.assess.data import get_funds
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

    return render_template("fund.html", fund=fund)


@assess_bp.route("/<fund_id>/application/<application_id>", methods=["GET"])
def application(fund_id: str, application_id: str):
    fund = get_fund(fund_id)
    if not fund:
        abort(404)

    application = get_application(fund_id=fund_id, identifier=application_id)
    if not application:
        abort(404)

    return render_template(
        "application.html",
        fund=fund,
        application=application,
    )
