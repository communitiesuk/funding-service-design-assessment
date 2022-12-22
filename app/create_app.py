from app.assess.views.filters import all_caps_to_human
from app.assess.views.filters import datetime_format
from app.assess.views.filters import datetime_format_24hr
from app.assess.views.filters import format_address
from app.assess.views.filters import format_project_ref
from app.assess.views.filters import remove_dashes_underscores_capitalize
from app.assess.views.filters import slash_separated_day_month_year
from app.assess.views.filters import status_to_human
from app.assets import compile_static_assets
from config import Config
from flask import Flask
from flask import g
from flask import redirect
from flask import request
from flask_assets import Environment
from flask_compress import Compress
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from fsd_utils.authentication.decorators import login_requested
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from jinja2 import ChoiceLoader
from jinja2 import PackageLoader
from jinja2 import PrefixLoader
from fsd_utils.authentication.models import User


def create_app() -> Flask:

    flask_app = Flask("Assessment Frontend")

    flask_app.config.from_object("config.Config")
    flask_app.static_url_path = flask_app.config.get("STATIC_URL_PATH")
    flask_app.static_folder = flask_app.config.get("STATIC_FOLDER")

    flask_app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PrefixLoader(
                {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
            ),
        ]
    )

    flask_app.jinja_env.trim_blocks = True
    flask_app.jinja_env.lstrip_blocks = True
    flask_app.jinja_env.filters["datetime_format"] = datetime_format
    flask_app.jinja_env.filters[
        "slash_separated_day_month_year"
    ] = slash_separated_day_month_year
    flask_app.jinja_env.filters["all_caps_to_human"] = all_caps_to_human
    flask_app.jinja_env.filters["status_to_human"] = status_to_human
    flask_app.jinja_env.filters["datetime_format_24hr"] = datetime_format_24hr
    flask_app.jinja_env.filters["format_project_ref"] = format_project_ref
    flask_app.jinja_env.filters[
        "remove_dashes_underscores_capitalize"
    ] = remove_dashes_underscores_capitalize
    flask_app.jinja_env.filters["format_address"] = format_address

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
            service_title="Assessment Hub",
            service_meta_description=(
                "Assessment Hub"
            ),
            service_meta_keywords="Assessment Hub",
            service_meta_author="DLUHC",
        )

    with flask_app.app_context():
        from app.default.routes import (
            default_bp,
            not_found,
            internal_server_error,
        )
        from app.assess.routes import assess_bp
        from app.assess.api import api_bp
        from app.assess.views.assess import AssessQuestionView

        flask_app.register_error_handler(404, not_found)
        flask_app.register_error_handler(500, internal_server_error)
        flask_app.register_blueprint(default_bp)
        flask_app.register_blueprint(assess_bp)
        flask_app.register_blueprint(api_bp)
        flask_app.add_url_rule(
            "/".join(
                [
                    Config.ASSESSMENT_HUB_ROUTE,
                    "application",
                    "<application_id>",
                    "question",
                    "<question_id>",
                ]
            )
            + "/",
            view_func=AssessQuestionView.as_view("application_question"),
        )

        # Bundle and compile assets
        assets = Environment()
        assets.init_app(flask_app)
        compile_static_assets(assets, flask_app)

        health = Healthcheck(flask_app)
        health.add_check(FlaskRunningChecker())
        @flask_app.before_request
        def allow_login():
            g.is_authenticated = True
            g.account_id = "123"            
            g.user = User(
                full_name="full_name",
                email="email",
                roles=["COMMENTER"],
                highest_role="COMMENTER",
            )
            if request.path in ["","/"]:
                return redirect(flask_app.config.get("DASHBOARD_ROUTE"))
        # @flask_app.before_request
        # @login_requested
        # def ensure_minimum_required_roles():
        #     minimum_roles_required = ["COMMENTER"]
        #     unprotected_routes = ["/"]
        #     if g.is_authenticated:
        #         # Ensure that authenticated users have
        #         # all minimum required roles
        #         if not g.user.roles or not all(
        #             role_required in g.user.roles
        #             for role_required in minimum_roles_required
        #         ):
        #             return redirect(
        #                 flask_app.config.get("AUTHENTICATOR_HOST")
        #                 + "/service/user"
        #                 + "?roles_required="
        #                 + "|".join(minimum_roles_required)
        #             )
        #         elif request.path == "/":
        #             return redirect(flask_app.config.get("DASHBOARD_ROUTE"))
        #     elif (
        #         request.path not in unprotected_routes
        #         and not request.path.startswith("/static/")
        #     ):  # noqa
        #         # Redirect unauthenticated users to
        #         # login on the home page
        #         return redirect("/")

        return flask_app


app = create_app()
