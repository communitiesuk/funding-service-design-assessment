import re
from collections import defaultdict
from functools import wraps
from typing import Tuple

from app.assess.data import get_application_metadata
from app.assess.data import get_fund
from app.assess.helpers import get_application_id_from_request
from app.assess.helpers import get_fund_short_name_from_request
from flask import abort
from flask import g

_UK_COUNTRIES = [
    "ENGLAND",
    "SCOTLAND",
    "WALES",
    "NORTHERNIRELAND",  # normalise locations
]

_ROLES = [
    "LEAD_ASSESSOR",
    "ASSESSOR",
    "COMMENTER",
]

_HAS_DEVOLVED_AUTHORITY_VALIDATION = defaultdict(
    lambda *_: False,  # by default, no devolved authority validation
    {
        "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4": True,
        "COF": True,
    },  # a dict of fund_round_id: bool, this could eventually be moved to fund store
)

_UK_COUNTRIES = [
    "ENGLAND",
    "SCOTLAND",
    "WALES",
    "NORTHERNIRELAND",  # normalise locations
]


def normalise_country(country: str):
    country = country.casefold()
    if country in {c.casefold() for c in _UK_COUNTRIES}:
        return country
    if country in ("ni", "northern ireland"):
        return "NORTHERNIRELAND".casefold()
    return country


def get_countries_from_roles(short_name) -> set[str]:
    all_roles, _ = _roles_and_countries(short_name)
    country_names = "|".join(_UK_COUNTRIES)
    regex_pattern = r".*({})$".format(country_names)
    regex = re.compile(regex_pattern, re.IGNORECASE)

    countries = set()
    for role in all_roles:
        match = re.match(regex, role)
        if match:
            countries.add(match.group(1).casefold())
    return countries


def _roles_and_countries(short_name) -> Tuple[set, set]:
    all_roles = set(r.casefold() for r in g.user.roles)
    uk_countries = {
        f"{short_name}_{r}_{c}".casefold()
        for r in _ROLES
        for c in _UK_COUNTRIES
    }
    return all_roles, uk_countries


def _get_valid_country_roles(short_name) -> bool:
    all_roles, uk_countries = _roles_and_countries(short_name)
    return all_roles.intersection(uk_countries)


def _get_invalid_country_roles(short_name) -> bool:
    all_roles, uk_countries = _roles_and_countries(short_name)
    return all_roles.difference(uk_countries)


def _has_at_least_one_uk_country(short_name) -> bool:
    return bool(_get_valid_country_roles(short_name))


# Eventually this function will be redundant, we could just add a boolean or something to the fund-store.
# If a fund supports devolved authorities, then we return True, else False (by default) (fund.has_devolved_authority) ?
def has_devolved_authority_validation(
    *, fund_id=None, short_name=None
) -> bool:
    return _HAS_DEVOLVED_AUTHORITY_VALIDATION[fund_id or short_name]


def has_access_to_fund(short_name: str) -> bool:
    all_roles, _ = _roles_and_countries(short_name)
    return any(role.startswith(short_name.casefold()) for role in all_roles)


def has_relevant_country_role(country, short_name) -> bool:
    all_roles, _ = _roles_and_countries(short_name)
    country_roles = {
        f"{short_name}_{role}_{country}".casefold() for role in _ROLES
    }
    return bool(all_roles.intersection(country_roles))


def get_relevant_country_roles(short_name) -> set[str]:
    return _get_valid_country_roles(short_name)


def get_irrelevant_country_roles(short_name) -> set[str]:
    return _get_invalid_country_roles(short_name)


def check_access_application_id(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        application_id = get_application_id_from_request()
        if not application_id:
            abort(404)

        application_metadata = get_application_metadata(application_id)
        if country := application_metadata.get("location_json_blob", {}).get(
            "country"
        ):
            normalised_country = normalise_country(country)
            short_name = get_fund(application_metadata["fund_id"]).short_name
            if has_access_to_fund(short_name):
                if not has_devolved_authority_validation(
                    fund_id=application_metadata["fund_id"]
                ):
                    return func(*args, **kwargs)
                if has_relevant_country_role(normalised_country, short_name):
                    return func(*args, **kwargs)
        abort(403)

    return decorated_function


def check_access_fund_short_name(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        short_name = get_fund_short_name_from_request()
        if not short_name:
            abort(404)

        if has_access_to_fund(short_name):
            return func(*args, **kwargs)
        abort(403)

    return decorated_function
