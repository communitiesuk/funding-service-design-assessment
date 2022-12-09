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
from app.assess.models.sub_criteria import SubCriteria
from config import Config
from flask import abort
from flask import current_app


def get_data(endpoint: str, use_local_data: bool = Config.USE_LOCAL_DATA):
    if use_local_data:
        current_app.logger.info(f"Fetching local data from '{endpoint}'.")
        data = get_local_data(endpoint)
    else:
        current_app.logger.info(f"Fetching data from '{endpoint}'.")
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
        else:
            return None
    return data


def get_local_data(endpoint: str):
    api_data_json = os.path.join(
        Config.FLASK_ROOT, "tests", "api_data", "endpoint_data.json"
    )
    fp = open(api_data_json)
    api_data = json.load(fp)
    fp.close()
    if endpoint in api_data:
        return api_data.get(endpoint)


def call_search_applications(params: dict | str):
    applications_endpoint = (
        Config.APPLICATION_STORE_API_HOST
        + Config.APPLICATION_SEARCH_ENDPOINT.format(params=urlencode(params))
    )
    applications_response = get_data(applications_endpoint)
    return applications_response


def get_application_overviews(fund_id, round_id, search_params):
    overviews_endpoint = (
        Config.ASSESSMENT_STORE_API_HOST
    ) + Config.APPLICATION_OVERVIEW_ENDPOINT_FUND_ROUND_PARAMS.format(
        fund_id=fund_id, round_id=round_id, params=urlencode(search_params)
    )

    overviews_response = get_data(overviews_endpoint)
    return overviews_response


def get_funds() -> Union[List[Fund], None]:
    endpoint = Config.FUND_STORE_API_HOST + Config.FUNDS_ENDPOINT
    response = get_data(endpoint)
    if response and len(response) > 0:
        funds = []
        for fund in response:
            funds.append(Fund.from_json(fund))
        return funds
    return None


def get_fund(fund_id: str) -> Union[Fund, None]:
    endpoint = Config.FUND_STORE_API_HOST + Config.FUND_ENDPOINT.format(
        fund_id=fund_id
    )
    response = get_data(endpoint)
    if len(response) > 0:
        fund = Fund.from_json(response[0])
        if "rounds" in response and len(response["rounds"]) > 0:
            for fund_round in response["rounds"]:
                fund.add_round(Round.from_json(fund_round))
        return fund
    return None


def get_rounds(fund_id: str) -> Union[Fund, List]:
    endpoint = Config.FUND_STORE_API_HOST + Config.ROUNDS_ENDPOINT.format(
        fund_id=fund_id
    )
    response = get_data(endpoint)

    rounds = []
    if response and len(response) > 0:
        for round_data in response:
            rounds.append(Round.from_json(round_data))
    return rounds


def get_round(fund_id: str, round_id: str) -> Union[Round, None]:
    round_endpoint = Config.FUND_STORE_API_HOST + Config.ROUND_ENDPOINT.format(
        fund_id=fund_id, round_id=round_id
    )
    round_response = get_data(round_endpoint)
    if round_response and "assessment_deadline" in round_response:
        round_dict = Round.from_dict(round_response)
        return round_dict
    return None


def get_round_with_applications(
    fund_id: str, round_id: str
) -> Union[Round, None]:
    round_response = get_round(fund_id, round_id)
    if round_response:
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


def submit_score_and_justification(
    assessment_id, person_id, score, justification, sub_crit_id
):

    data_dict = {
        "score": score,
        "justification": justification,
        "person_id": person_id,
    }
    url = Config.ASSESSMENT_SCORES_ENDPOINT.format(
        assessment_id=assessment_id, sub_criteria_id=sub_crit_id
    )
    response = requests.post(url, json=data_dict)
    print(response.content)
    if response.status_code == 200:
        return True
    else:
        return False


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
        Config.APPLICATION_STORE_API_HOST
        + Config.APPLICATION_ENDPOINT.format(application_id=identifier)
    )
    application_response = get_data(application_endpoint)
    if application_response and "id" in application_response:
        application = Application.from_json(application_response)

        return application
    return None


def get_assessor_task_list_state(application_id: str) -> Union[dict, None]:
    overviews_endpoint = (
        Config.ASSESSMENT_STORE_API_HOST
    ) + Config.APPLICATION_OVERVIEW_ENDPOINT_APPLICATION_ID.format(
        application_id=application_id
    )

    metadata = get_data(overviews_endpoint)

    return metadata


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
        Config.APPLICATION_STORE_API_HOST
        + Config.APPLICATION_STATUS_ENDPOINT.format(
            application_id=application_id
        )
    )

    questions = get_data(status_endpoint)
    if questions:
        data = {title: status for title, status in questions.items()}
        return data


def  get_sub_criteria(application_id, sub_criteria_id):
    """_summary_: Function is set up to retrieve
    the data from assessment store with
    get_data() function.

    Args:
        application_id:
        sub_criteria_id

    Returns:
      {
        "sub_criteria_id": "",
        "sub_criteria_name": "", 
        "score_submitted": "",
        "themes": []
    }
    """
    sub_criteria_endpoint = (
        Config.ASSESSMENT_STORE_API_HOST
        + Config.SUB_CRITERIA_OVERVIEW_ENDPOINT.format(
            application_id=application_id,
            sub_criteria_id=sub_criteria_id
        )
    )
    sub_criteria_response = get_data(sub_criteria_endpoint)
    if sub_criteria_response and "id" in sub_criteria_response:
        return SubCriteria.from_filtered_dict(sub_criteria_response)
    else:
        msg = f"sub_criteria: '{sub_criteria_id}' not found."
        current_app.logger.warn(msg)
        abort(404, description=msg)


def get_assessment_config_mapping(
    fund_id: str, round_id: str
) -> Union[Dict, None]:
    assessment_mapping_endpoint = (
        Config.ASSESSMENT_MAPPING_CONFIG_ENDPOINT.format(
            fund_id=fund_id, round_id=round_id
        )
    )
    current_app.logger.info(assessment_mapping_endpoint)
    assessment_mapping_response = get_data(
        assessment_mapping_endpoint, use_local_data=False
    )
    if assessment_mapping_response:
        return assessment_mapping_response
    return None
