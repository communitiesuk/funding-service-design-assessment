from app.assets import compile_static_assets
from config import Config
from flask import Flask
from flask_assets import Environment
from flask_compress import Compress
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from fsd_utils.logging import logging
from jinja2 import ChoiceLoader
from jinja2 import PackageLoader
from jinja2 import PrefixLoader


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
            service_title="Funding Service Design - Assessment Hub",
            service_meta_description=(
                "Funding Service Design Iteration - Assessment Hub"
            ),
            service_meta_keywords="Funding Service Design - Assessment Hub",
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

        return flask_app


app = create_app()
