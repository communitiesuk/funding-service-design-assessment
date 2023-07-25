from app.assess.auth.validation import check_access_application_id
from app.assess.auth.validation import check_access_fund_id
from app.assess.data import get_associated_tags_for_application
from app.assess.data import get_available_tags_for_fund_round
from app.assess.data import get_fund
from app.assess.data import get_round
from app.assess.data import get_tag_types
from app.assess.data import post_new_tag_for_fund_round
from app.assess.data import update_associated_tags
from app.assess.forms.tags import NewTagForm
from app.assess.forms.tags import TagAssociationForm
from app.assess.helpers import get_state_for_tasklist_banner
from config import Config
from flask import Blueprint
from flask import current_app
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

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
    available_tags = get_available_tags_for_fund_round(
        state.fund_id, state.round_id
    )
    associated_tags = get_associated_tags_for_application(application_id)
    if associated_tags:
        associated_tag_ids = [tag.tag_id for tag in associated_tags]
        for tag in available_tags:
            if tag.id in associated_tag_ids:
                tag.associated = True
    return render_template(
        "change_tags.html",
        form=tag_association_form,
        state=state,
        available_tags=available_tags,
        tag_config=Config.TAGGING_PURPOSE_CONFIG,
        application_id=application_id,
    )


@tag_bp.route("/tags/manage/<fund_id>/<round_id>", methods=["GET"])
@check_access_fund_id(roles_required=["ASSESSOR"])
def load_fund_round_tags(fund_id, round_id):
    fund = get_fund(fund_id, use_short_name=False)
    round = get_round(fund_id, round_id, use_short_name=False)
    fund_round = {
        "fund_name": fund.name,
        "round_name": round.title,
        "fund_id": fund_id,
        "round_id": round_id,
    }
    available_tags = get_available_tags_for_fund_round(fund_id, round_id)
    return render_template(
        "manage_tags.html",
        fund_round=fund_round,
        available_tags=available_tags,
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
    fund = get_fund(fund_id, use_short_name=False)
    round = get_round(fund_id, round_id, use_short_name=False)
    new_tag_form.type.choices = [tag_type.id for tag_type in tag_types]
    fund_round = {
        "fund_name": fund.name,
        "round_name": round.title,
        "fund_id": fund_id,
        "round_id": round_id,
    }
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

    available_tags = get_available_tags_for_fund_round(fund_id, round_id)
    return render_template(
        "create_tag.html",
        form=new_tag_form,
        tag_types=tag_types,
        tag_config=Config.TAGGING_PURPOSE_CONFIG,
        available_tags=available_tags,
        fund_round=fund_round,
    )
