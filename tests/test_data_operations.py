from app.assess.data import get_application_overviews
from app.assess.data import get_fund
from app.assess.data import get_round
from config.envs.default import DefaultConfig
from flask import Flask


class TestDataOperations:

    test_app = Flask("app")

    def test_get_application_overviews(self):

        with self.test_app.app_context():
            params = { "search_term":"" } 
            result = get_application_overviews(
                DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID, params
            )
        assert 3 == len(result), "wrong number of application overviews"

    def test_get_application_overviews_search_ref(self):

        with self.test_app.app_context():
            params = { "search_term":"fund-abc" } 
            result = get_application_overviews(
                DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID, params
            )
        assert 1 == len(result), "wrong number of application overviews"
     
    def test_get_application_overviews_search_project_name(self):

        with self.test_app.app_context():
            params = { "search_term":"Save the village" } 
            result = get_application_overviews(
                DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID, params
            )
        assert 1 == len(result), "wrong number of application overviews"

    def test_get_round(self, flask_test_client):

        with self.test_app.app_context():
            round = get_round(
                DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID
            )
        assert "Round 2 Window 2" == round.title, "Wrong round title"

    def test_get_fund(self):

        with self.test_app.app_context():
            fund = get_fund(DefaultConfig.COF_FUND_ID)
        assert "Community Ownership Fund" == fund.name, "Wrong fund title"
