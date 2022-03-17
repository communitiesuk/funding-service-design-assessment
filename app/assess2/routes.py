from flask import abort
from flask import Blueprint
from flask import render_template

from assess2.data_handling import get_application_data

assessv2_bp = Blueprint(
    "assessv2_bp",
    __name__,
    url_prefix="/new",
    template_folder="assessment_templates",
)

@assessv2_bp.route("/view_application/<application_id>", methods=["GET"])
def view_applcation(application_id):

    application_data = get_application_data(application_id)

    return render_template("assesser_project_view.html", application_id=application_id)