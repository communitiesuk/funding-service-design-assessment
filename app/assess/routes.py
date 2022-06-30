# flake8: noqa
from app.assess.data import *
from app.assess.models.question_field import QuestionField
from app.assess.models.total_table import TotalMoneyTableView

from app.config import APPLICATION_STORE_API_HOST_PUBLIC
from app.config import ASSESSMENT_HUB_ROUTE
from flask import abort
from flask import Blueprint
from flask import render_template
from flask import request

assess_bp = Blueprint(
    "assess_bp",
    __name__,
    url_prefix=ASSESSMENT_HUB_ROUTE,
    template_folder="templates",
)


@assess_bp.route("/", methods=["GET"])
def funds():
    """
    Page showing available funds
    from fund store
    :return:
    """

    funds = get_funds()

    return render_template("funds.html", funds=funds)


@assess_bp.route("/fragments/total_table_view", methods=["GET"])
def total_table_view():

    question_data = {
        "question": "About your project",
        "fields": [
            {
                "key": "about-your-project-capital-expenditure",
                "title": "Capital expenditure",
                "type": "text",
                "answer": "£10",
            },
            {
                "key": "about-your-project-revenue",
                "title": "Revenue",
                "type": "text",
                "answer": "£4",
            },
            {
                "key": "about-your-project-subsidy",
                "title": "Subsidy",
                "type": "text",
                "answer": "£5",
            },
        ],
    }

    question_model = TotalMoneyTableView.from_question_json(question_data)

    return render_template(
        "total_table.html",
        question_data=question_data,
        row_dict=question_model.row_dict(),
    )


@assess_bp.route("/landing/", methods=["GET"])
def landing():
    """
    Landing page for assessors
    Provides a summary of available applications
    with a keyword searchable and filterable list
    of applications and their statuses
    """

    # Initialise empty search params
    search_params = {
        "id_contains": "",
        "order_by": "",
        "order_rev": "",
        "status_only": "",
    }

    # Add request arg search params to dict
    for key, value in request.args.items():
        if key in search_params:
            search_params.update({key: value})

    applications = get_applications(params=search_params)

    todo_summary = get_todo_summary()

    return render_template(
        "landing.html",
        applications=applications,
        search_params=search_params,
        todo_summary=todo_summary,
        applications_endpoint="".join(
            [
                APPLICATION_STORE_API_HOST_PUBLIC,
                APPLICATION_SEARCH_ENDPOINT.replace("{params}", ""),
            ]
        ),
    )


@assess_bp.route("/application/<application_id>", methods=["GET"])
def application(application_id):

    """
    Application summary page
    Shows information about the fund, application ID
    and all the application questions and their assessment status
    :param application_id:
    :return:
    """

    application = get_application_status(application_id=application_id)
    if not application:
        abort(404)

    fund = get_fund(application.fund_id)
    if not fund:
        abort(404)

    return render_template(
        "application.html", application=application, fund=fund
    )


"""
 Legacy
 The following routes serve information relating to
 individual funds and fund rounds and are not shown in the assessor views
"""


@assess_bp.route("/<fund_id>/", methods=["GET"])
def fund(fund_id: str):
    """
    Page showing available rounds for a given fund
    from round store
    :param fund_id:
    :return:
    """

    fund = get_fund(fund_id)
    if not fund:
        abort(404)

    rounds = get_rounds(fund_id)

    return render_template("fund.html", fund=fund, rounds=rounds)


@assess_bp.route("/<fund_id>/<round_id>/", methods=["GET"])
def fund_round(fund_id: str, round_id: str):
    """
    Page showing available applications
    from a given fund_id and round_id
    from the application store
    :param fund_id:
    :param round_id:
    :return:
    """

    fund = get_fund(fund_id)
    if not fund:
        abort(404)

    fund_round = get_round_with_applications(
        fund_id=fund_id, round_id=round_id
    )
    if not fund_round:
        abort(404)

    return render_template("round.html", fund=fund, round=fund_round)


@assess_bp.route("/fragments/upload_documents/")
def upload_documents():
    """
    Render html page with json contains title & answer/url.
    """

    uploaded_file_json = {
        "name": "Digital Form Builder - Runner test-form-",
        "questions": [
            {
                "question": "Upload documents page",
                "fields": [
                    {
                        "key": "ocdeay",
                        "title": "Python language - Introduction & courses",
                        "type": "file",
                        "answer": "https://en.wikipedia.org/wiki/Python_(programming_language)",
                    }
                ],
            }
        ],
    }

    json_fields = uploaded_file_json["questions"][0]["fields"][0]
    attachment_file_json = QuestionField.from_json(json_fields)

    return render_template(
        "macros/example_upload_documents.html", file=attachment_file_json
    )
