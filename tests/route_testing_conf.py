"""
Our single source of truth for which
routes need to be tested and their expected
content.
"""
import jwt
from app.assess.data import get_local_data
from config import Config

intro_routes_and_test_content = {
    "/": [{"tag": "h1", "name": None, "contains": "Assessment Hub"}],
    "/assess": [{"tag": "h1", "name": None, "contains": "Funds"}],
    "/assess/landing": [
        {"tag": "h1", "name": None, "contains": "Team dashboard"}
    ],
}


def assessment_form_test_routes():
    application_endpoint = "application_store/applications/fund-app123-a"
    question_page_root = "/assess/application/fund-app123-a"
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


# For testing routes with login_required/requested decoraters
algorithm = "RS256"


def create_token(payload):
    return jwt.encode(payload, Config.RSA256_PRIVATE_KEY, algorithm=algorithm)
