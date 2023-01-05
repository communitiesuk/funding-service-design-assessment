from unittest import mock

import pytest
from app.assess.models.score import Score
from config import Config
from flask import session
from tests.conftest import create_valid_token
from tests.conftest import test_commenter_claims
from tests.conftest import test_lead_assessor_claims


class TestRoutes:
    def test_route_landing(self, flask_test_client):
        with mock.patch(
            "app.assess.routes.get_application_overviews",
            return_value=[],
        ) as mock_get_application_overviews_func:
            response = flask_test_client.get("/assess/assessor_dashboard/")

            assert 200 == response.status_code, "Wrong status code on response"

            mock_get_application_overviews_func.assert_called_once_with(
                Config.COF_FUND_ID,
                Config.COF_ROUND2_ID,
                {
                    "search_term": "",
                    "search_in": "project_name,short_id",
                    "asset_type": "ALL",
                    "status": "ALL",
                },
            )

            assert (
                b"Team dashboard" in response.data
            ), "Response does not contain expected heading"

    def test_route_landing_filter_status(self, flask_test_client):
        with mock.patch(
            "app.assess.routes.get_application_overviews",
            return_value=[],
        ) as mock_get_application_overviews_func:
            response = flask_test_client.get(
                "/assess/assessor_dashboard/",
                query_string={"status": "QA_COMPLETE"},
            )

            assert 200 == response.status_code, "Wrong status code on response"

            mock_get_application_overviews_func.assert_called_once_with(
                Config.COF_FUND_ID,
                Config.COF_ROUND2_ID,
                {
                    "search_term": "",
                    "search_in": "project_name,short_id",
                    "asset_type": "ALL",
                    "status": "QA_COMPLETE",
                },
            )

            assert (
                b"Team dashboard" in response.data
            ), "Response does not contain expected heading"

    def test_route_landing_filter_asset_type(self, flask_test_client):
        with mock.patch(
            "app.assess.routes.get_application_overviews",
            return_value=[],
        ) as mock_get_application_overviews_func:
            response = flask_test_client.get(
                "/assess/assessor_dashboard/",
                query_string={"asset_type": "pub"},
            )

            assert 200 == response.status_code, "Wrong status code on response"

            mock_get_application_overviews_func.assert_called_once_with(
                Config.COF_FUND_ID,
                Config.COF_ROUND2_ID,
                {
                    "search_term": "",
                    "search_in": "project_name,short_id",
                    "asset_type": "pub",
                    "status": "ALL",
                },
            )

            assert (
                b"Team dashboard" in response.data
            ), "Response does not contain expected heading"

    def test_route_landing_search_term(self, flask_test_client):
        with mock.patch(
            "app.assess.routes.get_application_overviews",
            return_value=[],
        ) as mock_get_application_overviews_func:
            response = flask_test_client.get(
                "/assess/assessor_dashboard/",
                query_string={"search_term": "hello"},
            )

            assert 200 == response.status_code, "Wrong status code on response"

            mock_get_application_overviews_func.assert_called_once_with(
                Config.COF_FUND_ID,
                Config.COF_ROUND2_ID,
                {
                    "search_term": "hello",
                    "search_in": "project_name,short_id",
                    "asset_type": "ALL",
                    "status": "ALL",
                },
            )

            assert (
                b"Team dashboard" in response.data
            ), "Response does not contain expected heading"

    def test_route_landing_clear_filters(self, flask_test_client):
        with mock.patch(
            "app.assess.routes.get_application_overviews",
            return_value=[],
        ) as mock_get_application_overviews_func:
            response = flask_test_client.get(
                "/assess/assessor_dashboard/",
                query_string={
                    "clear_filters": "",
                    "search_term": "hello",
                    "asset_type": "cinema",
                    "status": "in-progress",
                },
            )

            assert 200 == response.status_code, "Wrong status code on response"

            mock_get_application_overviews_func.assert_called_once_with(
                Config.COF_FUND_ID,
                Config.COF_ROUND2_ID,
                {
                    "search_term": "",
                    "search_in": "project_name,short_id",
                    "asset_type": "ALL",
                    "status": "ALL",
                },
            )

            assert (
                b"Team dashboard" in response.data
            ), "Response does not contain expected heading"

    @pytest.mark.parametrize(
        "expected_names",
        [b"Current score: 5", b"Rescore", b"Add rationale for this"],
    )
    def test_route_sub_criteria_scoring(
        self, flask_test_client, expected_names
    ):
        # Define a dummy value for the return value of get_score_and_justification # noqa
        mock_scores = [
            Score(
                id="123",
                application_id="app_123",
                sub_criteria_id="1a2b3c4d",
                score="5",
                justification="test justification",
                date_created="2022-01-01T00:00:00",
                user_id="test-user",
                user_full_name="Test User",
                user_email="test@example.com",
                highest_role="LEAD_ASSESSOR",
            )
        ]

        # Use unittest.mock to create a mock object for get_scores_and_justification # noqa
        with mock.patch(
            "app.assess.routes.get_score_and_justification"
        ) as mock_get_score_and_justification:
            # Set the return value of the mock object
            mock_get_score_and_justification.return_value = mock_scores

            # Mocking fsd-user-token cookie
            test_payload = {
                "accountId": "test-user",
                "email": "test@example.com",
                "fullName": "Test User",
                "roles": ["LEAD_ASSESSOR", "ASSESSOR", "COMMENTER"],
            }
            token = create_valid_token(test_payload)
            flask_test_client.set_cookie("localhost", "fsd_user_token", token)

            # Send a request to the route you want to test
            response = flask_test_client.get(
                "/assess/application_id/app_123/sub_criteria_id/1a2b3c4d?theme_id=score"  # noqa
            )

            # Assert that the response has the expected status code
            assert 200 == response.status_code, "Wrong status code on response"

            # Assert that the response contains the expected ids
            assert (
                expected_names in response.data
            ), "Response does not contain expected names"

    @pytest.mark.parametrize(
        "expected_ids, expected_names",
        [
            (b"general-information", b"General information"),
            (b"activities", b"Activities"),
            (b"partnerships", b"Partnerships"),
            (b"score-subcriteria-link", b"Score the subcriteria"),
        ],
    )
    def test_route_sub_criteria_side_bar_lead_assessor(
        self,
        flask_test_client,
        monkeypatch,
        expected_ids,
        expected_names,
        mocker,
    ):
        mocker.patch(
            "app.assess.models.ui.applicants_response.get_file_url",
            return_value="sample1.doc",
        )
        # Mocking fsd-user-token cookie
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        # Send a request to the route you want to test
        response = flask_test_client.get(
            "/assess/application_id/app_123/sub_criteria_id/1a2b3c4d?theme_id=general-information"  # noqa
        )

        # Assert that the response has the expected status code
        assert 200 == response.status_code, "Wrong status code on response"

        # Assert that the response contains the expected ids and names
        assert (
            expected_ids in response.data
        ), "Response does not contain expected id"
        assert (
            expected_names in response.data
        ), "Response does not contain expected name"

    def test_route_sub_criteria_scoring_inaccessible_to_commenters(
        self, flask_test_client
    ):

        # Mocking fsd-user-token cookie
        token = create_valid_token(test_commenter_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        # Send a request to the route you want to test
        response = flask_test_client.get(
            "/assess/application_id/app_123/sub_criteria_id/1a2b3c4d?theme_id=score"  # noqa
        )

        # Assert that the response has the expected status code
        assert 404 == response.status_code, (
            "Commenter should receive a 404 when trying to access the sub"
            " criteria scoring page"
        )

    @pytest.mark.parametrize(
        "expected_ids, expected_names",
        [
            (b"general-information", b"General information"),
            (b"activities", b"Activities"),
            (b"partnerships", b"Partnerships"),
        ],
    )
    def test_route_sub_criteria_side_bar_commenter(
        self,
        flask_test_client,
        monkeypatch,
        expected_ids,
        expected_names,
        mocker,
    ):
        mocker.patch(
            "app.assess.models.ui.applicants_response.get_file_url",
            return_value="sample1.doc",
        )
        # Mocking fsd-user-token cookie
        token = create_valid_token(test_commenter_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        # Send a request to the route you want to test
        response = flask_test_client.get(
            "/assess/application_id/app_123/sub_criteria_id/1a2b3c4d?theme_id=general-information"  # noqa
        )

        # Assert that the response has the expected status code
        assert 200 == response.status_code, "Wrong status code on response"

        # Assert that the response contains the expected ids and names
        assert (
            expected_ids in response.data
        ), "Response does not contain expected id"
        assert (
            expected_names in response.data
        ), "Response does not contain expected name"
        assert (
            b"score-subcriteria-link" not in response.data
        ), "Sidebar should not contain score subcriteria link"
        assert (
            b"Score the subcriteria" not in response.data
        ), "Sidebar should not contain the link to score subcriteria"

    def test_flag_route_already_flagged(self, flask_test_client, mocker):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        mock_get_flags = mocker.patch("app.assess.routes.get_flags")
        mock_get_flags.return_value = [
            {"reason": "Test reason", "section": "Test section"}
        ]

        response = flask_test_client.get("assess/flag/1")

        assert response.status_code == 400

    def test_flag_route_submit_flag(
        self, flask_test_client, mocker, request_ctx
    ):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        session["csrf_token"] = "test"

        mocker.patch("app.assess.routes.submit_flag", return_value=None)
        mock_get_flags = mocker.patch("app.assess.routes.get_flags")
        mock_get_banner_state = mocker.patch(
            "app.assess.routes.get_banner_state"
        )
        mock_get_fund = mocker.patch("app.assess.routes.get_fund")
        mock_get_flags.return_value = []
        mock_get_banner_state.return_value = {"fund_id": 1}
        mock_get_fund.return_value = mock.Mock(name="Test Fund")

        response = flask_test_client.post(
            "assess/flag/1",
            data={"reason": "Test reason", "section": "Test section"},
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/assess/application/1"
