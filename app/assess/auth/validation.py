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
        "cof": True,
    },  # a dict of fund_round_id: bool, this could eventually be moved to fund store
)

_UK_COUNTRIES = [
    "ENGLAND",
    "SCOTLAND",
    "WALES",
    "NORTHERNIRELAND",  # normalise locations
]


def _normalise_country(country: str):
    country = country.casefold()
    if country in {c.casefold() for c in _UK_COUNTRIES}:
        return country
    if country in ("ni", "northern ireland"):
        return "NORTHERNIRELAND".casefold()
    return country


def _get_all_country_roles(short_name: str) -> Tuple[set, set]:
    return {f"{short_name}_{c}".casefold() for c in _UK_COUNTRIES}


def _get_all_users_roles() -> Tuple[set, set]:
    return set(r.casefold() for r in g.user.roles)


def get_valid_country_roles(short_name) -> bool:
    all_roles = _get_all_users_roles()
    country_roles = _get_all_country_roles(short_name)
    return all_roles.intersection(country_roles)


def get_countries_from_roles(short_name) -> set[str]:
    valid_country_roles = get_valid_country_roles(short_name)
    partitioned_country_roles = [
        vcr.partition("_") for vcr in valid_country_roles
    ]
    return {country for _, _, country in partitioned_country_roles}


def has_relevant_country_role(country: str, short_name: str) -> bool:
    all_roles = _get_all_users_roles()
    country_roles = {f"{short_name}_{country}".casefold()}
    return bool(all_roles.intersection(country_roles))


def has_devolved_authority_validation(
    *, fund_id=None, short_name=None
) -> bool:
    identifier = fund_id or short_name
    if not identifier:
        return False
    identifier = identifier.casefold()
    return _HAS_DEVOLVED_AUTHORITY_VALIDATION[identifier]


def has_access_to_fund(short_name: str) -> bool:
    all_roles = _get_all_users_roles()
    return any(role.startswith(short_name.casefold()) for role in all_roles)


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
            normalised_country = _normalise_country(country)
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
