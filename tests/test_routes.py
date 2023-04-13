from unittest import mock

import app
import pytest
from app.assess.models.flag import Flag
from app.assess.models.score import Score
from bs4 import BeautifulSoup
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

            soup = BeautifulSoup(response.data, "html.parser")
            assert soup.title.string == "Team dashboard - Assessment Hub"

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
                "/assess/assessor_dashboard/"
                f"{Config.COF_FUND_ID}/{Config.COF_ROUND2_ID}",
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
        [b"Current score: 5", b"Rescore", b"Current score:"],
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
                "/assess/application_id/app_123/sub_criteria_id/1a2b3c4d/score"  # noqa
            )

            # Assert that the response has the expected status code
            assert 200 == response.status_code, "Wrong status code on response"
            soup = BeautifulSoup(response.data, "html.parser")
            assert (
                soup.title.string
                == "Score - Engagement - Community Gym - Assessment Hub"
            )
            assert b"This is a comment" in response.data

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
        self, flask_test_client, monkeypatch, expected_ids, expected_names
    ):

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
            "/assess/application_id/app_123/sub_criteria_id/1a2b3c4d/score"  # noqa
        )

        # Assert that the response has the expected status code
        assert 302 == response.status_code, (
            "Commenter should receive a 302 to authenticator when trying to"
            " access the sub criteria scoring page"
        )
        assert (
            response.location
            == "https://authenticator/service/user?roles_required=LEAD_ASSESSOR|ASSESSOR"  # noqa
        )

    def test_homepage_route_accessible(self, flask_test_client):

        # Remove fsd-user-token cookie
        flask_test_client.set_cookie("localhost", "fsd_user_token", "")

        # Send a request to the homepage "/" route
        response = flask_test_client.get("/")

        # Assert that the response has the expected status code
        assert (
            200 == response.status_code
        ), "Homepage route should be accessible"

        # Send a request to the root route
        response = flask_test_client.get("", follow_redirects=True)

        # Assert that the response has the expected status code
        assert (
            200 == response.status_code
        ), "Homepage route should be accessible"

    def test_healthcheck_route_accessible(self, flask_test_client):

        # Remove fsd-user-token cookie
        flask_test_client.set_cookie("localhost", "fsd_user_token", "")

        # Send a request to the /healthcheck route
        response = flask_test_client.get("/healthcheck")  # noqa

        # Assert that the response has the expected status code
        assert (
            200 == response.status_code
        ), "Healthcheck route should be accessible"

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
    ):
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

    def test_flag_route_already_flagged(self, flask_test_client):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        response = flask_test_client.get("assess/flag/app_123")

        assert response.status_code == 400

    def test_flag_route_works_for_applciation_with_latest_resolved_flag(
        self, flask_test_client
    ):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        response = flask_test_client.get("assess/flag/resolved_app")

        assert response.status_code == 200

    def test_application_route_should_show_stopped_flag(
        self, flask_test_client
    ):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        response = flask_test_client.get("assess/application/stopped_app")

        assert response.status_code == 200
        assert b"21/01/2023" in response.data
        assert b"Stopped" in response.data

    def test_application_route_should_not_show_resolved_flag(
        self, flask_test_client
    ):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        response = flask_test_client.get("assess/application/resolved_app")

        assert response.status_code == 200
        assert b"01/01/2023" not in response.data
        assert b"Reason" not in response.data
        assert b"Section flagged" not in response.data

    def test_flag_route_submit_flag(
        self, flask_test_client, mocker, request_ctx
    ):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        session["csrf_token"] = "test"

        mocker.patch("app.assess.routes.submit_flag", return_value=None)

        response = flask_test_client.post(
            "assess/flag/1",
            data={
                "justification": "Test justification",
                "section": "Test section",
            },
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/assess/application/1"

    def test_flag_route_get_resolve_flag(
        self,
        flask_test_client,
    ):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        response = flask_test_client.get(
            "assess/resolve_flag/app_123?section=org_info",
        )

        assert response.status_code == 200
        assert b"Resolve flag" in response.data
        assert b"Query resolved" in response.data
        assert b"Stop assessment" in response.data
        assert b"Reason" in response.data
        soup = BeautifulSoup(response.data, "html.parser")
        assert soup.title.string == "Resolve flag - Assessment Hub"

    def test_post_resolved_flag(self, flask_test_client, mocker):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        mocker.patch(
            "app.assess.helpers.submit_flag",
            return_value=Flag.from_dict(
                {
                    "application_id": "app_123",
                    "date_created": "2023-01-01T00:00:00",
                    "flag_type": "RESOLVED",
                    "id": "flagid",
                    "justification": "string",
                    "section_to_flag": "community",
                    "user_id": "test@example.com",
                }
            ),
        )

        response = flask_test_client.post(
            "assess/resolve_flag/app_123?section=org_info",
            data={
                "resolution_flag": "RESOLVED",
                "justification": "Checked with so and so.",
            },
        )
        app.assess.helpers.submit_flag.assert_called_once()
        app.assess.helpers.submit_flag.assert_called_once_with(
            "app_123",
            "RESOLVED",
            "lead",
            "Checked with so and so.",
            "section not specified",
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/assess/application/app_123"

    def test_flag_route_get_continue_application(
        self,
        flask_test_client,
    ):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        response = flask_test_client.get(
            "/assess/continue_assessment/stopped_app",
        )

        assert response.status_code == 200
        assert b"short" in response.data
        assert b"Reason for continuing assessment" in response.data
        assert b"10.00" in response.data
        assert b"Stopped" in response.data

    def test_post_continue_application(self, flask_test_client, mocker):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        mocker.patch(
            "app.assess.helpers.submit_flag",
            return_value=Flag.from_dict(
                {
                    "application_id": "app_123",
                    "date_created": "2023-01-01T00:00:00",
                    "flag_type": "RESOLVED",
                    "id": "flagid",
                    "justification": "string",
                    "section_to_flag": "community",
                    "user_id": "test@example.com",
                }
            ),
        )

        response = flask_test_client.post(
            "assess/resolve_flag/app_123?section=org_info",
            data={
                "resolution_flag": "RESOLVED",
                "justification": "We should continue the application.",
            },
        )
        app.assess.helpers.submit_flag.assert_called_once()
        app.assess.helpers.submit_flag.assert_called_once_with(
            "app_123",
            "RESOLVED",
            "lead",
            "We should continue the application.",
            "section not specified",
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/assess/application/app_123"

    def test_qa_complete_flag_displayed(self, flask_test_client, mocker):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        mocker.patch(
            "app.assess.routes.get_assessor_task_list_state",
            return_value={
                "criterias": [],
                "date_submitted": "2022-10-27T08:32:13.383999",
                "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
                "funding_amount_requested": 4600.0,
                "project_name": "Remodel the beautiful cinema in Cardiff",
                "sections": [],
                "short_id": "COF-R2W2-VPWRNH",
                "workflow_status": "COMPLETED",
            },
        )
        mocker.patch(
            "app.assess.routes.get_latest_flag",
            return_value=Flag.from_dict(
                {
                    "application_id": "app_123",
                    "date_created": "2023-01-01T00:00:00",
                    "flag_type": "QA_COMPLETED",
                    "id": "flagid",
                    "justification": "string",
                    "section_to_flag": "community",
                    "user_id": "test@example.com",
                    "is_qa_complete": True,
                }
            ),
        )
        response = flask_test_client.get(
            "assess/application/app_123",
        )
        app.assess.routes.get_latest_flag.assert_called_once()
        app.assess.routes.get_latest_flag.assert_called_once_with("app_123")

        assert response.status_code == 200
        assert b"Marked as QA complete" in response.data
        assert b"01/01/2023 at 00:00am" in response.data
        assert b"Flagged" not in response.data

    def test_qa_completed_flagged_application(self, flask_test_client, mocker):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        mocker.patch(
            "app.assess.routes.get_assessor_task_list_state",
            return_value={
                "criterias": [],
                "date_submitted": "2022-10-27T08:32:13.383999",
                "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
                "funding_amount_requested": 4600.0,
                "project_name": "Remodel the beautiful cinema in Cardiff",
                "sections": [],
                "short_id": "COF-R2W2-VPWRNH",
                "workflow_status": "COMPLETED",
            },
        )
        mocker.patch(
            "app.assess.routes.get_latest_flag",
            return_value=Flag.from_dict(
                {
                    "application_id": "app_123",
                    "date_created": "2023-01-01T00:00:00",
                    "flag_type": "FLAGGED",
                    "id": "flagid",
                    "justification": "string",
                    "section_to_flag": "community",
                    "user_id": "test@example.com",
                    "is_qa_complete": True,
                }
            ),
        )
        response = flask_test_client.get(
            "assess/application/app_123",
        )
        app.assess.routes.get_latest_flag.assert_called_once()
        app.assess.routes.get_latest_flag.assert_called_once_with("app_123")

        assert response.status_code == 200
        assert b"Marked as QA complete" in response.data
        assert b"01/01/2023 at 00:00am" in response.data
        assert b"Flagged" in response.data
        assert b"Reason" in response.data
        assert b"Resolve flag" in response.data

    def test_route_landing_shows_flagged(self, flask_test_client):
        response = flask_test_client.get("/assess/assessor_dashboard/")

        assert 200 == response.status_code, "Wrong status code on response"

        assert (
            b"stopped-tag" in response.data
        ), "Stopped Flag is not displaying"

        assert (
            b"flagged-tag" in response.data
        ), "Flagged Flag is not displaying"

        assert (
            b"Resolved" not in response.data
        ), "Resolved Flag is displaying and should not"

    def test_page_title_subcriteria_theme_match(self, flask_test_client):
        # Mocking fsd-user-token cookie
        token = create_valid_token(test_commenter_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        # Send a request to the route you want to test
        response = flask_test_client.get(
            "/assess/application_id/app_123/sub_criteria_id/business_plan"  # noqa
        )
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.title.string
            == "Business plan - Community Gym - Assessment Hub"
        )

    def test_get_docs_for_download(
        self,
        flask_test_client,
        mock_get_banner_state,
        mock_get_fund,
        templates_rendered,
        mocker,
    ):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        mocker.patch(
            "app.assess.routes.get_application_json",
            return_value={"jsonb_blob": "mock"},
        )
        with mock.patch(
            "app.assess.routes.get_files_for_application_upload_fields",
            return_value=[
                ("sample1.doc", "mock/url/for/get/file"),
                ("sample2.doc", "mock/url/for/get/file"),
            ],
        ):
            response = flask_test_client.get(
                "/assess/application/abc123/export"
            )
            assert 200 == response.status_code
            assert 1 == len(templates_rendered)
            rendered_template = templates_rendered[0]
            assert "contract_downloads.html" == rendered_template[0].name
            assert "abc123" == rendered_template[1]["application_id"]
            assert b"sample1.doc" in response.data
            assert b"sample2.doc" in response.data

    def test_download_q_and_a(self, flask_test_client, mocker):

        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        mock_q_and_a = "Q) What is your quest?\nA) The holy grail"
        mocker.patch(
            "app.assess.routes.get_application_json",
            return_value={"jsonb_blob": "mock"},
        )
        mocker.patch(
            "app.assess.routes.extract_questions_and_answers_from_json_blob",
            return_value={"What is your quest?": "The holy grail"},
        )
        mocker.patch(
            "app.assess.routes.generate_text_of_application",
            return_value=mock_q_and_a,
        )
        with mock.patch(
            "app.assess.routes.download_file", return_value=""
        ) as mock_download_file:

            flask_test_client.get(
                "/assess/application/abc123/export/QWERTY/answers.txt"
            )
            mock_download_file.assert_called_once_with(
                mock_q_and_a, "text/plain", "QWERTY_answers.txt"
            )

    def test_get_file_with_short_id(self, flask_test_client, mocker):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        mocker.patch(
            "app.assess.routes.get_file_for_download_from_aws",
            return_value=("some file contents", "mock_mimetype"),
        )
        with mock.patch(
            "app.assess.routes.download_file", return_value=""
        ) as mock_download_file:
            flask_test_client.get(
                "/assess/application/abc123/export/business_plan.txt?short_id=QWERTY"  # noqa
            )
            mock_download_file.assert_called_once_with(
                "some file contents",
                "mock_mimetype",
                "QWERTY_business_plan.txt",
            )

    def test_get_file_without_short_id(self, flask_test_client, mocker):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        mocker.patch(
            "app.assess.routes.get_file_for_download_from_aws",
            return_value=("some file contents", "mock_mimetype"),
        )
        with mock.patch(
            "app.assess.routes.download_file", return_value=""
        ) as mock_download_file:
            flask_test_client.get(
                "/assess/application/abc123/export/business_plan.txt"
            )
            mock_download_file.assert_called_once_with(
                "some file contents", "mock_mimetype", "business_plan.txt"
            )

    def test_get_file(self, flask_test_client):
        from app.assess.routes import download_file

        response = download_file("file_data", "text/plain", "file_name.abc")
        assert "text/plain" in response.content_type
        assert "attachment;filename=file_name.abc" == response.headers.get(
            "Content-Disposition"
        )
