from app.assess.data import get_application_overviews
from app.assess.data import get_comments
from app.assess.data import get_fund
from app.assess.data import get_round
from flask import Flask
from tests.api_data.test_data import mock_api_results


class TestDataOperations:

    test_app = Flask("app")

    def test_get_fund(self, mocker):
        mock_fund_result = mock_api_results["fund_store/funds/{fund_id}"]
        get_data_mock = mocker.patch(
            "app.assess.data.get_data", return_value=mock_fund_result
        )
        arg = "test-fund"
        with self.test_app.app_context():
            fund = get_fund(arg)
        assert fund, "No fund returned"
        assert (
            "Funding Service Design Unit Test Fund" == fund.name
        ), "Wrong fund title"
        assert arg in get_data_mock.call_args.args[0]

    def test_get_round(self, mocker):
        mock_round_result = mock_api_results[
            "fund_store/funds/{fund_id}/rounds/{round_id}"
        ]
        get_data_mock = mocker.patch(
            "app.assess.data.get_data", return_value=mock_round_result
        )
        args = ("test-fund", "test-round")
        with self.test_app.app_context():
            round = get_round(*args)
        assert round, "No round returned"
        assert "Test round" == round.title, "Wrong round title"
        assert all(arg in get_data_mock.call_args.args[0] for arg in args)

    def test_get_application_overviews(self, mocker):
        mock_fund_result = mock_api_results[
            "assessment_store/application_overviews/{fund_id}/{round_id}?"
        ]
        get_data_mock = mocker.patch(
            "app.assess.data.get_data", return_value=mock_fund_result
        )

        with self.test_app.app_context():
            params = {
                "search_term": "",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "ALL",
            }
            args = ("test-fund", "test-round")
            result = get_application_overviews(*args, params)
        assert result, "No result returned"
        assert 3 == len(result), "wrong number of application overviews"
        assert all(arg in get_data_mock.call_args.args[0] for arg in args)

    def test_get_application_overviews_search_with_params(self, mocker):
        mock_overview_result = mock_api_results[
            "assessment_store/application_overviews/{fund_id}/{round_id}?"
            "search_term=Project+S&search_in=project_name%2Cshort_id&"
            "asset_type=gallery&status=STOPPED"
        ]
        get_data_mock = mocker.patch(
            "app.assess.data.get_data", return_value=mock_overview_result
        )

        with self.test_app.app_context():
            params = {
                "search_term": "Project S",
                "search_in": "project_name,short_id",
                "asset_type": "ALL",
                "status": "ALL",
            }
            args = ("test-fund", "test-round")
            result = get_application_overviews(*args, params)
        assert result, "No result returned"
        assert result[0]["short_id"] == "FS"
        assert result[0]["project_name"] == "Project In prog and Stop"
        assert 1 == len(result), "wrong number of application overviews"
        assert all(arg in get_data_mock.call_args.args[0] for arg in args)

    def test_get_comments(self, mocker):
        mock_comments_result = mock_api_results["assessment_store/comment?"]
        get_data_mock = mocker.patch(
            "app.assess.data.get_data", return_value=mock_comments_result
        )
        args = ("resolved_app", "test_sub_criteria_id", "test_theme_id")
        with self.test_app.app_context():
            comments = get_comments(*args)
        assert 5 == len(comments), "wrong number of comments"
        assert all(arg in get_data_mock.call_args.args[0] for arg in args)
