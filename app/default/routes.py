import traceback

from app.assess.data import get_default_round_data
from app.assess.routes import assess_bp
from config import Config
from flask import Blueprint
from flask import current_app
from flask import render_template
from flask import request

default_bp = Blueprint("default_bp", __name__, template_folder="templates")


@default_bp.route("/")
def index():
    return render_template(
        "index.html",
        login_url=Config.SSO_LOGIN_URL,
        logout_url=Config.SSO_LOGOUT_URL,
        assessment_url=Config.ASSESSMENT_HUB_ROUTE + "/assessor_dashboard/",
    )


@assess_bp.errorhandler(404)
@default_bp.errorhandler(404)
def not_found(error):
    current_app.logger.info(f"Encountered 404 against url {request.path}")
    return render_template("404.html"), 404


@assess_bp.errorhandler(403)
@default_bp.errorhandler(403)
def forbidden(error):
    error_message = f"Encountered 403: {error}"
    stack_trace = traceback.format_exc()
    current_app.logger.info(f"{error_message}\n{stack_trace}")
    return render_template("403.html"), 403


@assess_bp.errorhandler(500)
@default_bp.errorhandler(500)
@assess_bp.errorhandler(Exception)
@default_bp.errorhandler(Exception)
def internal_server_error(error):
    error_message = f"Encountered 500: {error}"
    stack_trace = traceback.format_exc()
    current_app.logger.error(f"{error_message}\n{stack_trace}")
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
