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


@default_bp.route("/debug-sentry")
def trigger_error():
    1 / 0


@default_bp.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@default_bp.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500
