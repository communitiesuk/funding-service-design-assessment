import traceback

from flask import current_app
from flask import render_template
from flask import request


def not_found(error):
    current_app.logger.info(f"Encountered 404 against url {request.path}")
    return render_template("404.html"), 404


def forbidden(error):
    error_message = f"Encountered 403: {error}"
    stack_trace = traceback.format_exc()
    current_app.logger.info(f"{error_message}\n{stack_trace}")
    return render_template("403.html"), 403


def internal_server_error(error):
    error_message = f"Encountered 500: {error}"
    stack_trace = traceback.format_exc()
    current_app.logger.error(f"{error_message}\n{stack_trace}")
    return render_template("500.html"), 500
