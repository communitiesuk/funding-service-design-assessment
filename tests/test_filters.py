from app.assess.views.filters import all_caps_to_human
from app.assess.views.filters import datetime_format
from app.assess.views.filters import slash_separated_day_month_year
from app.assess.views.filters import status_to_human


class TestFilters(object):
    def test_datetime(self):
        time_in = "2023-01-30 12:00:00"
        result = datetime_format(time_in, "%d %B %Y at %H:%M")
        assert "30 January 2023 at 12:00pm" == result, "Wrong format returned"

    def test_caps_to_human(self):
        word_in = "HELLO WORLD"
        result = all_caps_to_human(word_in)
        assert "Hello world" == result, "Wrong format returned"

    def test_status_to_human(self):
        status_in = "NOT_STARTED"
        result = status_to_human(status_in)
        assert "Not started" == result, "Wrong format returned"

    def test_slash_separated_day_month_year(self):
        date_in = "2023-01-30T12:00:00.500"
        result = slash_separated_day_month_year(date_in)
        assert "30/01/23" == result, "Wrong format returned"
