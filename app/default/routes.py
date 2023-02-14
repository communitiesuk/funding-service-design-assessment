from app.assess.data import get_default_round_data
from config import Config
from flask import Blueprint
from flask import render_template

default_bp = Blueprint("default_bp", __name__, template_folder="templates")


@default_bp.route("/")
def index():
    return render_template(
        "index.html",
        login_url=Config.SSO_LOGIN_URL,
        logout_url=Config.SSO_LOGOUT_URL,
        assessment_url=Config.ASSESSMENT_HUB_ROUTE + "/assessor_dashboard/",
    )


@default_bp.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@default_bp.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500


@default_bp.route("/help", methods=["GET"])
def get_help():
    round_data = get_default_round_data() or {}
    return render_template(
        "get_help.html",
        # this contact information is for the round, so different email.
        # contact_details=round_data.get('contact_details'),
        contact_details={"email_address": "FSD.Support@levellingup.gov.uk"},
        support_availability=round_data.get("support_availability"),
    )
