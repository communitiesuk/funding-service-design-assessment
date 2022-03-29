from app.assess.data import get_data
from app.config import APPLICATION_STORE_API_HOST

STATUS_ENDPOINT = (
    "/fund/funding-service-design?application_id={application_id}"
)


def get_statuses(application_id):
    """_summary_: Function is set up to retrive
     the data with get_data() function from application store.

    Args:
        application_id: Takes an application_id.

    Returns:
        Returns a dictionary of questions & their statuses.
    """
    status_endpoint = APPLICATION_STORE_API_HOST + STATUS_ENDPOINT.format(
        application_id=application_id
    )
    api_data = get_data(status_endpoint)
    if application_id in api_data.get("id"):
        questions = api_data.get("questions")
        data = {data.get("question"): data.get("status") for data in questions}
        return data


def get_status_not_completed(statuses):
    """_summary_: Given function returns the length
    of status for "IN PROGRESS" or "NOT STARTED"
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
    number_of_questions_not_completed = {
        question: status
        for question, status in statuses.items()
        if (status == "NOT STARTED" or status == "IN PROGRESS")
    }

    return len(number_of_questions_not_completed)


def get_status_completed(statuses):
    """_summary_:Given function returns the length
    of status "COMPLETED" only from all the
     questions/statuses retrived from get_status_data
    function.

    Args:
        statuses: Takes an instance of get_status_data
        function.

    Returns:
        Returns questions with status of "COMPLETED".

    """
    number_of_questions_completed = {
        question: status
        for question, status in statuses.items()
        if status == "COMPLETED"
    }

    return len(number_of_questions_completed)
