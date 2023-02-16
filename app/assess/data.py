import json
import os
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import quote_plus
from urllib.parse import urlencode

import boto3
import requests
from app.assess.models.application import Application
from app.assess.models.banner import Banner
from app.assess.models.comment import Comment
from app.assess.models.flag import Flag
from app.assess.models.fund import Fund
from app.assess.models.round import Round
from app.assess.models.score import Score
from app.assess.models.sub_criteria import SubCriteria
from botocore.exceptions import ClientError
from config import Config
from flask import abort
from flask import current_app
from flask import Response
from fsd_utils.locale_selector.get_lang import get_lang


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


def get_assessment_progress(application_metadata):
    application_ids_list = {
        "application_ids": [
            x.get("application_id") for x in application_metadata
        ]
    }
    endpoint_url = Config.ASSESSMENT_PROGRESS_ENDPOINT
    current_app.logger.info(
        f"Fetching assessment progress from '{endpoint_url}', with json"
        f" payload: {application_ids_list}."
    )
    response = requests.post(endpoint_url, json=application_ids_list)

    if not response.ok:
        current_app.logger.error(
            f"Could not get assessment progress for endpoint '{endpoint_url}'"
        )
        return application_metadata

    response_json = response.json()
    for res in response_json:
        for am in application_metadata:
            if am.get("application_id") == res.get("application_id"):
                am["progress"] = res.get("progress")

    return application_metadata


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


def get_bulk_accounts_dict(account_ids: List):
    account_url = Config.BULK_ACCOUNTS_ENDPOINT
    account_params = {"account_id": account_ids}
    return get_data(account_url, account_params)


def get_score_and_justification(
    application_id, sub_criteria_id, score_history=True
):
    score_url = Config.ASSESSMENT_SCORES_ENDPOINT
    score_params = {
        "application_id": application_id,
        "sub_criteria_id": sub_criteria_id,
        "score_history": score_history,
    }
    score_response = get_data(score_url, score_params)

    if not score_response or len(score_response) == 0:
        current_app.logger.info(
            f"No scores found for application: {application_id},"
            f" sub_criteria_id: {sub_criteria_id}"
        )
        return None

    current_app.logger.info(
        f"Response from Assessment Store: '{score_response}'."
    )
    account_ids = [score["user_id"] for score in score_response]
    bulk_accounts_dict = get_bulk_accounts_dict(account_ids)
    scores: list[Score] = [
        Score.from_dict(
            score
            | {
                "user_full_name": bulk_accounts_dict[score["user_id"]][
                    "full_name"
                ],
                "user_email": bulk_accounts_dict[score["user_id"]][
                    "email_address"
                ],
                "highest_role": bulk_accounts_dict[score["user_id"]][
                    "highest_role"
                ],
            }
        )
        for score in score_response
    ]
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


def get_assessments_stats(fund_id: str, round_id: str) -> Dict | None:
    assessments_stats_endpoint = (
        Config.ASSESSMENT_STORE_API_HOST
    ) + Config.ASSESSMENTS_STATS_ENDPOINT.format(
        fund_id=fund_id, round_id=round_id
    )
    current_app.logger.info(f"Endpoint '{assessments_stats_endpoint}'.")
    return get_data(assessments_stats_endpoint)


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


def get_banner_state(application_id: str):
    banner_state_endpoint = (
        Config.ASSESSMENT_STORE_API_HOST
        + Config.BANNER_STATE_ENDPOINT.format(application_id=application_id)
    )

    banner = get_data(banner_state_endpoint)

    if banner:
        return Banner.from_filtered_dict(banner)
    else:
        msg = f"banner_state: '{application_id}' not found."
        current_app.logger.warn(msg)
        abort(404, description=msg)


def get_latest_flag(application_id: str) -> Optional[Flag]:
    flag = get_data(
        Config.ASSESSMENT_LATEST_FLAG_ENDPOINT.format(
            application_id=application_id
        )
    )
    if flag:
        return Flag.from_dict(flag)
    else:
        msg = f"flag for application: '{application_id}' not found."
        current_app.logger.warn(msg)
        return None


def submit_flag(
    application_id: str,
    flag_type: str,
    user_id: str,
    justification: str = None,
    section: str = None,
) -> Flag | None:
    """Submits a new flag to the assessment store for an application.
    Returns Flag if a flag is created

    :param application_d: The application the flag belongs to.
    :param flag_type: The type of flag (e.g: 'FLAGGED' or 'STOPPED')
    :param user_id: The id of the user raising the flag
    :param justification: The justification for raising the flag
    :param section: The assessment section the flag has been raised for.
    """
    current_app.logger.info(
        "POSTing new flag to endpoint"
        f" '{Config.ASSESSMENT_LATEST_FLAG_ENDPOINT}'.\n"
        "Details: \n"
        f" - flag_type: {flag_type} \n"
        f" - application_id: '{application_id}') \n"
    )
    flag = requests.post(
        Config.ASSESSMENT_LATEST_FLAG_ENDPOINT,
        json={
            "application_id": application_id,
            "justification": justification,
            "section_to_flag": section,
            "flag_type": flag_type,
            "user_id": user_id,
        },
    )
    if flag:
        flag_json = flag.json()
        return Flag.from_dict(flag_json)


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


def get_comments(
    application_id: str, sub_criteria_id: str, theme_id: str | None, themes
):
    """_summary_: Get comments from the assessment store
    Args:
        application_id: application_id,
        sub_criteria_id: sub_criteria_id
        theme_id: optional theme_id (else returns all comments for subcriteria)
        themes: list of subcriteria themes
    Returns:
        Returns a dictionary of comments.
    """
    query_params = {
        "application_id": application_id,
        "sub_criteria_id": sub_criteria_id,
        "theme_id": theme_id,
    }
    # Strip theme_id from dict if None
    query_params_strip_nones = {
        k: v for k, v in query_params.items() if v is not None
    }
    comment_endpoint = (
        f"{Config.ASSESSMENT_COMMENT_ENDPOINT}"
        f"?{urlencode(query=query_params_strip_nones)}"
    )
    comment_response = get_data(comment_endpoint)

    if not comment_response or len(comment_response) == 0:
        current_app.logger.info(
            f"No comments found for application: {application_id},"
            f" sub_criteria_id: {sub_criteria_id}"
        )
        return None

    account_ids = [comment["user_id"] for comment in comment_response]
    bulk_accounts_dict = get_bulk_accounts_dict(account_ids)

    comments: list[Comment] = [
        Comment.from_dict(
            comment
            | {
                "full_name": bulk_accounts_dict[comment["user_id"]][
                    "full_name"
                ],
                "email_address": bulk_accounts_dict[comment["user_id"]][
                    "email_address"
                ],
                "highest_role": bulk_accounts_dict[comment["user_id"]][
                    "highest_role"
                ],
            }
        )
        for comment in comment_response
    ]
    theme_id_to_comments_list_map = {
        theme.id: [
            comment for comment in comments if comment.theme_id == theme.id
        ]
        for theme in themes
    }
    return theme_id_to_comments_list_map


def submit_comment(
    comment, application_id, sub_criteria_id, user_id, theme_id
):
    data_dict = {
        "comment": comment,
        "user_id": user_id,
        "application_id": application_id,
        "sub_criteria_id": sub_criteria_id,
        "comment_type": "COMMENT",
        "theme_id": theme_id,
    }
    url = Config.ASSESSMENT_COMMENT_ENDPOINT
    response = requests.post(url, json=data_dict)
    current_app.logger.info(
        f"Response from Assessment Store: '{response.json()}'."
    )

    return response.ok


def get_file_response(file_name: str, application_id: str):
    """_summary_: Function is set up to retrieve
    files from aws bucket.
    Args:
        filename: Takes an filename
        application_id: Takes an application_id # noqa
    Returns:
        Returns a response with a file from aws.
    """

    if file_name is None:
        return None

    prefixed_file_name = application_id + "/" + file_name

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        region_name=Config.AWS_REGION,
    )

    try:
        obj = s3_client.get_object(
            Bucket=Config.AWS_BUCKET_NAME, Key=prefixed_file_name
        )

        mimetype = obj["ResponseMetadata"]["HTTPHeaders"]["content-type"]
        data = obj["Body"].read()

        response = Response(
            data,
            mimetype=mimetype,
            headers={
                "Content-Disposition": (
                    f"attachment;filename={quote_plus(file_name)}"
                )
            },
        )
        return response
    except ClientError as e:
        current_app.logger.error(e)
        raise Exception(e)


def get_default_round_data():
    language = {"language": get_lang()}
    round_request_url = Config.GET_ROUND_DATA_FOR_FUND_ENDPOINT.format(
        fund_id=Config.DEFAULT_FUND_ID, round_id=Config.DEFAULT_ROUND_ID
    )
    round_response = get_data(round_request_url, language)
    return round_response
