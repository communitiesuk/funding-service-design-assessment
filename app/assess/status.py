import json
import os

import requests
from app.config import FLASK_ROOT


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
