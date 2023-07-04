import inspect
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


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
    latest_allocation: str
    application_id: str
    updates: list

    def __post_init__(self):
        if isinstance(self.latest_status, int):
            self.latest_status = FlagTypeV2(self.latest_status)
        for item in self.updates:
            item["status"] = FlagTypeV2(item["status"])
            item["date_created"] = datetime.fromisoformat(
                item["date_created"]
            ).strftime("%Y-%m-%d %X")

        self.latest_user_id = (
            self.updates[-1]["user_id"] if self.updates else ""
        )
        self.date_created = (
            self.updates[0]["date_created"] if self.updates else ""
        )

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

    @classmethod
    def from_list(cls, lst: list):
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
