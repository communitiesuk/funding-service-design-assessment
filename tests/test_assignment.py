import re
from unittest import mock

import pytest
from bs4 import BeautifulSoup
from flask import url_for

from tests.api_data.test_data import fund_specific_claim_map
from tests.conftest import create_valid_token


# Test assign_assessments route
@pytest.mark.mock_parameters(
    {
        "fund_short_name": "COF",
        "round_short_name": "TR",
        "expected_search_params": {
            "search_term": "",
            "search_in": "project_name,short_id",
            "assigned_to": "ALL",
            "asset_type": "ALL",
            "status": "ALL",
            "filter_by_tag": "ALL",
        },
    }
)
def test_assign_assessments_get(
    request,
    flask_test_client,
    mock_get_funds,
    mock_get_round,
    mock_get_fund,
    mock_get_application_overviews,
    mock_get_users_for_fund,
    mock_get_assessment_progress,
    mock_get_application_metadata,
    mock_get_active_tags_for_fund_round,
    mock_get_tag_types,
):

    params = request.node.get_closest_marker("mock_parameters").args[0]
    fund_short_name = params["fund_short_name"]
    round_short_name = params["round_short_name"]

    flask_test_client.set_cookie(
        "localhost",
        "fsd_user_token",
        create_valid_token(fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"]),
    )

    response = flask_test_client.get(
        url_for(
            "assessment_bp.assign_assessments",
            fund_short_name=fund_short_name,
            round_short_name=round_short_name,
        )
    )

    soup = BeautifulSoup(response.data, "html.parser")

    # Check that there is a checkbox for each project
    project_checkboxes = soup.find_all(
        "input", {"type": "checkbox", "name": "selected_assessments"}
    )
    assert (
        len(project_checkboxes) == 4
    ), f"Expected 4 project checkboxes, found {len(project_checkboxes)}"

    assert response.status_code == 200
    assert b"Assign assessments" in response.data


@pytest.mark.mock_parameters(
    {
        "fund_short_name": "COF",
        "round_short_name": "TR",
        "expected_search_params": "",
    }
)
def test_assign_assessments_post(
    request,
    flask_test_client,
    mock_get_funds,
    mock_get_round,
    mock_get_fund,
    mock_get_application_overviews,
    mock_get_users_for_fund,
    patch_resolve_redirect,
):

    params = request.node.get_closest_marker("mock_parameters").args[0]
    fund_short_name = params["fund_short_name"]
    round_short_name = params["round_short_name"]

    flask_test_client.set_cookie(
        "localhost",
        "fsd_user_token",
        create_valid_token(fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"]),
    )

    form_data = {
        "selected_assessments": ["assessment1"],
    }

    headers = {
        "Referer": url_for(
            "assessment_bp.assign_assessments",
            fund_short_name=fund_short_name,
            round_short_name=round_short_name,
            _external=True,
        ),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = flask_test_client.post(
        url_for(
            "assessment_bp.assign_assessments",
            fund_short_name=fund_short_name,
            round_short_name=round_short_name,
        ),
        headers=headers,
        data=form_data,
        follow_redirects=True,
    )

    # Check that there are two radio buttons, one for general assessor and one for lead assessor
    soup = BeautifulSoup(response.data, "html.parser")

    # Check form data has been processed and stored as hidden fields.
    hidden_fields = soup.find_all(
        "input", {"type": "hidden", "name": "selected_assessments"}
    )
    assert hidden_fields[0].get("value") == "assessment1"

    radio_buttons = soup.find_all("input", {"type": "radio"})

    assert (
        len(radio_buttons) == 2
    ), f"Expected 2 radio buttons, found {len(radio_buttons)}"

    radio_values = [radio.get("value") for radio in radio_buttons]
    assert (
        "general_assessor" in radio_values
    ), "Radio button for 'general_assessor' not found"
    assert "lead_assessor" in radio_values, "Radio button for 'lead_assessor' not found"

    assert response.status_code == 200
    assert b"Select the type of role you would like to assign." in response.data


@pytest.mark.mock_parameters(
    {
        "fund_short_name": "COF",
        "round_short_name": "TR",
        "expected_search_params": "",
    }
)
def test_assessor_type_post(
    request,
    flask_test_client,
    mock_get_funds,
    mock_get_round,
    mock_get_fund,
    mock_get_application_overviews,
    mock_get_users_for_fund,
    patch_resolve_redirect,
):

    params = request.node.get_closest_marker("mock_parameters").args[0]
    fund_short_name = params["fund_short_name"]
    round_short_name = params["round_short_name"]

    flask_test_client.set_cookie(
        "localhost",
        "fsd_user_token",
        create_valid_token(fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"]),
    )

    form_data = {
        "selected_assessments": ["assessment1"],
        "assessor_role": ["lead_assessor"],
    }

    headers = {
        "Referer": url_for(
            "assessment_bp.assessor_type",
            fund_short_name=fund_short_name,
            round_short_name=round_short_name,
            _external=True,
        ),
    }

    with mock.patch(
        "app.blueprints.assessments.routes.get_application_assignments",
        return_value=[{"user_id": "user2"}],
    ):
        response = flask_test_client.post(
            url_for(
                "assessment_bp.assessor_type",
                fund_short_name=fund_short_name,
                round_short_name=round_short_name,
            ),
            headers=headers,
            data=form_data,
            follow_redirects=True,
        )

    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")

    # Check form data has been processed and stored as hidden fields.
    for key, value in form_data.items():
        hidden_field = soup.find("input", {"type": "hidden", "name": key})
        assert hidden_field is not None
        assert hidden_field.get("value") == value[0]

    # Check for the "select all" checkbox
    select_all_checkbox = soup.find(
        "input", {"id": "select_all_users", "type": "checkbox"}
    )
    assert select_all_checkbox is not None, "Select all checkbox not found"

    table_body = soup.find("tbody", class_="govuk-table__body")
    assert table_body is not None, "Table body not found"

    # Check there is only a single assignable user ("Lead Test User")
    rows = table_body.find_all("tr", class_="govuk-table__row")
    assert len(rows) == 1, f"Expected 1 row, found {len(rows)}"

    row = rows[0]

    name_cell = row.find_all("td", class_="govuk-table__cell")[1]
    assert (
        fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"]["fullName"]
        in name_cell.text.strip()
    ), f"Expected 'Lead Test User', found {name_cell.text.strip()}"

    # Check that there is a checkbox for this entry
    checkbox = row.find(
        "input",
        {
            "type": "checkbox",
            "name": "selected_users",
            "value": fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"][
                "accountId"
            ],
        },
    )
    assert (
        checkbox is not None
    ), f"Checkbox for {fund_specific_claim_map[fund_short_name]['LEAD_ASSESSOR']['accountId']} not found"

    assert not checkbox.has_attr("checked"), "Checkbox is not checked"


@pytest.mark.mock_parameters(
    {
        "fund_short_name": "COF",
        "round_short_name": "TR",
        "expected_search_params": "",
    }
)
def test_assessor_type_post_existing_assignment(
    request,
    flask_test_client,
    mock_get_funds,
    mock_get_round,
    mock_get_fund,
    mock_get_application_overviews,
    mock_get_users_for_fund,
    patch_resolve_redirect,
):
    params = request.node.get_closest_marker("mock_parameters").args[0]
    fund_short_name = params["fund_short_name"]
    round_short_name = params["round_short_name"]

    flask_test_client.set_cookie(
        "localhost",
        "fsd_user_token",
        create_valid_token(fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"]),
    )

    form_data = {
        "selected_assessments": ["assessment1"],
        "assessor_role": ["lead_assessor"],
    }

    headers = {
        "Referer": url_for(
            "assessment_bp.assessor_type",
            fund_short_name=fund_short_name,
            round_short_name=round_short_name,
            _external=True,
        ),
    }

    with mock.patch(
        "app.blueprints.assessments.routes.get_application_assignments",
        return_value=[{"user_id": "cof-lead-assessor"}],
    ):
        response = flask_test_client.post(
            url_for(
                "assessment_bp.assessor_type",
                fund_short_name=fund_short_name,
                round_short_name=round_short_name,
            ),
            headers=headers,
            data=form_data,
            follow_redirects=True,
        )

    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")

    table_body = soup.find("tbody", class_="govuk-table__body")
    assert table_body is not None, "Table body not found"

    # Check there is only a single assignable user ("Lead Test User")
    rows = table_body.find_all("tr", class_="govuk-table__row")
    assert len(rows) == 1, f"Expected 1 row, found {len(rows)}"

    row = rows[0]

    name_cell = row.find_all("td", class_="govuk-table__cell")[1]
    assert (
        fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"]["fullName"]
        in name_cell.text.strip()
    ), f"Expected 'Lead Test User', found {name_cell.text.strip()}"

    # Check that there is a checkbox for this entry
    checkbox = row.find(
        "input",
        {
            "type": "checkbox",
            "name": "selected_users",
            "value": fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"][
                "accountId"
            ],
        },
    )

    assert checkbox is not None, "Checkbox not found"

    # Check if the checkbox is checked
    assert checkbox.has_attr("checked"), "Checkbox is not checked"


@pytest.mark.mock_parameters(
    {
        "fund_short_name": "COF",
        "round_short_name": "TR",
        "expected_search_params": "",
    }
)
def test_assessor_type_list_post(
    request,
    flask_test_client,
    mock_get_funds,
    mock_get_round,
    mock_get_fund,
    mock_get_application_overviews,
    mock_get_users_for_fund,
    mock_get_assessment_progress,
    patch_resolve_redirect,
):

    params = request.node.get_closest_marker("mock_parameters").args[0]
    fund_short_name = params["fund_short_name"]
    round_short_name = params["round_short_name"]

    flask_test_client.set_cookie(
        "localhost",
        "fsd_user_token",
        create_valid_token(fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"]),
    )

    form_data = {
        "selected_assessments": ["stopped_app"],
        "assessor_role": ["general_assessor"],
        "selected_users": [
            fund_specific_claim_map[fund_short_name]["ASSESSOR"]["accountId"]
        ],
    }
    headers = {
        "Referer": url_for(
            "assessment_bp.assessor_type_list",
            fund_short_name=fund_short_name,
            round_short_name=round_short_name,
            _external=True,
        ),
    }
    response = flask_test_client.post(
        url_for(
            "assessment_bp.assessor_type_list",
            fund_short_name=fund_short_name,
            round_short_name=round_short_name,
        ),
        data=form_data,
        headers=headers,
        follow_redirects=True,
    )

    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")

    # Check form data has been processed and stored as hidden fields.
    for key, value in form_data.items():
        hidden_field = soup.find("input", {"type": "hidden", "name": key})
        assert hidden_field is not None
        assert hidden_field.get("value") == value[0]

    # Check get_assessment_progress() is only called for the selected assessments
    assert len(mock_get_assessment_progress.call_args[0][0]) == 1
    assert (
        mock_get_assessment_progress.call_args[0][0][0]["application_id"]
        == form_data["selected_assessments"][0]
    )
    strip_html_regx = re.compile("<.*?>")
    html_stripped_output = re.sub(strip_html_regx, "", str(response.data))
    assert (
        f"You are about to assign {fund_specific_claim_map[fund_short_name]['ASSESSOR']['fullName']}"
        " to 1 assessment as a general assessor" in html_stripped_output
    )


@pytest.mark.mock_parameters(
    {
        "fund_short_name": "COF",
        "round_short_name": "TR",
        "expected_search_params": {
            "search_term": "",
            "search_in": "project_name,short_id",
            "asset_type": "ALL",
            "status": "ALL",
            "filter_by_tag": "ALL",
            "assigned_to": "ALL",
        },
    }
)
def test_assignment_overview_post(
    request,
    flask_test_client,
    mock_get_funds,
    mock_get_round,
    mock_get_fund,
    mock_get_application_overviews,
    mock_get_users_for_fund,
    mock_get_assessment_progress,
    mock_get_application_metadata,
    mock_get_active_tags_for_fund_round,
    mock_get_tag_types,
):

    params = request.node.get_closest_marker("mock_parameters").args[0]
    fund_short_name = params["fund_short_name"]
    round_short_name = params["round_short_name"]

    flask_test_client.set_cookie(
        "localhost",
        "fsd_user_token",
        create_valid_token(fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"]),
    )

    form_data = {
        "selected_assessments": ["assessment1", "assessment2"],
        "assessor_role": ["lead_assessor"],
        "selected_users": ["user1", "user2"],
    }

    headers = {
        "Referer": url_for(
            "assessment_bp.assignment_overview",
            fund_short_name=fund_short_name,
            round_short_name=round_short_name,
            _external=True,
        ),
    }
    with mock.patch(
        "app.blueprints.assessments.routes.get_application_assignments",
        return_value=[{"user_id": "user2"}],
    ), mock.patch(
        "app.blueprints.assessments.routes.assign_user_to_assessment",
    ) as mock_assign_user_to_assessment_1:
        response = flask_test_client.post(
            url_for(
                "assessment_bp.assignment_overview",
                fund_short_name=fund_short_name,
                round_short_name=round_short_name,
            ),
            data=form_data,
            headers=headers,
            follow_redirects=True,
        )

        # For User 1 this is a new assignment, for User 2 this is an existing assignment that should be activated.
        mock_assign_user_to_assessment_1.assert_has_calls(
            [
                mock.call(
                    "assessment1",
                    "user1",
                    fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"][
                        "accountId"
                    ],
                    False,
                ),
                mock.call(
                    "assessment2",
                    "user1",
                    fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"][
                        "accountId"
                    ],
                    False,
                ),
                mock.call(
                    "assessment1",
                    "user2",
                    fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"][
                        "accountId"
                    ],
                    True,
                ),
                mock.call(
                    "assessment2",
                    "user2",
                    fund_specific_claim_map[fund_short_name]["LEAD_ASSESSOR"][
                        "accountId"
                    ],
                    True,
                ),
            ],
            any_order=True,
        )

        assert len(mock_assign_user_to_assessment_1.mock_calls) == 4

    assert response.status_code == 200
