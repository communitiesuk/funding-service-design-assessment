from flask import Blueprint

from config import Config

comment_bp = Blueprint(
    "comment_bp",
    __name__,
    url_prefix=Config.ASSESSMENT_HUB_ROUTE,
    template_folder="templates",
)
