import traceback

from app.blueprints.assessments.routes import assessment_bp
from app.blueprints.flagging.routes import flagging_bp
from app.blueprints.scoring.routes import scoring_bp
from app.blueprints.shared.routes import shared_bp
from app.blueprints.tagging.routes import tagging_bp
from flask import current_app
from flask import render_template
from flask import request


def not_found(error):
    current_app.logger.info(f"Encountered 404 against url {request.path}")
    return render_template("404.html"), 404


def forbidden(error):
    # Override the default message to match design if no custom message is provided
    error.description = (
        "You do not have permission to access this page."
        if "It is either read-protected or not readable by the server."
        in error.description
        else error.description
    )

    error_message = f"Encountered 403: {error}"
    stack_trace = traceback.format_exc()
    current_app.logger.info(f"{error_message}\n{stack_trace}")
    return (
        render_template("403.html", error_description=error.description),
        403,
    )


@assessment_bp.errorhandler(500)
@assessment_bp.errorhandler(Exception)
@shared_bp.errorhandler(500)
@shared_bp.errorhandler(Exception)
@flagging_bp.errorhandler(500)
@flagging_bp.errorhandler(Exception)
@tagging_bp.errorhandler(500)
@tagging_bp.errorhandler(Exception)
@scoring_bp.errorhandler(500)
@scoring_bp.errorhandler(Exception)
def internal_server_error(error):
    error_message = f"Encountered 500: {error}"
    stack_trace = traceback.format_exc()
    current_app.logger.error(f"{error_message}\n{stack_trace}")
    return render_template("500.html"), 500
