from datetime import datetime

from pytz import timezone


def slash_separated_day_month_year(value: str):
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
    return parsed.strftime("%d/%m/%y")


def datetime_format(value, format):
    am_pm_format = "%p"
    formatted_time = datetime.strptime(value, "%Y-%m-%d %X").strftime(format)
    formatted_time = (
        formatted_time
        + datetime.strptime(value, "%Y-%m-%d %X")
        .strftime(am_pm_format)
        .lower()
    )
    return formatted_time


def utc_to_tz(value, tz="Europe/London"):
    utc_time = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    uk_time = utc_time.astimezone(timezone(tz))
    return uk_time.strftime("%Y-%m-%d %H:%M:%S")


def format_date(value, from_, to_):
    return datetime.strptime(value, from_).strftime(to_)


def datetime_format_24hr(value):
    return datetime.fromisoformat(value).strftime("%d/%m/%Y at %H:%M")


def remove_dashes_underscores_capitalize(s: str) -> str:
    return s.replace("-", " ").replace("_", " ").capitalize()


def format_address(address: str) -> list[str]:
    address_parts = address.split(", ")
    address_parts = [part for part in address_parts if part != "null"]
    return address_parts


def all_caps_to_human(word):
    if word:
        result = word.replace("_", " ")
        return result.capitalize()


def format_project_ref(value: str):
    secions = value.split("-")
    return secions[len(secions) - 1]


def utc_to_bst(value, tz="Europe/London"):
    dt_formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"]
    for dt_format in dt_formats:
        try:
            utc_time = datetime.strptime(value, dt_format)
            break
        except ValueError:
            pass
    else:
        raise ValueError("Invalid datetime format")

    uk_time = utc_time.astimezone(timezone(tz))
    return uk_time.strftime("%d/%m/%Y at %H:%M")
