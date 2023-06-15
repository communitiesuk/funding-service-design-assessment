from collections import defaultdict
from functools import wraps
from typing import Tuple

from app.assess.data import get_application_metadata
from app.assess.data import get_fund
from app.assess.helpers import get_application_id_from_request
from flask import abort
from flask import g

_UK_COUNTRIES = [
    "ENGLAND",
    "SCOTLAND",
    "WALES",
    "NORTHERNIRELAND",  # normalise locations
]

_HAS_DEVOLVED_AUTHORITY_VALIDATION = defaultdict(
    lambda *_: False,  # by default, no devolved authority validation
    {
        "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4": True,
        "COF": True,
    },  # a dict of fund_round_id: bool, this could eventually be moved to fund store
)


def _roles_and_countries(short_name) -> Tuple[set, set]:
    all_roles = set(r.upper() for r in g.user.roles)
    uk_countries = {f"{short_name}_{c}".upper() for c in _UK_COUNTRIES}
    return all_roles, uk_countries


def _get_valid_country_roles(short_name) -> bool:
    all_roles, uk_countries = _roles_and_countries(short_name)
    return all_roles.intersection(uk_countries)


def _has_at_least_one_uk_country(short_name) -> bool:
    return bool(_get_valid_country_roles(short_name))


# Eventually this function will be redundant, we could just add a boolean or something to the fund-store.
# If a fund supports devolved authorities, then we return True, else False (by default) (fund.has_devolved_authority) ?
def has_devolved_authority_validation(
    *, fund_id=None, short_name=None
) -> bool:
    return _HAS_DEVOLVED_AUTHORITY_VALIDATION[fund_id or short_name]


def has_relevant_country_role(country, short_name) -> bool:
    all_roles, _ = _roles_and_countries(short_name)
    return bool(all_roles.intersection({f"{short_name}_{country}".upper()}))


# will return all country roles the user has access to
# probably use for filtering database queries/altering stats?
def get_relevant_country_roles(short_name) -> set[str]:
    return _get_valid_country_roles(short_name)


def ensure_location_access(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        application_id = get_application_id_from_request()
        if not application_id:
            abort(404)

        application_metadata = get_application_metadata(application_id)
        if has_devolved_authority_validation(
            fund_id=application_metadata["fund_id"]
        ):
            if country := application_metadata.get(
                "location_json_blob", {}
            ).get("country"):
                # TODO(tferns): Normalise country i.e. Northern Ireland -> NORTHERNIRELAND
                short_name = get_fund(
                    application_metadata["fund_id"]
                ).short_name
                has_relevant_location_access = has_relevant_country_role(
                    country, short_name
                )
                if not has_relevant_location_access:
                    abort(403)

        return func(*args, **kwargs)

    return decorated_function
