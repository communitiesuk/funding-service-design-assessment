from app.blueprints.services.data_services import get_default_round_data
from config import Config
from flask import Blueprint
from flask import render_template

core_bp = Blueprint("core_bp", __name__, template_folder="templates")


@core_bp.route("/")
def index():
    return render_template(
        "index.html",
        login_url=Config.SSO_LOGIN_URL,
        logout_url=Config.SSO_LOGOUT_URL,
        assessment_url=Config.ASSESSMENT_HUB_ROUTE + "/assessor_dashboard/",
    )


@core_bp.route("/help", methods=["GET"])
def get_help():
    round_data = get_default_round_data() or {}
    return render_template(
        "get_help.html",
        # TODO: this contact information is for the round, so different email.
        # contact_details=round_data.get('contact_details'),
        contact_details={"email_address": "FSD.Support@levellingup.gov.uk"},
        support_availability=round_data.get("support_availability"),
    )
