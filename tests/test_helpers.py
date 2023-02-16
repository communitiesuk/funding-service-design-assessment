from app.assess.helpers import determine_display_status
from app.assess.models.flag import Flag


def test_determine_display_status():
    flagged_flag = Flag.from_dict(
        {
            "application_id": "app_123",
            "date_created": "2023-01-01T00:00:00",
            "flag_type": "FLAGGED",
            "id": "flagid",
            "justification": "string",
            "section_to_flag": "community",
            "user_id": "test@example.com",
            "is_qa_complete": True,
        }
    )
    resolved_flag = Flag.from_dict(
        {
            "application_id": "app_123",
            "date_created": "2023-01-01T00:00:00",
            "flag_type": "RESOLVED",
            "id": "flagid",
            "justification": "string",
            "section_to_flag": "community",
            "user_id": "test@example.com",
            "is_qa_complete": True,
        }
    )

    assert (
        determine_display_status(
            workflow_status="IN_PROGRESS", latest_flag=None
        )
        == "IN_PROGRESS"
    )
    assert (
        determine_display_status(
            workflow_status="IN_PROGRESS", latest_flag=flagged_flag
        )
        == "FLAGGED"
    )
    assert (
        determine_display_status(
            workflow_status="IN_PROGRESS", latest_flag=resolved_flag
        )
        == "IN_PROGRESS"
    )
