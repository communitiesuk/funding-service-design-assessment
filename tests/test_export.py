from unittest import mock

from app.assess.data import get_files_for_application_upload_fields
from fsd_utils import extract_questions_and_answers_from_json_blob
from fsd_utils import generate_text_of_application
from tests.api_data.example_application_answers import test_application_answers
from tests.api_data.example_application_json_blob import (
    single_application_json_blob,
)


class TestExport:
    
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
