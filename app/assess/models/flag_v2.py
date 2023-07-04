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
    user_name: str = ""
    user_email_address: str = ""
    user_highest_role: str = ""

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
                    if k in inspect.signature(cls).parameters
                    else getattr(cls(), k)
                    for k, v in d.items()
                }
            )
            for d in lst
        ]
        return all_flags

    @classmethod
    def update_user_details(cls, flags_list, account_list):
        for flag in flags_list:
            if flag.updates:
                for user in flag.updates:
                    user_id = user["user_id"]
                    if user_id in account_list:
                        user_details = account_list[user_id]
                        flag.user_name = user_details["full_name"]
                        flag.user_email_address = user_details["email_address"]
                        flag.user_highest_role = user_details["highest_role"]
        return flags_list
