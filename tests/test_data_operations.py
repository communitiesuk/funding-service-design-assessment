from app.assess.data import get_application_overviews
from app.assess.data import get_fund
from app.assess.data import get_round
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
