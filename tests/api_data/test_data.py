# flake8: noqa
# There is config for any linked information shared across the mock api queries
# General config
from dataclasses import dataclass

test_fund_id = "test-fund"
test_round_id = "test-round"
test_user_id_lead_assessor = "test_user_lead_assessor"
test_user_id_assessor = "test_user_assessor"
test_user_id_commenter = "test_user_commenter"
test_funding_requested = 5000.0

# application specific config
flagged_app_id = "flagged_app"
flagged_app = {
    "id": flagged_app_id,
    "workflow_status": "IN_PROGRESS",
    "project_name": "Project In prog and Res",
    "short_id": "INP",
    "flags_v2": [
        {
            "id": "1c5e8bea-f5ed-4b74-8823-e64fec27a7db",
            "latest_status": "RAISED",
            "latest_allocation": None,
            "application_id": flagged_app_id,
            "sections_to_flag": ["Test section"],
            "updates": [
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6a",
                    "user_id": test_user_id_lead_assessor,
                    "date_created": "2023-02-19 12:00:00",
                    "justification": "Test",
                    "status": "RAISED",
                    "allocation": None,
                }
            ],
        },
    ],
    "qa_complete": [],
    "is_qa_complete": False,
    "criteria_sub_criteria_name": "test_sub_criteria",
    "criteria_sub_criteria_id": "test_sub_criteria_id",
    "theme_id": "test_theme_id",
    "theme_name": "test_theme_name",
    "mock_field": {
        "answer": "Yes",
        "field_id": "JCACTy",
        "field_type": "yesNoField",
        "form_name": "community-engagement",
        "presentation_type": "text",
        "question": "Have you done any fundraising in the community?",
    },
}

resolved_app_id = "resolved_app"
resolved_app = {
    "id": resolved_app_id,
    "workflow_status": "IN_PROGRESS",
    "project_name": "Project In prog and Res",
    "short_id": "INP",
    "flags_v2": [
        {
            "id": "1c5e8bea-f5ed-4b74-8823-e64fec27a7dc",
            "latest_status": "RESOLVED",
            "latest_allocation": None,
            "application_id": resolved_app_id,
            "sections_to_flag": ["Test section"],
            "updates": [
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6a",
                    "user_id": test_user_id_lead_assessor,
                    "date_created": "2023-02-20 12:00:00",
                    "justification": "Test",
                    "status": "RAISED",
                    "allocation": None,
                },
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6a",
                    "user_id": test_user_id_lead_assessor,
                    "date_created": "2023-02-20 12:00:00",
                    "justification": "Test",
                    "status": "RESOLVED",
                    "allocation": None,
                },
            ],
        },
    ],
    "qa_complete": [],
    "is_qa_complete": False,
    "criteria_sub_criteria_name": "test_sub_criteria",
    "criteria_sub_criteria_id": "test_sub_criteria_id",
    "theme_id": "test_theme_id",
    "theme_name": "test_theme_name",
    "mock_field": {
        "answer": "Yes",
        "field_id": "JCACTy",
        "field_type": "yesNoField",
        "form_name": "community-engagement",
        "presentation_type": "text",
        "question": "Have you done any fundraising in the community?",
    },
}

stopped_app_id = "stopped_app"
stopped_app = {
    "id": stopped_app_id,
    "workflow_status": "IN_PROGRESS",
    "project_name": "Project In prog and Stop",
    "short_id": "FS",
    "asset_type": "gallery",
    "flags_v2": [
        {
            "id": "1c5e8bea-f5ed-4b74-8823-e64fec27a7bd",
            "latest_status": "STOPPED",
            "latest_allocation": None,
            "application_id": stopped_app_id,
            "sections_to_flag": ["Test section"],
            "updates": [
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6a",
                    "user_id": test_user_id_lead_assessor,
                    "date_created": "2023-02-20 12:00:00",
                    "justification": "Test",
                    "status": "STOPPED",
                    "allocation": None,
                }
            ],
        },
    ],
    "qa_complete": [],
    "is_qa_complete": False,
}

flagged_qa_completed_app_id = "flagged_qa_completed_app"
flagged_qa_completed_app = {
    "id": flagged_qa_completed_app_id,
    "workflow_status": "COMPLETED",
    "project_name": "Project Completed Flag and QA",
    "short_id": "FQAC",
    "flags_v2": [
        {
            "id": "1c5e8bea-f5ed-4b74-8823-e64fec27a7bd",
            "latest_status": "RAISED",
            "latest_allocation": None,
            "application_id": flagged_qa_completed_app_id,
            "justification": "Test",
            "sections_to_flag": ["Test section"],
            "updates": [
                {
                    "id": "316f607a-03b7-4592-b927-5021a28b7d6b",
                    "user_id": test_user_id_lead_assessor,
                    "date_created": "2023-02-20 12:00:00",
                    "justification": "Test",
                    "status": "RAISED",
                    "allocation": None,
                }
            ],
        },
    ],
    "qa_complete": [
        {
            "id": "416f607a-03b7-4592-b927-5021a28b7d6b",
            "application_id": flagged_qa_completed_app_id,
            "user_id": test_user_id_lead_assessor,
            "date_created": "2023-02-19 12:00:00",
        }
    ],
    "is_qa_complete": True,
}

# mock api call results
mock_api_results = {
    "fund_store/funds/{fund_id}": {
        "id": test_fund_id,
        "name": "Funding Service Design Unit Test Fund",
        "short_name": "TF",
        "description": "unit testing fund",
    },
    "fund_store/funds/NSTF": {
        "id": "NSTF",
        "name": "Night Shelter Test Fund",
        "short_name": "NSTF",
        "description": "unit testing fund",
    },
    "fund_store/funds/COF": {
        "id": "COF",
        "name": "Community Ownership Fund",
        "short_name": "COF",
        "description": "unit testing fund",
    },
    "fund_store/funds/{fund_id}/rounds/{round_id}": {
        "id": test_round_id,
        "fund_id": test_fund_id,
        "short_name": "TR",
        "title": "Test round",
        "assessment_criteria_weighting": [
            {"id": "crit1", "name": "Test criteria", "value": 1.0}
        ],
        "assessment_deadline": "2023-03-01T12:00:00",
        "deadline": "2022-12-01T12:00:00",
        "opens": "2022-10-01T12:00:00",
    },
    "assessment_store/application_overviews/{fund_id}/{round_id}?": [
        {
            "fund_id": test_fund_id,
            "round_id": test_round_id,
            "application_id": flagged_qa_completed_app_id,
            "asset_type": "gallery",
            "flags_v2": flagged_qa_completed_app["flags_v2"],
            "qa_complete": flagged_qa_completed_app["qa_complete"],
            "funding_amount_requested": test_funding_requested + 2000,
            "is_qa_complete": True,
            "language": "en",
            "location_json_blob": {
                "constituency": "test-constituency",
                "country": "England",
                "county": "test-county",
                "error": False,
                "postcode": "QQ12QQ",
                "region": "England",
            },
            "project_name": flagged_qa_completed_app["project_name"],
            "short_id": flagged_qa_completed_app["short_id"],
            "type_of_application": "COF",
            "workflow_status": flagged_qa_completed_app["workflow_status"],
        },
        {
            "fund_id": test_fund_id,
            "round_id": test_round_id,
            "application_id": stopped_app_id,
            "asset_type": stopped_app["asset_type"],
            "flags_v2": stopped_app["flags_v2"],
            "qa_complete": stopped_app["qa_complete"],
            "funding_amount_requested": test_funding_requested + 1000,
            "is_qa_complete": False,
            "language": "en",
            "location_json_blob": {
                "constituency": "test-constituency",
                "country": "Wales",
                "county": "test-county",
                "error": False,
                "postcode": "QQ12QQ",
                "region": "Wales",
            },
            "project_name": stopped_app["project_name"],
            "short_id": stopped_app["short_id"],
            "type_of_application": "COF",
            "workflow_status": stopped_app["workflow_status"],
        },
        {
            "fund_id": test_fund_id,
            "round_id": test_round_id,
            "application_id": resolved_app_id,
            "asset_type": "gallery",
            "flags_v2": resolved_app["flags_v2"],
            "qa_complete": resolved_app["qa_complete"],
            "funding_amount_requested": test_funding_requested,
            "is_qa_complete": False,
            "language": "en",
            "location_json_blob": {
                "constituency": "test-constituency",
                "country": "Scotland",
                "county": "test-county",
                "error": False,
                "postcode": "QQ12QQ",
                "region": "Scotland",
            },
            "project_name": resolved_app["project_name"],
            "short_id": resolved_app["short_id"],
            "type_of_application": "COF",
            "workflow_status": resolved_app["workflow_status"],
        },
    ],
    "assessment_store/application_overviews/{fund_id}/{round_id}?search_term=Project+S&search_in=project_name%2Cshort_id&asset_type=gallery&status=STOPPED": [
        {
            "fund_id": test_fund_id,
            "round_id": test_round_id,
            "application_id": stopped_app_id,
            "asset_type": stopped_app["asset_type"],
            "flags_v2": stopped_app["flags_v2"],
            "qa_complete": stopped_app["qa_complete"],
            "funding_amount_requested": test_funding_requested,
            "is_qa_complete": False,
            "language": "en",
            "location_json_blob": {
                "constituency": "test-constituency",
                "country": "England",
                "county": "test-county",
                "error": False,
                "postcode": "QQ12QQ",
                "region": "England",
            },
            "project_name": stopped_app["project_name"],
            "short_id": stopped_app["short_id"],
            "type_of_application": "COF",
            "workflow_status": stopped_app["workflow_status"],
        }
    ],
    "assessment_store/assessments/get-stats/{fund_id}/{round_id}": {
        "completed": 1,
        "assessing": 1,
        "not_started": 1,
        "qa_completed": 1,
        "stopped": 1,
        "flagged": 1,
        "total": 3,
    },
    "assessment_store/assessments/get-team-flag-stats/{fund_id}/{round_id}": [
        {"raised": 1, "resolved": 5, "stopped": 0, "team_name": "Team 1"}
    ],
    "assessment_store/progress": [],
    "assessment_store/application_overviews/stopped_app": {
        "criterias": [
            {
                "name": "string",
                "sub_criterias": [
                    {
                        "id": "string",
                        "name": "string",
                        "theme_count": 0,
                        "score": 0,
                        "status": "string",
                    }
                ],
                "total_criteria_score": 0,
                "total_criteria_score_possible": 0,
                "weighting": 0,
            }
        ],
        "sections": [
            {
                "name": "string",
                "sub_criterias": [{"id": "string", "name": "string"}],
            }
        ],
        "project_name": stopped_app["project_name"],
        "short_id": stopped_app["short_id"],
        "workflow_status": stopped_app["workflow_status"],
        "fund_id": test_fund_id,
        "round_id": test_round_id,
        "qa_complete": stopped_app["qa_complete"],
    },
    "assessment_store/application_overviews/resolved_app": {
        "criterias": [
            {
                "name": "string",
                "sub_criterias": [
                    {
                        "id": resolved_app["criteria_sub_criteria_id"],
                        "name": resolved_app["criteria_sub_criteria_name"],
                        "theme_count": 1,
                        "score": 4,
                        "status": "string",
                    }
                ],
                "total_criteria_score": 4,
                "total_criteria_score_possible": 5,
                "weighting": 0,
            }
        ],
        "sections": [
            {
                "name": "string",
                "sub_criterias": [{"id": "string", "name": "string"}],
            }
        ],
        "project_name": resolved_app["project_name"],
        "short_id": resolved_app["short_id"],
        "workflow_status": resolved_app["workflow_status"],
        "fund_id": test_fund_id,
        "round_id": test_round_id,
        "qa_complete": resolved_app["qa_complete"],
    },
    "assessment_store/application_overviews/flagged_app": {
        "criterias": [
            {
                "name": "string",
                "sub_criterias": [
                    {
                        "id": flagged_app["criteria_sub_criteria_id"],
                        "name": flagged_app["criteria_sub_criteria_name"],
                        "theme_count": 1,
                        "score": 4,
                        "status": "string",
                    }
                ],
                "total_criteria_score": 4,
                "total_criteria_score_possible": 5,
                "weighting": 0,
            }
        ],
        "sections": [
            {
                "name": "string",
                "sub_criterias": [{"id": "string", "name": "string"}],
            }
        ],
        "project_name": flagged_app["project_name"],
        "short_id": flagged_app["short_id"],
        "workflow_status": flagged_app["workflow_status"],
        "fund_id": test_fund_id,
        "round_id": test_round_id,
        "qa_complete": flagged_app["qa_complete"],
    },
    "assessment_store/application_overviews/flagged_qa_completed_app": {
        "criterias": [],
        "sections": [],
        "fund_id": test_fund_id,
        "round_id": test_round_id,
        "project_name": flagged_qa_completed_app["project_name"],
        "short_id": flagged_qa_completed_app["short_id"],
        "workflow_status": flagged_qa_completed_app["workflow_status"],
        "qa_complete": flagged_qa_completed_app["qa_complete"],
    },
    "assessment_store/sub_criteria_overview/banner_state/resolved_app": {
        "short_id": resolved_app["short_id"],
        "project_name": resolved_app["project_name"],
        "funding_amount_requested": test_funding_requested,
        "workflow_status": resolved_app["workflow_status"],
        "fund_id": test_fund_id,
    },
    "assessment_store/sub_criteria_overview/banner_state/stopped_app": {
        "short_id": stopped_app["short_id"],
        "project_name": stopped_app["project_name"],
        "funding_amount_requested": test_funding_requested,
        "workflow_status": stopped_app["workflow_status"],
        "fund_id": test_fund_id,
    },
    "assessment_store/sub_criteria_overview/banner_state/flagged_qa_completed_app": {
        "short_id": flagged_qa_completed_app["short_id"],
        "project_name": flagged_qa_completed_app["project_name"],
        "funding_amount_requested": test_funding_requested,
        "workflow_status": flagged_qa_completed_app["workflow_status"],
        "fund_id": test_fund_id,
    },
    "assessment_store/flag_data_v2?flag_id=flagged_app": flagged_app[
        "flags_v2"
    ][-1],
    "assessment_store/flag_data_v2?flag_id=resolved_app": resolved_app[
        "flags_v2"
    ][-1],
    "assessment_store/flag_data_v2?flag_id=stopped_app": stopped_app[
        "flags_v2"
    ][-1],
    "assessment_store/flag_data_v2?flag_id=flagged_qa_completed_app": flagged_qa_completed_app[
        "flags_v2"
    ][
        -1
    ],
    "assessment_store/flags_v2?application_id=flagged_app": flagged_app[
        "flags_v2"
    ],
    "assessment_store/flags_v2?application_id=resolved_app": resolved_app[
        "flags_v2"
    ],
    "assessment_store/flags_v2?application_id=stopped_app": stopped_app[
        "flags_v2"
    ],
    "assessment_store/flags_v2?application_id=flagged_qa_completed_app": flagged_qa_completed_app[
        "flags_v2"
    ],
    "assessment_store/qa_complete/flagged_app": {},
    "assessment_store/qa_complete/resolved_app": {},
    "assessment_store/qa_complete/stopped_app": {},
    "assessment_store/qa_complete/flagged_qa_completed_app": flagged_qa_completed_app[
        "qa_complete"
    ][
        0
    ],
    "account_store/bulk-accounts": {
        test_user_id_lead_assessor: {
            "user_id": test_user_id_lead_assessor,
            "full_name": "Lead User",
            "highest_role": "LEAD_ASSESSOR",
            "email_address": "lead@test.com",
        },
        test_user_id_commenter: {
            "user_id": test_user_id_commenter,
            "full_name": "Commenter User",
            "highest_role": "COMMENTER",
            "email_address": "commenter@test.com",
        },
        test_user_id_assessor: {
            "user_id": test_user_id_assessor,
            "full_name": "Assessor User",
            "highest_role": "ASSESSOR",
            "email_address": "assessor@test.com",
        },
    },
    f"assessment_store/sub_criteria_overview/{resolved_app_id}/{resolved_app['criteria_sub_criteria_id']}": {
        "id": resolved_app["criteria_sub_criteria_id"],
        "name": resolved_app["criteria_sub_criteria_name"],
        "is_scored": True,
        "fund_id": test_fund_id,
        "funding_amount_requested": test_funding_requested,
        "project_name": resolved_app["project_name"],
        "short_id": resolved_app["short_id"],
        "workflow_status": resolved_app["workflow_status"],
        "themes": [
            {
                "answers": [resolved_app["mock_field"]],
                "id": resolved_app["theme_id"],
                "name": resolved_app["theme_name"],
            }
        ],
    },
    f"assessment_store/sub_criteria_themes/{resolved_app_id}/{resolved_app['theme_id']}": [
        resolved_app["mock_field"]
    ],
    "assessment_store/comment?": [
        {
            "comment": "This is a comment",
            "user_id": test_user_id_lead_assessor,
            "date_created": "2022-12-08T08:00:01.748170",
            "theme_id": resolved_app["theme_id"],
        },
        {
            "comment": "You're missing some details",
            "user_id": test_user_id_lead_assessor,
            "date_created": "2022-10-27T08:00:02.748170",
            "theme_id": resolved_app["theme_id"],
        },
        {
            "comment": "Im a lead assessor",
            "user_id": test_user_id_lead_assessor,
            "date_created": "2022-10-27T08:00:03.748170",
            "theme_id": resolved_app["theme_id"],
        },
        {
            "comment": "Im an assessor",
            "user_id": test_user_id_assessor,
            "date_created": "2022-10-27T08:00:04.748170",
            "theme_id": resolved_app["theme_id"],
        },
        {
            "comment": "Im a commenter",
            "user_id": test_user_id_commenter,
            "date_created": "2022-10-27T08:00:05.748170",
            "theme_id": resolved_app["theme_id"],
        },
    ],
    "assessment_store/score?": [
        {
            "application_id": resolved_app_id,
            "date_created": "2022-12-08T15:45:54.664955",
            "id": "ba4ce3fb-6819-4f33-94ae-b830dc4c662b",
            "justification": "good",
            "score": 3,
            "sub_criteria_id": resolved_app["criteria_sub_criteria_id"],
            "user_id": test_user_id_lead_assessor,
        },
        {
            "application_id": resolved_app_id,
            "date_created": "2022-12-08T15:45:15.802821",
            "id": "a96513cd-b1f8-435d-81e9-d8b760c8bb7d",
            "justification": "better",
            "score": 4,
            "sub_criteria_id": resolved_app["criteria_sub_criteria_id"],
            "user_id": test_user_id_lead_assessor,
        },
    ],
    "assessment_store/applications/{application_id}": {
        "fund_id": "TF",
    },
    "/application/stopped_app/metadata": {
        "fund_id": test_fund_id,
        "round_id": test_round_id,
        "application_id": stopped_app_id,
        "asset_type": stopped_app["asset_type"],
        "flags_v2": stopped_app["flags_v2"],
        "qa_complete": stopped_app["qa_complete"],
        "funding_amount_requested": test_funding_requested + 1000,
        "is_qa_complete": False,
        "language": "en",
        "location_json_blob": {
            "constituency": "test-constituency",
            "country": "Wales",
            "county": "test-county",
            "error": False,
            "postcode": "QQ12QQ",
            "region": "Wales",
        },
        "project_name": stopped_app["project_name"],
        "short_id": stopped_app["short_id"],
        "type_of_application": "COF",
        "workflow_status": stopped_app["workflow_status"],
    },
}


@dataclass
class TestSanitiseData:
    tag: str = None
    style: str = None

    @property
    def input(self):
        if self.style:
            return {
                "answer": (
                    f"<{self.tag} style='list-style-type:{self.style};'>Example"
                    f" text <li>One</li>\n<li>Two</li></{self.tag}>"
                )
            }
        else:
            return {
                "answer": (
                    f"<{self.tag}>Example text"
                    f" <li>One</li>\n<li>Two</li></{self.tag}>"
                )
            }

    @property
    def response(self):
        if self.style:
            return {
                "answer": (
                    f"<{self.tag} class='list-type-{self.style}'"
                    f" style='list-style-type:{self.style};'>Example text"
                    f" <li>One</li>\n<li>Two</li></{self.tag}>"
                )
            }

        else:
            if self.tag == "p":
                return {
                    "answer": (
                        f"<{self.tag} class='govuk-body'>Example text"
                        f" <li>One</li>\n<li>Two</li></{self.tag}>"
                    )
                }
            if self.tag == "ul":
                return {
                    "answer": (
                        f"<{self.tag} class='govuk-list"
                        " govuk-list--bullet'>Example text"
                        f" <li>One</li>\n<li>Two</li></{self.tag}>"
                    )
                }
            if self.tag == "ol":
                return {
                    "answer": (
                        f"<{self.tag} class='govuk-list"
                        " govuk-list--number'>Example text"
                        f" <li>One</li>\n<li>Two</li></{self.tag}>"
                    )
                }
