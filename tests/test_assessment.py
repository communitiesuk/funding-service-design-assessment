import urllib
from unittest import mock

import pytest
from bs4 import BeautifulSoup
from flask import session
from flask import url_for

from app.blueprints.assessments.models.round_status import RoundStatus
from app.blueprints.assessments.models.round_summary import RoundSummary
from app.blueprints.assessments.models.round_summary import Stats
from app.blueprints.services.models.flag import Flag
from tests.api_data.test_data import fund_specific_claim_map
from tests.conftest import create_valid_token
from tests.conftest import test_commenter_claims
from tests.conftest import test_lead_assessor_claims
from tests.api_data.test_data import stopped_app_id


class TestRoutes:
    @pytest.mark.mock_parameters(
        {
            "get_assessment_stats_path": [
                "app.blueprints.assessments.models.round_summary.get_assessments_stats",
            ],
            "get_rounds_path": [
                "app.blueprints.assessments.models.round_summary.get_rounds",
            ],
            "fund_id": "test-fund",
            "round_id": "test-round",
        }
    )

    @pytest.mark.application_id("stopped_app")
    def test_assign_to_you_section_for_lead_with_no_assignees(
        self,
        request,
        flask_test_client,
        mock_get_assessor_tasklist_state,
        mock_get_fund,
        mock_get_funds,
        mock_get_application_metadata,
        mock_get_round,
        mock_get_flags,
        mock_get_qa_complete,
        mock_get_bulk_accounts,
        mock_get_associated_tags_for_application,
        mocker,
        mock_get_scoring_system,
    ):
        marker = request.node.get_closest_marker("application_id")
        application_id = marker.args[0]
        token = create_valid_token(test_lead_assessor_claims)
        flask_test_client.set_cookie("fsd_user_token", token)

        response = flask_test_client.get(f"assess/application/{application_id}")

        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.find("h3", class_="govuk-heading-m").string.strip()
            == "Assigned to you"
        )
        assert (
            soup.find("button", class_="secondary-button").string.strip()
            == "Reassign assessment"
        )

    @pytest.mark.application_id("stopped_app")
    def test_assign_to_you_section_for_nonlead_with_no_assignees(
        self,
        request,
        flask_test_client,
        mock_get_assessor_tasklist_state,
        mock_get_fund,
        mock_get_funds,
        mock_get_application_metadata,
        mock_get_round,
        mock_get_flags,
        mock_get_qa_complete,
        mock_get_bulk_accounts,
        mock_get_associated_tags_for_application,
        mocker,
        mock_get_scoring_system,
    ):
        marker = request.node.get_closest_marker("application_id")
        application_id = marker.args[0]
        token = create_valid_token(test_commenter_claims)
        flask_test_client.set_cookie("fsd_user_token", token)

        response = flask_test_client.get(f"assess/application/{application_id}")

        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.find("h3", class_="govuk-heading-m").string.strip()
            == "Assigned to you"
        )

       #TODO: test there is no button

    @pytest.mark.application_id("stopped_app")
    def test_assign_to_you_section_for_lead_with_assignees(
        self,
        request,
        flask_test_client,
        mock_get_assessor_tasklist_state,
        mock_get_fund,
        mock_get_funds,
        mock_get_application_metadata,
        mock_get_round,
        mock_get_flags,
        mock_get_qa_complete,
        mock_get_bulk_accounts,
        mock_get_associated_tags_for_application,
        mocker,
        mock_get_scoring_system,
        mock_get_application_assignments,
    ):
        marker = request.node.get_closest_marker("application_id")
        application_id = marker.args[0]
        token = create_valid_token(test_commenter_claims)
        flask_test_client.set_cookie("fsd_user_token", token)

        response = flask_test_client.get(f"assess/application/{application_id}")

        assert 200 == response.status_code, "Wrong status code on response"
        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.find("h3", class_="govuk-heading-m").string.strip()
            == "Assigned to you"
        )

        assert b"Development User assigned the assessors:" in response.data