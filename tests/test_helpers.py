from collections import OrderedDict

import pytest
from app.blueprints.assessments.helpers import generate_assessment_info_csv
from app.blueprints.assessments.helpers import generate_csv_of_application
from app.blueprints.assessments.helpers import generate_maps_from_form_names
from app.blueprints.scoring.forms.scores_and_justifications import (
    OneToFiveScoreForm,
)
from app.blueprints.scoring.forms.scores_and_justifications import (
    ZeroToThreeScoreForm,
)
from app.blueprints.scoring.helpers import get_scoring_class
from app.blueprints.services.models.flag import Flag
from app.blueprints.services.models.fund import Fund
from app.blueprints.shared.helpers import determine_display_status
from app.blueprints.shared.helpers import is_flaggable
from app.blueprints.shared.helpers import process_assessments_stats
from werkzeug.exceptions import HTTPException

RAISED_FLAG = [
    Flag.from_dict(
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
    Flag.from_dict(
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
    Flag.from_dict(
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
    assert determine_display_status(workflow_status="IN_PROGRESS", Flags=None, is_qa_complete=False) == "In progress"
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
        {
            "AppId": "de36ae35-9ef6-4dc5-a2bf-de9ee481c8af",
            "Charity number ": "Test missing keys",
        },
    ]

    expected_result = (
        "AppId,Charity number ,Do you need to do any further feasibility"
        " work?,Project name,Doc"
        " Name\r\n9a8b6c00-e461-466c-acb3-2519621b3a38,Test,False,Save the"
        " humble pub in"
        " Bangor,sample1.doc\r\nde36ae35-9ef6-4dc5-a2bf-de9ee481c8af,Test,False,Save"
        " the humble pub in"
        " Bangor,sample1.doc\r\nde36ae35-9ef6-4dc5-a2bf-de9ee481c8af,Test"
        " missing keys,,,\r\n"
    )

    result = generate_assessment_info_csv(test_data)

    assert result == expected_result


def test_generate_maps_from_form_names_simple_case():
    data = [
        {
            "form_name": "form1",
            "title": "Title1",
            "path": "Path1",
            "children": None,
        },
        {
            "form_name": "form2",
            "title": "Title2",
            "path": "Path2",
            "children": None,
        },
    ]
    title_map, path_map = generate_maps_from_form_names(data)
    assert title_map == OrderedDict([("form1", "Title1"), ("form2", "Title2")])
    assert path_map == OrderedDict([("form1", "Path1"), ("form2", "Path2")])


def test_generate_maps_from_form_names_nested_case():
    data = [
        {
            "form_name": "form1",
            "title": "Title1",
            "path": "Path1",
            "children": [
                {
                    "form_name": "form1_1",
                    "title": "Title1_1",
                    "path": "Path1_1",
                    "children": None,
                },
                {
                    "form_name": "form1_2",
                    "title": "Title1_2",
                    "path": "Path1_2",
                    "children": None,
                },
            ],
        }
    ]
    title_map, path_map = generate_maps_from_form_names(data)
    expected_title = OrderedDict([("form1", "Title1"), ("form1_1", "Title1_1"), ("form1_2", "Title1_2")])
    expected_path = OrderedDict([("form1", "Path1"), ("form1_1", "Path1_1"), ("form1_2", "Path1_2")])
    assert title_map == expected_title
    assert path_map == expected_path


@pytest.mark.parametrize(
    "input_data, expected_response",
    [
        (
            [
                {
                    "workflow_status": "NOT_STARTED",
                    "flags": [],
                    "is_qa_complete": False,
                },
                {
                    "workflow_status": "NOT_STARTED",
                    "flags": [],
                    "is_qa_complete": True,
                },
            ],
            {"total": 2, "qa_completed": 1},
        )
    ],
)
def test_process_assessment_stats(input_data, expected_response):
    stats = process_assessments_stats(input_data)

    assert stats["total"] == expected_response["total"]
    assert stats["qa_completed"] == expected_response["qa_completed"]


@pytest.mark.parametrize(
    "returned_scoring_system, expect_exception, scoring_class",
    [
        ("OneToFive", False, OneToFiveScoreForm),
        ("ZeroToThree", False, ZeroToThreeScoreForm),
        ("NotScoringSystem", True, None),
    ],
)
def test_get_scoring_class(
    flask_test_client,
    mocker,
    returned_scoring_system,
    expect_exception,
    scoring_class,
):
    mocker.patch(
        "app.blueprints.scoring.helpers.get_scoring_system",
        return_value=returned_scoring_system,
    )

    if expect_exception:
        with pytest.raises(HTTPException) as excinfo:
            response = get_scoring_class("test_round_id")
        assert excinfo.value.code == 500
    else:
        response = get_scoring_class("test_round_id")
        assert response == scoring_class
