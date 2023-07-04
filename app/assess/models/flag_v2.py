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
        self.latest_status = self.get_enum_status(self.latest_status)
        for item in self.updates:
            item["status"] = self.get_enum_status(item["status"])
            item["date_created"] = datetime.fromisoformat(
                item["date_created"]
            ).strftime("%Y-%m-%d %X")

        self.latest_user_id = (
            self.updates[-1]["user_id"] if self.updates else ""
        )
        self.date_created = (
            self.updates[0]["date_created"] if self.updates else ""
        )

    def get_enum_status(self, status):
        if isinstance(status, int):
            return FlagTypeV2(status)
        elif isinstance(status, str):
            return FlagTypeV2[status]
        return status

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
