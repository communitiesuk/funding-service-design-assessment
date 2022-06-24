from app.assess.data import *
from app.assess.models.question_field import QuestionField
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


@assess_bp.route("/fragments/text_input")
def text_input():
    """
    Render html page with json of question & answers & page title.
    """

    input_text_json = {
        "name": "Digital Form Builder - Runner text-input-form",
        "questions": [
            {
                "question": "First page",
                "fields": [
                    {
                        "key": "oLfixk",
                        "title": "Your name",
                        "type": "text",
                        "answer": "Harry The Great",
                    },
                    {
                        "key": "npenre",
                        "title": "Your phone number",
                        "type": "text",
                        "answer": "01234567890",
                    },
                    {
                        "key": "CAKCpJ",
                        "title": "Your email address",
                        "type": "text",
                        "answer": "example@example.com",
                    },
                    {
                        "key": "gOgMvi",
                        "title": "Your UK address",
                        "type": "text",
                        "answer": "99 evoco, example street, London, UB5 5FF",
                    },
                    {
                        "key": "suITII",
                        "title": "Assessor comment",
                        "type": "text",
                        "answer": "testing text area",
                    },
                ],
            }
        ],
        "metadata": {"paymentSkipped": False},
    }
    text_template = QuestionField.get_question_fields(input_text_json)
    page_title = QuestionField.get_page_title(input_text_json)

    return render_template(
        "text_input.html", page_title=page_title, json=text_template
    )
