import app
from app.assess.data import list_files_in_folder


def test_list_files_in_folder(monkeypatch):
    def mock_list_objects_v2(Bucket, Prefix):  # noqa
        return {
            "Contents": [
                {"Key": "app_id/form_name/path/name/filename1.png"},
                {"Key": "app_id/form_name/path/name/filename2.docx"},
                {"Key": "app_id/form_name/path/name/filename3.jpeg"},
                {"Key": "app_id/form_name/path/name/filename4.png"},
                {"Key": "app_id/form_name/path/name/filename5.pdf"},
                {"Key": "app_id/form_name/path/name/filename6.txt"},
                {"Key": "app_id/form_name/path/name/filename7.doc"},
                {"Key": "app_id/form_name/path/name/filename8.docx"},
                {"Key": "app_id/form_name/path/name/filename9.odt"},
                {"Key": "app_id/form_name/path/name/filename10.csv"},
                {"Key": "app_id/form_name/path/name/filename11.xls"},
                {"Key": "app_id/form_name/path/name/filename12.xlsx"},
                {"Key": "app_id/form_name/path/name/filename13.ods"},
            ]
        }

    monkeypatch.setattr(
        app.assess.data._S3_CLIENT, "list_objects_v2", mock_list_objects_v2
    )

    prefix = "app_id/form_name/path/name/"
    files = list_files_in_folder(prefix)

    assert files == [
        "form_name/path/name/filename1.png",
        "form_name/path/name/filename2.docx",
        "form_name/path/name/filename3.jpeg",
        "form_name/path/name/filename4.png",
        "form_name/path/name/filename5.pdf",
        "form_name/path/name/filename6.txt",
        "form_name/path/name/filename7.doc",
        "form_name/path/name/filename8.docx",
        "form_name/path/name/filename9.odt",
        "form_name/path/name/filename10.csv",
        "form_name/path/name/filename11.xls",
        "form_name/path/name/filename12.xlsx",
        "form_name/path/name/filename13.ods",
    ]


POST_PROCESSED_OVERVIEWS = {
    "none_country": [
        {
            "application_id": "app-123",
            "language": "en",
            "location_json_blob": {
                "error": True,
                "country": None,
            },
            "project_name": (
                "Save the beautiful community centre in Colchester"
            ),
        }
    ],
    "none_location_json_blob": [
        {
            "application_id": "app-123",
            "language": "en",
            "project_name": (
                "Save the beautiful community centre in Colchester"
            ),
        }
    ],
    "valid_location_data": [
        {
            "application_id": "app-123",
            "language": "en",
            "location_json_blob": {
                "error": False,
                "constituency": "Newport West",
                "country": "Wales",
                "county": "Newport",
                "postcode": "NP108QQ",
                "region": "Wales",
            },
            "project_name": "Restore the derelict museum in Newport",
        }
    ],
}
