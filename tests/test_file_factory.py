from unittest.mock import MagicMock

import pytest
from app.assess.models.file_factory import ApplicationFileRepresentationArgs
from app.assess.models.file_factory import generate_file_content
from werkzeug.exceptions import NotFound


@pytest.fixture
def mock_fund():
    return MagicMock(name="Fund")


@pytest.fixture
def mock_round():
    return MagicMock(name="Round")


@pytest.fixture
def application_args(mock_fund, mock_round):
    return ApplicationFileRepresentationArgs(
        fund=mock_fund,
        round=mock_round,
        short_id="12345",
        form_name_to_title_map={},
        question_to_answer={},
        application_json={"date_submitted": "2023-06-06T13:38:51.467199"},
        all_uploaded_documents=[],
    )


@pytest.mark.parametrize(
    "file_type, expected_function",
    [
        ("txt", "generate_text_of_application"),
        ("csv", "generate_csv_of_application"),
        ("pdf", "generate_full_application_pdf"),
    ],
)
def test_generate_file_content_supported_types(
    file_type, expected_function, application_args, mocker, request_ctx
):
    mocked_response = MagicMock()
    mocked_response.seek = lambda _: None
    mocker.patch(
        f"app.assess.models.file_factory.{expected_function}",
        return_value=mocked_response,
    )
    mocker.patch(
        "app.assess.models.file_factory.send_file", return_value=MagicMock()
    )
    result = generate_file_content(application_args, file_type)
    assert result is not None


def test_generate_file_content_unsupported_type(application_args):
    with pytest.raises(Exception) as e_info:
        generate_file_content(application_args, "unsupported_type")
    assert e_info.type is NotFound
