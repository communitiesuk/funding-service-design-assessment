"""
A very basic python configuration file.
Our single source of truth for which
routes need to be tested and their expected
content.
"""
routes_and_test_content = {
    "/": b"Assessment Hub",
    "/assess/": b"Funds"
}

known_routes_and_test_content = {
    "/": [
        {"tag": "a", "name": None, "contains": "Assessment Hub"}
    ],
    "/assess": [
        {"tag": "h1", "name": None, "contains": "Funds"}
    ],
    "/assess/funding-service-design": [
        {"tag": "p", "name": None, "contains": "Please choose a round"}
    ],
    "/assess/funding-service-design/1": [
        {"tag": "p", "name": None, "contains": "Please choose an application"}
    ],
    "/assess/funding-service-design/1/application/bd65600d-8669-4903-8a14-af88203add38": [
        {"tag": "a", "name": None, "contains": "bd65600d-8669-4903-8a14-af88203add38"}
    ],
}
