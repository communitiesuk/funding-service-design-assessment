"""
Our single source of truth for which
routes need to be tested and their expected
content.
"""
from app.assess.data import get_local_data

intro_routes_and_test_content = {
    "/": [{"tag": "a", "name": None, "contains": "Assessment Hub"}],
    "/assess": [{"tag": "h1", "name": None, "contains": "Funds"}],
    "/assess/funding-service-design": [
        {"tag": "p", "name": None, "contains": "Please choose a round"}
    ],
    "/assess/funding-service-design/1": [
        {"tag": "p", "name": None, "contains": "Please choose an application"}
    ],
    "/assess/funding-service-design/1/application/bd65600d-8669-4903-8a14-af88203add38": [
        {
            "tag": "a",
            "name": None,
            "contains": "bd65600d-8669-4903-8a14-af88203add38",
        }
    ],
}


def assessment_form_test_routes():
    application_endpoint = "application_store/fund/funding-service-design?application_id=bd65600d-8669-4903-8a14-af88203add38"
    question_page_root = "/assess/funding-service-design/1/application/bd65600d-8669-4903-8a14-af88203add38"
    application_form = get_local_data(application_endpoint)
    routes = {}
    for index, question in enumerate(application_form["questions"]):
        question_path_suffix = "/question/" + str(index + 1)
        question_path = question_page_root + question_path_suffix
        tags = []
        for field in question["fields"]:
            tags.append(
                {
                    "tag": None,
                    "name": "qfield_key_" + field["key"],
                    "contains": field["title"],
                }
            )
            tags.append(
                {
                    "tag": None,
                    "name": "qfield_answer_" + field["key"],
                    "contains": field["answer"],
                }
            )
        routes.update({question_path: tags})
    return routes
