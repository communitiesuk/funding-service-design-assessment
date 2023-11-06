import inspect
from dataclasses import dataclass
from enum import auto
from enum import Enum


class FlagType(Enum):
    STOPPED = auto()


@dataclass
class UpdatedFlags:
    allocation: str
    date_created: str
    id: str
    justification: str
    status: FlagType
    user_id: str

    @classmethod
    def process_flags(cls, flags_list) -> list[dict]:
        return [
            update
            for flag in flags_list
            if flag.latest_status.name != "RAISED"
            for update in flag.updates
            if update["status"].name == "STOPPED"
            or update["status"].name == "RESOLVED"
        ]

    @classmethod
    def from_dict(cls, flags_list: list[dict]):
        flags = cls.process_flags(flags_list)

        all_flags = [
            cls(
                **{
                    k: v
                    for k, v in d.items()
                    if k in inspect.signature(cls).parameters
                }
            )
            for d in flags
        ]
        return all_flags


def order_by_dates(lst: list[dict]) -> tuple[dict]:
    """Sort items by date_created"""
    return sorted(lst, key=lambda item: item.date_created, reverse=True)


def get_dates(all_flags):
    """Just to check the dates and delete it aftewards"""

    for flag in all_flags:
        print(flag.date_created)


def validate_class(obj, class_name: list):
    """Not sure we need this"""
    if obj.__class__.__name__ in class_name:
        return True
    return False
