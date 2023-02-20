from unittest import mock
from unittest.mock import MagicMock

from app.assess.data import get_application_overviews
from app.assess.data import get_comments
from app.assess.data import get_file_names_for_application_upload_fields
from app.assess.data import get_fund
from app.assess.data import get_round
from app.assess.models.theme import Theme
from config.envs.default import DefaultConfig
from flask import Flask


class TestDataOperations:

    test_app = Flask("app")

    def test_get_application_overviews(self):

        with self.test_app.app_context():
            params = {
                "search_term": "",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "ALL",
            }
            result = get_application_overviews(
                DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID, params
            )
        assert result, "No result returned"
        assert 3 == len(result), "wrong number of application overviews"

    def test_get_application_overviews_search_ref(self):

        with self.test_app.app_context():
            params = {
                "search_term": "AJTRIB",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "ALL",
            }
            result = get_application_overviews(
                DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID, params
            )
        assert result, "No result returned"
        assert 1 == len(result), "wrong number of application overviews"

    def test_get_application_overviews_search_project_name(self):

        with self.test_app.app_context():
            params = {
                "search_term": "Save our village",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "ALL",
            }
            result = get_application_overviews(
                DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID, params
            )
        assert result, "No result returned"
        assert 1 == len(result), "wrong number of application overviews"

    def test_get_application_overviews_filter_status(self):

        with self.test_app.app_context():
            params = {
                "search_term": "",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "QA_READY",
            }
            result = get_application_overviews(
                DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID, params
            )
        assert result, "No result returned"
        assert 1 == len(result), "wrong number of application overviews"

    def test_get_application_overviews_filter_asset_type(self):

        with self.test_app.app_context():
            params = {
                "search_term": "",
                "search_in": "project_name,short_id",
                "asset_type": "pub",
                "status": "ALL",
            }
            result = get_application_overviews(
                DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID, params
            )
        assert result, "No result returned"
        assert 1 == len(result), "wrong number of application overviews"

    def test_get_round(self, flask_test_client):

        with self.test_app.app_context():
            round = get_round(
                DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID
            )
        assert round, "No round returned"
        assert "Round 2 Window 2" == round.title, "Wrong round title"

    def test_get_fund(self):

        with self.test_app.app_context():
            fund = get_fund(DefaultConfig.COF_FUND_ID)
        assert fund, "No fund returned"
        assert "Community Ownership Fund" == fund.name, "Wrong fund title"

    def test_get_comments(self):

        with self.test_app.app_context():
            themes = [
                Theme(id="general-information", name="General information"),
                Theme(id="activities", name="Activities"),
                Theme(id="partnerships", name="Partnerships"),
            ]
            comments = get_comments(
                "app_123", "1a2b3c4d", "general-information", themes
            )
        assert 3 == len(comments), "wrong number of comments"

    def test_get_file_names_for_application_upload_fields(self):
        application_id = "test_application_id"
        short_id = "ABCDEF"
        file_name = "file1.txt"
        expected_output = [
            (
                "file1.txt",
                "http://fsd/test_application_id/file1.txt",
            ),
            (
                "file1.txt",
                "http://fsd/test_application_id/file1.txt",
            ),
        ]

        with mock.patch("app.assess.data.resource") as mock_boto3_resource:

            # Create a mock S3 resource
            mock_s3 = MagicMock()
            mock_boto3_resource.return_value = mock_s3

            # Create a mock S3 Bucket
            mock_bucket = MagicMock()
            mock_s3.Bucket.return_value = mock_bucket

            mock_file1 = MagicMock(key="test_application_id/file1.txt")
            mock_file1.Object = lambda: MagicMock(
                metadata={"componentname": "ArVrka"}
            )
            mock_file2 = MagicMock(key="test_application_id/file1.txt")
            mock_file2.Object = lambda: MagicMock(
                metadata={"componentname": "EEBFao"}
            )

            mock_bucket.objects.filter.return_value = [mock_file1, mock_file2]

            with mock.patch("app.assess.data.url_for") as mock_url_for:
                mock_url_for.return_value = "http://fsd/{}/{}".format(
                    application_id, file_name
                )

                assert (
                    get_file_names_for_application_upload_fields(
                        application_id, short_id
                    )
                    == expected_output
                )
