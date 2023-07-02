import inspect
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# TODO : Need to rework this module once old rounds are migrated to use flags_v2
class FlagTypeV2(Enum):
    RAISED = 0
    STOPPED = 1
    QA_COMPLETED = 2
    RESOLVED = 3


@dataclass()
class FlagV2:
    id: str
    sections_to_flag: list
    latest_status: FlagTypeV2 | str
    application_id: str
    updates: list

    def __post_init__(self):
        if self.latest_status:
            self.latest_status = FlagTypeV2[self.latest_status]
        for item in self.updates:
            item["date_created"] = datetime.fromisoformat(
                item["date_created"]
            ).strftime("%Y-%m-%d %X")

    @classmethod
    def from_dict(cls, d: dict):
        # Filter unknown fields from JSON dictionary
        return cls(
            **{
                k: v
                for k, v in d.items()
                if k in inspect.signature(cls).parameters
            }
        )


# TODO: Refactor below class after assessment-store schema changes for multiple flags
@dataclass()
class Flags:
    id: str
    # justification: str
    sections_to_flag: str
    status: FlagTypeV2 | str
    application_id: str
    # user_id: str
    updates: list
    # is_qa_complete: bool = False
    allocation: str

    def __post_init__(self):
        # TODO: Uncomment below code after Enum types are upodated with ESCALATED & RAISED
        # in assessment-store and in above class `FlagType`

        if self.flag_type:
            self.flag_type = FlagTypeV2[self.flag_type]

        for item in self.updates:
            item["date_created"] = datetime.fromisoformat(
                item["date_created"]
            ).strftime("%Y-%m-%d %X")

    @classmethod
    def from_dict(cls, lst: list):
        all_flags = [
            cls(
                **{
                    k: v
                    for k, v in d.items()
                    if k in inspect.signature(cls).parameters
                }
            )
            for d in lst
        ]
        return all_flags
