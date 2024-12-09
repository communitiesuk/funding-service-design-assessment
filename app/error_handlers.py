from flask import current_app, render_template, request

from app.blueprints.assessments.routes import assessment_bp
from app.blueprints.flagging.routes import flagging_bp
from app.blueprints.scoring.routes import scoring_bp
from app.blueprints.shared.routes import shared_bp
from app.blueprints.tagging.routes import tagging_bp


def not_found(error):
    current_app.logger.info("Encountered 404 against url {request_path}", extra=dict(request_path=request.path))
    return render_template("404.html"), 404


def forbidden(error):
    # Override the default message to match design if no custom message is provided
    error.description = (
        "You do not have permission to access this page."
        if "It is either read-protected or not readable by the server." in error.description
        else error.description
    )

    current_app.logger.info("Encountered 403: {error}", extra=dict(error=str(error)))
    return (
        render_template("403.html", error_description=error.description),
        403,
    )


def error_503(error):
    return render_template("maintenance.html"), 503


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
    current_app.logger.exception("Encountered 500: {error}", extra=dict(error=str(error)))
    return render_template("500.html"), 500
