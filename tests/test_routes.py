import pytest
from unittest import mock
from config import Config


class TestRoutes:
    def test_route_landing(self, flask_test_client):
        with mock.patch(
            "app.assess.routes.get_application_overviews",
            return_value=[],
        ) as mock_get_application_overviews_func:
            response = flask_test_client.get("/assess/landing/")

            assert 200 == response.status_code, "Wrong status code on response"

            mock_get_application_overviews_func.assert_called_once_with(
                Config.COF_FUND_ID,
                Config.COF_ROUND2_ID,
                {
                    "search_term": "",
                    "search_in": "project_name,application_short_id",
                    "asset_type": "all",
                    "status": "all",
                },
            )

            assert (
                b"Assessor dashboard</p>" in response.data
            ), "Response does not contain expected heading"

    def test_route_landing_filter_status(self, flask_test_client):
        with mock.patch(
            "app.assess.routes.get_application_overviews",
            return_value=[],
        ) as mock_get_application_overviews_func:

            response = flask_test_client.get(
                "/assess/landing/", query_string={"status": "completed"}
            )

            assert 200 == response.status_code, "Wrong status code on response"

            mock_get_application_overviews_func.assert_called_once_with(
                Config.COF_FUND_ID,
                Config.COF_ROUND2_ID,
                {
                    "search_term": "",
                    "search_in": "project_name,application_short_id",
                    "asset_type": "all",
                    "status": "completed",
                },
            )

            assert (
                b"Assessor dashboard</p>" in response.data
            ), "Response does not contain expected heading"

    def test_route_landing_filter_asset_type(self, flask_test_client):
        with mock.patch(
            "app.assess.routes.get_application_overviews",
            return_value=[],
        ) as mock_get_application_overviews_func:

            response = flask_test_client.get(
                "/assess/landing/", query_string={"asset_type": "pub"}
            )

            assert 200 == response.status_code, "Wrong status code on response"

            mock_get_application_overviews_func.assert_called_once_with(
                Config.COF_FUND_ID,
                Config.COF_ROUND2_ID,
                {
                    "search_term": "",
                    "search_in": "project_name,application_short_id",
                    "asset_type": "pub",
                    "status": "all",
                },
            )

            assert (
                b"Assessor dashboard</p>" in response.data
            ), "Response does not contain expected heading"

    def test_route_landing_search_term(self, flask_test_client):
        with mock.patch(
            "app.assess.routes.get_application_overviews",
            return_value=[],
        ) as mock_get_application_overviews_func:

            response = flask_test_client.get(
                "/assess/landing/", query_string={"search_term": "hello"}
            )

            assert 200 == response.status_code, "Wrong status code on response"

            mock_get_application_overviews_func.assert_called_once_with(
                Config.COF_FUND_ID,
                Config.COF_ROUND2_ID,
                {
                    "search_term": "hello",
                    "search_in": "project_name,application_short_id",
                    "asset_type": "all",
                    "status": "all",
                },
            )

            assert (
                b"Assessor dashboard</p>" in response.data
            ), "Response does not contain expected heading"

    def test_route_landing_clear_filters(self, flask_test_client):
        with mock.patch(
            "app.assess.routes.get_application_overviews",
            return_value=[],
        ) as mock_get_application_overviews_func:

            response = flask_test_client.get(
                "/assess/landing/",
                query_string={
                    "clear_filters": "",
                    "search_term": "hello",
                    "asset_type": "cinema",
                    "status": "in-progress",
                },
            )

            assert 200 == response.status_code, "Wrong status code on response"

            mock_get_application_overviews_func.assert_called_once_with(
                Config.COF_FUND_ID,
                Config.COF_ROUND2_ID,
                {
                    "search_term": "",
                    "search_in": "project_name,application_short_id",
                    "asset_type": "all",
                    "status": "all",
                },
            )

            assert (
                b"Assessor dashboard</p>" in response.data
            ), "Response does not contain expected heading"

    @pytest.mark.parametrize("expected_strings", [b"general-information", b"activities", b"partnerships"])
    def test_route_sidebar(self, flask_test_client, expected_strings):

        response = flask_test_client.get("/assess/sub_criteria/1a2b3c4d/general-information")

        assert 200 == response.status_code, "Wrong status code on response"

        assert (
            expected_strings in response.data
        ), "Response does not contain expected heading"