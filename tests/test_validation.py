import pytest
from app.assess.auth.validation import _roles_and_countries
from app.assess.auth.validation import get_countries_from_roles
from app.assess.auth.validation import get_relevant_country_roles
from app.assess.auth.validation import has_relevant_country_role
from app.assess.auth.validation import normalise_country


class _MockUser:
    def __init__(self, roles):
        self.roles = roles


class _MockGlobal:
    def __init__(self, roles=[]):
        self.user = _MockUser(roles)


def test__roles_and_countries(monkeypatch):
    monkeypatch.setattr("app.assess.auth.validation.g", _MockGlobal())
    _, uk_countries = _roles_and_countries("COF")
    assert uk_countries == {
        "cof_lead_assessor_england",
        "cof_lead_assessor_scotland",
        "cof_lead_assessor_wales",
        "cof_lead_assessor_northernireland",
        "cof_assessor_england",
        "cof_assessor_scotland",
        "cof_assessor_wales",
        "cof_assessor_northernireland",
        "cof_commenter_england",
        "cof_commenter_scotland",
        "cof_commenter_wales",
        "cof_commenter_northernireland",
    }


def test_has_relevant_country_role(monkeypatch):
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(roles=["COF_LEAD_ASSESSOR_ENGLAND"]),
    )
    assert has_relevant_country_role("ENGLAND", "COF") is True
    assert has_relevant_country_role("SCOTLAND", "COF") is False


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
def test_normalise_country(country, expected):
    assert normalise_country(country) == expected


def test_get_relevant_country_roles(monkeypatch):
    monkeypatch.setattr(
        "app.assess.auth.validation.g",
        _MockGlobal(
            roles=["COF_LEAD_ASSESSOR_ENGLAND", "COF_LEAD_ASSESSOR_SCOTLAND"]
        ),
    )
    relevant_country_roles = get_relevant_country_roles("COF")
    assert relevant_country_roles == {
        "cof_lead_assessor_england",
        "cof_lead_assessor_scotland",
    }


@pytest.mark.parametrize(
    "roles, expected",
    [
        (
            {"cof_lead_assessor_england", "cof_lead_assessor_Scotland"},
            {"england", "scotland"},
        ),
        ({"cof_lead_assessor_england"}, {"england"}),
        ({"cof_lead_assessor_scotland"}, {"scotland"}),
        ({"cof_lead_assessor_Scotland"}, {"scotland"}),
        ({"cof_lead_assessor_England"}, {"england"}),
        ({"cof_lead_assessor_invalid_country"}, set()),
        ({"cof_lead_assessor"}, set()),
        ({"nstf_lead_assessor_scotland"}, set()),
        ({""}, set()),
    ],
)
def test_get_countries_from_roles(monkeypatch, roles, expected):
    monkeypatch.setattr(
        "app.assess.auth.validation.g", _MockGlobal(roles=roles)
    )
    countries = get_countries_from_roles("COF")
    assert countries == expected
