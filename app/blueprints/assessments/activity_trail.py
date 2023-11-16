import inspect
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import auto
from enum import Enum

from app.blueprints.services.data_services import get_bulk_accounts_dict
from app.blueprints.tagging.models.tag import AssociatedTag
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired


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
                    and k != "date_created"
                },
                date_created=cls._format_date(d.get("date_created")),
            )
            for d in data_list
        ]

    @staticmethod
    def _format_date(date_str):
        if date_str:
            try:
                return datetime.fromisoformat(date_str).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:
                # Handle the case where the date_str is not in ISO format
                return date_str
        return date_str


@dataclass
class AssociatedTags(AssociatedTag):
    full_name: str = ""
    email_address: str = ""
    highest_role: str = ""
    email_address: str = ""
    date_created: str = field(default="", metadata={"name": "created_at"})

    @classmethod
    def from_associated_tags_list(cls, associated_tags_list):
        return [
            cls(**asdict(tag), date_created=tag.created_at)
            for tag in associated_tags_list
        ]


@dataclass
class Flags(BaseModel):
    allocation: str
    date_created: str
    id: str
    justification: str
    status: FlagType
    user_id: str
    sections_to_flag: list = ""
    full_name: str = ""
    email_address: str = ""
    highest_role: str = ""
    email_address: str = ""

    @classmethod
    def process_flags(cls, flags_list) -> list[dict]:
        result = []

        for flag in flags_list:
            for update in flag.updates:
                if update.get("status").name == "RAISED":
                    sections_to_flag = flag.sections_to_flag

                    updated_update = {
                        **update,
                        "sections_to_flag": sections_to_flag,
                    }
                    result.append(updated_update)
                else:
                    result.append(update)
        return result

    @classmethod
    def from_list(cls, flags_list: list[dict]):
        flags = cls.process_flags(flags_list)
        return super().from_list(flags)


@dataclass
class Comments(BaseModel):
    id: str
    comment: str
    comment_type: str
    date_created: str
    sub_criteria_id: str
    theme_id: str
    user_id: str
    full_name: str
    email_address: str
    highest_role: str
    email_address: str

    @classmethod
    def process_comments(cls, comments_list) -> list[dict]:
        result = []

        for comment in comments_list:
            for update in comment.get("updates"):
                updated_update = {
                    **update,
                    "user_id": comment.get("user_id"),
                    "sub_criteria_id": comment.get("sub_criteria_id"),
                    "theme_id": comment.get("theme_id"),
                    "comment_type": comment.get("comment_type"),
                    "full_name": comment.get("full_name"),
                    "email_address": comment.get("email_address"),
                    "highest_role": comment.get("highest_role"),
                }
                result.append(updated_update)

        return result

    @classmethod
    def from_list(cls, comments_list: list[dict]):
        comments = cls.process_comments(comments_list)
        return super().from_list(comments)


@dataclass
class Scores(BaseModel):
    application_id: str
    date_created: str
    id: str
    justification: str
    score: int
    sub_criteria_id: str
    user_id: str
    full_name: str
    email_address: str
    highest_role: str
    email_address: str


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


def extract_user_info(list_data, state, class_name=None):
    if list_data is None:
        return []

    user_list = []
    for item in list_data:
        if isinstance(item, dict):
            user_id = item.get("user_id")
        elif class_name:
            user_id = item.user_id
        else:
            continue

        if user_id is not None and user_id not in user_list:
            user_list.append(user_id)

    if user_list:
        account_list = get_bulk_accounts_dict(
            user_list,
            state.fund_short_name,
        )

        return account_list
    else:
        return []


def _add_user_info(list_data, user_info, class_name=None):
    if list_data is None:
        return []

    for item in list_data:
        if isinstance(item, dict):
            user_id = item.get("user_id")
        elif class_name:
            user_id = item.user_id
        else:
            continue

        if user_id in user_info:
            user_data = user_info[user_id]
            if isinstance(item, dict):
                item.update(user_data)
            elif class_name:
                for key, value in user_data.items():
                    setattr(item, key, value)

    return list_data


class SearchForm(FlaskForm):
    search_term = StringField("Search", validators=[DataRequired()])
    # Define other fields if needed
    submit = SubmitField("Submit")
