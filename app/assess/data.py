import json
import os
from typing import List
from app.config import FUND_STORE_API_HOST
from app.config import APPLICATION_STORE_API_HOST
from app.config import FLASK_ROOT
from app.assess.models.fund import Fund
from app.assess.models.round import Round
from app.assess.models.application import Application
import requests


# Fund Store Endpoints
FUNDS_ENDPOINT = "/funds/"
FUND_ENDPOINT = "/funds/{fund_id}"
ROUND_ENDPOINT = "/funds/{fund_id}/round/{round_number}"

# Application Store Endpoints
APPLICATIONS_ENDPOINT = "/fund/{fund_id}?datetime_start={datetime_start}&datetime_end={datetime_end}"
APPLICATION_ENDPOINT = "/fund/{fund_id}?application_id={application_id}"


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
    api_data_json = os.path.join(FLASK_ROOT, "tests", "api_data", "endpoint_data.json")
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
    endpoint = FUND_STORE_API_HOST + FUND_ENDPOINT.format(
        fund_id=fund_id
    )
    response = get_data(endpoint)
    if response and "name" in response:
        fund = Fund.from_json(response)
        if "rounds" in response and len(response["rounds"]) > 0:
            for fund_round in response["rounds"]:
                new_round = Round.from_json(fund_round)
                fund.add_round(new_round)
        return fund
    return None


def get_round(fund_id: str, identifier: str) -> Round | None:
    round_endpoint = FUND_STORE_API_HOST + ROUND_ENDPOINT.format(
        fund_id=fund_id, round_number=identifier
    )
    round_response = get_data(round_endpoint)
    if round_response and "round_identifier" in round_response:
        fund_round = Round.from_json(round_response)
        applications_endpoint = APPLICATION_STORE_API_HOST + APPLICATIONS_ENDPOINT.format(
            fund_id=fund_id,
            datetime_start=fund_round.opens,
            datetime_end=fund_round.deadline
        )
        applications_response = get_data(applications_endpoint)
        if applications_response and len(applications_response) > 0:
            for application in applications_response:
                fund_round.add_application(
                    Application.from_json(application)
                )

        return fund_round
    return None


def get_application(fund_id: str, identifier: str) -> Application | None:
    application_endpoint = APPLICATION_STORE_API_HOST + APPLICATION_ENDPOINT.format(
        fund_id=fund_id,
        application_id=identifier
    )
    application_response = get_data(application_endpoint)
    if application_response and "id" in application_response:
        application = Application.from_json(application_response)

        return application
    return None


