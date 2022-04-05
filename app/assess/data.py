import json
import os
from typing import List
from urllib.parse import urlencode

import requests
from app.assess.models.application import Application
from app.assess.models.fund import Fund
from app.assess.models.question import QuestionAnswerPage
from app.assess.models.round import Round
from app.config import APPLICATION_STORE_API_HOST
from app.config import FLASK_ROOT
from app.config import FUND_STORE_API_HOST
from app.config import ROUND_STORE_API_HOST


# Fund Store Endpoints
FUNDS_ENDPOINT = "/funds/"
FUND_ENDPOINT = "/funds/{fund_id}"

# Round Store Endpoints
ROUNDS_ENDPOINT = "/fund/{fund_id}"
ROUND_ENDPOINT = "/fund/{fund_id}/round/{round_id}"

# Application Store Endpoints
APPLICATIONS_ENDPOINT = "".join(
    [
        "/fund/{fund_id}?",
        "datetime_start={datetime_start}&datetime_end={datetime_end}",
    ]
)
APPLICATION_SEARCH_ENDPOINT = "/search?{params}"
APPLICATION_ENDPOINT = "/fund/{fund_id}?application_id={application_id}"

# Status endpoints
STATUS_ENDPOINT = "/fund/status/{application_id}"


def get_data(endpoint: str):
    if endpoint[:8] == "https://":
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
        else:
            return None
    else:
        data = get_local_data(endpoint)
    return data


def get_local_data(endpoint: str):
    api_data_json = os.path.join(
        FLASK_ROOT, "tests", "api_data", "endpoint_data.json"
    )
    fp = open(api_data_json)
    api_data = json.load(fp)
    fp.close()
    if endpoint in api_data:
        return api_data.get(endpoint)


def get_funds() -> List[Fund] | None:
    endpoint = FUND_STORE_API_HOST + FUNDS_ENDPOINT
    response = get_data(endpoint)
    if response and len(response) > 0:
        funds = []
        for fund in response:
            funds.append(Fund.from_json(fund))
        return funds
    return None


def get_fund(fund_id: str) -> Fund | None:
    endpoint = FUND_STORE_API_HOST + FUND_ENDPOINT.format(fund_id=fund_id)
    response = get_data(endpoint)
    if response and "fund_id" in response:
        fund = Fund.from_json(response)
        if "rounds" in response and len(response["rounds"]) > 0:
            for fund_round in response["rounds"]:
                fund.add_round(Round.from_json(fund_round))
        return fund
    return None


def get_rounds(fund_id: str) -> Fund | List:
    endpoint = ROUND_STORE_API_HOST + ROUNDS_ENDPOINT.format(fund_id=fund_id)
    response = get_data(endpoint)
    rounds = []
    if response and len(response) > 0:
        for round_data in response:
            rounds.append(Round.from_json(round_data))
    return rounds


def get_round(fund_id: str, round_id: str) -> Round | None:
    round_endpoint = ROUND_STORE_API_HOST + ROUND_ENDPOINT.format(
        fund_id=fund_id, round_id=round_id
    )
    round_response = get_data(round_endpoint)
    if round_response and "round_id" in round_response:
        fund_round = Round.from_json(round_response)
        applications_endpoint = (
            APPLICATION_STORE_API_HOST
            + APPLICATIONS_ENDPOINT.format(
                fund_id=fund_id,
                datetime_start=fund_round.opens,
                datetime_end=fund_round.deadline,
            )
        )
        applications_response = get_data(applications_endpoint)
        if applications_response and len(applications_response) > 0:
            for application in applications_response:
                fund_round.add_application(Application.from_json(application))

        return fund_round
    return None


def get_applications(params: dict) -> List[Application] | None:
    applications_endpoint = (
        APPLICATION_STORE_API_HOST
        + APPLICATION_SEARCH_ENDPOINT.format(params=urlencode(params))
    )
    applications_response = get_data(applications_endpoint)
    if applications_response and len(applications_response) > 0:
        applications = []
        for application_data in applications_response:
            applications.append(Application.from_json(application_data))

        return applications
    return None


def get_todo_summary() -> dict | None:
    applications_endpoint = (
        APPLICATION_STORE_API_HOST
        + APPLICATION_SEARCH_ENDPOINT.format(params="")
    )
    applications = get_data(applications_endpoint)
    if applications and len(applications) > 0:
        todo_summary = {}
        todo_summary.update(
            {
                "completed": len(
                    [
                        1
                        for application in applications
                        if application["status"] == "COMPLETED"
                    ]
                ),
                "assessing": len(
                    [
                        1
                        for application in applications
                        if application["status"] == "ASSESSING"
                    ]
                ),
                "not_started": len(
                    [
                        1
                        for application in applications
                        if application["status"] == "NOT_STARTED"
                    ]
                ),
            }
        )

        return todo_summary
    return None


def get_application(fund_id: str, identifier: str) -> Application | None:
    application_endpoint = (
        APPLICATION_STORE_API_HOST
        + APPLICATION_ENDPOINT.format(
            fund_id=fund_id, application_id=identifier
        )
    )
    application_response = get_data(application_endpoint)
    if application_response and "id" in application_response:
        application = Application.from_json(application_response)
        return application
    return None


def get_questions_and_statuses(application_id, fund_id):
    """_summary_: Function is set up to retrieve
    the data from application store with
    get_data() function.

    Args:
        application_id: Takes an application_id.
        fund_id: Takes a fund_id

    Returns:
        Returns a dictionary of questions & their statuses.
    """
    status_endpoint = APPLICATION_STORE_API_HOST + STATUS_ENDPOINT.format(
        application_id=application_id
    )
    questions = get_data(status_endpoint)
    if questions:
        data = {title: status for title, status in questions.items()}
        return data


def get_questions_tuple(
    identifier: str, fund_id: str, page_title: str
) -> Application:
    """
    _summary_: Function retrieves all questions in a tuple from
        given page title
    Args:
        identifier: Takes an application id/ identifier
        fund_id: Takes a fund id
        page_title: Takes a questions page title
    Returns:
        returns a tuple of questions
    """
    application_response = get_application(
        identifier=identifier, fund_id=fund_id
    )
    data_from_questions_page = application_response.questions
    questions = QuestionAnswerPage.get_questions(
        page_title=page_title, questions_page=data_from_questions_page
    )
    return questions


def get_answers_tuple(
    identifier: str, fund_id: str, page_title: str
) -> Application:
    """
    _summary_: Function retrieves all questions in a tuple from
        given page title
    Args:
        identifier (str):Takes an application_id/ identifier
        fund_id (str): Takes a fund id
        page_title (str): Takes a question page title
    Returns:
        Application: Return a tuple of answers from application
    """
    application_response = get_application(
        identifier=identifier, fund_id=fund_id
    )
    data_from_questions_page = application_response.questions
    answers = QuestionAnswerPage.get_answers(
        page_title=page_title, answers_page=data_from_questions_page
    )
    return answers
