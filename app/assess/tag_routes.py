from typing import Dict

from app.assess.auth.validation import check_access_application_id
from app.assess.auth.validation import check_access_fund_id
from app.assess.data import get_associated_tags_for_application
from app.assess.data import get_fund
from app.assess.data import get_round
from app.assess.data import get_tag
from app.assess.data import get_tag_for_fund_round
from app.assess.data import get_tag_types
from app.assess.data import get_tags_for_fund_round
from app.assess.data import post_new_tag_for_fund_round
from app.assess.data import update_associated_tags
from app.assess.data import update_tag
from app.assess.data import update_tags
from app.assess.display_value_mappings import search_params_tag
from app.assess.forms.tags import DeactivateTagForm
from app.assess.forms.tags import EditTagForm
from app.assess.forms.tags import NewTagForm
from app.assess.forms.tags import ReactivateTagForm
from app.assess.forms.tags import TagAssociationForm
from app.assess.helpers import determine_assessment_status
from app.assess.helpers import get_state_for_tasklist_banner
from app.assess.helpers import match_search_params
from app.assess.models.tag import TagType
from config import Config
from flask import Blueprint
from flask import current_app
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

TAG_DEACTIVATE_ERROR_MESSAGE = "Tag not deactivated."
TAG_REACTIVATE_ERROR_MESSAGE = "Tag not reactivated."


tag_bp = Blueprint(
    "tag_bp",
    __name__,
    url_prefix=Config.ASSESSMENT_HUB_ROUTE,
    template_folder="templates",
)


@tag_bp.route("/application/<application_id>/tags", methods=["GET", "POST"])
@check_access_application_id(roles_required=["ASSESSOR"])
def load_change_tags(application_id):
    tag_association_form = TagAssociationForm()

    if request.method == "POST":
        updated_tags = []
        for tag_id in tag_association_form.tags.data:
            updated_tags.append({"tag_id": tag_id, "user_id": g.account_id})
        update_associated_tags(application_id, updated_tags)
        return redirect(
            url_for(
                "assess_bp.application",
                application_id=application_id,
            )
        )
    state = get_state_for_tasklist_banner(application_id)
    available_tags = get_tags_for_fund_round(state.fund_id, state.round_id, "")
    associated_tags = get_associated_tags_for_application(application_id)
    if associated_tags:
        associated_tag_ids = [tag.tag_id for tag in associated_tags]
        for tag in available_tags:
            if tag.id in associated_tag_ids:
                tag.associated = True
    assessment_status = determine_assessment_status(
        state.workflow_status, state.is_qa_complete
    )
    return render_template(
        "change_tags.html",
        form=tag_association_form,
        state=state,
        available_tags=available_tags,
        tag_config=Config.TAGGING_PURPOSE_CONFIG,
        application_id=application_id,
        assessment_status=assessment_status,
    )


def get_fund_round(fund_id, round_id) -> Dict:
    fund = get_fund(fund_id, use_short_name=False)
    round = get_round(fund_id, round_id, use_short_name=False)
    fund_round = {
        "fund_name": fund.name,
        "round_name": round.title,
        "fund_id": fund_id,
        "round_id": round_id,
    }
    return fund_round


@tag_bp.route("/tags/manage/<fund_id>/<round_id>", methods=["GET"])
@check_access_fund_id(roles_required=["ASSESSOR"])
def load_fund_round_tags(fund_id, round_id):
    fund_round = get_fund_round(fund_id, round_id)
    search_params, show_clear_filters = match_search_params(
        search_params_tag, request.args
    )
    tags = get_tags_for_fund_round(fund_id, round_id, search_params)
    tag_types = get_tag_types()
    tag_types.insert(0, TagType(id="all", purpose="All", description="all"))
    tag_status_configs = [
        {"text": "Only active tags", "value": "True"},
        {"text": "Only inactive tags", "value": "False"},
    ]
    return render_template(
        "manage_tags.html",
        fund_round=fund_round,
        search_params=search_params,
        tags=tags,
        show_clear_filters=show_clear_filters,
        tag_types=tag_types,
        tag_status_configs=tag_status_configs,
        tag_config=Config.TAGGING_PURPOSE_CONFIG,
    )


FLAG_ERROR_MESSAGE = (
    "Tags must be unique, only contain apostrophes, hyphens, letters, digits,"
    " and spaces."
)


@tag_bp.route("/tags/create/<fund_id>/<round_id>", methods=["GET", "POST"])
@check_access_fund_id(roles_required=["ASSESSOR"])
def create_tag(fund_id, round_id):
    go_back = request.args.get("go_back") or False
    new_tag_form = NewTagForm()
    tag_types = get_tag_types()
    new_tag_form.type.choices = [tag_type.id for tag_type in tag_types]
    fund_round = get_fund_round(fund_id, round_id)
    if new_tag_form.validate_on_submit():
        current_app.logger.info("Tag creation form validated")
        tag = {
            "value": new_tag_form.value.data,
            "tag_type_id": new_tag_form.type.data,
            "creator_user_id": g.account_id,
        }

        tag_created = post_new_tag_for_fund_round(fund_id, round_id, tag)
        if not tag_created:
            flash(FLAG_ERROR_MESSAGE)

        if go_back:
            return redirect(
                url_for(
                    "tag_bp.load_fund_round_tags",
                    fund_id=fund_id,
                    round_id=round_id,
                )
            )

        return redirect(
            url_for("tag_bp.create_tag", fund_id=fund_id, round_id=round_id)
        )
    elif request.method == "POST":
        current_app.logger.info(
            f"Tag creation form failed validation: {new_tag_form.errors}"
        )
        flash(FLAG_ERROR_MESSAGE)
    return render_template(
        "create_tag.html",
        form=new_tag_form,
        tag_types=tag_types,
        tag_config=Config.TAGGING_PURPOSE_CONFIG,
        fund_round=fund_round,
    )


@tag_bp.route(
    "/tags/deactivate/<fund_id>/<round_id>/<tag_id>", methods=["GET", "POST"]
)
@check_access_fund_id(roles_required=["ASSESSOR"])
def deactivate_tag(fund_id, round_id, tag_id):
    deactivate_tag_form = DeactivateTagForm()
    tag_to_deactivate = get_tag_for_fund_round(fund_id, round_id, tag_id)
    fund = get_fund(fund_id, use_short_name=False)
    round = get_round(fund_id, round_id, use_short_name=False)
    fund_round = {
        "fund_name": fund.name,
        "round_name": round.title,
        "fund_id": fund_id,
        "round_id": round_id,
    }
    if deactivate_tag_form.validate_on_submit():
        current_app.logger.info(
            f"Tag deactivation form validated, deactivating tag_id: {tag_id}."
        )
        tag_update_to_deactivate = [{"id": tag_id, "active": False}]
        tag_deactivated = update_tags(
            fund_id, round_id, tag_update_to_deactivate
        )
        if tag_deactivated:
            return redirect(
                url_for(
                    "tag_bp.load_fund_round_tags",
                    fund_id=fund_id,
                    round_id=round_id,
                )
            )
        flash(TAG_DEACTIVATE_ERROR_MESSAGE)

    elif request.method == "POST":
        current_app.logger.info(
            "Tag deactivation form failed validation:"
            f" {deactivate_tag_form.errors}"
        )
        flash(TAG_DEACTIVATE_ERROR_MESSAGE)
    return render_template(
        "deactivate_tag.html",
        form=deactivate_tag_form,
        tag=tag_to_deactivate,
        tag_config=Config.TAGGING_PURPOSE_CONFIG,
        fund_round=fund_round,
    )


@tag_bp.route(
    "/tags/reactivate/<fund_id>/<round_id>/<tag_id>", methods=["GET", "POST"]
)
@check_access_fund_id(roles_required=["ASSESSOR"])
def reactivate_tag(fund_id, round_id, tag_id):
    reactivate_tag_form = ReactivateTagForm()
    tag_to_reactivate = get_tag_for_fund_round(fund_id, round_id, tag_id)
    fund = get_fund(fund_id, use_short_name=False)
    round = get_round(fund_id, round_id, use_short_name=False)
    fund_round = {
        "fund_name": fund.name,
        "round_name": round.title,
        "fund_id": fund_id,
        "round_id": round_id,
    }
    if reactivate_tag_form.validate_on_submit():
        current_app.logger.info(
            f"Tag reactivation form validated, reactivating tag_id: {tag_id}."
        )
        tag_to_reactivate = [{"id": tag_id, "active": True}]
        tag_reactivated = update_tags(fund_id, round_id, tag_to_reactivate)
        if tag_reactivated:
            return redirect(
                url_for(
                    "tag_bp.load_fund_round_tags",
                    fund_id=fund_id,
                    round_id=round_id,
                )
            )
        flash(TAG_REACTIVATE_ERROR_MESSAGE)
    elif request.method == "POST":
        current_app.logger.info(
            "Tag reactivation form failed validation:"
            f" {reactivate_tag_form.errors}"
        )
        flash(TAG_REACTIVATE_ERROR_MESSAGE)
    return render_template(
        "reactivate_tag.html",
        form=reactivate_tag_form,
        tag=tag_to_reactivate,
        tag_config=Config.TAGGING_PURPOSE_CONFIG,
        fund_round=fund_round,
    )


@tag_bp.route(
    "/tags/edit/<fund_id>/<round_id>/<tag_id>", methods=["GET", "POST"]
)
@check_access_fund_id(roles_required=["ASSESSOR"])
def edit_tag(fund_id, round_id, tag_id):
    edit_tag_form = EditTagForm()
    fund_round = get_fund_round(fund_id, round_id)
    tag = get_tag(fund_id, round_id, tag_id)
    if request.method == "GET":
        current_app.logger.info(f"Loading edit tag page for id {tag_id}")

    elif request.method == "POST":
        current_app.logger.info("In edit tag post")
        if edit_tag_form.validate_on_submit():
            # Save changes
            payload = {"id": tag_id, "value": edit_tag_form.value.data}
            if update_tag(fund_id, round_id, payload):
                return redirect(
                    url_for(
                        "tag_bp.load_fund_round_tags",
                        fund_id=fund_id,
                        round_id=round_id,
                    )
                )
            else:
                flash(
                    "An error occurred and your changes were not saved. Please"
                    " try again later."
                )
        else:
            current_app.logger.info(
                f"Edit tag form failed validation: {edit_tag_form.errors}"
            )
            flash(FLAG_ERROR_MESSAGE)

    return render_template(
        "edit_tag.html",
        form=edit_tag_form,
        fund_round=fund_round,
        tag=tag,
    )
