import json
import os
from typing import List

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
ROUNDS_ENDPOINT = "/fund/{fund_id}"
ROUND_ENDPOINT = "/fund/{fund_id}/round/{round_id}"

# Application Store Endpoints
APPLICATIONS_ENDPOINT = "".join(
    [
        "/fund/{fund_id}?",
        "datetime_start={datetime_start}&datetime_end={datetime_end}",
    ]
)
APPLICATION_ENDPOINT = "/fund/{fund_id}?application_id={application_id}"


def get_data(endpoint: str):
    if endpoint[:8] == "https://":
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            print(data)
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


def get_status_data(endpoint, application_id):
    """_summary_: Function is set up to retrive
     the data with GET request from application store.

    Args:
        endpoint: Takes an application store endpoint.
        application_id: Takes an application_id.

    Returns:
        Returns a dictionary of questions & their statuses.
    """
    if endpoint[:8] == "https://":
        endpoint = f"{endpoint}/fund/status/{application_id}"
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
        else:
            return None
    else:
        data = get_local_status_data(endpoint, application_id)
    return data


def get_local_status_data(endpoint, application_id):
    """_summary_: GIVEN function triggers during development
    to grab the moc data from local machine when get_status_data
    has no communication with the application data store.

    Args:
        endpoint: Takes endpoint from the moc data.
        application_id: Takes application id from the moc data.

    Returns:
         Returns a dictionary of questions & their statuses.
    """
    local_data_endpoint = os.path.join(
        FLASK_ROOT, "tests", "api_data", "endpoint_data.json"
    )
    fp = open(local_data_endpoint)
    api_data = json.load(fp)
    fp.close()
    application_endpoint = f"{endpoint}/fund/funding-service-design?application_id={application_id}"  # noqa

    if application_endpoint in api_data:
        questions = api_data.get(application_endpoint).get("questions")
        data = {data.get("question"): data.get("status") for data in questions}
        return data


def get_status_NOT_COMPLETED(statuses):
    """_summary_: Given function returns
    "IN PROGRESS" or "NOT STARTED" status
    only from all the questions/statuses retrived
    from get_status_data
    function.

    Args:
        statuses: Takes an instance of get_status_data
        function.

    Returns:
        Returns questions with status of "IN PROGRESS" or
         "NOT STARTED".
    """
    return {
        question: status
        for question, status in statuses.items()
        if (status == "NOT STARTED" or status == "IN PROGRESS")
    }


def get_status_COMPLETED(statuses):
    """_summary_:Given function returns
    "COMPLETED" status only from all the
     questions/statuses retrived from get_status_data
    function.

    Args:
        statuses: Takes an instance of get_status_data
        function.

    Returns:
        Returns questions with status of "COMPLETED".

    """
    return {
        question: status
        for question, status in statuses.items()
        if status == "COMPLETED"
    }
