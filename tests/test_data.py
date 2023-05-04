import app
from app.assess.data import list_files_in_folder


def test_list_files_in_folder(monkeypatch):
    def mock_list_objects_v2(Bucket, Prefix):  # noqa
        return {
            "Contents": [
                {"Key": "app_id/form_name/path/name/filename1.png"},
                {"Key": "app_id/form_name/path/name/filename2.docx"},
            ]
        }

    monkeypatch.setattr(
        app.assess.data.s3_client, "list_objects_v2", mock_list_objects_v2
    )

    prefix = "app_id/form_name/path/name/"
    files = list_files_in_folder(prefix)

    assert files == [
        "form_name/path/name/filename1.png",
        "form_name/path/name/filename2.docx",
    ]
