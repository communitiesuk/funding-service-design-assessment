from collections import namedtuple

ALL_VALUE = "ALL"
ON_VALUE = "ON"
OFF_VALUE = "OFF"

asset_types = {
    ALL_VALUE: "All",
    "community-centre": "Community centre",
    "cinema": "Cinema",
    "gallery": "Gallery",
    "museum": "Museum",
    "music-venue": "Music venue",
    "park": "Park",
    "post-office": "Post office",
    "pub": "Pub",
    "shop": "Shop",
    "sporting": "Sporting leisure facility",
    "theatre": "Theatre",
    "other": "Other",
}

assessment_statuses = {
    ALL_VALUE: "All",
    "NOT_STARTED": "Not started",
    "IN_PROGRESS": "In progress",
    "COMPLETED": "Assessment complete",
    "QA_COMPLETED": "QA complete",
    "FLAGGED": "Flagged",
    "STOPPED": "Stopped",
    "MULTIPLE_FLAGS": "Multiple flags to resolve",
}

funding_types = {
    ALL_VALUE: "All",
    "both-revenue-and-capital": "Capital and revenue",
    "capital": "Capital",
    "revenue": "Revenue",
}

cohort = {
    ALL_VALUE: "All",
    "ukrainian-schemes": "Ukraine",
    "hong-kong-british-nationals": "Hong Kong",
    "afghan-citizens-resettlement-scheme": "Afghanistan",
}

search_params_cof = {
    "search_term": "",
    "search_in": "project_name,short_id",
    "asset_type": ALL_VALUE,
    "status": ALL_VALUE,
    "filter_by_tag": ALL_VALUE,
    "country": ALL_VALUE,
    "region": ALL_VALUE,
    "local_authority": ALL_VALUE,
}
search_params_nstf = {
    "search_term": "",
    "search_in": "organisation_name,short_id",
    "funding_type": ALL_VALUE,
    "status": ALL_VALUE,
    "filter_by_tag": ALL_VALUE,
    "country": ALL_VALUE,
    "region": ALL_VALUE,
    "local_authority": ALL_VALUE,
}
search_params_cyp = {
    "search_term": "",
    "search_in": "organisation_name,short_id",
    "cohort": ALL_VALUE,
    "status": ALL_VALUE,
    "filter_by_tag": ALL_VALUE,
    "country": ALL_VALUE,
    "region": ALL_VALUE,
    "local_authority": ALL_VALUE,
}

search_params_dpif = {
    "search_term": "",
    "search_in": "value",
    "status": ALL_VALUE,
    "filter_by_tag": ALL_VALUE,
}

search_params_tag = {
    "search_term": "",
    "search_in": "value",
    "tag_purpose": ALL_VALUE,
    "tag_status": True,
}

LandingFilters = namedtuple(
    "LandingFilters", ["filter_status", "filter_fund_type", "filter_fund_name"]
)
landing_filters = LandingFilters(
    filter_status=ALL_VALUE, filter_fund_type=ALL_VALUE, filter_fund_name=""
)
