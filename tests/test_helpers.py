import pytest
from app.assess.helpers import determine_display_status
from app.assess.helpers import generate_assessment_info_csv
from app.assess.helpers import generate_csv_of_application
from app.assess.helpers import is_flaggable
from app.assess.models.flag_v2 import FlagV2
from app.assess.models.fund import Fund

RAISED_FLAG = [
    FlagV2.from_dict(
        {
            "application_id": "app_123",
            "latest_status": "RAISED",
            "latest_allocation": "TEAM_1",
            "id": "flagid",
            "sections_to_flag": ["community"],
            "updates": [
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6a",
                    "user_id": "test@example.com",
                    "date_created": "2023-01-01T00:00:00",
                    "justification": "Test flag",
                    "status": "RAISED",
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
            "latest_status": "RESOLVED",
            "latest_allocation": "TEAM_1",
            "id": "flagid",
            "sections_to_flag": ["community"],
            "updates": [
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6a",
                    "user_id": "test@example.com",
                    "date_created": "2023-01-01T00:00:00",
                    "justification": "Test flag",
                    "status": "RESOLVED",
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
            "latest_status": "STOPPED",
            "latest_allocation": "TEAM_1",
            "id": "flagid",
            "sections_to_flag": ["community"],
            "updates": [
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6a",
                    "user_id": "test@example.com",
                    "date_created": "2023-01-01T00:00:00",
                    "justification": "Test flag",
                    "status": "STOPPED",
                    "allocation": "TEAM_1",
                }
            ],
        }
    )
]


def test_determine_display_status():
    assert (
        determine_display_status(
            workflow_status="IN_PROGRESS", Flags=None, is_qa_complete=False
        )
        == "In progress"
    )
    assert (
        determine_display_status(
            workflow_status="IN_PROGRESS",
            Flags=RAISED_FLAG,
            is_qa_complete=False,
        )
        == "Flagged for TEAM_1"
    )
    assert (
        determine_display_status(
            workflow_status="IN_PROGRESS",
            Flags=RESOLVED_FLAG,
            is_qa_complete=False,
        )
        == "In progress"
    )


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (determine_display_status("NOT_STARTED", RESOLVED_FLAG, False), True),
        (determine_display_status("COMPLETED", RESOLVED_FLAG, True), True),
        (determine_display_status("NOT_STARTED", RAISED_FLAG, False), True),
        (determine_display_status("IN_PROGRESS", RAISED_FLAG, False), True),
        (determine_display_status("NOT_STARTED", STOPPED_FLAG, False), False),
    ],
)
def test_is_flaggable(test_input, expected):
    assert is_flaggable(test_input) == expected


def test_generate_csv_of_application():
    q_and_a = {
        "section1": {"question1": "- answer1", "question2": "answer2"},
        "section2": {"question3": "- answer3", "question4": "answer4"},
        "section3": {"question5": "", "question6": None},
    }
    fund = Fund(
        name="Test Fund",
        id="fund-uuid",
        description="Test Fund Description",
        short_name="Test Short Name",
    )

    application = {
        "application_id": "application-uuid",
        "short_id": "applcation-short-reference",
    }

    expected_output = (
        "Fund,Test Fund,fund-uuid\r\n"
        "Application,applcation-short-reference,application-uuid\r\n"
        "Section,Question,Answer\r\n"
        "Section1,question1,'- answer1\r\n"
        "Section1,question2,answer2\r\n"
        "Section2,question3,'- answer3\r\n"
        "Section2,question4,answer4\r\n"
        "Section3,question5,Not provided\r\n"
        "Section3,question6,Not provided\r\n"
    )

    result = generate_csv_of_application(q_and_a, fund, application)

    assert result == expected_output


def test_generate_csv_for_fields():
    test_data = [
        {
            "AppId": "9a8b6c00-e461-466c-acb3-2519621b3a38",
            "Charity number ": "Test",
            "Do you need to do any further feasibility work?": False,
            "Project name": "Save the humble pub in Bangor",
            "Doc Name": "sample1.doc",
        },
        {
            "AppId": "de36ae35-9ef6-4dc5-a2bf-de9ee481c8af",
            "Charity number ": "Test",
            "Do you need to do any further feasibility work?": False,
            "Project name": "Save the humble pub in Bangor",
            "Doc Name": "sample1.doc",
        },
    ]

    expected_result = (
        "AppId,Charity number ,Do you need to do any further feasibility"
        " work?,Project name,Doc"
        " Name\r\n9a8b6c00-e461-466c-acb3-2519621b3a38,Test,False,Save the"
        " humble pub in"
        " Bangor,sample1.doc\r\nde36ae35-9ef6-4dc5-a2bf-de9ee481c8af,Test,False,Save"
        " the humble pub in Bangor,sample1.doc\r\n"
    )

    result = generate_assessment_info_csv(test_data)

    assert result == expected_result
