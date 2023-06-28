ALL_VALUE = "ALL"

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
}

funding_types = {
    ALL_VALUE: "All",
    "both-revenue-and-capital": "Capital and revenue",
    "capital": "Capital",
    "revenue": "Revenue",
}


search_params_cof = {
    "search_term": "",
    "search_in": "project_name,short_id",
    "asset_type": ALL_VALUE,
    "status": ALL_VALUE,
}
search_params_nstf = {
    "search_term": "",
    "search_in": "organisation_name,short_id",
    "funding_type": ALL_VALUE,
    "status": ALL_VALUE,
}
