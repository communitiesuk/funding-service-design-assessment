from app.assess.data import *
from app.assess.question_parser_utils import question_to_table_view, format_selection_fragment_dict
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

@assess_bp.route("/fragments/text_area_2", methods=["GET"])
def text_area_2():
    """
    Page showing available funds
    from fund store
    :return:
    """

    question_data = {
            "question": "About your project",
            "fields": [
                {
                    "key": "about-your-project-capital-expenditure",
                    "title": "Capital expenditure",
                    "type": "text",
                    "answer": "£10"
                },
                {
                    "key": "about-your-project-revenue",
                    "title": "Revenue",
                    "type": "text",
                    "answer": "£4"
                },
                {
                    "key": "about-your-project-subsidy",
                    "title": "Subsidy",
                    "type": "text",
                    "answer": "£5"
                }
            ]
        }

    row_dict = question_to_table_view(question_data, with_total=True, numeric_answers=True)

    return render_template("text_area_2.html", question_data=question_data, row_dict=row_dict)


@assess_bp.route("/fragments/selection", methods=["GET"])
def selection_fragment():
    """
    Fragment to display selection type answers
    """

    # this would be passed to route
    example_selection_fragment = {
            "question": "Declarations",
            "fields": [
                # Radio answer
                {
                    "key": "declarations-state-aid",
                    "title": "Would funding your organisation be classed as State Aid?",
                    "type": "list",
                    "answer": "False"
                },
                {
                    "key": "declarations-environmental",
                    "title": "Does your application comply with all relevant environmental standards?",
                    "type": "list",
                    "answer": "True"
                },
                # Checkbox answer
                {
                    "key": "who-is-endorsing-your-application",
                    "title": "Who is endorsing your application?",
                    "type": "list",
                    "answer": "['Member of parliament (MP)']"
                },
                {
                    "key": "about-your-project-policy-aims",
                    "title": "Which policy aims will your project deliver against?",
                    "type": "list",
                    "answer": "['regeneration', 'Level up skills', 'Fight climate change']"
                },
                # select list answer (selected '1')
                {
                    "key": "your-project-sector",
                    "title": "Project sector",
                    "type": "list",
                    "answer": "1"
                },
                {
                    "key": "rDyIBy",
                    "title": "Risk Level",
                    "type": "list",
                    "answer": "medium"
                },
                {
                    "key": "XBxwLy",
                    "title": "Categorise your risk",
                    "type": "list",
                    "answer": "reputational risk"
                }
            ]
        }

    question_title = example_selection_fragment["question"]
    selection_fragment_answers = format_selection_fragment_dict(example_selection_fragment)


    return render_template("components/selection_fragment.html", selection_fragment_answers=selection_fragment_answers, question_title=question_title)


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
