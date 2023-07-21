from unittest import mock

import pytest
from app.assess.data import get_associated_tags_for_application
from app.assess.data import get_available_tags_for_fund_round
from app.assess.data import post_new_tag_for_fund_round
from app.assess.data import update_associated_tags
from app.assess.models.tag import AssociatedTag
from app.assess.models.tag import Tag
from app.assess.routes import FLAG_ERROR_MESSAGE
from bs4 import BeautifulSoup
from tests.api_data.test_data import test_fund_id
from tests.api_data.test_data import test_round_id

test_tags = [
    {
        "id": "123",
        "value": "Val 1",
        "creator_user_id": "Bob",
        "active": True,
        "purpose": "POSITIVE",
        "type_id": "type_1",
    },
    {
        "id": "432",
        "value": "Val 2",
        "creator_user_id": "Bob",
        "active": False,
        "purpose": "POSITIVE",
        "type_id": "type_1",
    },
]


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
                purpose="POSITIVE",
                type_id="type_1",
            )
        ],
    ), mock.patch(
        "app.assess.routes.get_associated_tags_for_application",
        return_value=[
            AssociatedTag(
                application_id="75dabe60-ae89-4a47-9263-d35e010b6c66",
                associated=True,
                tag_id="75f4296f-502b-4293-82a8-b828e678dd9e",
                user_id="65f4296f-502b-4293-82a8-b828e678dd9e",
                value="Tag one red",
                purpose="POSITIVE",
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
            table.findAll("tr")[1].findAll("td")[0].text.strip() == "POSITIVE"
        )
        assert (
            table.findAll("tr")[1]
            .findAll("td")[0]
            .find("strong", class_="govuk-tag--green")
            .text.strip()
            == "POSITIVE"
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
                purpose="POSITIVE",
                type_id="type_1",
            ),
            Tag(
                id="456",
                value="Tag 1",
                creator_user_id="Bob",
                active=True,
                purpose="NEGATIVE",
                type_id="type_2",
            ),
        ],
    ), mock.patch(
        "app.assess.routes.get_associated_tags_for_application",
        return_value=[
            AssociatedTag(
                application_id="75dabe60-ae89-4a47-9263-d35e010b6c66",
                associated=True,
                purpose="POSITIVE",
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


# Functions


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


def test_get_associated_tags_for_applications(flask_test_client):

    with mock.patch(
        "app.assess.data.get_data",
        return_value=[
            {
                "application_id": "155df6dc-541e-4d7c-82bb-9d8e3b7e52ef",
                "associated": True,
                "purpose": "PEOPLE",
                "tag_id": "c62abab1-41b5-4956-b496-4a8862d748a9",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "test tag",
            }
        ],
    ):
        result = get_associated_tags_for_application(
            "155df6dc-541e-4d7c-82bb-9d8e3b7e52ef"
        )
        assert len(result) == 1
        assert result[0].value == "test tag"


def test_update_associated_tag_returns_True(flask_test_client):

    with mock.patch("requests.put") as mock_put:
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_put.return_value = mock_response

        new_tags = [
            {
                "tag_id": "13c7ba20-1d12-4a08-9a95-76d2fa447db1",
                "user_id": "00000000-0000-0000-0000-000000000000",
            },
            {
                "tag_id": "c62abab1-41b5-4956-b496-4a8862d748a9",
                "user_id": "00000000-0000-0000-0000-000000000000",
            },
            {
                "tag_id": "d74d6bb2-a14d-4d4e-98a9-96731aa94f28",
                "user_id": "00000000-0000-0000-0000-000000000000",
            },
        ]

        result = update_associated_tags(
            "155df6dc-541e-4d7c-82bb-9d8e3b7e52ef", new_tags
        )
        assert result is True


def test_post_new_tag_for_fund_round_returns_True(flask_test_client):
    with mock.patch("requests.post") as mock_post:
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_post.return_value = mock_response

        fund_id = "c62abab1-41b5-4956-b496-4a8862d748a9"
        round_id = "13c7ba20-1d12-4a08-9a95-76d2fa447db1"
        tag = {
            "value": "v",
            "tag_type_id": "f07b4d46-e078-4e2c-9066-be2b96c3140d",
            "creator_user_id": "00000000-0000-0000-0000-000000000000",
        }

        result = post_new_tag_for_fund_round(fund_id, round_id, tag)
        assert result is True


@pytest.mark.parametrize(
    "expect_flagging",
    [
        False,
    ],
)
def test_create_tag_initial_render_get(
    expect_flagging,
    client_with_valid_session,
    mock_get_funds,
    mock_get_fund,
    mock_get_tag_types,
    mock_get_round,
    mock_get_available_tags_for_fund_round,
):
    response = client_with_valid_session.get(
        f"/assess/tags/create/{test_fund_id}/{test_round_id}"
    )

    assert response.status_code == 200
    assert "Type 1 description" in response.text


@pytest.mark.parametrize(
    "expect_flagging",
    [
        False,
    ],
)
def test_create_tag_invalid_form_post(
    expect_flagging,
    client_with_valid_session,
    mock_get_funds,
    mock_get_fund,
    mock_get_tag_types,
    mock_get_round,
    mock_get_available_tags_for_fund_round,
):
    response = client_with_valid_session.post(
        f"/assess/tags/create/{test_fund_id}/{test_round_id}",
        data={},  # empty form, so invalid
    )

    assert response.status_code == 200
    assert FLAG_ERROR_MESSAGE in response.text


@pytest.mark.parametrize(
    "expect_flagging",
    [
        False,
    ],
)
def test_create_tag_invalid_character_post(
    expect_flagging,
    client_with_valid_session,
    mock_get_funds,
    mock_get_fund,
    mock_get_tag_types,
    mock_get_round,
    mock_get_available_tags_for_fund_round,
):
    response = client_with_valid_session.post(
        f"/assess/tags/create/{test_fund_id}/{test_round_id}",
        data={"value": "!!", "type": "type_1"},  # SPECIAL CHARACTER
    )

    assert response.status_code == 200
    assert FLAG_ERROR_MESSAGE in response.text


@pytest.mark.parametrize(
    "expect_flagging",
    [
        False,
    ],
)
def test_create_tag_shows_error_if_valid_form_post_but_request_fails(
    expect_flagging,
    client_with_valid_session,
    mock_get_funds,
    mock_get_fund,
    mock_get_tag_types,
    mock_get_round,
    mocker,
):
    mocker.patch(
        "app.assess.routes.post_new_tag_for_fund_round",
        return_value=lambda *_: False,
    )

    response = client_with_valid_session.post(
        f"/assess/tags/create/{test_fund_id}/{test_round_id}",
        data={"value": "Tag value", "type": "type_1"},
    )

    # this redirects and will flash the error message
    assert response.status_code == 302
    assert response.location == "/assess/tags/create/test-fund/test-round"


@pytest.mark.parametrize(
    "expect_flagging",
    [
        False,
    ],
)
def test_create_tag_valid_form_post(
    expect_flagging,
    client_with_valid_session,
    mock_get_funds,
    mock_get_fund,
    mock_get_tag_types,
    mock_get_round,
    mocker,
):
    mocker.patch(
        "app.assess.routes.post_new_tag_for_fund_round",
        return_value=lambda *_: True,
    )

    response = client_with_valid_session.post(
        f"/assess/tags/create/{test_fund_id}/{test_round_id}",
        data={"value": "Tag value", "type": "type_1"},
    )

    assert response.status_code == 302
    assert response.location == "/assess/tags/create/test-fund/test-round"
    assert FLAG_ERROR_MESSAGE not in response.text


@pytest.mark.parametrize(
    "expect_flagging",
    [
        False,
    ],
)
def test_create_tag_valid_form_go_back_post(
    expect_flagging,
    client_with_valid_session,
    mock_get_funds,
    mock_get_fund,
    mock_get_tag_types,
    mock_get_round,
    mocker,
):
    mocker.patch(
        "app.assess.routes.post_new_tag_for_fund_round",
        return_value=lambda *_: True,
    )

    response = client_with_valid_session.post(
        f"/assess/tags/create/{test_fund_id}/{test_round_id}?go_back=True",
        data={"value": "Tag value", "type": "type_1"},
    )

    assert response.status_code == 302
    assert response.location == "/assess/tags/manage/test-fund/test-round"


@pytest.mark.parametrize(
    "expect_flagging",
    [
        False,
    ],
)
def test_manage_tag_page_renders_with_tags(
    expect_flagging,
    client_with_valid_session,
    mock_get_funds,
    mock_get_fund,
    mock_get_tag_types,
    mock_get_round,
    mock_get_available_tags_for_fund_round,
):
    response = client_with_valid_session.get(
        f"/assess/tags/manage/{test_fund_id}/{test_round_id}",
    )

    assert response.status_code == 200
    assert "Val 1" in response.text
    assert "Val 2" in response.text
    assert "ACTIVE" in response.text
    assert "NOT ACTIVE" in response.text
