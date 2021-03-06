from app.assess.data import *
from app.assess.forms.comments_form import CommentsForm
from app.assess.models.question import Question
from app.assess.models.question_field import QuestionField
from app.assess.models.total_table import TotalMoneyTableView
from app.assess.data import submit_score_and_justification
from config import Config
from flask import abort
from flask import Blueprint
from flask import render_template
from flask import request
from app.assess.forms.scores_and_justifications import JustScoreForm


assess_bp = Blueprint(
    "assess_bp",
    __name__,
    url_prefix=Config.ASSESSMENT_HUB_ROUTE,
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

@assess_bp.route("/fragments/structured_question", methods=["GET"])
def selection_fragment():
    """
    An example route showing passing data from select type
    answers (radio, checkbox, select) through to a base
    template that utilises the 'structured_question'
    macro.
    """

    example_assessment_store_data_for_select_type_data = {
        "question": "Declarations",
        "status": "completed",
        "fields": [
            # Radio answer
            {
                "key": "declarations-state-aid",
                "title": (
                    "Would funding your organisation be classed as State Aid?"
                ),
                "type": "list",
                "answer": "False",
            },
            {
                "key": "declarations-environmental",
                "title": (
                    "Does your application comply with all relevant"
                    " environmental standards?"
                ),
                "type": "list",
                "answer": "True",
            },
            # Checkbox answer
            {
                "key": "who-is-endorsing-your-application",
                "title": "Who is endorsing your application?",
                "type": "list",
                "answer": "['Member of parliament (MP)']",
            },
            {
                "key": "about-your-project-policy-aims",
                "title": (
                    "Which policy aims will your project deliver against?"
                ),
                "type": "list",
                "answer": (
                    "['regeneration', 'Level up skills', 'Fight climate"
                    " change']"
                ),
            },
            # select list answer (selected '1')
            {
                "key": "your-project-sector",
                "title": "Project sector",
                "type": "list",
                "answer": "1",
            },
            {
                "key": "rDyIBy",
                "title": "Risk Level",
                "type": "list",
                "answer": "medium",
            },
            {
                "key": "XBxwLy",
                "title": "Categorise your risk",
                "type": "list",
                "answer": "reputational risk",
            },
        ],
    }
    # collect different answer types here to pass to base template such as
    # select type (radio, checkbox), free-text, table etc
    question = Question.from_json(
        example_assessment_store_data_for_select_type_data
    )
    structured_question_data = question.as_structured_question()
    template_data = {"structured_question_data": structured_question_data}

    return render_template(
        "structured_question.html", title=question.title, data=template_data
    )


@assess_bp.route("/fragments/title_answer_pairs", methods=["GET"])
def text_area_1():
    """
    Page showing fragment of text_area_1
    :return:
    """

    question_data = {
        "question": "About your organisation",
        "fields": [
            {
                "key": "application-name",
                "title": "Applicant name",
                "type": "text",
                "answer": "Bobby Bob",
            },
            {
                "key": "applicant-email",
                "title": "Email",
                "type": "text",
                "answer": "a@example.com",
            },
            {
                "key": "applicant-telephone-number",
                "title": "Telephone number",
                "type": "text",
                "answer": "01632 960 000",
            },
            {
                "key": "applicant-website",
                "title": "Website",
                "type": "text",
                "answer": "https://www.onedirection.com",
            },
        ],
    }

    data_dict = {}

    data_dict["title"] = question_data["question"]

    data_dict["answers"] = [
        {"title": data_dict["title"], "answer": data_dict["answer"]}
        for data_dict in question_data["fields"]
    ]

    return render_template("title_answer_pairs.html", data_dict=data_dict)


@assess_bp.route("/fragments/total_table_view", methods=["GET"])
def total_table_view():

    question_data = {
        "question": "About your project",
        "fields": [
            {
                "key": "about-your-project-capital-expenditure",
                "title": "Capital expenditure",
                "type": "text",
                "answer": "??10",
            },
            {
                "key": "about-your-project-revenue",
                "title": "Revenue",
                "type": "text",
                "answer": "??4",
            },
            {
                "key": "about-your-project-subsidy",
                "title": "Subsidy",
                "type": "text",
                "answer": "??5",
            },
        ],
    }

    question_model = TotalMoneyTableView.from_question_json(question_data)

    return render_template(
        "total_table.html",
        question_data=question_data,
        row_dict=question_model.row_dict(),
    )

@assess_bp.route("/fragments/sub_criteria_scoring", methods=["POST","GET"])
def sub_crit_scoring():

    form = JustScoreForm()

    if form.validate_on_submit():

        score = int(form.score.data)
        just = form.justification.data

        assessment_id = "test_assess_id"
        person_id = "test_person_id"
        sub_crit_id = "test_sub_crit_id"

        submit_score_and_justification(score=score, assessment_id=assessment_id, person_id=person_id, justification=just,sub_crit_id=sub_crit_id)
        scores_submitted = True

    else:

        scores_submitted = False

    return render_template("scores_justification.html",scores_submitted=scores_submitted, form=form)

@assess_bp.route("/fragments/text_input")
def text_input():
    """
    Render html page with json contains question & answer.
    """

    input_text_name = {
        "questions": [
            {
                "fields": [
                    {
                        "key": "oLfixk",
                        "title": "Your name",
                        "type": "text",
                        "answer": "Steve",
                    },
                ],
            }
        ],
    }

    input_text_address = {
        "questions": [
            {
                "fields": [
                    {
                        "key": "gOgMvi",
                        "title": "Your UK address",
                        "type": "text",
                        "answer": "99 evoco, example street, London, UB5 5FF",
                    },
                ],
            }
        ],
    }

    name = QuestionField.from_json(
        input_text_name["questions"][0]["fields"][0]
    )
    address = QuestionField.from_json(
        input_text_address["questions"][0]["fields"][0]
    )

    return render_template(
        "macros/example_text_input.html",
        name=name,
        address=address,
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
                Config.APPLICATION_STORE_API_HOST_PUBLIC,
                Config.APPLICATION_SEARCH_ENDPOINT.replace("{params}", ""),
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
                        "title": "Python language - Introduction & course",
                        "type": "file",
                        "answer": "https://en.wikipedia.org/wiki/Python_(programming_language)",  # noqa
                    }
                ],
            }
        ],
    }

    json_fields = uploaded_file_json["questions"][0]["fields"][0]
    file_metadata = QuestionField.from_json(json_fields)

    return render_template(
        "macros/example_upload_documents.html", file_metadata=file_metadata
    )


@assess_bp.route("/comments/", methods=["GET", "POST"])
def comments():
    """
    example route to call macro for text area field
    """
    form = CommentsForm()

    if form.validate_on_submit():
        comment_data = form.comment.data
        return render_template(
            "macros/example_comments_template.html",
            form=form,
            comment_data=comment_data,
        )

    return render_template("macros/example_comments_template.html", form=form)
