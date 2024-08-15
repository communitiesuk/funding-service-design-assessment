import os
import re
from gettext import ngettext

from flask import Flask
from flask import current_app
from flask import g
from flask import render_template
from flask import request
from flask_assets import Environment
from flask_compress import Compress
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from fsd_utils import init_sentry
from fsd_utils.authentication.decorators import login_requested
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from fsd_utils.toggles.toggles import create_toggles_client
from fsd_utils.toggles.toggles import initialise_toggles_redis_store
from fsd_utils.toggles.toggles import load_toggles
from jinja2 import ChoiceLoader
from jinja2 import PackageLoader
from jinja2 import PrefixLoader

import static_assets
from app.blueprints.assessments.routes import assessment_bp
from app.blueprints.authentication.auth import auth_protect
from app.blueprints.flagging.routes import flagging_bp
from app.blueprints.scoring.routes import scoring_bp
from app.blueprints.shared.filters import add_to_dict
from app.blueprints.shared.filters import all_caps_to_human
from app.blueprints.shared.filters import ast_literal_eval
from app.blueprints.shared.filters import datetime_format
from app.blueprints.shared.filters import datetime_format_24hr
from app.blueprints.shared.filters import format_address
from app.blueprints.shared.filters import format_project_ref
from app.blueprints.shared.filters import remove_dashes_underscores_capitalize
from app.blueprints.shared.filters import (
    remove_dashes_underscores_capitalize_keep_uppercase,
)
from app.blueprints.shared.filters import slash_separated_day_month_year
from app.blueprints.shared.filters import utc_to_bst
from app.blueprints.shared.routes import shared_bp
from app.blueprints.tagging.routes import tagging_bp
from app.error_handlers import error_503
from app.error_handlers import forbidden
from app.error_handlers import internal_server_error
from app.error_handlers import not_found
from config import Config


def create_app() -> Flask:
    flask_app = Flask("Assessment Frontend")
    with flask_app.app_context():

        init_sentry()
        flask_app.config.from_object("config.Config")

        toggle_client = None
        if os.getenv("FLASK_ENV") != "unit_test":
            initialise_toggles_redis_store(flask_app)
            toggle_client = create_toggles_client()
            load_toggles(Config.FEATURE_CONFIG, toggle_client)

        flask_app.register_error_handler(404, not_found)
        flask_app.register_error_handler(403, forbidden)
        flask_app.register_error_handler(503, error_503)
        flask_app.register_error_handler(500, internal_server_error)
        flask_app.register_blueprint(shared_bp)
        flask_app.register_blueprint(assessment_bp)
        flask_app.register_blueprint(flagging_bp)
        flask_app.register_blueprint(tagging_bp)
        flask_app.register_blueprint(scoring_bp)

        flask_app.static_url_path = flask_app.config.get("STATIC_URL_PATH")
        flask_app.static_folder = flask_app.config.get("STATIC_FOLDER")

        template_loaders = [
            PackageLoader("app"),
            PackageLoader("app.blueprints.shared"),
            PackageLoader("app.blueprints.assessments"),
            PackageLoader("app.blueprints.flagging"),
            PackageLoader("app.blueprints.tagging"),
            PackageLoader("app.blueprints.scoring"),
            PrefixLoader(
                {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
            ),
        ]

        flask_app.jinja_loader = ChoiceLoader(template_loaders)

        flask_app.jinja_env.trim_blocks = True
        flask_app.jinja_env.lstrip_blocks = True
        flask_app.jinja_env.filters["ast_literal_eval"] = ast_literal_eval
        flask_app.jinja_env.filters["datetime_format"] = datetime_format
        flask_app.jinja_env.filters["utc_to_bst"] = utc_to_bst
        flask_app.jinja_env.filters["add_to_dict"] = add_to_dict
        flask_app.jinja_env.filters["slash_separated_day_month_year"] = (
            slash_separated_day_month_year
        )
        flask_app.jinja_env.filters["all_caps_to_human"] = all_caps_to_human
        flask_app.jinja_env.filters["datetime_format_24hr"] = datetime_format_24hr
        flask_app.jinja_env.filters["format_project_ref"] = format_project_ref
        flask_app.jinja_env.filters["remove_dashes_underscores_capitalize"] = (
            remove_dashes_underscores_capitalize
        )
        flask_app.jinja_env.filters[
            "remove_dashes_underscores_capitalize_keep_uppercase"
        ] = remove_dashes_underscores_capitalize_keep_uppercase
        flask_app.jinja_env.filters["format_address"] = format_address
        flask_app.jinja_env.add_extension("jinja2.ext.i18n")
        flask_app.jinja_env.globals["ngettext"] = ngettext

        Compress(flask_app)

        logging.init_app(flask_app)

        # Configure application security with Talisman
        Talisman(flask_app, **Config.TALISMAN_SETTINGS)

        csrf = CSRFProtect()

        csrf.init_app(flask_app)

        # This is silently used by flask in the background.
        @flask_app.context_processor
        def inject_global_constants():
            return dict(
                stage="beta",
                service_title="Assessment Hub – GOV.UK",
                service_meta_description="Assessment Hub",
                service_meta_keywords="Assessment Hub",
                service_meta_author="DLUHC",
                sso_logout_url=flask_app.config.get("SSO_LOGOUT_URL"),
                g=g,
                toggle_dict=(
                    {
                        feature.name: feature.is_enabled()
                        for feature in toggle_client.list()
                    }
                    if toggle_client
                    else {}
                ),
            )

        # Bundle and compile assets
        assets = Environment()
        assets.init_app(flask_app)
        static_assets.init_assets(
            flask_app,
            auto_build=Config.ASSETS_AUTO_BUILD,
            static_folder=Config.STATIC_FOLDER,
        )

        health = Healthcheck(flask_app)
        health.add_check(FlaskRunningChecker())

        @flask_app.before_request
        def check_for_maintenance():
            if flask_app.config.get("MAINTENANCE_MODE") and not (
                request.path.endswith("js")
                or request.path.endswith("css")
                or request.path.endswith("/healthcheck")
            ):
                current_app.logger.warning(
                    f"""Application is in the Maintenance mode
                    reach url: {request.url}"""
                )
                return (
                    render_template(
                        "maintenance.html",
                        maintenance_end_time=flask_app.config.get(
                            "MAINTENANCE_END_TIME"
                        ),
                    ),
                    503,
                )

        @flask_app.before_request
        @login_requested
        def ensure_minimum_required_roles():
            return auth_protect(
                minimum_roles_required=["COMMENTER"],
                unprotected_routes=["/", "/healthcheck", "/cookie_policy"],
            )

        # Get static filenames list
        static_files_list = []
        for _, _, files in os.walk(flask_app.static_url_path):
            for file in files:
                static_files_list.append(file)

        @flask_app.after_request
        def set_response_headers(response):
            filename = (
                re.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
                if response.headers.get("Content-Disposition")
                else ""
            )

            # enable caching for static files
            if filename in static_files_list:
                response.headers["Cache-Control"] = "public, max-age=3600"
            else:
                response.headers["Cache-Control"] = (
                    "no-cache, no-store, must-revalidate"
                )
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
            return response

        return flask_app


app = create_app()
