from app.assess.views.filters import all_caps_to_human
from app.assess.views.filters import datetime_format


class TestFilters:
    def test_datetime(self):
        time_in = "2023-01-30 12:00:00"
        result = datetime_format(time_in)
        assert "30 January 2023 at 12:00pm" == result, "Wrong format returned"

    def test_caps_to_human(self):
        word_in = "HELLO WORLD"
        result = all_caps_to_human(word_in)
        assert "Hello world" == result, "Wrong format returned"
