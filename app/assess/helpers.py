from collections import defaultdict
from io import StringIO
from typing import Optional

from app.assess.data import get_fund
from app.assess.data import get_latest_flag
from app.assess.data import get_sub_criteria_banner_state
from app.assess.data import submit_flag
from app.assess.models.flag import Flag
from app.assess.models.flag import FlagType
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from fsd_utils import NotifyConstants


def determine_display_status(
    workflow_status: str,
    latest_flag: Optional[Flag] = None,
) -> str:
    """
    Deduce whether to override display_status with a
    flag.
    """
    if not latest_flag or (
        latest_flag and latest_flag.flag_type == FlagType.RESOLVED
    ):
        return workflow_status
    else:
        return latest_flag.flag_type.name


def is_flaggable(latest_flag: Optional[Flag]):
    return not latest_flag or (
        latest_flag.flag_type in [FlagType.RESOLVED, FlagType.QA_COMPLETED]
    )


def resolve_application(
    form,
    application_id,
    flag,
    user_id,
    justification,
    section,
    page_to_render,
    state=None,
    reason_to_flag="",
    allocated_team="",
):
    """This function is used to resolve an application
      by submitting a flag, justification, and section for the application.

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
    sub_criteria_banner_state = get_sub_criteria_banner_state(application_id)
    latest_flag = get_latest_flag(application_id)
    if latest_flag:
        display_status = determine_display_status(
            sub_criteria_banner_state.workflow_status, latest_flag
        )

    fund = get_fund(sub_criteria_banner_state.fund_id)
    return render_template(
        page_to_render,
        application_id=application_id,
        fund=fund,
        sub_criteria=sub_criteria_banner_state,
        form=form,
        referrer=request.referrer,
        display_status=display_status,
        state=state,
        sections_to_flag=section,
        reason_to_flag=reason_to_flag,
        allocated_team=allocated_team,
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
                elif (
                    # if it's a bool we display yes/no instead of true/false
                    isinstance(answer, bool)
                    and field["type"] == "list"
                ):
                    answer = "Yes" if answer else "No"
                questions_answers[form_name][question_title] = answer
    return questions_answers


def generate_text_of_application(q_and_a: dict, fund_name: str):
    output = StringIO()
    output.write(f"********* {fund_name} **********\n")
    for section_name, values in q_and_a.items():
        title = section_name.split("-")
        output.write(f"\n* {' '.join(title).capitalize()}\n\n")
        for questions, answers in values.items():
            output.write(f"  Q) {questions}\n")
            output.write(f"  A) {answers}\n\n")
    return output.getvalue()
