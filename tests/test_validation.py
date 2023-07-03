import pytest
import werkzeug
from app.assess.auth.validation import _get_all_country_roles
from app.assess.auth.validation import _get_all_users_roles
from app.assess.auth.validation import _get_roles_by_fund_short_name
from app.assess.auth.validation import _normalise_country
from app.assess.auth.validation import check_access_application_id
from app.assess.auth.validation import check_access_fund_short_name
from app.assess.auth.validation import get_countries_from_roles
from app.assess.auth.validation import get_valid_country_roles
from app.assess.auth.validation import has_access_to_fund
from app.assess.auth.validation import has_devolved_authority_validation
from app.assess.auth.validation import has_relevant_country_role
from app.assess.models.fund import Fund


class _MockUser:
    def __init__(self, roles):
        self.roles = roles


class _MockGlobal:
    def __init__(self, roles=[]):
        self.user = _MockUser(roles)


@pytest.mark.parametrize(
    "country, expected",
    [
        ("England", "england"),
        ("Scotland", "scotland"),
        ("Wales", "wales"),
        ("NorthernIreland", "northernireland"),
        ("ni", "northernireland"),
        ("Northern Ireland", "northernireland"),
    ],
)
def test__normalise_country(country, expected):
    assert _normalise_country(country) == expected


def test__get_all_country_roles():
    _get_all_country_roles("COF") == {
        "cof_england",
        "cof_scotland",
        "cof_wales",
        "cof_northernireland",
    }


def test__get_all_users_roles(monkeypatch):
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(
            roles=[
                "COF_LEAD_ASSESSOR",
                "COF_ASSESSOR",
                "COF_COMMENTER",
                "COF_ENGLAND",
                "COF_SCOTLAND",
            ]
        ),
    )
    assert _get_all_users_roles() == {
        "cof_lead_assessor",
        "cof_assessor",
        "cof_commenter",
        "cof_england",
        "cof_scotland",
    }


def test_get_valid_country_roles(monkeypatch):
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(roles=["COF_ENGLAND", "COF_SCOTLAND"]),
    )
    valid_country_roles = get_valid_country_roles("COF")
    assert valid_country_roles == {
        "cof_england",
        "cof_scotland",
    }


@pytest.mark.parametrize(
    "roles, expected",
    [
        (
            {"cof_england", "cof_Scotland"},
            {"england", "scotland"},
        ),
        ({"cof_england"}, {"england"}),
        ({"cof_scotland"}, {"scotland"}),
        ({"cof_Scotland"}, {"scotland"}),
        ({"cof_England"}, {"england"}),
        ({"cof_invalid_country"}, set()),
        ({"cof_lead_assessor"}, set()),
        ({"nstf_scotland"}, set()),
        ({""}, set()),
    ],
)
def test_get_countries_from_roles(monkeypatch, roles, expected):
    monkeypatch.setattr(
        "app.assess.auth.validation.g", _MockGlobal(roles=roles)
    )
    countries = get_countries_from_roles("COF")
    assert countries == expected


def test_has_relevant_country_role(monkeypatch):
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(roles=["COF_ENGLAND"]),
    )
    assert has_relevant_country_role("ENGLAND", "COF") is True
    assert has_relevant_country_role("SCOTLAND", "COF") is False


@pytest.mark.parametrize(
    "short_name, expected",
    [
        ("cof", True),
        ("COF", True),
        ("NSTF", False),
        ("nstf", False),
    ],
)
def test_has_devolved_authority_validation_short_names(short_name, expected):
    assert has_devolved_authority_validation(short_name=short_name) == expected


@pytest.mark.parametrize(
    "fund_id, expected",
    [
        ("47aef2f5-3fcb-4d45-acb5-f0152b5f03c4", True),
        ("random_fund_id", False),
    ],
)
def test_has_devolved_authority_validation_ids(fund_id, expected):
    assert has_devolved_authority_validation(fund_id=fund_id) == expected


@pytest.mark.parametrize(
    "short_name, roles, expected",
    [
        ("cof", {"COF_COMMENTER", "COF_SCOTLAND"}, True),
        ("COF", {"NSTF_COMMENTER", "NSTF_SCOTLAND"}, False),
    ],
)
def test_has_access_to_fund(monkeypatch, short_name, roles, expected):
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(roles=roles),
    )
    assert has_access_to_fund(short_name) == expected


@check_access_application_id
def _dummy_function_check_access_application_id():
    ...


def test_check_access_application_id_throws_404_when_no_application_id(
    request_ctx,
):
    # GIVEN no application id in the request
    # WHEN the check_access_application_id decorator is applied to a function
    # THEN a 404 is thrown
    with pytest.raises(werkzeug.exceptions.NotFound):
        _dummy_function_check_access_application_id()


def test_check_access_application_id_cant_access_application_when_no_country_role(
    request_ctx, monkeypatch
):
    # GIVEN an English COF application/assessment record
    # WHEN the user has no COF_ENGLAND role
    # THEN the user cannot access the application
    monkeypatch.setattr(
        "app.assess.auth.validation.get_application_id_from_request",
        lambda: "00000000-0000-0000-0000-000000000000",
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.get_application_metadata",
        lambda _: {
            "location_json_blob": {"country": "England"},
            "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
        },
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.get_fund",
        lambda _: Fund.from_json(
            {
                "id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
                "short_name": "cof",
                "name": "...",
                "description": "...",
            }
        ),
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(
            roles=["COF_SCOTLAND", "COF_WALES", "COF_NORTHERNIRELAND"]
        ),
    )

    with pytest.raises(werkzeug.exceptions.Forbidden):
        _dummy_function_check_access_application_id()


def test_check_access_application_id_can_access_application_when_has_country_role(
    request_ctx, monkeypatch
):
    # GIVEN an English COF application/assessment record
    # WHEN the user has the COF_ENGLAND role
    # THEN the user can access the application

    # we're not testing the decorator here, so we can just mock it out
    monkeypatch.setattr(
        "app.assess.auth.validation.login_required",
        lambda *_, **__: lambda *_, **__: ...,
    )

    monkeypatch.setattr(
        "app.assess.auth.validation.get_application_id_from_request",
        lambda: "00000000-0000-0000-0000-000000000000",
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.get_application_metadata",
        lambda _: {
            "location_json_blob": {"country": "England"},
            "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
        },
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.get_fund",
        lambda _: Fund.from_json(
            {
                "id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
                "short_name": "cof",
                "name": "...",
                "description": "...",
            }
        ),
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(roles=["COF_ENGLAND"]),
    )

    _dummy_function_check_access_application_id()  # no fail means pass


def test_check_access_application_id_can_access_application_when_fund_has_no_devolved_authority_auth(
    request_ctx, monkeypatch
):
    # GIVEN an NSTF application/assessment record
    # WHEN the user doesn't have any country role
    # THEN the user can access the application
    # AS NSTF has no devolved authority validation

    # we're not testing the decorator here, so we can just mock it out
    monkeypatch.setattr(
        "app.assess.auth.validation.login_required",
        lambda *_, **__: lambda *_, **__: ...,
    )

    monkeypatch.setattr(
        "app.assess.auth.validation.get_application_id_from_request",
        lambda: "00000000-0000-0000-0000-000000000000",
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.get_application_metadata",
        lambda _: {
            "location_json_blob": {"country": "England"},
            "fund_id": "mock-nstf-fund-id",
        },
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.get_fund",
        lambda _: Fund.from_json(
            {
                "id": "mock-nstf-fund-id",
                "short_name": "nstf",
                "name": "...",
                "description": "...",
            }
        ),
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(roles=["NSTF_COMMENTER"]),
    )

    _dummy_function_check_access_application_id()  # no fail means pass


def test_check_access_application_id_cant_access_application_when_no_relevant_fund_role(
    request_ctx, monkeypatch
):
    # GIVEN an COF application/assessment record
    # WHEN the user has no COF role
    # THEN the user cannot access the application
    monkeypatch.setattr(
        "app.assess.auth.validation.get_application_id_from_request",
        lambda: "00000000-0000-0000-0000-000000000000",
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.get_application_metadata",
        lambda _: {
            "location_json_blob": {"country": "England"},
            "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
        },
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.get_fund",
        lambda _: Fund.from_json(
            {
                "id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
                "short_name": "cof",
                "name": "...",
                "description": "...",
            }
        ),
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(roles=["NSTF_COMMENTER"]),  # no COF role
    )

    with pytest.raises(werkzeug.exceptions.Forbidden):
        _dummy_function_check_access_application_id()


@check_access_fund_short_name
def _dummy_function_check_access_fund_short_name():
    ...


def test_check_access_fund_short_name_throws_404_when_no_fund_short_name(
    request_ctx,
):
    # GIVEN no fund short name
    # WHEN the decorator is applied
    # THEN a 404 is thrown
    with pytest.raises(werkzeug.exceptions.NotFound):
        _dummy_function_check_access_fund_short_name()


def test_check_access_fund_short_name_cant_access(request_ctx, monkeypatch):
    # GIVEN a COF fund short name page
    # WHEN the user has no COF role
    # THEN the user cannot the page
    monkeypatch.setattr(
        "app.assess.auth.validation.get_fund_short_name_from_request",
        lambda: "cof",
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(roles=["NSTF_COMMENTER"]),  # no COF role
    )

    with pytest.raises(werkzeug.exceptions.Forbidden):
        _dummy_function_check_access_fund_short_name()


def test_check_access_fund_short_name_can_access(request_ctx, monkeypatch):
    # GIVEN a COF fund short name page
    # WHEN the user has the COF role
    # THEN the user can access the page

    # we're not testing the decorator here, so we can just mock it out
    monkeypatch.setattr(
        "app.assess.auth.validation.login_required",
        lambda *_, **__: lambda *_, **__: ...,
    )

    monkeypatch.setattr(
        "app.assess.auth.validation.get_fund_short_name_from_request",
        lambda: "cof",
    )
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(roles=["COF_COMMENTER"]),
    )

    _dummy_function_check_access_fund_short_name()  # no fail means pass


def test__get_roles_by_fund_short_name():
    assert _get_roles_by_fund_short_name(
        "cof", ["lead_assessor", "COMMENTER"]
    ) == ["COF_LEAD_ASSESSOR", "COF_COMMENTER"]
