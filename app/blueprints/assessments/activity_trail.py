import inspect
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime

from app.blueprints.services.data_services import get_bulk_accounts_dict
from app.blueprints.services.models.assessor_task_list import AssessorTaskList
from app.blueprints.services.models.flag import FlagType
from app.blueprints.tagging.models.tag import AssociatedTag
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import StringField


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
                current_app.logger.info("Formatting date")
                return datetime.fromisoformat(date_str).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:
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
        """Change the  attribute 'created_at' to 'date_created'"""
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
        """
        Retrive all flags from updates & add sections_to_flag to RAISED flag.

        Args: flags_list (list): A list of flags.

        Returns:
            list[dict]: A list of dictionaries containing flags with additional attribute.
        """
        result = []

        for flag in flags_list:
            for update in flag.updates:
                if update.get("status").name == "RAISED":
                    sections_to_flag = flag.sections_to_flag

                    updated_update = {
                        **update,
                        "sections_to_flag": sections_to_flag,
                    }
                    current_app.logger.info(
                        "Adding flagged sections to RAISED flag"
                    )
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
    def process_comments(cls, comments_list: list) -> list[dict]:
        """
        Retrieve all comments from updates and add the following attributes to each comment:
        - "user_id"
        - "sub_criteria_id"
        - "theme_id"
        - "comment_type"
        - "full_name"
        - "email_address"
        - "highest_role"

        Args: comments_list (list): A list of comments.

        Returns:
            list[dict]: A list of dictionaries containing comments with additional attributes.
        """
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
                current_app.logger.info(
                    "Adding required information to comment"
                )
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


def get_user_info(
    list_data: list, state: AssessorTaskList, class_name=None
) -> dict:
    """Retrieves account information based on user data.

    Args:
        list_data: List of user data or a dictionary containing user information.
        state: Object representing the state with fund_short_name attribute.
        class_name (str, optional): Name of the class. Defaults to None.

    Returns:
        dict: A dictionary containing account information for unique user IDs retrieved from list_data.
    """

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
        current_app.logger.info("Retrieving account information")
        account_list = get_bulk_accounts_dict(
            user_list,
            state.fund_short_name,
        )
        return account_list
    else:
        current_app.logger.warning(
            "Could not retrieve the account information"
        )
        return []


def add_user_info(
    list_data: list, account_info: list, class_name=None
) -> list:
    """Add user information to a list of data.

    Parameters:
    - list_data: List containing user data.
    - account_info: Dictionary containing user information mapped by user IDs.
    - class_name (str, optional):
      - For dictionary items, it updates the dictionary with user information from account_info.
      - For class instances, it sets attributes matching user information from account_info.

    Returns:
    List containing user data with updated information."""

    if list_data is None:
        return []

    for item in list_data:
        if isinstance(item, dict):
            user_id = item.get("user_id")
        elif class_name:
            user_id = item.user_id
        else:
            continue

        if user_id in account_info:
            user_data = account_info[user_id]
            if isinstance(item, dict):
                current_app.logger.info("Adding account information to dict")
                item.update(user_data)
            elif class_name:
                current_app.logger.info(
                    f"Adding account information to class {class_name}"
                )
                for key, value in user_data.items():
                    setattr(item, key, value)
    return list_data


def order_by_dates(lst: list[dict]) -> tuple[dict]:
    """Sorts a list of items by 'date_created' in descending order"""

    return sorted(lst, key=lambda item: item.date_created, reverse=True)


def get_dates(all_flags):
    for flag in all_flags:
        print(flag.date_created)


class SearchForm(FlaskForm):
    search = StringField("Search")


class CheckboxForm(FlaskForm):
    all_activity = BooleanField("All activity", default=True)
    comments = BooleanField("Comments")
    assessment_status = BooleanField("Assessment status")
    score = BooleanField("Score")
    flag = BooleanField("Flags")
    tag = BooleanField("Tags")


def map_activities_classes_with_checkbox_filters(filters):
    filters = [f.replace(" ", "") for f in filters if f != "All activity"]
    _filters = []
    for filter in filters:
        if filter == "Score":
            _filters.append("Scores")
        if filter == "Tags":
            _filters.append("AssociatedTags")
        else:
            _filters.append(filter)

    return _filters


def filter_all_activities(
    all_activities: list, search_keyword: str = "", filters: list = None
):
    all_activities = order_by_dates(all_activities)
    filtered_classes = map_activities_classes_with_checkbox_filters(filters)

    if not search_keyword and not filtered_classes:
        return all_activities

    if search_keyword and filtered_classes:
        return [
            activity
            for activity in all_activities
            if any(
                search_keyword.lower() in str(attr).lower()
                for attr in asdict(activity).values()
            )
            and any(
                class_name.lower() == activity.__class__.__name__.lower()
                for class_name in filtered_classes
            )
        ]

    if not search_keyword and filters:
        return [
            activity
            for activity in all_activities
            if any(
                class_name.lower() == activity.__class__.__name__.lower()
                for class_name in filtered_classes
            )
        ]

    if search_keyword and not filtered_classes:
        return [
            activity
            for activity in all_activities
            if any(
                search_keyword.lower() in str(attr).lower()
                for attr in asdict(activity).values()
            )
        ]

    else:
        return all_activities
