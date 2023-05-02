from unittest import mock

import app
import pytest
from app.assess.models.flag import Flag
from bs4 import BeautifulSoup
from flask import session
from tests.conftest import create_valid_token
from tests.conftest import test_commenter_claims
from tests.conftest import test_lead_assessor_claims


class TestRoutes:
    @pytest.mark.mock_parameters(
        {
            "get_assessment_stats_path": (
                "app.assess.models.fund_summary.get_assessments_stats"
            ),
            "get_rounds_path": "app.assess.models.fund_summary.get_rounds",
            "fund_id": "test-fund",
            "round_id": "test-round",
            "expected_search_params": {
                "search_term": "",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "ALL",
            },
        }
    )
    def test_route_landing(
        self,
        flask_test_client,
        mock_get_funds,
        mock_get_rounds,
        mock_get_assessment_stats,
    ):

        response = flask_test_client.get("/assess/assessor_tool_dashboard/")
        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.title.string == "Assessment tool dashboard - Assessment Hub"
        ), "Response does not contain expected heading"
        all_table_data_elements = str(
            soup.find_all("td", class_="govuk-table__cell")
        )
        project_titles = [
            "Assessment closing date",
            "Applications received",
            "Assessments completed",
            "QA Complete",
        ]
        assert all(
            title in all_table_data_elements for title in project_titles
        )

    @pytest.mark.mock_parameters(
        {
            "fund_short_name": "TF",
            "round_short_name": "TR",
            "expected_search_params": {
                "search_term": "",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "ALL",
            },
        }
    )
    def test_route_fund_dashboard(
        self,
        request,
        flask_test_client,
        mock_get_fund,
        mock_get_round,
        mock_get_application_overviews,
        mock_get_assessment_stats,
        mock_get_assessment_progress,
    ):

        params = request.node.get_closest_marker("mock_parameters").args[0]

        fund_short_name = params["fund_short_name"]
        round_short_name = params["round_short_name"]

        response = flask_test_client.get(
            f"/assess/assessor_dashboard/{fund_short_name}/{round_short_name}",
            follow_redirects=True,
        )
        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.title.string == "Team dashboard - Assessment Hub"
        ), "Response does not contain expected heading"
        all_table_data_elements = str(
            soup.find_all("td", class_="govuk-table__cell")
        )
        project_titles = [
            "Project In prog and Res",
            "Project In prog and Stop",
            "Project Completed Flag and QA",
        ]
        assert all(
            title in all_table_data_elements for title in project_titles
        )

    @pytest.mark.mock_parameters(
        {
            "fund_short_name": "TF",
            "round_short_name": "TR",
            "expected_search_params": {
                "search_term": "",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "QA_COMPLETE",
            },
        }
    )
    def test_route_fund_dashboard_filter_status(
        self,
        request,
        flask_test_client,
        mock_get_fund,
        mock_get_round,
        mock_get_application_overviews,
        mock_get_assessment_stats,
        mock_get_assessment_progress,
    ):

        params = request.node.get_closest_marker("mock_parameters").args[0]
        fund_short_name = params["fund_short_name"]
        round_short_name = params["round_short_name"]

        response = flask_test_client.get(
            f"/assess/assessor_dashboard/{fund_short_name}/{round_short_name}",
            follow_redirects=True,
            query_string={"status": "QA_COMPLETE"},
        )

        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.title.string == "Team dashboard - Assessment Hub"
        ), "Response does not contain expected heading"

    @pytest.mark.mock_parameters(
        {
            "fund_short_name": "TF",
            "round_short_name": "TR",
            "expected_search_params": {
                "search_term": "",
                "search_in": "project_name,short_id",
                "asset_type": "pub",
                "status": "ALL",
            },
        }
    )
    def test_route_fund_dashboard_filter_asset_type(
        self,
        request,
        flask_test_client,
        mock_get_fund,
        mock_get_round,
        mock_get_application_overviews,
        mock_get_assessment_stats,
        mock_get_assessment_progress,
    ):

        params = request.node.get_closest_marker("mock_parameters").args[0]
        fund_short_name = params["fund_short_name"]
        round_short_name = params["round_short_name"]

        response = flask_test_client.get(
            f"/assess/assessor_dashboard/{fund_short_name}/{round_short_name}",
            follow_redirects=True,
            query_string={"asset_type": "pub"},
        )

        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.title.string == "Team dashboard - Assessment Hub"
        ), "Response does not contain expected heading"

    @pytest.mark.mock_parameters(
        {
            "fund_short_name": "TF",
            "round_short_name": "TR",
            "expected_search_params": {
                "search_term": "hello",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "ALL",
            },
        }
    )
    def test_route_fund_dashboard_search_term(
        self,
        request,
        flask_test_client,
        mock_get_fund,
        mock_get_round,
        mock_get_application_overviews,
        mock_get_assessment_stats,
        mock_get_assessment_progress,
    ):

        params = request.node.get_closest_marker("mock_parameters").args[0]
        fund_short_name = params["fund_short_name"]
        round_short_name = params["round_short_name"]

        response = flask_test_client.get(
            f"/assess/assessor_dashboard/{fund_short_name}/{round_short_name}",
            follow_redirects=True,
            query_string={"search_term": "hello"},
        )

        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.title.string == "Team dashboard - Assessment Hub"
        ), "Response does not contain expected heading"

    @pytest.mark.mock_parameters(
        {
            "fund_short_name": "TF",
            "round_short_name": "TR",
            "expected_search_params": {
                "search_term": "",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "ALL",
            },
        }
    )
    def test_route_fund_dashboard_clear_filters(
        self,
        request,
        flask_test_client,
        mock_get_fund,
        mock_get_round,
        mock_get_application_overviews,
        mock_get_assessment_stats,
        mock_get_assessment_progress,
    ):

        params = request.node.get_closest_marker("mock_parameters").args[0]
        fund_short_name = params["fund_short_name"]
        round_short_name = params["round_short_name"]

        response = flask_test_client.get(
            f"/assess/assessor_dashboard/{fund_short_name}/{round_short_name}",
            follow_redirects=True,
            query_string={
                "clear_filters": "",
                "search_term": "hello",
                "asset_type": "cinema",
                "status": "in-progress",
            },
        )

        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.title.string == "Team dashboard - Assessment Hub"
        ), "Response does not contain expected heading"

    @pytest.mark.mock_parameters(
        {
            "fund_short_name": "TF",
            "round_short_name": "TR",
            "expected_search_params": {
                "search_term": "",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "ALL",
            },
        }
    )
    @pytest.mark.parametrize(
        "sort_column,sort_order,column_id",
        [
            ("location", "asc", 4),
            ("location", "desc", 4),
            ("funding_requested", "asc", 3),
            ("funding_requested", "desc", 3),
            ("", "", 4),
        ],
    )
    def test_route_fund_dashboard_sort_column(
        self,
        request,
        flask_test_client,
        mock_get_fund,
        mock_get_round,
        mock_get_application_overviews,
        mock_get_assessment_stats,
        mock_get_assessment_progress,
        sort_column,
        sort_order,
        column_id,
    ):

        params = request.node.get_closest_marker("mock_parameters").args[0]
        fund_short_name = params["fund_short_name"]
        round_short_name = params["round_short_name"]

        response = flask_test_client.get(
            f"/assess/assessor_dashboard/{fund_short_name}/{round_short_name}",
            follow_redirects=True,
            query_string={
                "sort_column": sort_column,
                "sort_order": sort_order,
            },
        )

        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")

        # Find the table element by its class name
        tbody = soup.find("tbody", {"class": "govuk-table__body"})

        # Find all the elements in the column
        column_data = [
            row.find_all("td")[column_id].text
            for idx, row in enumerate(tbody.find_all("tr"))
        ]

        if sort_order == "asc":
            all_table_data_elements = str(
                soup.find_all(
                    "th",
                    attrs={
                        "class": "govuk-table__header",
                        "aria-sort": "ascending",
                    },
                )
            )
            assert 'aria-sort="ascending"' in all_table_data_elements
            assert sort_column in all_table_data_elements
            # check if the data is in ascending order
            assert all(
                column_data[i] <= column_data[i + 1]
                for i in range(len(column_data) - 1)
            )
        elif sort_order == "desc":
            all_table_data_elements = str(
                soup.find_all(
                    "th",
                    attrs={
                        "class": "govuk-table__header",
                        "aria-sort": "descending",
                    },
                )
            )
            assert 'aria-sort="descending"' in all_table_data_elements
            assert sort_column in all_table_data_elements
            # check if the data is in descending order
            assert all(
                column_data[i] >= column_data[i + 1]
                for i in range(len(column_data) - 1)
            )
        else:
            all_table_data_elements = str(
                soup.find_all(
                    "th",
                    attrs={
                        "class": "govuk-table__header",
                        "aria-sort": "none",
                    },
                )
            )
            assert 'aria-sort="none"' in all_table_data_elements

    @pytest.mark.application_id("resolved_app")
    @pytest.mark.sub_criteria_id("test_sub_criteria_id")
    def test_route_sub_criteria_scoring(
        self,
        flask_test_client,
        request,
        mock_get_sub_criteria,
        mock_get_fund,
        mock_get_comments,
        mock_get_latest_flag,
        mock_get_scores,
        mock_get_bulk_accounts,
    ):

        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]
        sub_criteria_id = request.node.get_closest_marker(
            "sub_criteria_id"
        ).args[0]
        # Use unittest.mock to create a mock object for get_scores_and_justification # noqa

        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        # Send a request to the route you want to test
        response = flask_test_client.get(
            f"/assess/application_id/{application_id}/sub_criteria_id/{sub_criteria_id}/score"  # noqa
        )

        # Assert that the response has the expected status code
        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.title.string
            == "Score - test_sub_criteria - Project In prog and Res -"
            " Assessment Hub"
        )
        assert b"Current score: 3" in response.data
        assert b"Rescore" in response.data
        assert b"Lead assessor" in response.data
        assert b"This is a comment" in response.data

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

    @pytest.mark.application_id("flagged_qa_completed_app")
    def test_flag_route_already_flagged(
        self,
        request,
        flask_test_client,
        mock_get_latest_flag,
        mock_get_sub_criteria_banner_state,
        mock_get_fund,
    ):

        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        response = flask_test_client.get(f"assess/flag/{application_id}")

        assert response.status_code == 400

    @pytest.mark.application_id("resolved_app")
    def test_flag_route_works_for_application_with_latest_resolved_flag(
        self,
        request,
        flask_test_client,
        mock_get_latest_flag,
        mock_get_sub_criteria_banner_state,
        mock_get_fund,
    ):

        marker = request.node.get_closest_marker("application_id")
        application_id = marker.args[0]
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        response = flask_test_client.get(f"assess/flag/{application_id}")

        assert response.status_code == 200

    @pytest.mark.application_id("stopped_app")
    def test_application_route_should_show_stopped_flag(
        self,
        request,
        flask_test_client,
        mock_get_assessor_tasklist_state,
        mock_get_fund,
        mock_get_round,
        mock_get_latest_flag,
        mock_get_bulk_accounts,
    ):
        marker = request.node.get_closest_marker("application_id")
        application_id = marker.args[0]
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        response = flask_test_client.get(
            f"assess/application/{application_id}"
        )

        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.find("h1", class_="assessment-alert__heading").string
            == "Assessment Stopped"
        )
        assert b"Lead User (Lead assessor) lead@test.com" in response.data
        assert b"20/02/2023 at 12:00" in response.data

    @pytest.mark.application_id("resolved_app")
    def test_application_route_should_not_show_resolved_flag(
        self,
        request,
        flask_test_client,
        mock_get_assessor_tasklist_state,
        mock_get_fund,
        mock_get_round,
        mock_get_latest_flag,
        mock_get_bulk_accounts,
    ):
        marker = request.node.get_closest_marker("application_id")
        application_id = marker.args[0]
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        response = flask_test_client.get(
            f"assess/application/{application_id}"
        )

        assert response.status_code == 200
        assert b"Remove flag" not in response.data
        assert b"Resolve flag" not in response.data
        assert b"Reason" not in response.data
        assert b"flagged" not in response.data
        assert b"Flagged" not in response.data

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

    @pytest.mark.application_id("flagged_qa_completed_app")
    def test_flag_route_get_resolve_flag(
        self,
        request,
        flask_test_client,
        mock_get_latest_flag,
        mock_get_sub_criteria_banner_state,
        mock_get_fund,
    ):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]
        response = flask_test_client.get(
            f"assess/resolve_flag/{application_id}?section=org_info",
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

    @pytest.mark.application_id("stopped_app")
    def test_flag_route_get_continue_application(
        self,
        request,
        flask_test_client,
        mock_get_latest_flag,
        mock_get_sub_criteria_banner_state,
        mock_get_fund,
    ):
        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        response = flask_test_client.get(
            f"/assess/continue_assessment/{application_id}",
        )

        assert response.status_code == 200
        assert b"Continue assessment" in response.data
        assert b"Reason for continuing assessment" in response.data
        assert b"Project In prog and Stop" in response.data

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

    @pytest.mark.application_id("flagged_qa_completed_app")
    def test_qa_complete_flag_displayed(
        self,
        request,
        flask_test_client,
        mock_get_round,
        mock_get_assessor_tasklist_state,
        mock_get_latest_flag,
        mock_get_bulk_accounts,
        mock_get_sub_criteria_banner_state,
        mock_get_fund,
    ):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]
        response = flask_test_client.get(
            f"assess/application/{application_id}",
        )

        assert response.status_code == 200
        assert b"Marked as QA complete" in response.data
        assert b"20/02/2023 at 12:00" in response.data

    @pytest.mark.application_id("flagged_qa_completed_app")
    def test_qa_completed_flagged_application(
        self,
        request,
        flask_test_client,
        mock_get_assessor_tasklist_state,
        mock_get_fund,
        mock_get_round,
        mock_get_latest_flag,
        mock_get_bulk_accounts,
    ):
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        marker = request.node.get_closest_marker("application_id")
        application_id = marker.args[0]

        response = flask_test_client.get(
            f"assess/application/{application_id}",
        )

        assert response.status_code == 200
        assert b"Marked as QA complete" in response.data
        assert b"20/02/2023 at 12:00" in response.data
        assert b"Section flagged" in response.data
        assert b"Reason" in response.data
        assert b"Resolve flag" in response.data

    @pytest.mark.mock_parameters(
        {
            "fund_short_name": "TF",
            "round_short_name": "TR",
            "expected_search_params": {
                "search_term": "",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "ALL",
            },
        }
    )
    def test_route_fund_dashboard_shows_flagged(
        self,
        request,
        flask_test_client,
        mock_get_fund,
        mock_get_round,
        mock_get_application_overviews,
        mock_get_assessment_stats,
        mock_get_assessment_progress,
    ):

        params = request.node.get_closest_marker("mock_parameters").args[0]
        fund_short_name = params["fund_short_name"]
        round_short_name = params["round_short_name"]
        response = flask_test_client.get(
            f"/assess/assessor_dashboard/{fund_short_name}/{round_short_name}",
            follow_redirects=True,
        )

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

        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.title.string == "Team dashboard - Assessment Hub"
        ), "Response does not contain expected heading"

    @pytest.mark.application_id("resolved_app")
    @pytest.mark.sub_criteria_id("test_sub_criteria_id")
    def test_page_title_subcriteria_theme_match(
        self,
        request,
        flask_test_client,
        mock_get_sub_criteria,
        mock_get_fund,
        mock_get_latest_flag,
        mock_get_comments,
        mock_get_sub_criteria_theme,
    ):
        # Mocking fsd-user-token cookie
        token = create_valid_token(test_commenter_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]
        sub_criteria_id = request.node.get_closest_marker(
            "sub_criteria_id"
        ).args[0]

        response = flask_test_client.get(
            f"/assess/application_id/{application_id}/sub_criteria_id/{sub_criteria_id}"  # noqa
        )
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.title.string
            == "test_theme_name - test_sub_criteria - Project In prog and"
            " Res -"
            " Assessment Hub"
        )

    @pytest.mark.application_id("resolved_app")
    def test_get_docs_for_download(
        self,
        flask_test_client,
        request,
        mock_get_sub_criteria_banner_state,
        mock_get_fund,
        mock_get_latest_flag,
        templates_rendered,
        mocker,
    ):

        marker = request.node.get_closest_marker("application_id")
        application_id = marker.args[0]

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
                f"/assess/application/{application_id}/export"
            )
            assert 200 == response.status_code
            assert 1 == len(templates_rendered)
            rendered_template = templates_rendered[0]
            assert "contract_downloads.html" == rendered_template[0].name
            assert application_id == rendered_template[1]["application_id"]
            assert b"sample1.doc" in response.data
            assert b"sample2.doc" in response.data

    def test_download_q_and_a(
        self, flask_test_client, mock_get_fund, mock_get_application
    ):

        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        response = flask_test_client.get(
            "/assess/application/test_app_id/export/test_short_id/answers.txt"
        )
        sample_expected_q_a = (
            "Project information\n\n  Q) Have you been given funding through"
            " the Community Ownership Fund before?\n  A) Yes\n\n"
        )
        assert response.status_code == 200
        assert sample_expected_q_a in response.text

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
