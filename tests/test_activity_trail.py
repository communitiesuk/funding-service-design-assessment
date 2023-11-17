import pytest
from app.blueprints.assessments.activity_trail import add_user_info
from app.blueprints.assessments.activity_trail import AssociatedTags
from app.blueprints.assessments.activity_trail import BaseModel
from app.blueprints.assessments.activity_trail import get_user_info
from flask import Flask


class TestActivityTrail:
    test_app = Flask("app")
    list_data_class = [type("AssociatedTags", (), {"user_id": "00000"})]
    list_data_dict = [{"user_id": "00000"}]
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
        "list_data, class_name",
        [(list_data_class, "AssociatedTags"), (list_data_dict, None)],
    )
    def test_get_user_info(self, list_data, class_name, mocker):
        state = type("AssessorTaskList", (), {"fund_short_name": "COF"})()

        # Patching the get_bulk_accounts_dict function
        mocker.patch(
            "app.blueprints.assessments.activity_trail.get_bulk_accounts_dict",
            return_value=self._accounts_list,
        )

        with self.test_app.app_context():
            result = get_user_info(list_data, state, class_name)
        assert result == self._accounts_list

    def test_add_user_info(self):
        with self.test_app.app_context():
            result = add_user_info(
                self.list_data_class, self._accounts_list, "AssociatedTags"
            )

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
