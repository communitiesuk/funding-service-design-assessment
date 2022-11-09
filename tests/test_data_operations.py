from app.assess.data import get_application_overviews
from app.assess.data import get_round
from config.envs.default import DefaultConfig


class TestDataOperations:
    def test_get_local_application_overviews(self):
        result = get_application_overviews(
            DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID
        )
        assert 3 == len(result), "wrong number of application overviews"

    def test_get_round(self):
        round = get_round(
            DefaultConfig.COF_FUND_ID, DefaultConfig.COF_ROUND2_ID
        )
        assert "Round 2 Window 2" == round.title, "Wrong round title"
