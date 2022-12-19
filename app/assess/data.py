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
from app.assess.models.score import Score
from app.assess.models.sub_criteria import SubCriteria
from config import Config
from flask import abort
from flask import current_app


def get_data(
    endpoint: str,
    payload: Dict = None,
    use_local_data: bool = Config.USE_LOCAL_DATA,
):
    if use_local_data:
        current_app.logger.info(f"Fetching local data from '{endpoint}'.")
        return get_local_data(endpoint)
    else:
        if payload:
            current_app.logger.info(
                f"Fetching data from '{endpoint}', with payload: {payload}."
            )
            response = requests.get(endpoint, payload)
        else:
            current_app.logger.info(f"Fetching data from '{endpoint}'.")
            response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            current_app.logger.error(
                f"Could not get data for endpoint '{endpoint}' "
            )
            return None


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
    current_app.logger.info(f"Endpoint '{overviews_endpoint}'.")
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
    fund = Fund.from_json(response)
    if "rounds" in response and len(response["rounds"]) > 0:
        for fund_round in response["rounds"]:
            fund.add_round(Round.from_json(fund_round))
    return fund


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
    current_app.logger.info(round_response)
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


def get_score_and_justification(
    application_id, sub_criteria_id, score_history=True
):
    url = Config.ASSESSMENT_SCORES_ENDPOINT
    params = {
        "application_id": application_id,
        "sub_criteria_id": sub_criteria_id,
        "score_history": score_history,
    }
    response = get_data(url, params)
    current_app.logger.info(f"Response from Assessment Store: '{response}'.")

    scores: list[Score] = [Score.from_dict(score) for score in response]

    return scores


def submit_score_and_justification(
    score, justification, application_id, user_id, sub_criteria_id
):
    data_dict = {
        "score": score,
        "justification": justification,
        "user_id": user_id,
        "application_id": application_id,
        "sub_criteria_id": sub_criteria_id,
    }
    url = Config.ASSESSMENT_SCORES_ENDPOINT
    response = requests.post(url, json=data_dict)
    current_app.logger.info(
        f"Response from Assessment Store: '{response.json()}'."
    )
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


def get_sub_criteria(application_id, sub_criteria_id):
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
            application_id=application_id, sub_criteria_id=sub_criteria_id
        )
    )
    sub_criteria_response = get_data(sub_criteria_endpoint)
    if sub_criteria_response and "id" in sub_criteria_response:
        return SubCriteria.from_filtered_dict(sub_criteria_response)
    else:
        msg = f"sub_criteria: '{sub_criteria_id}' not found."
        current_app.logger.warn(msg)
        abort(404, description=msg)


def get_sub_criteria_theme_answers(
    application_id: str, theme_id: str
) -> Union[list, None]:
    theme_answers_endpoint = (
        Config.ASSESSMENT_STORE_API_HOST
        + Config.SUB_CRITERIA_THEME_ANSWERS_ENDPOINT.format(
            application_id=application_id, theme_id=theme_id
        )
    )
    theme_answers_response = get_data(theme_answers_endpoint)

    if theme_answers_response:
        return theme_answers_response
    else:
        msg = f"theme_answers: '{theme_id}' not found."
        current_app.logger.warn(msg)
        abort(404, description=msg)


def get_comments(application_id: str, sub_criteria_id: str):
    """_summary_: Function is set up to retrieve
    the data from application store with
    get_data() function.
    Args:
        application_id: Takes an application_id, sub_criteria_id: takes a sub_criteria_id # noqa
    Returns:
        Returns a dictionary of comments.
    """
    comment_endpoint = (
        Config.ASSESSMENT_STORE_API_HOST
        + Config.COMMENTS_ENDPOINT.format(
            application_id=application_id, sub_criteria_id=sub_criteria_id
        )
    )
    comment_response = get_data(comment_endpoint)
    return comment_response
