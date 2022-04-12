from app.assets import compile_static_assets
from flask import Flask
from flask_assets import Environment
from flask_compress import Compress
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from jinja2 import ChoiceLoader
from jinja2 import PackageLoader
from jinja2 import PrefixLoader


def create_app() -> Flask:

    flask_app = Flask(
        __name__, static_url_path="/assets", static_folder="static/dist"
    )

    flask_app.config.from_pyfile("config.py")

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

    csp = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "'sha256-+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU='",
            "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",
        ],
        "img-src": ["data:", "'self'"],
    }

    if str(
        flask_app.config.get(
            "".join(["APPLICATION_STORE", "_API_HOST_PUBLIC"])
        )
    ).startswith("https://"):
        csp.update(
            {
                "connect-src": [
                    flask_app.config.get("APPLICATION_STORE_API_HOST_PUBLIC"),
                ],
            }
        )

    hss = {
        "Strict-Transport-Security": (
            "max-age=31536000; includeSubDomains; preload"
        ),
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "Feature_Policy": (
            "microphone 'none'; camera 'none'; geolocation 'none'"
        ),
    }

    Compress(flask_app)
    Talisman(
        flask_app,
        content_security_policy=csp,
        strict_transport_security=hss,
        content_security_policy_nonce_in=["script-src"],
    )

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
                    flask_app.config["ASSESSMENT_HUB_ROUTE"],
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
        compile_static_assets(assets)

        return flask_app


app = create_app()
