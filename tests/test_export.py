from app.assess.helpers import extract_questions_and_answers_from_json_blob
from tests.api_data.test_data import single_application_json_blob


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
