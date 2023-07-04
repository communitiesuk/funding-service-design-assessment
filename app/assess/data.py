from copy import deepcopy
from functools import lru_cache
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import urlencode

import requests
from app.assess.models.application import Application
from app.assess.models.banner import Banner
from app.assess.models.comment import Comment
from app.assess.models.flag import Flag
from app.assess.models.flag_v2 import FlagTypeV2
from app.assess.models.flag_v2 import FlagV2
from app.assess.models.fund import Fund
from app.assess.models.round import Round
from app.assess.models.score import Score
from app.assess.models.sub_criteria import SubCriteria
from boto3 import client
from botocore.exceptions import ClientError
from config import Config
from flask import abort
from flask import current_app
from flask import url_for
from fsd_utils import NotifyConstants
from fsd_utils.locale_selector.get_lang import get_lang

# TODO : Need to remove this once old rounds are migrated to use new flags
rounds_using_old_flags = [
    "c603d114-5364-4474-a0c4-c41cbf4d3bbd",
    "5cf439bf-ef6f-431e-92c5-a1d90a4dd32f",
]


def get_data(endpoint: str, payload: Dict = None):

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
    ) + Config.APPLICATION_OVERVIEW_FLAGS_V2_ENDPOINT_FUND_ROUND_PARAMS.format(
        fund_id=fund_id, round_id=round_id, params=urlencode(search_params)
    )
    current_app.logger.info(f"Endpoint '{overviews_endpoint}'.")
    overviews_response = get_data(overviews_endpoint)

    return overviews_response


@lru_cache(maxsize=1)
def get_funds(ttl_hash=None) -> Union[List[Fund], None]:
    del ttl_hash  # unused, but required for lru_cache
    current_app.logger.info("Fetching funds from fund store.")
    endpoint = Config.FUND_STORE_API_HOST + Config.FUNDS_ENDPOINT
    response = get_data(endpoint)
    if response and len(response) > 0:
        funds = []
        for fund in response:
            funds.append(Fund.from_json(fund))
        return funds
    return None


def get_fund(fid: str, use_short_name: bool = False) -> Union[Fund, None]:
    endpoint = Config.FUND_STORE_API_HOST + Config.FUND_ENDPOINT.format(
        fund_id=fid, use_short_name=use_short_name
    )
    response = get_data(endpoint)
    if not response:
        return None

    fund = Fund.from_json(response)
    if "rounds" in response and len(response["rounds"]) > 0:
        for fund_round in response["rounds"]:
            fund.add_round(Round.from_json(fund_round))
    return fund


def get_rounds(fund_id: str) -> list[Round]:
    endpoint = Config.FUND_STORE_API_HOST + Config.ROUNDS_ENDPOINT.format(
        fund_id=fund_id
    )
    response = get_data(endpoint)

    rounds = []
    if response and len(response) > 0:
        for round_data in response:
            rounds.append(Round.from_dict(round_data))
    return rounds


def get_round(
    fid: str, rid: str, use_short_name: bool = False
) -> Union[Round, None]:
    round_endpoint = Config.FUND_STORE_API_HOST + Config.ROUND_ENDPOINT.format(
        fund_id=fid, round_id=rid, use_short_name=use_short_name
    )
    round_response = get_data(round_endpoint)
    current_app.logger.info(round_response)
    if round_response and "assessment_deadline" in round_response:
        round_dict = Round.from_dict(round_response)
        return round_dict
    return None


def get_bulk_accounts_dict(account_ids: List, fund_short_name: str):
    if account_ids:
        account_ids_to_retrieve = list(set(account_ids))
        account_url = Config.BULK_ACCOUNTS_ENDPOINT
        account_params = {"account_id": account_ids_to_retrieve}
        users_result = get_data(account_url, account_params)
        if Config.FLASK_ENV == "development":
            debug_user_config = deepcopy(Config.DEBUG_USER)
            debug_user_config["email_address"] = Config.DEBUG_USER["email"]
            debug_user_config["highest_role_map"] = {
                fund_short_name: Config.DEBUG_USER_ROLE
            }
            del debug_user_config["highest_role"]
            users_result[Config.DEBUG_USER_ACCOUNT_ID] = debug_user_config

        for user_result in users_result.values():
            # we only need the highest role for the fund we are currently viewing
            highest_role = user_result["highest_role_map"][fund_short_name]
            user_result["highest_role"] = highest_role
            del user_result["highest_role_map"]

        return users_result
    else:
        current_app.logger.info("No account ids supplied")
        return {}


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
    if score_response:
        current_app.logger.info(
            f"Response from Assessment Store: '{score_response}'."
        )

    else:
        current_app.logger.info(
            f"No scores found for application: {application_id},"
            f" sub_criteria_id: {sub_criteria_id}"
        )
    return score_response


def match_score_to_user_account(scores, fund_short_name):
    account_ids = [score["user_id"] for score in scores]
    bulk_accounts_dict = get_bulk_accounts_dict(account_ids, fund_short_name)
    scores_with_account: list[Score] = [
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
        for score in scores
    ]
    return scores_with_account


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


def get_assessments_stats(
    fund_id: str, round_id: str, search_params: dict = {}
) -> Dict | None:
    assessments_stats_endpoint = (
        Config.ASSESSMENT_STORE_API_HOST
    ) + Config.ASSESSMENTS_STATS_ENDPOINT.format(
        fund_id=fund_id, round_id=round_id, params=urlencode(search_params)
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


def get_application_metadata(application_id: str) -> Union[dict, None]:
    application_endpoint = Config.APPLICATION_METADATA_ENDPOINT.format(
        application_id=application_id
    )
    application_metadata = get_data(application_endpoint)
    return application_metadata


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


def get_sub_criteria_banner_state(application_id: str):
    SUB_CRITERIA_BANNER_STATE_ENDPOINT = (
        Config.ASSESSMENT_STORE_API_HOST
        + Config.SUB_CRITERIA_BANNER_STATE_ENDPOINT.format(
            application_id=application_id
        )
    )

    banner = get_data(SUB_CRITERIA_BANNER_STATE_ENDPOINT)

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


def get_flag(flag_id: str) -> Optional[FlagV2]:
    flag = get_data(Config.ASSESSMENT_FLAG_V2_ENDPOINT.format(flag_id=flag_id))
    if flag:
        return FlagV2.from_dict(flag)
    else:
        msg = f"flag for id: '{flag_id}' not found."
        current_app.logger.warn(msg)
        return None


def get_flags(application_id: str) -> List[FlagV2]:
    flag = get_data(
        Config.ASSESSMENT_FLAGS_V2_ENDPOINT.format(
            application_id=application_id
        )
    )
    if flag:
        return FlagV2.from_list(flag)
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
    allocation: str = None,
    flag_id: str = None,
) -> FlagV2 | None:
    """Submits a new flag to the assessment store for an application.
    Returns Flag if a flag is created

    :param application_d: The application the flag belongs to.
    :param flag_type: The type of flag (e.g: 'FLAGGED' or 'STOPPED')
    :param user_id: The id of the user raising the flag
    :param justification: The justification for raising the flag
    :param section: The assessment section the flag has been raised for.
    """
    flag_type = FlagTypeV2[flag_type]
    if flag_id:
        flag = requests.put(
            Config.ASSESSMENT_FLAGS_V2_POST_ENDPOINT,
            json={
                "assessment_flag_id": flag_id,
                "justification": justification,
                "user_id": user_id,
                "allocation": allocation,
                "status": flag_type.value,
            },
        )
    else:
        flag = requests.post(
            Config.ASSESSMENT_FLAGS_V2_POST_ENDPOINT,
            json={
                "application_id": application_id,
                "justification": justification,
                "sections_to_flag": section,
                "user_id": user_id,
                "allocation": allocation,
                "status": flag_type.value,
            },
        )
    if flag:
        flag_json = flag.json()
        return FlagV2.from_dict(flag_json)


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
    application_id: str, sub_criteria_id: str, theme_id: str | None
):
    """_summary_: Get comments from the assessment store
    Args:
        application_id: application_id,
        sub_criteria_id: sub_criteria_id
        theme_id: optional theme_id (else returns all comments for subcriteria)
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
    else:
        return comment_response


def match_comment_to_theme(comment_response, themes, fund_short_name):
    """_summary_: match the comment response to its theme and account information
    Args:
        comment_response: assessment store comments response for a theme,
        themes: list of subcriteria themes
        fund_short_name: fund short name
    Returns:
        Returns a dictionary of comments.
    """
    account_ids = [comment["user_id"] for comment in comment_response]
    bulk_accounts_dict = get_bulk_accounts_dict(account_ids, fund_short_name)

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
                "fund_short_name": fund_short_name,
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


_S3_CLIENT = client(
    "s3",
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.AWS_REGION,
)


def get_file_for_download_from_aws(file_name: str, application_id: str):
    """_summary_: Function is set up to retrieve
    files from aws bucket.
    Args:
        filename: Takes an filename
        application_id: Takes an application_id # noqa
    Returns:
        Returns a tuple of (file_content, mime_type)
    """

    if file_name is None:
        return None

    prefixed_file_name = application_id + "/" + file_name

    try:
        obj = _S3_CLIENT.get_object(
            Bucket=Config.AWS_BUCKET_NAME, Key=prefixed_file_name
        )

        mimetype = obj["ResponseMetadata"]["HTTPHeaders"]["content-type"]
        data = obj["Body"].read()

        return data, mimetype
    except ClientError as e:
        current_app.logger.error(e)
        raise Exception(e)


def list_files_in_folder(prefix):
    response = _S3_CLIENT.list_objects_v2(
        Bucket=Config.AWS_BUCKET_NAME, Prefix=prefix
    )
    keys = []
    for obj in response.get("Contents") or []:
        # we cut off the application id.
        _, key = obj["Key"].split("/", 1)
        keys.append(key)
    return keys


def get_files_for_application_upload_fields(
    application_id: str, short_id: str, application_json: dict
) -> List[tuple]:
    """
    This function retrieves the file names from an application_json
    then uses this to create a lsit of tuples containing the file name
    and download link for this file.

    Parameters:
    application_id (str): The unique identifier of the application.
    short_id (str): The unique short-hand identifier of the application.
    application_json (dict): The jsonified data for an application

    Returns:
    List[tuple]: A list of tuples, where each tuple contains the
    file name and its download link.
    """
    forms = application_json["jsonb_blob"]["forms"]
    file_names = []

    for form in forms:
        for question in form[NotifyConstants.APPLICATION_QUESTIONS_FIELD]:
            for field in question["fields"]:
                if field["type"] == "file" and field.get("answer"):
                    file_names.append(field["answer"])

    files = [
        (
            file,
            url_for(
                "assess_bp.get_file",
                application_id=application_id,
                file_name=file,
                short_id=short_id,
            ),
        )
        for file in file_names
    ]
    return files


def get_application_json(application_id):
    endpoint = Config.APPLICATION_JSON_ENDPOINT.format(
        application_id=application_id
    )
    response = requests.get(endpoint)
    return response.json()


def get_default_round_data():
    language = {"language": get_lang()}
    round_request_url = Config.GET_ROUND_DATA_FOR_FUND_ENDPOINT.format(
        fund_id=Config.DEFAULT_FUND_ID, round_id=Config.DEFAULT_ROUND_ID
    )
    round_response = get_data(round_request_url, language)
    return round_response
