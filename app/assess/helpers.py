from collections import defaultdict
from io import StringIO

from app.assess.data import get_banner_state
from app.assess.data import get_fund
from app.assess.data import get_latest_flag
from app.assess.data import submit_flag
from app.assess.models.flag import FlagType
from config import Config
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from fsd_utils import NotifyConstants


def determine_display_status(state, latest_flag=None):
    """
    Deduce whether to override display_status with a
    flag.
    """
    if not latest_flag:
        state.display_status = state.workflow_status
    elif latest_flag and latest_flag.flag_type == FlagType.RESOLVED:
        state.display_status = state.workflow_status
        state.flag_resolved = True
    else:
        state.display_status = latest_flag.flag_type.name


def resolve_application(
    form, application_id, flag, user_id, justification, section, page_to_render
):
    """This function is used to resolve an application by submitting a flag,
    justification, and section for the application.

    Args:
        form (obj): Form object to be validated and submitted
        application_id (int): ID of the application
        flag (str): Flag submitted for the application
        justification (str): Justification for the flag submitted
        section (str): Section of the application the flag is submitted for
        page_to_render (str): Template name to be rendered

    Returns:
        redirect: Redirects to the application page if the request method is
                  "POST" and form is valid.
        render_template: Renders the specified template with the
                         application_id, fund_name, state, form, and referrer
                         as parameters.
    """
    if request.method == "POST" and form.validate_on_submit():
        submit_flag(application_id, flag, user_id, justification, section)
        return redirect(
            url_for(
                "assess_bp.application",
                application_id=application_id,
            )
        )
    state = get_banner_state(application_id)
    latest_flag = get_latest_flag(application_id)
    if latest_flag:
        determine_display_status(state, latest_flag)

    fund = get_fund(state.fund_id)
    return render_template(
        page_to_render,
        application_id=application_id,
        fund_name=fund.name,
        state=state,
        form=form,
        referrer=request.referrer,
    )


def extract_questions_and_answers_from_json_blob(
    application_json_blob,
) -> dict:
    """function takes the form data and returns
    dict of questions & answers.
    """
    questions_answers = defaultdict(dict)
    forms = application_json_blob["forms"]

    for form in forms:
        form_name = form["name"]
        for question in form[NotifyConstants.APPLICATION_QUESTIONS_FIELD]:
            for field in question["fields"]:
                question_title = field["title"]
                answer = field.get("answer")
                if field["type"] == "file":
                    # we check if the question type is "file"
                    # then we remove the aws
                    # key attached to the answer

                    if isinstance(answer, str):
                        answer = answer.split("/")[-1]

                questions_answers[form_name][question_title] = answer
    return questions_answers


def generate_text_of_application(q_and_a: dict):
    output = StringIO()
    # output = BytesIO()

    output.write(f"********* {Config.COF_FUND_NAME} **********\n")
    for section_name, values in q_and_a.items():
        title = section_name.split("-")
        output.write(f"\n* {' '.join(title).capitalize()}\n\n")
        for questions, answers in values.items():
            output.write(f"  Q) {questions}\n")
            output.write(f"  A) {answers}\n\n")
    return output.getvalue()
