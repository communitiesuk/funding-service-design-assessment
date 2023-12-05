import multiprocessing
import platform
from collections import OrderedDict
from pathlib import Path
from unittest import mock

import jwt as jwt
import pytest
from app.blueprints.services.models.assessor_task_list import AssessorTaskList
from app.blueprints.shared.helpers import get_ttl_hash
from app.blueprints.tagging.models.tag import AssociatedTag
from app.blueprints.tagging.models.tag import Tag
from app.blueprints.tagging.models.tag import TagType
from config import Config
from create_app import create_app
from distutils.util import strtobool
from flask import template_rendered
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from tests.api_data.example_get_full_application import (
    mock_full_application_json,
)
from tests.api_data.test_data import mock_api_results
from tests.test_tags import associated_tag
from tests.test_tags import test_get_tag
from tests.test_tags import test_tags_active
from tests.test_tags import test_tags_inactive
from webdriver_manager.chrome import ChromeDriverManager

if platform.system() == "Darwin":
    multiprocessing.set_start_method("fork")  # Required on macOSX

test_lead_assessor_claims = {
    "accountId": "lead",
    "email": "lead@test.com",
    "fullName": "Test User",
    "roles": ["TF_LEAD_ASSESSOR", "TF_ASSESSOR", "TF_COMMENTER"],
}

test_assessor_claims = {
    "accountId": "assessor",
    "email": "assessor@test.com",
    "fullName": "Test User",
    "roles": ["TF_ASSESSOR", "TF_COMMENTER"],
}

test_commenter_claims = {
    "accountId": "commenter",
    "email": "commenter@test.com",
    "fullName": "Test User",
    "roles": ["TF_COMMENTER"],
}

fund_specific_claim_map = {
    "CYP": {
        "LEAD_ASSESSOR": {
            "accountId": "cyp-lead-assessor",
            "email": "cyp-lead-assessor@test.com",
            "fullName": "Test User",
            "roles": ["CYP_LEAD_ASSESSOR", "CYP_ASSESSOR", "CYP_COMMENTER"],
        },
        "ASSESSOR": {
            "accountId": "cyp-assessor",
            "email": "cyp-assessor@test.com",
            "fullName": "Test User",
            "roles": ["CYP_ASSESSOR", "CYP_COMMENTER"],
        },
        "COMMENTER": {
            "accountId": "cyp-commenter",
            "email": "cyp-commenter@test.com",
            "fullName": "Test User",
            "roles": ["CYP_COMMENTER"],
        },
    },
    "NSTF": {
        "LEAD_ASSESSOR": {
            "accountId": "nstf-lead-assessor",
            "email": "nstf-lead-assessor@test.com",
            "fullName": "Test User",
            "roles": ["NSTF_LEAD_ASSESSOR", "NSTF_ASSESSOR", "NSTF_COMMENTER"],
        },
        "ASSESSOR": {
            "accountId": "nstf-assessor",
            "email": "nstf-assessor@test.com",
            "fullName": "Test User",
            "roles": ["NSTF_ASSESSOR", "NSTF_COMMENTER"],
        },
        "COMMENTER": {
            "accountId": "nstf-commenter",
            "email": "nstf-commenter@test.com",
            "fullName": "Test User",
            "roles": ["NSTF_COMMENTER"],
        },
    },
    "COF": {
        "LEAD_ASSESSOR": {
            "accountId": "cof-lead-assessor",
            "email": "cof-lead-assessor@test.com",
            "fullName": "Test User",
            "roles": ["COF_LEAD_ASSESSOR", "COF_ASSESSOR", "COF_COMMENTER"],
        },
        "ASSESSOR": {
            "accountId": "cof-assessor",
            "email": "cof-assessor@test.com",
            "fullName": "Test User",
            "roles": ["COF_ASSESSOR", "COF_COMMENTER"],
        },
        "COMMENTER": {
            "accountId": "cof-commenter",
            "email": "cof-commenter@test.com",
            "fullName": "Test User",
            "roles": ["COF_COMMENTER"],
        },
    },
    "DPIF": {
        "LEAD_ASSESSOR": {
            "accountId": "dpif-lead-assessor",
            "email": "dpif-lead-assessor@test.com",
            "fullName": "Test User",
            "roles": ["DPIF_LEAD_ASSESSOR", "DPIF_ASSESSOR", "DPIF_COMMENTER"],
        },
        "ASSESSOR": {
            "accountId": "dpif-assessor",
            "email": "dpif-assessor@test.com",
            "fullName": "Test User",
            "roles": ["DPIF_ASSESSOR", "DPIF_COMMENTER"],
        },
        "COMMENTER": {
            "accountId": "dpif-commenter",
            "email": "dpif-commenter@test.com",
            "fullName": "Test User",
            "roles": ["DPIF_COMMENTER"],
        },
    },
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


@pytest.fixture(scope="function")
def flask_test_maintenance_client(request, user_token=None):
    """
    Creates the test maintenance client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """
    marker = request.node.get_closest_marker("maintenance_mode")
    maintenance_mode = marker.args[0]
    app = create_app()
    app.config.update({"MAINTENANCE_MODE": strtobool(maintenance_mode)})
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
def mock_get_sub_criteria_banner_state(request):
    from app.blueprints.services.models.banner import Banner

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
            "app.blueprints.flagging.helpers.get_sub_criteria_banner_state",
            return_value=mock_banner_info,
        ),
        mock.patch(
            "app.blueprints.flagging.routes.get_sub_criteria_banner_state",
            return_value=mock_banner_info,
        ),
    ):
        yield


@pytest.fixture(scope="function")
def mock_get_fund(mocker):
    from app.blueprints.services.models.fund import Fund

    mock_fund_info = Fund.from_json(
        mock_api_results["fund_store/funds/{fund_id}"]
    )

    mock_funcs = [
        "app.blueprints.assessments.routes.get_fund",
        "app.blueprints.authentication.validation.get_fund",
        "app.blueprints.flagging.helpers.get_fund",
        "app.blueprints.tagging.routes.get_fund",
        "app.blueprints.services.shared_data_helpers.get_fund",
    ]

    for mock_func in mock_funcs:
        mocker.patch(mock_func, return_value=mock_fund_info),

    yield


@pytest.fixture(scope="function")
def mock_get_funds():
    from app.blueprints.services.models.fund import Fund

    mock_fund_info = [
        Fund.from_json(mock_api_results["fund_store/funds/{fund_id}"]),
        Fund.from_json(mock_api_results["fund_store/funds/NSTF"]),
        Fund.from_json(mock_api_results["fund_store/funds/CYP"]),
        Fund.from_json(mock_api_results["fund_store/funds/COF"]),
        Fund.from_json(mock_api_results["fund_store/funds/DPIF"]),
    ]

    with (
        mock.patch(
            "app.blueprints.assessments.routes.get_funds",
            return_value=mock_fund_info,
        ),
        mock.patch(
            "app.blueprints.authentication.auth.get_funds",
            return_value=mock_fund_info,
        ),
    ):
        yield


@pytest.fixture(scope="function")
def mock_get_application_metadata(mocker):
    mocker.patch(
        "app.blueprints.authentication.validation.get_application_metadata",
        return_value=mock_api_results[
            "assessment_store/applications/{application_id}"
        ],
    )
    yield


@pytest.fixture
def mocks_for_file_export_download(mocker):
    mocker.patch(
        "app.blueprints.assessments.routes.get_application_sections_display_config",
        return_value=[],
    )

    mocker.patch(
        "app.blueprints.assessments.routes.generate_maps_from_form_names",
        return_value=COF_R2_W2_GENERATE_MAPS_FROM_FORM_NAMES,
    )

    mocker.patch(
        "app.blueprints.assessments.helpers.generate_maps_from_form_names",
        return_value=COF_R2_W2_GENERATE_MAPS_FROM_FORM_NAMES,
    )
    yield


@pytest.fixture(scope="function")
def mock_get_round(mocker):
    from app.blueprints.services.models.round import Round

    mock_funcs = [
        "app.blueprints.assessments.routes.get_round",
        "app.blueprints.tagging.routes.get_round",
        "app.blueprints.services.shared_data_helpers.get_round",
        "app.blueprints.authentication.validation.get_round",
    ]

    mock_round_info = Round.from_dict(
        mock_api_results["fund_store/funds/{fund_id}/rounds/{round_id}"]
    )

    mocked_rounds = []
    for mock_func in mock_funcs:
        mocked_round = mocker.patch(mock_func, return_value=mock_round_info)
        mocked_rounds.append(mocked_round)

    yield mocked_rounds


@pytest.fixture(scope="function")
def mock_get_rounds(request, mocker):
    from app.blueprints.services.models.round import Round

    marker = request.node.get_closest_marker("mock_parameters")
    func_calls = [
        "app.blueprints.assessments.models.fund_summary.get_rounds",
    ]
    if marker:
        params = marker.args[0]
        mock_funcs = params.get("get_rounds_path", func_calls)
        fund_id = params.get("fund_id", "test-fund")
    else:
        mock_funcs = func_calls
        fund_id = "test-fund"

    mock_round_info = [
        Round.from_dict(
            mock_api_results["fund_store/funds/{fund_id}/rounds/{round_id}"]
        )
    ]
    mocked_get_rounds = []
    for mock_func in mock_funcs:
        mocked_round = mocker.patch(mock_func, return_value=mock_round_info)
        mocked_get_rounds.append(mocked_round)

    yield mocked_get_rounds

    for mocked_round in mocked_get_rounds:
        mocked_round.assert_called_with(
            fund_id, ttl_hash=get_ttl_hash(Config.LRU_CACHE_TIME)
        )


@pytest.fixture(scope="function")
def mock_get_application_overviews(request, mocker):
    marker = request.node.get_closest_marker("mock_parameters")
    func_path = "app.blueprints.assessments.routes.get_application_overviews"
    if marker:
        params = marker.args[0]
        search_params = params.get("expected_search_params")
        fund_id = params.get("fund_id", "test-fund")
        round_id = params.get("round_id", "test-round")
        path = params.get(
            "application_overviews_path",
            func_path,
        )
    else:
        search_params = {
            "search_term": "",
            "search_in": "project_name,short_id",
            "asset_type": "ALL",
            "status": "ALL",
            "filter_by_tag": "ALL",
            "country": "ALL",
            "region": "ALL",
            "local_authority": "ALL",
        }
        path = func_path
        fund_id = "test-fund"
        round_id = "test-round"

    mocked_apps_overview = mocker.patch(
        path,
        return_value=mock_api_results[
            "assessment_store/application_overviews/{fund_id}/{round_id}?"
        ],
    )

    yield mocked_apps_overview

    mocked_apps_overview.assert_called_with(fund_id, round_id, search_params)


@pytest.fixture(scope="function")
def mock_get_assessor_tasklist_state(request, mocker):
    marker = request.node.get_closest_marker("application_id")
    if "expect_flagging" in request.fixturenames:
        expect_flagging = request.getfixturevalue("expect_flagging")
    else:
        expect_flagging = True

    application_id = marker.args[0]
    mock_tasklist_state = mock_api_results[
        f"assessment_store/application_overviews/{application_id}"
    ]
    mocked_tasklist_state = mocker.patch(
        "app.blueprints.services.shared_data_helpers.get_assessor_task_list_state",
        return_value=mock_tasklist_state,
    )
    yield mocked_tasklist_state

    if expect_flagging:
        mocked_tasklist_state.assert_called_with(application_id)


@pytest.fixture(scope="function")
def mock_get_assessment_stats(request, mocker):
    marker = request.node.get_closest_marker("mock_parameters")
    params = marker.args[0]
    mock_funcs = params.get(
        "get_assessment_stats_path",
        [
            "app.blueprints.assessments.models.fund_summary.get_assessments_stats",
        ],
    )
    # fund_id = params.get("fund_id", "test-fund")
    # round_id = params.get("round_id", "test-round")

    mock_stats = mock_api_results[
        "assessment_store/assessments/get-stats/{fund_id}/{round_id}"
    ]

    mocked_get_stats = []
    for mock_func in mock_funcs:
        mocked_stat = mocker.patch(mock_func, return_value=mock_stats)
        mocked_get_stats.append(mocked_stat)

    yield mocked_get_stats

    # if params.get("get_assessment_stats_path"):
    #     for mocked_stat in mocked_get_stats:
    #         mocked_stat.assert_called_with(fund_id, round_id)


@pytest.fixture(scope="function")
def mock_get_assessment_progress(mocker):
    mocked_progress_func = mocker.patch(
        "app.blueprints.assessments.routes.get_assessment_progress",
        return_value=mock_api_results[
            "assessment_store/application_overviews/{fund_id}/{round_id}?"
        ],
    )
    yield mocked_progress_func

    mocked_progress_func.assert_called_once()


@pytest.fixture(scope="function")
def mock_get_teams_flag_stats(mocker):
    mocked_progress_func = mocker.patch(
        "app.blueprints.assessments.routes.get_team_flag_stats",
        return_value=mock_api_results[
            "assessment_store/assessments/get-team-flag-stats/{fund_id}/{round_id}"
        ],
    )
    yield mocked_progress_func

    mocked_progress_func.assert_called_once()


@pytest.fixture(scope="function")
def mock_get_flags(request, mocker):
    from app.blueprints.services.models.flag import Flag

    marker = request.node.get_closest_marker("application_id")
    application_id = marker.args[0]

    mock_flag_info = Flag.from_list(
        mock_api_results[
            f"assessment_store/flags?application_id={application_id}"
        ]
    )

    mock_funcs = [
        "app.blueprints.assessments.routes.get_flags",
        "app.blueprints.flagging.helpers.get_flags",
        "app.blueprints.flagging.routes.get_flags",
        "app.blueprints.scoring.routes.get_flags",
    ]

    mocked_flags = []
    for mock_func in mock_funcs:
        mocked_flags.append(
            mocker.patch(mock_func, return_value=mock_flag_info)
        )
    yield mocked_flags


@pytest.fixture(scope="function")
def mock_submit_flag(request, mocker):
    all_submit_flag_funcs = [
        "app.blueprints.flagging.helpers.submit_flag"
        "app.blueprints.flagging.routes.submit_flag"
    ]
    marker_submit_flag_paths = request.node.get_closest_marker(
        "submit_flag_paths"
    )
    submit_flag_paths = (
        marker_submit_flag_paths.args[0]
        if marker_submit_flag_paths
        else all_submit_flag_funcs
    )

    marker_flag = request.node.get_closest_marker("flag")
    flag = marker_flag.args[0] if marker_flag else None

    mock_funcs = (
        submit_flag_paths
        if marker_submit_flag_paths
        else [
            "app.blueprints.flagging.helpers.submit_flag",
            "app.blueprints.flagging.routes.submit_flag",
        ]
    )

    mocked_submit_flags = []
    for mock_func in mock_funcs:
        mocked_flag = mocker.patch(mock_func, return_value=flag)
        mocked_submit_flags.append(mocked_flag)

    yield mocked_submit_flags
    if marker_submit_flag_paths:
        for mocked_flag in mocked_submit_flags:
            mocked_flag.assert_called_once()


@pytest.fixture(scope="function")
def mock_get_qa_complete(request, mocker):
    marker = request.node.get_closest_marker("application_id")
    application_id = marker.args[0]

    mock_qa_info = mock_api_results[
        f"assessment_store/qa_complete/{application_id}"
    ]
    mocker.patch(
        "app.blueprints.assessments.routes.get_qa_complete",
        return_value=mock_qa_info,
    )
    yield


@pytest.fixture(scope="function")
def mock_get_flag(request, mocker):
    from app.blueprints.services.models.flag import Flag

    marker = request.node.get_closest_marker("flag_id")
    flag_id = marker.args[0]

    mock_flag_info = Flag.from_dict(
        mock_api_results[f"assessment_store/flag_data?flag_id={flag_id}"]
    )

    mock_funcs = ["app.blueprints.flagging.routes.get_flag"]

    get_flag_mocks = []
    for mock_func in mock_funcs:
        get_flag_mocks.append(
            mocker.patch(mock_func, return_value=mock_flag_info)
        )

    yield get_flag_mocks


@pytest.fixture(scope="function")
def mock_get_available_teams(request, mocker):
    mocker.patch(
        "app.blueprints.flagging.routes.get_available_teams",
        return_value=[{"key": "TEAM_A", "value": "Team A"}],
    )

    yield


@pytest.fixture(scope="function")
def mock_get_bulk_accounts(request, mocker):
    mock_bulk_accounts = mock_api_results["account_store/bulk-accounts"]
    mocker.patch(
        "app.blueprints.assessments.routes.get_bulk_accounts_dict",
        return_value=mock_bulk_accounts,
    )
    mocker.patch(
        "app.blueprints.services.data_services.get_bulk_accounts_dict",
        return_value=mock_bulk_accounts,
    )
    yield


@pytest.fixture(scope="function")
def mock_get_sub_criteria(request, mocker):
    application_id = request.node.get_closest_marker("application_id").args[0]
    sub_criteria_id = request.node.get_closest_marker("sub_criteria_id").args[
        0
    ]
    from app.blueprints.services.models.sub_criteria import SubCriteria

    mock_funcs = [
        "app.blueprints.assessments.routes.get_sub_criteria",
        "app.blueprints.scoring.routes.get_sub_criteria",
    ]
    mock_sub_crit = SubCriteria.from_filtered_dict(
        mock_api_results[
            "assessment_store/sub_criteria_overview/"
            f"{application_id}/{sub_criteria_id}"
        ]
    )
    mocked_sub_crits = []
    for mock_func in mock_funcs:
        mocked_sub_crits.append(
            mocker.patch(mock_func, return_value=mock_sub_crit)
        )

    yield mocked_sub_crits


@pytest.fixture(scope="function")
def mock_get_sub_criteria_theme(request, mocker):
    application_id = request.node.get_closest_marker("application_id").args[0]
    mock_theme = mock_api_results[
        f"assessment_store/sub_criteria_themes/{application_id}/test_theme_id"
    ]
    mocker.patch(
        "app.blueprints.assessments.routes.get_sub_criteria_theme_answers",
        return_value=mock_theme,
    )
    yield


@pytest.fixture(scope="function")
def mock_get_comments(mocker):
    mock_comments = mock_api_results["assessment_store/comment?"]
    mocker.patch(
        "app.blueprints.assessments.routes.get_comments",
        return_value=mock_comments,
    ),
    mocker.patch(
        "app.blueprints.scoring.routes.get_comments",
        return_value=mock_comments,
    ),
    yield


@pytest.fixture(scope="function")
def mock_get_scores(mocker):
    mock_scores = mock_api_results["assessment_store/score?"]
    mocker.patch(
        "app.blueprints.scoring.routes.get_score_and_justification",
        return_value=mock_scores,
    )
    yield


@pytest.fixture(scope="function")
def mock_get_application_json(mocker):
    full_application = mock_full_application_json
    mocker.patch(
        "app.blueprints.assessments.routes.get_application_json",
        return_value=mock_full_application_json,
    )
    yield full_application


@pytest.fixture(scope="function")
def mock_get_tasklist_state_for_banner(mocker):
    mock_task_list = AssessorTaskList(
        is_qa_complete="",
        fund_guidance_url="",
        fund_name="",
        fund_short_name="",
        fund_id="",
        round_id="",
        round_short_name="",
        project_name="",
        short_id="",
        workflow_status="IN_PROGRESS",
        date_submitted="2023-01-01 12:00:00",
        funding_amount_requested="123",
        project_reference="ABGCDF",
        sections=[],
        criterias=[],
    )
    mocker.patch(
        "app.blueprints.assessments.routes.get_state_for_tasklist_banner",
        return_value=mock_task_list,
    )
    mocker.patch(
        "app.blueprints.flagging.routes.get_state_for_tasklist_banner",
        return_value=mock_task_list,
    )
    mocker.patch(
        "app.blueprints.scoring.routes.get_state_for_tasklist_banner",
        return_value=mock_task_list,
    )
    mocker.patch(
        "app.blueprints.tagging.routes.get_state_for_tasklist_banner",
        return_value=mock_task_list,
    )
    mocker.patch(
        "app.blueprints.services.shared_data_helpers.get_state_for_tasklist_banner",
        return_value=mock_task_list,
    )
    yield


@pytest.fixture(scope="function")
def client_with_valid_session(flask_test_client):
    token = create_valid_token(test_lead_assessor_claims)
    flask_test_client.set_cookie("localhost", "fsd_user_token", token)
    yield flask_test_client


@pytest.fixture(scope="function")
def mock_get_associated_tags_for_application(mocker):
    for function_module_path in [
        "app.blueprints.assessments.routes.get_associated_tags_for_application",
        "app.blueprints.tagging.routes.get_associated_tags_for_application",
    ]:
        mocker.patch(
            function_module_path,
            return_value=[AssociatedTag.from_dict(associated_tag)],
        )
    yield


@pytest.fixture(scope="function")
def mock_get_inactive_tags_for_fund_round(mocker):
    mocker.patch(
        "app.blueprints.assessments.routes.get_tags_for_fund_round",
        return_value=[Tag.from_dict(t) for t in test_tags_inactive],
    )
    mocker.patch(
        "app.blueprints.tagging.routes.get_tags_for_fund_round",
        return_value=[Tag.from_dict(t) for t in test_tags_inactive],
    )
    yield


@pytest.fixture(scope="function")
def mock_get_active_tags_for_fund_round(mocker):
    mocker.patch(
        "app.blueprints.assessments.routes.get_tags_for_fund_round",
        return_value=[Tag.from_dict(t) for t in test_tags_active],
    )
    mocker.patch(
        "app.blueprints.tagging.routes.get_tags_for_fund_round",
        return_value=[Tag.from_dict(t) for t in test_tags_active],
    )
    yield


@pytest.fixture(scope="function")
def mock_get_tag_for_fund_round(mocker):
    tag = Tag.from_dict(test_get_tag)
    mocker.patch(
        "app.blueprints.tagging.routes.get_tag_for_fund_round",
        return_value=tag,
    )
    yield tag


@pytest.fixture(scope="function")
def mock_get_tag_types(mocker):
    for function_module_path in [
        "app.blueprints.tagging.routes.get_tag_types",
        "app.blueprints.assessments.helpers.get_tag_types",
    ]:
        mocker.patch(
            function_module_path,
            return_value=[
                TagType(
                    id="type_1",
                    purpose="POSITIVE",
                    description="Tag type 1 description",
                )
            ],
        )
    yield


@pytest.fixture(scope="function")
def mock_update_tags(mocker, request):
    tag_updated_bool = request.node.get_closest_marker(
        "tag_updated_bool"
    ).args[0]
    mocker.patch(
        "app.blueprints.tagging.routes.update_tags",
        return_value=tag_updated_bool,
    )
    yield


@pytest.fixture(scope="function")
def mock_get_tag_map_and_tag_options(mocker):
    for function_module_path in [
        "app.blueprints.assessments.routes.get_tag_map_and_tag_options",
        "app.blueprints.assessments.helpers.get_tag_map_and_tag_options",
    ]:
        mocker.patch(
            function_module_path,
            return_value=(
                [
                    AssociatedTag(
                        application_id="75dabe60-ae89-4a47-9263-d35e010b6c66",
                        associated=True,
                        purpose="NEGATIVE",
                        tag_id="75f4296f-502b-4293-82a8-b828e678dd9e",
                        user_id="65f4296f-502b-4293-82a8-b828e678dd9e",
                        value="Tag one red",
                    )
                ],
                [
                    TagType(
                        id="tag_type_1",
                        purpose="POSITIVE",
                        description="Tag type 1 description",
                    )
                ],
            ),
        )
    yield


@pytest.fixture(scope="function")
def mock_get_scoring_system(request, mocker):
    mocker.patch(
        "app.blueprints.scoring.helpers.get_scoring_system",
        return_value="OneToFive",
    )

    yield


COF_R2_W2_FORM_NAME_TO_TITLE_MAP = OrderedDict(
    [
        ("organisation-information", "Organisation Information"),
        ("applicant-information", "Applicant Information"),
        ("project-information", "Project Information"),
        ("asset-information", "Asset Information"),
        ("community-use", "Community Use"),
        ("community-engagement", "Community Engagement"),
        ("local-support", "Local Support"),
        ("environmental-sustainability", "Environmental Sustainability"),
        ("funding-required", "Funding Required"),
        ("feasibility", "Feasibility"),
        ("risk", "Risk"),
        ("project-costs", "Project Costs"),
        ("skills-and-resources", "Skills And Resources"),
        ("community-representation", "Community Representation"),
        ("inclusiveness-and-integration", "Inclusiveness And Integration"),
        ("upload-business-plan", "Upload Business Plan"),
        ("community-benefits", "Community Benefits"),
        ("value-to-the-community", "Value To The Community"),
        ("project-qualification", "Project Qualification"),
        ("declarations", "Declarations"),
    ]
)
COF_R2_W2_FORM_NAME_TO_PATH_MAP = OrderedDict(
    [
        ("organisation-information", "1.1.1.1"),
        ("applicant-information", "1.1.1.2"),
        ("project-information", "1.1.2.1"),
        ("asset-information", "1.1.2.2"),
        ("community-use", "1.1.3.1"),
        ("community-engagement", "1.1.3.2"),
        ("local-support", "1.1.3.3"),
        ("environmental-sustainability", "1.1.3.4"),
        ("funding-required", "1.1.4.1"),
        ("feasibility", "1.1.4.2"),
        ("risk", "1.1.4.3"),
        ("project-costs", "1.1.4.4"),
        ("skills-and-resources", "1.1.4.5"),
        ("community-representation", "1.1.4.6"),
        ("inclusiveness-and-integration", "1.1.4.7"),
        ("upload-business-plan", "1.1.4.8"),
        ("community-benefits", "1.1.5.1"),
        ("value-to-the-community", "1.1.6.1"),
        ("project-qualification", "1.1.7.1"),
        ("declarations", "1.1.8.1"),
    ]
)
COF_R2_W2_GENERATE_MAPS_FROM_FORM_NAMES = (
    COF_R2_W2_FORM_NAME_TO_TITLE_MAP,
    COF_R2_W2_FORM_NAME_TO_PATH_MAP,
)
