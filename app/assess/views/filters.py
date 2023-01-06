from datetime import datetime


def status_to_human(status: str):
    status_to_human_map = {
        "NOT_STARTED": "Not Started",
        "IN_PROGRESS": "In Progress",
        "SUBMITTED": "Submitted",
        "COMPLETED": "Completed",
        "FLAGGED": "Flagged",
    }
    return status_to_human_map[status]


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
