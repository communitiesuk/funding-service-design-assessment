"""
Our single source of truth for which
routes need to be tested and their expected
content.
"""
from app.assess.data import get_local_data

intro_routes_and_test_content = {
    "/": [{"tag": "a", "name": None, "contains": "Assessment Hub"}],
    "/assess": [{"tag": "h1", "name": None, "contains": "Funds"}],
    "/assess/landing": [
        {"tag": "p", "name": None, "contains": "Assessor dashboard"}
    ],
    # TODO work out what these should be once design finalised
    # "/assess/funding-service-design": [
    #     {"tag": "p", "name": None, "contains": "Please choose a round"}
    # ],
    # "/assess/funding-service-design/spring": [
    #     {"tag": "p", "name": None, "contains":
    # "Please choose an application"}
    # ],
    # "/assess/funding-service-design/summer": [
    #     {
    #         "tag": "p",
    #         "name": None,
    #         "contains": "No applications exist for this round yet.",
    #     }
    # ],
    # "/assess/application/fund-app123-a": [
    #     {
    #         "tag": "h1",
    #         "name": None,
    #         "contains": "fund-app123-a",
    #     }
    # ],
    # "/assess/application/bad-id": [
    #     {"tag": "h1", "name": None, "contains": "Page not found"}
    # ],
    # "/assess/landing/": [
    #     {
    #         "tag": "p",
    #         "name": None,
    #         "contains": "Your assessments",
    #     },
    #     {
    #         "tag": "a",
    #         "name": None,
    #         "contains": "All",
    #     },
    #     {
    #         "tag": "a",
    #         "name": None,
    #         "contains": "Completed",
    #     },
    #     {
    #         "tag": "a",
    #         "name": None,
    #         "contains": "Assessing",
    #     },
    #     {
    #         "tag": "a",
    #         "name": None,
    #         "contains": "Not Started",
    #     },
    #     {
    #         "tag": "a",
    #         "name": None,
    #         "contains": "fund-app123-a",
    #     },
    #     {
    #         "tag": "div",
    #         "name": "todo-summary-not-started",
    #         "contains": "2",
    #     },
    #     {
    #         "tag": "div",
    #         "name": "todo-summary-assessing",
    #         "contains": "0",
    #     },
    #     {
    #         "tag": "div",
    #         "name": "todo-summary-completed",
    #         "contains": "4",
    #     },
    #     {
    #         "tag": "strong",
    #         "name": None,
    #         "contains": "COMPLETED",
    #     },
    # ],
    # "/assess/landing?status_only=completed": [
    #     {
    #         "tag": "p",
    #         "name": None,
    #         "contains": "Your assessments",
    #     },
    #     {
    #         "tag": "a",
    #         "name": None,
    #         "contains": "fund-app123-a",
    #     },
    #     {
    #         "tag": "strong",
    #         "name": None,
    #         "contains": "COMPLETED",
    #     },
    # ],
    # "/assess/fragments/structured_question": [
    #     {
    #         "tag": "h2",
    #         "name": None,
    #         "contains": "Declarations",
    #     },
    #     {
    #         "tag": "h3",
    #         "name": None,
    #         "contains": (
    #             "Would funding your organisation be classed as State Aid?"
    #         ),
    #     },
    #     {
    #         "tag": "h3",
    #         "name": None,
    #         "contains": (
    #             "Does your application comply
    # with all relevant environmental"
    #             " standards?"
    #         ),
    #     },
    # ],
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
