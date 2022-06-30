import json
import os
from typing import Dict
from typing import List
from typing import Union
from urllib.parse import urlencode

import requests
from app.assess.models.application import Application
from app.assess.models.fund import Fund
from app.assess.models.round import Round
from app.config import APPLICATION_STORE_API_HOST
from app.config import FLASK_ROOT
from app.config import FUND_STORE_API_HOST
from app.config import ROUND_STORE_API_HOST


# Fund Store Endpoints
FUNDS_ENDPOINT = "/funds/"
FUND_ENDPOINT = "/funds/{fund_id}"

# Round Store Endpoints
ROUNDS_ENDPOINT = "/funds/{fund_id}"
ROUND_ENDPOINT = "/funds/{fund_id}/rounds/{round_id}"

# Application Store Endpoints
APPLICATION_ENDPOINT = "/applications/{application_id}"
APPLICATION_STATUS_ENDPOINT = "/applications/{application_id}/status"
APPLICATION_SEARCH_ENDPOINT = "/applications?{params}"


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


def call_search_applications(params: dict):
    applications_endpoint = (
        APPLICATION_STORE_API_HOST
        + APPLICATION_SEARCH_ENDPOINT.format(params=urlencode(params))
    )
    applications_response = get_data(applications_endpoint)
    return applications_response


def get_funds() -> Union[List[Fund], None]:
    endpoint = FUND_STORE_API_HOST + FUNDS_ENDPOINT
    response = get_data(endpoint)
    if response and len(response) > 0:
        funds = []
        for fund in response:
            funds.append(Fund.from_json(fund))
        return funds
    return None


def get_fund(fund_id: str) -> Union[Fund, None]:
    endpoint = FUND_STORE_API_HOST + FUND_ENDPOINT.format(fund_id=fund_id)
    response = get_data(endpoint)
    if response and "fund_id" in response:
        fund = Fund.from_json(response)
        if "rounds" in response and len(response["rounds"]) > 0:
            for fund_round in response["rounds"]:
                fund.add_round(Round.from_json(fund_round))
        return fund
    return None


def get_rounds(fund_id: str) -> Union[Fund, List]:
    endpoint = ROUND_STORE_API_HOST + ROUNDS_ENDPOINT.format(fund_id=fund_id)
    response = get_data(endpoint)
    rounds = []
    if response and len(response) > 0:
        for round_data in response:
            rounds.append(Round.from_json(round_data))
    return rounds


def get_round_with_applications(
    fund_id: str, round_id: str
) -> Union[Round, None]:
    round_endpoint = ROUND_STORE_API_HOST + ROUND_ENDPOINT.format(
        fund_id=fund_id, round_id=round_id
    )
    round_response = get_data(round_endpoint)
    if round_response and "round_id" in round_response:
        fund_round = Round.from_json(round_response)
        applications_response = call_search_applications(
            {
                "fund_id": fund_id,
                "datetime_start": fund_round.opens,
                "datetime_end": fund_round.deadline,
            }
        )
        if applications_response and len(applications_response) > 0:
            for application in applications_response:
                fund_round.add_application(Application.from_json(application))

        return fund_round
    return None


def get_applications(params: dict) -> Union[List[Application], None]:
    applications_response = call_search_applications(params)
    if applications_response and len(applications_response) > 0:
        applications = []
        for application_data in applications_response:
            applications.append(Application.from_json(application_data))

        return applications
    return None


def get_todo_summary() -> Union[Dict, None]:
    applications = call_search_applications("")
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


def get_application(identifier: str) -> Union[Application, None]:
    application_endpoint = (
        APPLICATION_STORE_API_HOST
        + APPLICATION_ENDPOINT.format(application_id=identifier)
    )
    application_response = get_data(application_endpoint)
    if application_response and "id" in application_response:
        application = Application.from_json(application_response)

        return application
    return None


def get_application_status(application_id: str) -> Union[Application, None]:
    application_status_endpoint = (
        APPLICATION_STORE_API_HOST
        + APPLICATION_STATUS_ENDPOINT.format(application_id=application_id)
    )
    print(application_status_endpoint)
    application_status_response = get_data(application_status_endpoint)
    if application_status_response and "id" in application_status_response:
        application = Application.from_json(application_status_response)

        return application
    return None


def get_questions(application_id):
    """_summary_: Function is set up to retrieve
    the data from application store with
    get_data() function.

    Args:
        application_id: Takes an application_id.

    Returns:
        Returns a dictionary of questions & their statuses.
    """
    status_endpoint = (
        APPLICATION_STORE_API_HOST
        + APPLICATION_STATUS_ENDPOINT.format(application_id=application_id)
    )

    questions = get_data(status_endpoint)
    if questions:
        data = {title: status for title, status in questions.items()}
        return data
