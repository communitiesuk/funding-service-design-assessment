import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict
from typing import List

from app.blueprints.services.models.flag import Flag
from app.blueprints.services.models.flag import FlagType
from config.display_value_mappings import assessment_statuses
from flask import request


def process_assessments_stats(application_overviews) -> Dict:
    num_completed = 0
    num_assessing = 0
    num_not_started = 0
    num_qa_completed = 0
    num_stopped = 0
    num_flagged = 0
    num_multiple_flagged = 0

    for assessment in application_overviews:
        status = determine_display_status(
            assessment["workflow_status"],
            assessment["flags"],
            assessment["is_qa_complete"],
        )
        if status == "Assessment complete":
            num_completed += 1
        elif status == "In progress":
            num_assessing += 1
        elif status == "Not started":
            num_not_started += 1
        elif status == "QA complete":
            num_qa_completed += 1
        elif status == "Stopped":
            num_stopped += 1
        elif status == "Flagged":
            num_flagged += 1
        elif status == "Multiple flags to resolve":
            num_multiple_flagged += 1

    stats = {
        "completed": num_completed,
        "assessing": num_assessing,
        "not_started": num_not_started,
        "qa_completed": num_qa_completed,
        "stopped": num_stopped,
        "flagged": num_flagged,
        "multiple_flagged": num_multiple_flagged,
        "total": len(application_overviews),
    }

    return stats


def determine_assessment_status(
    workflow_status: str, is_qa_complete: bool
) -> str:
    if is_qa_complete:
        assessment_status = "QA complete"
    else:
        assessment_status = assessment_statuses[workflow_status]

    return assessment_status


def is_flaggable(flag_status: str):
    return flag_status != "Stopped"


def determine_display_status(
    workflow_status: str, Flags: List[Flag], is_qa_complete: bool
) -> str:
    flag_status = determine_flag_status(Flags)
    if flag_status:
        display_status = flag_status
    elif is_qa_complete:
        display_status = "QA complete"
    else:
        display_status = assessment_statuses[workflow_status]

    return display_status


def determine_flag_status(Flags: List[Flag]) -> str:
    flag_status = ""
    flags_list = (
        [
            (Flag.from_dict(flag) if isinstance(flag, dict) else flag)
            for flag in Flags
        ]
        if Flags
        else []
    )
    all_latest_status = [flag.latest_status for flag in flags_list]

    if FlagType.STOPPED in all_latest_status:
        flag_status = "Stopped"
    elif all_latest_status.count(FlagType.RAISED) > 1:
        flag_status = "Multiple flags to resolve"
    elif all_latest_status.count(FlagType.RAISED) == 1:
        for flag in flags_list:
            if flag.latest_status == FlagType.RAISED:
                flag_status = (
                    ("Flagged for " + flag.latest_allocation)
                    if flag.latest_allocation
                    else "Flagged"
                )
    return flag_status


def match_search_params(search_params, request_args):
    show_clear_filters = False
    if "clear_filters" not in request_args:
        search_params.update(
            {
                k: v
                for k, v in request_args.items()
                if k in search_params and k != "countries"
            }
        )
        show_clear_filters = any(
            k in request_args for k in search_params if k != "countries"
        )
    return search_params, show_clear_filters


def get_ttl_hash(seconds=3600) -> int:
    return round(time.time() / seconds)


def get_value_from_request(parameter_names) -> str | None:
    for parameter_name in parameter_names:
        value = request.view_args.get(parameter_name) or request.args.get(
            parameter_name
        )
        if value:
            return value


@dataclass
class LocationData:
    """
    A class to represent location data.

    Attributes:
        locations: A list of location dictionaries.
        local_authorities: A list of local authority names.
    """

    locations: list
    local_authorities: list

    @classmethod
    def from_json_blob(cls, json_blob):
        locations = [
            location["location_json_blob"]
            for location in json_blob
            if location is not None
        ]
        local_authorities = [
            item["local_authority"] for item in json_blob if item is not None
        ]
        return cls(locations, local_authorities)

    def _create_ordered_dict(self, key):
        """
        Creates a sorted and ordered dictionary of location data for the specified key.
        Returns an ordered dictionary of location data.
        """

        def _item(item):
            return item if key == "local_authority" else item[key]

        def _data(key):
            return (
                self.local_authorities
                if key == "local_authority"
                else self.locations
            )

        sorted_items = sorted(
            [
                (_item(item), _item(item))
                for item in _data(key)
                if item is not None
            ]
        )

        return OrderedDict({"ALL": "All", **dict(sorted_items)})

    @property
    def countries(self):
        return self._create_ordered_dict("country")

    @property
    def regions(self):
        return self._create_ordered_dict("region")

    @property
    def _local_authorities(self):
        return self._create_ordered_dict("local_authority")
