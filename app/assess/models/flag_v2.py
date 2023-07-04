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
        """Maps the user_id with accounts metadata and update the flag class
        with user information
        """
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
