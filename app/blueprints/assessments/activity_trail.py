import inspect
from dataclasses import dataclass
from enum import auto
from enum import Enum

from app.blueprints.services.data_services import get_bulk_accounts_dict


class FlagType(Enum):
    STOPPED = auto()


@dataclass
class BaseModel:
    @classmethod
    def from_list(cls, data_list: list[dict]):
        return [
            cls(
                **{
                    k: v
                    for k, v in d.items()
                    if k in inspect.signature(cls).parameters
                }
            )
            for d in data_list
        ]


@dataclass
class UpdatedFlags(BaseModel):
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
    def from_list(cls, flags_list: list[dict]):
        flags = cls.process_flags(flags_list)
        return super().from_list(flags)


@dataclass
class Comments(BaseModel):
    id: str
    comment: str
    date_created: str
    sub_criteria_id: str
    theme_id: str
    user_id: str
    full_name: str
    email_address: str
    highest_role: str
    email_address: str


@dataclass
class Scores(BaseModel):
    application_id: str
    date_created: str
    id: str
    justification: str
    score: int
    sub_criteria_id: str
    user_id: str


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


def extract_user_info(lst: list, state):
    if lst is None:
        return []
    user_list = []
    for item in lst:
        if isinstance(item, dict):
            user_id = item.get("user_id")
            if user_id is not None and user_id not in user_list:
                user_list.append(user_id)

    if user_list:
        account_list = get_bulk_accounts_dict(
            user_list,
            state.fund_short_name,
        )

        return account_list


def update_comment_with_user_info(lst: list, dct: dict):
    if lst is None:
        return []
    for item in lst:
        user_id = item.get("user_id")
        if user_id in dct:
            user_info = dct[user_id]
            item.update(user_info)
    return lst
