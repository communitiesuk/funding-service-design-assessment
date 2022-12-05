from datetime import datetime


def status_to_human(status: str):
    status_to_human_map = {
        "NOT_STARTED": "Not started",
        "IN_PROGRESS": "In progress",
        "SUBMITTED": "Submitted",
        "COMPLETED": "Completed",
    }
    return status_to_human_map[status]


def slash_separated_day_month_year(value: str):
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
    return parsed.strftime("%d/%m/%y")


def datetime_format(value):
    date_format = "%d %B %Y at %H:%M"
    am_pm_format = "%p"
    formatted_time = datetime.strptime(value, "%Y-%m-%d %X").strftime(
        date_format
    )
    formatted_time = (
        formatted_time
        + datetime.strptime(value, "%Y-%m-%d %X")
        .strftime(am_pm_format)
        .lower()
    )
    return formatted_time


def all_caps_to_human(word):
    if word:
        return word.capitalize()
