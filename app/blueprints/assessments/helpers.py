import csv
from collections import OrderedDict
from io import StringIO
from typing import Dict
from typing import List
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from flask import Response
from flask import url_for
from fsd_utils import NotifyConstants
from fsd_utils.mapping.application.application_utils import format_answer
from fsd_utils.mapping.application.application_utils import simplify_title

from app.blueprints.assessments.models.common import Option
from app.blueprints.assessments.models.common import OptionGroup
from app.blueprints.services.aws import generate_url
from app.blueprints.services.aws import list_files_by_prefix
from app.blueprints.services.data_services import get_tag_types
from app.blueprints.services.models.flag import FlagType
from app.blueprints.services.models.fund import Fund
from app.blueprints.shared.helpers import determine_display_status
from app.blueprints.tagging.models.tag import AssociatedTag
from config import Config
from config.display_value_mappings import assessment_statuses


def get_team_flag_stats(application_overviews) -> List[Dict]:
    def create_team_dict(team_name):
        return {
            "team_name": team_name,
            "raised": 0,
            "resolved": 0,
            "stopped": 0,
        }

    team_flag_stats = []

    for assessment in application_overviews:
        for flag in assessment.get("flags", []):
            latest_status = flag.get("latest_status")
            allocated_team = flag.get("latest_allocation")

            if allocated_team not in [team["team_name"] for team in team_flag_stats]:
                team_flag_stats.append(create_team_dict(allocated_team))

            for team in team_flag_stats:
                if team["team_name"] == allocated_team:
                    if latest_status == FlagType.RAISED.value:
                        team["raised"] += 1
                    elif latest_status == FlagType.STOPPED.value:
                        team["stopped"] += 1
                    elif latest_status == FlagType.RESOLVED.value:
                        team["resolved"] += 1

    return team_flag_stats


def generate_maps_from_form_names(
    data,
):
    form_name_to_title = OrderedDict()
    form_name_to_path = OrderedDict()

    for item in data:
        if item["form_name"]:
            form_name_to_title[item["form_name"]] = item["title"]
            form_name_to_path[item["form_name"]] = item["path"]

        if item["children"]:
            (
                child_form_name_to_title,
                child_form_name_to_path,
            ) = generate_maps_from_form_names(item["children"])
            form_name_to_title.update(child_form_name_to_title)
            form_name_to_path.update(child_form_name_to_path)

    return form_name_to_title, form_name_to_path


def set_application_status_in_overview(application_overviews):
    """Add the 'application_status' key and return the modified list of application overviews."""
    for overview in application_overviews:
        display_status = determine_display_status(
            overview["workflow_status"],
            overview["flags"],
            overview["is_qa_complete"],
        )
        status = ""
        for key, val in assessment_statuses.items():
            if val == display_status:
                status = key
                break
        if not status:
            status = display_status
        overview["application_status"] = status

    return application_overviews


def get_tag_map_and_tag_options(fund_round_tags, post_processed_overviews):
    tag_types = get_tag_types()
    tag_option_groups = [
        OptionGroup(
            label=", ".join(p.capitalize() for p in purposes),
            options=sorted(
                [
                    Option(value=tag.id, text_content=tag.value)
                    for tag in fund_round_tags
                    if tag.type_id
                    in {
                        tag_type.id
                        for tag_type in tag_types
                        if tag_type.purpose in purposes
                    }
                ],
                key=lambda option: option.text_content,
            ),
        )
        for purposes in Config.TAGGING_FILTER_CONFIG
    ]
    tags_in_application_map = {}
    for overview in post_processed_overviews:
        tags_in_application_map[overview["application_id"]] = (
            [
                AssociatedTag(
                    application_id=overview["application_id"],
                    tag_id=item["tag"]["id"],
                    value=item["tag"]["value"],
                    user_id=item["user_id"],
                    associated=item["associated"],
                    purpose=item["tag"]["tag_type"]["purpose"],
                )
                for item in overview["tag_associations"]
                if item["associated"] is True and item["tag"]["active"] is True
            ]
            if overview["tag_associations"]
            else None
        )

    return tags_in_application_map, tag_option_groups


def generate_csv_of_application(
    q_and_a: dict, fund: Fund, application_json, fund_round_name=None
):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fund", fund_round_name, fund.id])
    writer.writerow(
        [
            "Application",
            application_json["short_id"],
            application_json["application_id"],
        ]
    )
    writer.writerow(["Section", "Question", "Answer"])
    for section_name, values in q_and_a.items():
        section_title = simplify_title(section_name, remove_text=["cof", "ns"])
        section_title = " ".join(section_title).capitalize()
        for questions, answers in values.items():
            if answers and isinstance(answers, str) and answers.startswith("- "):
                answers = f"'{answers}"

            if not answers:
                answers = "Not provided"

            writer.writerow([section_title, questions, format_answer(answers)])
    return output.getvalue()


def generate_assessment_info_csv(data: dict):
    output = StringIO()
    headers = list(
        OrderedDict.fromkeys(
            key
            for d in data
            for key in d.keys()
            if key not in exclude_header(["COF-EOI"])
        )
    )
    csv_writer = csv.writer(output)

    if len(data) == 0:
        return output.getvalue()

    csv_writer.writerow(headers)

    for data_entry in data:
        rows = [data_entry.get(header, "") for header in headers]
        csv_writer.writerow(rows)

    return output.getvalue()


def download_file(data, mimetype, file_name):
    return Response(
        data,
        mimetype=mimetype,
        headers={"Content-Disposition": f"attachment;filename={quote_plus(file_name)}"},
    )


def get_files_for_application_upload_fields(
    application_id: str, short_id: str, application_json: dict
) -> List[tuple]:
    """
    This function retrieves the file names from an application_json
    then uses this to create a lsit of tuples containing the file name
    and download link for this file.

    Parameters:
    application_id (str): The unique identifier of the application.
    short_id (str): The unique short-hand identifier of the application.
    application_json (dict): The jsonified data for an application

    Returns:
    List[tuple]: A list of tuples, where each tuple contains the
    file name and its download link.
    """
    forms = application_json["jsonb_blob"]["forms"]
    file_names = []

    for form in forms:
        for question in form[NotifyConstants.APPLICATION_QUESTIONS_FIELD]:
            for field in question["fields"]:
                if field["type"] == "file" and field.get("answer"):
                    file_names.append(field["answer"])

    # files which used the old file upload component
    legacy_files = [
        (
            file,
            url_for(
                "assessment_bp.get_file",
                application_id=application_id,
                file_name=file,
                short_id=short_id,
            ),
        )
        for file in file_names
    ]

    # files which used the client side file upload component
    client_side_upload_files = list_files_by_prefix(application_id)
    files = [
        (file.filename, generate_url(file, short_id))
        for file in client_side_upload_files
    ]

    return legacy_files + files


def convert_bool_value(value):
    if value:
        return "Yes"
    if not value:
        return "No"
    if value is None:
        return "Not sure"


def strip_tags(text):
    if text == ["none"]:
        return "Not sure"
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()


def sanitise_export_data(data):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = sanitise_export_data(value)
    if isinstance(data, list):
        data = [sanitise_export_data(d) for d in data]

    if isinstance(data, bool):
        data = convert_bool_value(data)
    if isinstance(data, str):
        data = strip_tags(data)
    return data


def exclude_header(fund_names: list):
    if "COF-EOI" in fund_names:
        return [
            "Help with insolvency",
            "Help with organisation type",
            "Help with public authority",
            "Help gydag awdurdod cyhoeddus",
            "Help gyda'r math o sefydliad",
        ]
