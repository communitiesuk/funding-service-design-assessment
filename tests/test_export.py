from unittest import mock

from app.assess.data import get_files_for_application_upload_fields
from app.assess.helpers import extract_questions_and_answers_from_json_blob
from app.assess.helpers import generate_text_of_application
from tests.api_data.test_data import single_application_json_blob
from tests.api_data.test_data import test_application_answers


class TestExport:
    def test_extract_q_and_a(self):
        result = extract_questions_and_answers_from_json_blob(
            single_application_json_blob
        )
        assert (
            "sample1.doc"
            == result["upload-business-plan"]["Upload business plan"]
        )
        assert (
            "lots of surveys"
            == result["feasibility"][
                "Tell us about the feasibility studies you have carried out"
                " for your project"
            ]
        )
        assert (
            "No"
            == result["feasibility"][
                "Do you need to do any further feasibility work?"
            ]
        )
        assert (
            "Yes"
            == result["declarations"][
                "Confirm you have considered subsidy control"
                " and state aid implications for your project,"
                " and the information you have given us is"
                " correct"
            ]
        )

    def test_generate_text(self):
        result = generate_text_of_application(test_application_answers)
        assert "********* Community Ownership Fund" in result
        assert "Q) Capital funding" in result
        assert "A) 2300" in result

    def test_get_files_for_application_upload_fields(self):
        application_id = "dummy_id"
        short_id = "d_id"

        with mock.patch(
            "app.assess.data.url_for",
            return_value="dummy/path/to/file.dmp",
        ):
            ans = get_files_for_application_upload_fields(
                application_id,
                short_id,
                {"jsonb_blob": single_application_json_blob},
            )

        assert ans == [
            ("sample1.doc", "dummy/path/to/file.dmp"),
            ("awskey123123123123123/sample1.doc", "dummy/path/to/file.dmp"),
        ]
