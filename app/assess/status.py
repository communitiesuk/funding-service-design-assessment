def get_status(questions):
    """_summary_: GIVEN function return a dictionary
    of statuses.

    Args:
        questions: Takes get_questions() function

    Returns:
        Returns dictionary of statuses
    """
    status = {}
    if questions:
        status["NOT STARTED"] = sum(
            value == "NOT STARTED" for value in questions.values()
        )
        status["IN PROGRESS"] = sum(
            value == "IN PROGRESS" for value in questions.values()
        )
        status["COMPLETED"] = sum(
            value == "COMPLETED" for value in questions.values()
        )
        status["TOTAL"] = sum(
            (
                (value == "NOT STARTED")
                + (value == "IN PROGRESS")
                + (value == "COMPLETED")
            )
            for value in questions.values()
        )
    return status

def all_status_completed(criteria_list):
    """ Function checks if all statuses are completed then returns True 
    otherwise returns False"""
    return all(sub_criteria.status == "COMPLETED" for criteria in criteria_list.criterias for sub_criteria in criteria.sub_criterias)
