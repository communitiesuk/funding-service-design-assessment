from unittest import mock

import pytest
from app.assess.data import get_available_tags_for_fund_round
from app.assess.models.tag import AssociatedTag
from app.assess.models.tag import Tag
from bs4 import BeautifulSoup

test_tags = [
    {
        "id": "123",
        "value": "Val 1",
        "colour": "grey",
        "creator_user_id": "Bob",
        "active": True,
    },
    {
        "id": "432",
        "value": "Val 2",
        "colour": "red",
        "creator_user_id": "Bob",
        "active": False,
    },
]


def test_get_available_tags(flask_test_client):
    with mock.patch(
        "app.assess.data.get_data",
        return_value=test_tags,
    ):
        result = get_available_tags_for_fund_round("test_fund", "test_round")
        assert len(result) == 1
        assert result[0].value == "Val 1"


def test_get_available_tags_no_tags(flask_test_client):
    with mock.patch("app.assess.data.get_data", return_value=[]):
        result = get_available_tags_for_fund_round("test_fund", "test_round")
        assert len(result) == 0


@pytest.mark.application_id("resolved_app")
def test_change_tags_route(
    mock_get_tasklist_state_for_banner,
    client_with_valid_session,
    mock_get_funds,
    mock_get_application_metadata,
    mock_get_fund,
):
    with mock.patch(
        "app.assess.routes.get_available_tags_for_fund_round",
        return_value=[
            Tag(
                id="123",
                value="Tag 1",
                creator_user_id="Bob",
                active=True,
                colour="green",
            )
        ],
    ), mock.patch(
        "app.assess.routes.get_associated_tags_for_application",
        return_value=[
            AssociatedTag(
                application_id="75dabe60-ae89-4a47-9263-d35e010b6c66",
                associated=True,
                colour="RED",
                tag_id="75f4296f-502b-4293-82a8-b828e678dd9e",
                user_id="65f4296f-502b-4293-82a8-b828e678dd9e",
                value="Tag one red",
            )
        ],
    ):
        response = client_with_valid_session.get(
            "/assess/application/app_id/tags"
        )
        soup = BeautifulSoup(response.data, "html.parser")
        assert soup.find("h1").text == "Change tags"
        assert (
            table := soup.find(
                "table", class_="govuk-table dluhc-table-checkboxes"
            )
        )
        assert len(table.findAll("tr")) == 2
        assert (
            table.findAll("tr")[0].findAll("th")[0].text.strip() == "Tag name"
        )
        assert table.findAll("tr")[1].findAll("th")[0].text.strip() == "Tag 1"
        assert (
            table.findAll("tr")[1]
            .findAll("td")[0]
            .find("strong", class_="govuk-tag--green")
            .text.strip()
            == "Tag 1"
        )


@pytest.mark.application_id("resolved_app")
def test_change_tags_route_associated_tag_checked(
    mock_get_tasklist_state_for_banner,
    client_with_valid_session,
    mock_get_funds,
    mock_get_application_metadata,
    mock_get_fund,
):
    with mock.patch(
        "app.assess.routes.get_available_tags_for_fund_round",
        return_value=[
            Tag(
                id="123",
                value="This should be checked",
                creator_user_id="Bob",
                active=True,
                colour="This associated tag SHOULD be checked",
            ),
            Tag(
                id="456",
                value="Tag 1",
                creator_user_id="Bob",
                active=True,
                colour="This not associated tag should NOT be checked",
            ),
        ],
    ), mock.patch(
        "app.assess.routes.get_associated_tags_for_application",
        return_value=[
            AssociatedTag(
                application_id="75dabe60-ae89-4a47-9263-d35e010b6c66",
                associated=True,
                colour="RED",
                tag_id="123",
                user_id="65f4296f-502b-4293-82a8-b828e678dd9e",
                value="This associated tag SHOULD be checked",
            )
        ],
    ):
        response = client_with_valid_session.get(
            "/assess/application/app_id/tags"
        )
        soup = BeautifulSoup(response.data, "html.parser")
        assert soup.find("h1").text == "Change tags"
        assert (
            soup.find("input", {"id": "123"}).attrs.get("checked") is not None
        )
        assert soup.find("input", {"id": "456"}).attrs.get("checked") is None
        assert (
            table := soup.find(
                "table", class_="govuk-table dluhc-table-checkboxes"
            )
        )
        assert len(table.findAll("tr")) == 3


@pytest.mark.application_id("resolved_app")
def test_change_tags_route_no_tags(
    mock_get_tasklist_state_for_banner,
    client_with_valid_session,
    mock_get_funds,
    mock_get_application_metadata,
    mock_get_fund,
):

    with mock.patch(
        "app.assess.routes.get_available_tags_for_fund_round",
        return_value=[],
    ), mock.patch(
        "app.assess.routes.get_associated_tags_for_application",
        return_value=[],
    ):
        response = client_with_valid_session.get(
            "/assess/application/app_id/tags"
        )
        soup = BeautifulSoup(response.data, "html.parser")
        assert soup.find("h1").text == "Change tags"
        assert (
            soup.find(
                "p",
                class_="govuk-body dluhc-body-empty",
            ).text.strip()
            == "There are no tags available"
        )
