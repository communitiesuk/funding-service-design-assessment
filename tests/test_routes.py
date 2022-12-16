from unittest import mock

import pytest
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
                    "search_in": "project_name,short_id",
                    "asset_type": "ALL",
                    "status": "ALL",
                },
            )

            assert (
                b"Team dashboard" in response.data
            ), "Response does not contain expected heading"

    def test_route_landing_filter_status(self, flask_test_client):
        with mock.patch(
            "app.assess.routes.get_application_overviews",
            return_value=[],
        ) as mock_get_application_overviews_func:
            response = flask_test_client.get(
                "/assess/landing/", query_string={"status": "QA_COMPLETE"}
            )

            assert 200 == response.status_code, "Wrong status code on response"

            mock_get_application_overviews_func.assert_called_once_with(
                Config.COF_FUND_ID,
                Config.COF_ROUND2_ID,
                {
                    "search_term": "",
                    "search_in": "project_name,short_id",
                    "asset_type": "ALL",
                    "status": "QA_COMPLETE",
                },
            )

            assert (
                b"Team dashboard" in response.data
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
                    "search_in": "project_name,short_id",
                    "asset_type": "pub",
                    "status": "ALL",
                },
            )

            assert (
                b"Team dashboard" in response.data
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
                    "search_in": "project_name,short_id",
                    "asset_type": "ALL",
                    "status": "ALL",
                },
            )

            assert (
                b"Team dashboard" in response.data
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
                    "search_in": "project_name,short_id",
                    "asset_type": "ALL",
                    "status": "ALL",
                },
            )

            assert (
                b"Team dashboard" in response.data
            ), "Response does not contain expected heading"

    @pytest.mark.parametrize(
        "expected_names",
        [b"Current score: 5", b"Rescore", b"Add rationale for this"],
    )
    def test_route_sub_criteria_scroing(
        self, flask_test_client, expected_names
    ):
        response = flask_test_client.get(
            "/assess/application_id/app_123/sub_criteria_id/1a2b3c4d?theme_id=score"  # noqa
        )

        assert 200 == response.status_code, "Wrong status code on response"

        assert (
            expected_names in response.data
        ), "Response does not contain expected id"

    @pytest.mark.parametrize(
        "expected_names",
        [b"General information", b"Applicant's response", b"Comments"],
    )
    def test_route_sub_criteria_non_scroing(
        self, flask_test_client, expected_names
    ):
        response = flask_test_client.get(
            "/assess/application_id/app_123/sub_criteria_id/1a2b3c4d?theme_id=general-information"  # noqa
        )

        assert 200 == response.status_code, "Wrong status code on response"

        assert (
            expected_names in response.data
        ), "Response does not contain expected id"

    @pytest.mark.parametrize(
        "expected_ids, expected_names",
        [
            (b"general-information", b"General information"),
            (b"activities", b"Activities"),
            (b"partnerships", b"Partnerships"),
        ],
    )
    def test_route_sub_criteria_side_bar(
        self, flask_test_client, expected_ids, expected_names
    ):
        response = flask_test_client.get(
            "/assess/application_id/app_123/sub_criteria_id/1a2b3c4d?theme_id=general-information"  # noqa
        )

        assert 200 == response.status_code, "Wrong status code on response"

        assert (
            expected_ids in response.data
        ), "Response does not contain expected id"
        assert (
            expected_names in response.data
        ), "Response does not contain expected name"
