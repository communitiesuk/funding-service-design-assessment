def get_status(questions):
    """_summary_: GIVEN function return a dictionary
    of statuses.

    Args:
        questions: Takes get_questions() function

    Returns:
        Returns dictionary of statuses
    """
    status = {}
    status["NOT STARTED"] = sum(
        value == "NOT STARTED" for value in questions.values()
    )
    status["IN PROGRESS"] = sum(
        value == "IN PROGRESS" for value in questions.values()
    )
    status["COMPLETED"] = sum(
        value == "COMPLETED" for value in questions.values()
    )
    return status
