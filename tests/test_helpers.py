import pytest
from app.assess.helpers import determine_display_status
from app.assess.helpers import generate_csv_of_application
from app.assess.helpers import is_flaggable
from app.assess.models.flag_v2 import FlagV2

RAISED_FLAG = [
    FlagV2.from_dict(
        {
            "application_id": "app_123",
            "latest_status": 0,
            "latest_allocation": "TEAM_1",
            "id": "flagid",
            "sections_to_flag": ["community"],
            "updates": [
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6a",
                    "user_id": "test@example.com",
                    "date_created": "2023-01-01T00:00:00",
                    "justification": "Test flag",
                    "status": 0,
                    "allocation": "TEAM_1",
                }
            ],
        }
    )
]
RESOLVED_FLAG = [
    FlagV2.from_dict(
        {
            "application_id": "app_123",
            "latest_status": 3,
            "latest_allocation": "TEAM_1",
            "id": "flagid",
            "sections_to_flag": ["community"],
            "updates": [
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6a",
                    "user_id": "test@example.com",
                    "date_created": "2023-01-01T00:00:00",
                    "justification": "Test flag",
                    "status": 3,
                    "allocation": "TEAM_1",
                }
            ],
        }
    )
]
QA_COMPLETE_FLAG = [
    FlagV2.from_dict(
        {
            "application_id": "app_123",
            "latest_status": 2,
            "latest_allocation": "TEAM_1",
            "id": "flagid",
            "sections_to_flag": ["community"],
            "updates": [
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6a",
                    "user_id": "test@example.com",
                    "date_created": "2023-01-01T00:00:00",
                    "justification": "Test flag",
                    "status": 2,
                    "allocation": "TEAM_1",
                }
            ],
        }
    )
]
STOPPED_FLAG = [
    FlagV2.from_dict(
        {
            "application_id": "app_123",
            "latest_status": 1,
            "latest_allocation": "TEAM_1",
            "id": "flagid",
            "sections_to_flag": ["community"],
            "updates": [
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6a",
                    "user_id": "test@example.com",
                    "date_created": "2023-01-01T00:00:00",
                    "justification": "Test flag",
                    "status": 1,
                    "allocation": "TEAM_1",
                }
            ],
        }
    )
]


def test_determine_display_status():
    assert (
        determine_display_status(workflow_status="IN_PROGRESS", Flags=None)
        == "In progress"
    )
    assert (
        determine_display_status(
            workflow_status="IN_PROGRESS", Flags=RAISED_FLAG
        )
        == "Flagged for TEAM_1"
    )
    assert (
        determine_display_status(
            workflow_status="IN_PROGRESS", Flags=RESOLVED_FLAG
        )
        == "In progress"
    )


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (determine_display_status("NOT_STARTED", RESOLVED_FLAG), True),
        (determine_display_status("COMPLETED", QA_COMPLETE_FLAG), True),
        (determine_display_status("NOT_STARTED", RAISED_FLAG), True),
        (determine_display_status("IN_PROGRESS", RAISED_FLAG), True),
        (determine_display_status("NOT_STARTED", STOPPED_FLAG), False),
    ],
)
def test_is_flaggable(test_input, expected):
    assert is_flaggable(test_input) == expected


def test_generate_csv_of_application():
    q_and_a = {
        "section1": {"question1": "- answer1", "question2": "answer2"},
        "section2": {"question3": "- answer3", "question4": "answer4"},
    }
    fund_name = "Test Fund"

    expected_output = (
        "Fund,Test Fund\r\n"
        "Section,Question,Answer\r\n"
        "Section1,question1,'- answer1\r\n"
        "Section1,question2,answer2\r\n"
        "Section2,question3,'- answer3\r\n"
        "Section2,question4,answer4\r\n"
    )

    result = generate_csv_of_application(q_and_a, fund_name)

    assert result == expected_output
