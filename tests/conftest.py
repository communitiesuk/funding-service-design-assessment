import multiprocessing
import platform
from pathlib import Path

import jwt as jwt
import pytest
from app.create_app import create_app
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
def flask_test_client(user_token=None):
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """
    with create_app().app_context() as app_context:
        with app_context.app.test_client() as test_client:
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
def mock_get_banner_state(mocker, scope="function"):
    from app.assess.models.banner import Banner

    mock_banner_info = Banner.from_filtered_dict(
        {
            "short_id": "short",
            "project_name": "name",
            "funding_amount_requested": 10,
            "workflow_status": "IN_PROGRESS",
            "fund_id": "funding-service-design",
        }
    )

    mocker.patch(
        "app.assess.helpers.get_banner_state",
        return_value=mock_banner_info,
    )

    mocker.patch(
        "app.assess.routes.get_banner_state",
        return_value=mock_banner_info,
    )
