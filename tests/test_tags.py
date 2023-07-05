from unittest import mock

import pytest
from app.assess.data import get_available_tags_for_fund_round
from app.assess.models.tag import Tag
from bs4 import BeautifulSoup


def test_get_available_tags(flask_test_client):
    with mock.patch(
        "app.assess.data.get_tags",
        return_value=[
            {
                "id": "123",
                "value": "Val 1",
                "colour": "grey",
                "user": "Bob",
                "active": True,
            },
            {
                "id": "432",
                "value": "Val 2",
                "colour": "red",
                "user": "Bob",
                "active": False,
            },
        ],
    ):
        result = get_available_tags_for_fund_round("test_fund", "test_round")
        assert len(result) == 1
        assert result[0].value == "Val 1"


def test_get_available_tags_no_tags(flask_test_client):
    with mock.patch("app.assess.data.get_tags", return_value=[]):
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
                user="Bob",
                active=True,
                colour="green",
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
def test_change_tags_route_no_tags(
    mock_get_tasklist_state_for_banner,
    client_with_valid_session,
    mock_get_funds,
    mock_get_application_metadata,
    mock_get_fund,
):
    with mock.patch(
        "app.assess.routes.get_available_tags_for_fund_round", return_value=[]
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
