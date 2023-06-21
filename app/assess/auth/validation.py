from collections import defaultdict
from functools import wraps
from typing import List
from typing import Sequence
from typing import Tuple

from app.assess.data import get_application_metadata
from app.assess.data import get_fund
from app.assess.helpers import get_application_id_from_request
from app.assess.helpers import get_fund_short_name_from_request
from flask import abort
from flask import g
from fsd_utils.authentication.decorators import login_required

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


def _get_roles_by_fund_short_name(
    short_name: str, roles: Sequence[str]
) -> list[str]:
    return [f"{short_name.upper()}_{role.upper()}" for role in roles]


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


def check_access_application_id(func=None, roles_required: List[str] = []):

    if func is None:
        return lambda f: check_access_application_id(
            func=f, roles_required=roles_required
        )

    @wraps(func)
    def decorated_function(*args, **kwargs):
        application_id = get_application_id_from_request()
        if not application_id:
            abort(404)

        application_metadata = get_application_metadata(application_id)
        short_name = get_fund(application_metadata["fund_id"]).short_name
        if not has_access_to_fund(short_name):
            abort(403)

        fund_roles_required = _get_roles_by_fund_short_name(
            short_name, roles_required
        )
        login_required_function = login_required(
            func, roles_required=fund_roles_required
        )

        if has_devolved_authority_validation(
            fund_id=application_metadata["fund_id"]
        ):
            if country := application_metadata.get(
                "location_json_blob", {}
            ).get("country"):
                if not has_relevant_country_role(
                    _normalise_country(country), short_name
                ):
                    abort(403)

        g.access_controller = AssessmentAccessController(short_name)
        return login_required_function(*args, **kwargs)

    return decorated_function


def check_access_fund_short_name(func=None, roles_required: List[str] = []):

    if func is None:
        return lambda f: check_access_fund_short_name(
            func=f, roles_required=roles_required
        )

    @wraps(func)
    def decorated_function(*args, **kwargs):
        short_name = get_fund_short_name_from_request()
        if not short_name:
            abort(404)

        fund_roles_required = _get_roles_by_fund_short_name(
            short_name, roles_required
        )
        login_required_function = login_required(
            func, roles_required=fund_roles_required
        )
        if not has_access_to_fund(short_name):
            abort(403)

        g.access_controller = AssessmentAccessController(short_name)
        return login_required_function(*args, **kwargs)

    return decorated_function


class AssessmentAccessController(object):
    def __init__(self, fund_short_name: str = None):
        self.fund_short_name = fund_short_name

    @property
    def is_lead_assessor(self):
        return f"{self.fund_short_name}_LEAD_ASSESSOR" in g.user.roles

    @property
    def is_assessor(self):
        return f"{self.fund_short_name}_ASSESSOR" in g.user.roles

    @property
    def is_commenter(self):
        return f"{self.fund_short_name}_COMMENTER" in g.user.roles

    @property
    def has_any_assessor_role(self):
        return self.is_lead_assessor or self.is_assessor
