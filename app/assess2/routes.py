from flask import abort
from flask import Blueprint
from flask import render_template

assessv2_bp = Blueprint(
    "assessv2_bp",
    __name__,
    url_prefix="/new",
    template_folder="templates",
)

@assessv2_bp.route("/", methods=["GET"])
def welcome():

    return render_template("assesser_project_view.html")