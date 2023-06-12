import pytest
from app.assess.helpers import determine_display_status
from app.assess.helpers import is_flaggable
from app.assess.models.flag import Flag


FLAGGED_FLAG = Flag.from_dict(
    {
        "application_id": "app_123",
        "date_created": "2023-01-01T00:00:00",
        "flag_type": "FLAGGED",
        "id": "flagid",
        "justification": "string",
        "sections_to_flag": ["community"],
        "user_id": "test@example.com",
        "is_qa_complete": False,
    }
)
RESOLVED_FLAG = Flag.from_dict(
    {
        "application_id": "app_123",
        "date_created": "2023-01-01T00:00:00",
        "flag_type": "RESOLVED",
        "id": "flagid",
        "justification": "string",
        "sections_to_flag": ["community"],
        "user_id": "test@example.com",
        "is_qa_complete": False,
    }
)
QA_COMPLETE_FLAG = Flag.from_dict(
    {
        "application_id": "app_123",
        "date_created": "2023-01-01T00:00:00",
        "flag_type": "QA_COMPLETED",
        "id": "flagid",
        "justification": "string",
        "sections_to_flag": ["community"],
        "user_id": "test@example.com",
        "is_qa_complete": True,
    }
)
STOPPED_FLAG = Flag.from_dict(
    {
        "application_id": "app_123",
        "date_created": "2023-01-01T00:00:00",
        "flag_type": "STOPPED",
        "id": "flagid",
        "justification": "string",
        "sections_to_flag": ["community"],
        "user_id": "test@example.com",
        "is_qa_complete": True,
    }
)


def test_determine_display_status():

    assert (
        determine_display_status(
            workflow_status="IN_PROGRESS", latest_flag=None
        )
        == "IN_PROGRESS"
    )
    assert (
        determine_display_status(
            workflow_status="IN_PROGRESS", latest_flag=FLAGGED_FLAG
        )
        == "FLAGGED"
    )
    assert (
        determine_display_status(
            workflow_status="IN_PROGRESS", latest_flag=RESOLVED_FLAG
        )
        == "IN_PROGRESS"
    )


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (RESOLVED_FLAG, True),
        (QA_COMPLETE_FLAG, True),
        (None, True),
        (FLAGGED_FLAG, False),
        (STOPPED_FLAG, False),
    ],
)
def test_is_flaggable(test_input, expected):
    assert is_flaggable(test_input) == expected
