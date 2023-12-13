import pytest
from app.blueprints.assessments.activity_trail import add_user_info
from app.blueprints.assessments.activity_trail import AssociatedTags
from app.blueprints.assessments.activity_trail import BaseModel
from app.blueprints.assessments.activity_trail import get_user_info
from app.blueprints.assessments.activity_trail import Scores
from app.blueprints.services.data_services import get_score_and_justification
from app.blueprints.services.data_services import get_sub_criteria
from app.blueprints.services.models.sub_criteria import SubCriteria
from flask import Flask


class TestActivityTrail:
    test_app = Flask("app")
    list_data_class = [type("AssociatedTags", (), {"user_id": "00000"})]
    list_data_dict = [{"user_id": "00000"}]
    state = type("AssessorTaskList", (), {"fund_short_name": "COF"})()
    _accounts_list = {
        "00000": {
            "full_name": "Development User",
            "email": "dev@example.com",
            "roles": ["COF_LEAD_ASSESSOR", "COF_ASSESSOR"],
            "email_address": "dev@example.com",
            "highest_role": "LEAD_ASSESSOR",
        }
    }

    @pytest.mark.parametrize(
        "list_data",
        [(list_data_class)],
    )
    def test_get_user_info(self, list_data, mocker):

        # Patching the get_bulk_accounts_dict function
        mocker.patch(
            "app.blueprints.assessments.activity_trail.get_bulk_accounts_dict",
            return_value=self._accounts_list,
        )

        with self.test_app.app_context():
            result = get_user_info(list_data, self.state)
        assert result == self._accounts_list

    def test_add_user_info(self, mocker):
        with self.test_app.app_context():
            mocker.patch(
                "app.blueprints.assessments.activity_trail.get_user_info",
                return_value=self._accounts_list,
            )
            result = add_user_info(self.list_data_class, self.state)

        expected_result = [
            AssociatedTags(
                application_id="e67851a3-a190-456e-b2fa-9f1f8a2732cb",
                tag_id="bdd16710-5d13-4d15-a9b3-2344bc1fcc75",
                value="Test General tag",
                user_id="00000",
                associated=True,
                purpose="GENERAL",
                created_at="2023-11-16 13:12:21.617459+00:00",
                full_name="Development User",
                email_address="dev@example.com",
                highest_role="LEAD_ASSESSOR",
                date_created="2023-11-16 13:12:21",
            ),
        ]

        for instance in result:
            assert instance.user_id == expected_result[0].user_id
            assert "dev@example.com" == expected_result[0].email_address
            assert "LEAD_ASSESSOR" == expected_result[0].highest_role
            assert "2023-11-16 13:12:21" == expected_result[0].date_created

    @pytest.mark.parametrize(
        "date_str, expected_date_format",
        [
            ("2023-11-16T13:26:25.686556", "2023-11-16 13:26:25"),
            ("2023-11-16 18:35:08.285688+00:00", "2023-11-16 18:35:08"),
            ("2023-11-16 19:01:04", "2023-11-16 19:01:04"),
        ],
    )
    def test_format_date(self, date_str, expected_date_format):
        with self.test_app.app_context():
            result = BaseModel._format_date(date_str)

        assert result == expected_date_format

    def test_sub_criteria_name_populated(self, mocker):
        mocker.patch(
            "tests.test_activity_trail.get_score_and_justification",
            return_value=[
                {
                    "application_id": "test-app",
                    "date_created": "2023-12-12T10:22:22.785229",
                    "id": "0cd3bc1a-5798-4cb3-aa0d-dadac3e65f57",
                    "justification": "ok",
                    "score": 2,
                    "sub_criteria_id": "engaging_the_ODP_community",
                    "user_id": "00000000-0000-0000-0000-000000000000",
                }
            ],
        )
        mocker.patch(
            "tests.test_activity_trail.get_sub_criteria",
            return_value=SubCriteria.from_filtered_dict(
                {
                    "fund_id": "f493d512-5eb4-11ee-8c99-0242ac120002",
                    "funding_amount_requested": 0.0,
                    "id": "engaging_the_ODP_community",
                    "is_scored": True,
                    "name": "Engaging the ODP community",
                    "project_name": (
                        "Rebuild the old community centre in Cardiff"
                    ),
                    "short_id": "DPIF-R2-XNIWEP",
                    "themes": [
                        {
                            "id": "engaging_the_ODP_community",
                            "name": "Engaging the ODP community",
                        }
                    ],
                    "workflow_status": "IN_PROGRESS",
                }
            ),
        )
        scores = get_score_and_justification(
            application_id="test-app", score_history=True
        )
        _ = [  # retrive sub_criteria name and populate it
            score.update(
                {
                    "sub_criteria_name": get_sub_criteria(
                        "test-app", score.get("sub_criteria_id")
                    ).name
                }
            )
            for score in scores
        ]
        all_scores = Scores.from_list(scores)

        assert len(all_scores) == 1
        assert all_scores[0].sub_criteria_name == "Engaging the ODP community"
