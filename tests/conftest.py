import multiprocessing
import platform
from pathlib import Path
from unittest import mock

import jwt as jwt
import pytest
from app.create_app import create_app
from config import Config
from flask import template_rendered
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from tests.api_data.test_data import mock_api_results
from webdriver_manager.chrome import ChromeDriverManager

if platform.system() == "Darwin":
    multiprocessing.set_start_method("fork")  # Required on macOSX

test_lead_assessor_claims = {
    "accountId": "lead",
    "email": "lead@test.com",
    "fullName": "Test User",
    "roles": ["LEAD_ASSESSOR", "ASSESSOR", "COMMENTER"],
}

test_assessor_claims = {
    "accountId": "assessor",
    "email": "assessor@test.com",
    "fullName": "Test User",
    "roles": ["ASSESSOR", "COMMENTER"],
}

test_commenter_claims = {
    "accountId": "commenter",
    "email": "commenter@test.com",
    "fullName": "Test User",
    "roles": ["COMMENTER"],
}

test_roleless_user_claims = {
    "accountId": "test-user",
    "email": "test@example.com",
    "fullName": "Test User",
    "roles": [],
}


def create_valid_token(payload=test_assessor_claims):

    _test_private_key_path = (
        str(Path(__file__).parent) + "/keys/rsa256/private.pem"
    )
    with open(_test_private_key_path, mode="rb") as private_key_file:
        rsa256_private_key = private_key_file.read()

        return jwt.encode(payload, rsa256_private_key, algorithm="RS256")


def create_invalid_token():

    _test_private_key_path = (
        str(Path(__file__).parent) + "/keys/rsa256/private_invalid.pem"
    )
    with open(_test_private_key_path, mode="rb") as private_key_file:
        rsa256_private_key = private_key_file.read()

        return jwt.encode(
            test_assessor_claims, rsa256_private_key, algorithm="RS256"
        )


def post_driver(driver, path, params):
    driver.execute_script(
        """
    function post(path, params, method='post') {
        const form = document.createElement('form');
        form.method = method;
        form.action = path;

        for (const key in params) {
            if (params.hasOwnProperty(key)) {
            const hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.name = key;
            hiddenField.value = params[key];

            form.appendChild(hiddenField);
        }
      }

      document.body.appendChild(form);
      form.submit();
    }

    post(arguments[0], arguments[1]);
    """,
        path,
        params,
    )


@pytest.fixture(scope="session")
def app():
    """
    Returns an instance of the Flask app as a fixture for testing,
    which is available for the testing session and accessed with the
    @pytest.mark.uses_fixture('live_server')
    :return: An instance of the Flask app.
    """
    with create_app().app_context():
        yield create_app()


@pytest.fixture(scope="function")
def templates_rendered(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture(scope="function")
def flask_test_client(app, user_token=None):
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """
    with app.test_client() as test_client:
        test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            user_token or create_valid_token(),
        )
        yield test_client


@pytest.fixture(scope="class")
def selenium_chrome_driver(request, live_server):
    """
    Returns a Selenium Chrome driver as a fixture for testing.
    using an installed Chromedriver from the .venv chromedriver_py package
    install location. Accessible with the
    @pytest.mark.uses_fixture('selenium_chrome_driver')
    :return: A selenium chrome driver.
    """

    service_object = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # TODO: set chrome_options.binary_location = ...
    #  (if setting to run in container or on GitHub)
    chrome_driver = webdriver.Chrome(
        service=service_object, options=chrome_options
    )
    request.cls.driver = chrome_driver
    yield
    request.cls.driver.close()


@pytest.fixture(scope="function")
def mock_get_banner_state(request):
    from app.assess.models.banner import Banner

    marker = request.node.get_closest_marker("application_id")
    application_id = marker.args[0]

    mock_banner_info = Banner.from_filtered_dict(
        mock_api_results[
            "assessment_store/sub_criteria_overview/"
            f"banner_state/{application_id}"
        ]
    )

    with (
        mock.patch(
            "app.assess.helpers.get_banner_state",
            return_value=mock_banner_info,
        ),
        mock.patch(
            "app.assess.routes.get_banner_state",
            return_value=mock_banner_info,
        ),
    ):
        yield


@pytest.fixture(scope="function")
def mock_get_fund():
    from app.assess.models.fund import Fund

    mock_fund_info = Fund.from_json(
        mock_api_results["fund_store/funds/{fund_id}"]
    )

    with (
        mock.patch("app.assess.routes.get_fund", return_value=mock_fund_info),
        mock.patch("app.assess.helpers.get_fund", return_value=mock_fund_info),
    ):
        yield


@pytest.fixture(scope="function")
def mock_get_round():
    from app.assess.models.round import Round

    mock_fund_info = Round.from_dict(
        mock_api_results["fund_store/funds/{fund_id}/rounds/{round_id}"]
    )

    with mock.patch(
        "app.assess.routes.get_round", return_value=mock_fund_info
    ) as mocked_round:
        yield mocked_round

    mocked_round.assert_called_once_with(
        Config.COF_FUND_ID, Config.COF_ROUND2_W3_ID
    )


@pytest.fixture(scope="function")
def mock_get_application_overviews(request):
    marker = request.node.get_closest_marker("expected_search_params")
    if marker:
        search_params = marker.args[0]
    else:
        search_params = {
            "search_term": "",
            "search_in": "project_name,short_id",
            "asset_type": "ALL",
            "status": "ALL",
        }

    with mock.patch(
        "app.assess.routes.get_application_overviews",
        return_value=mock_api_results[
            "assessment_store/application_overviews/{fund_id}/{round_id}?"
        ],
    ) as mocked_apps_overview:
        yield mocked_apps_overview

    mocked_apps_overview.assert_called_with(
        Config.COF_FUND_ID, Config.COF_ROUND2_W3_ID, search_params
    )


@pytest.fixture(scope="function")
def mock_get_assessor_tasklist_state(request):
    marker = request.node.get_closest_marker("application_id")
    application_id = marker.args[0]
    mock_tasklist_state = mock_api_results[
        f"assessment_store/application_overviews/{application_id}"
    ]
    with mock.patch(
        "app.assess.routes.get_assessor_task_list_state",
        return_value=mock_tasklist_state,
    ) as mocked_tasklist_state:
        yield mocked_tasklist_state

    mocked_tasklist_state.assert_called_with(application_id)


@pytest.fixture(scope="function")
def mock_get_assessment_stats():

    with mock.patch(
        "app.assess.routes.get_assessments_stats",
        return_value=mock_api_results[
            "assessment_store/assessments/get-stats/{fund_id}/{round_id}"
        ],
    ) as mocked_assessment_stats:
        yield mocked_assessment_stats

    mocked_assessment_stats.assert_called_once_with(
        Config.COF_FUND_ID, Config.COF_ROUND2_W3_ID
    )


@pytest.fixture(scope="function")
def mock_get_assessment_progress():

    with mock.patch(
        "app.assess.routes.get_assessment_progress",
        return_value=mock_api_results[
            "assessment_store/application_overviews/{fund_id}/{round_id}?"
        ],
    ) as mocked_progress_func:
        yield mocked_progress_func

    mocked_progress_func.assert_called_once()


@pytest.fixture(scope="function")
def mock_get_latest_flag(request):
    from app.assess.models.flag import Flag

    marker = request.node.get_closest_marker("application_id")
    application_id = marker.args[0]

    mock_flag_info = Flag.from_dict(
        mock_api_results[
            f"assessment_store/flag?application_id={application_id}"
        ]
    )
    with (
        mock.patch(
            "app.assess.routes.get_latest_flag", return_value=mock_flag_info
        ),
        mock.patch(
            "app.assess.helpers.get_latest_flag", return_value=mock_flag_info
        ),
    ):
        yield


@pytest.fixture(scope="function")
def mock_get_bulk_accounts(request):
    mock_bulk_accounts = mock_api_results["account_store/bulk-accounts"]
    with (
        mock.patch(
            "app.assess.routes.get_bulk_accounts_dict",
            return_value=mock_bulk_accounts,
        ),
        mock.patch(
            "app.assess.data.get_bulk_accounts_dict",
            return_value=mock_bulk_accounts,
        ),
    ):
        yield


@pytest.fixture(scope="function")
def mock_get_sub_criteria(request):
    application_id = request.node.get_closest_marker("application_id").args[0]
    sub_criteria_id = request.node.get_closest_marker("sub_criteria_id").args[
        0
    ]
    from app.assess.models.sub_criteria import SubCriteria

    mock_sub_crit = SubCriteria.from_filtered_dict(
        mock_api_results[
            "assessment_store/sub_criteria_overview/"
            f"{application_id}/{sub_criteria_id}"
        ]
    )
    with mock.patch(
        "app.assess.routes.get_sub_criteria", return_value=mock_sub_crit
    ) as mocked_sub_crit_func:
        yield mocked_sub_crit_func

    mocked_sub_crit_func.assert_called_once_with(
        application_id, sub_criteria_id
    )


@pytest.fixture(scope="function")
def mock_get_sub_criteria_theme(request):
    application_id = request.node.get_closest_marker("application_id").args[0]
    mock_theme = mock_api_results[
        f"assessment_store/sub_criteria_themes/{application_id}/test_theme_id"
    ]
    with mock.patch(
        "app.assess.routes.get_sub_criteria_theme_answers",
        return_value=mock_theme,
    ) as mocked_theme_func:
        yield mocked_theme_func

    mocked_theme_func.assert_called_once()


@pytest.fixture(scope="function")
def mock_get_comments(request):
    mock_bulk_accounts = mock_api_results["account_store/bulk-accounts"]
    mock_comments = mock_api_results["assessment_store/comment?"]
    with (
        mock.patch(
            "app.assess.routes.get_comments", return_value=mock_comments
        ),
        mock.patch(
            "app.assess.data.get_bulk_accounts_dict",
            return_value=mock_bulk_accounts,
        ),
    ):
        yield


@pytest.fixture(scope="function")
def mock_get_scores(request):
    mock_scores = mock_api_results["assessment_store/score?"]
    with (
        mock.patch(
            "app.assess.routes.get_score_and_justification",
            return_value=mock_scores,
        )
    ):
        yield
