from flask import abort
from flask import current_app

from app.blueprints.scoring.forms.scores_and_justifications import OneToFiveScoreForm
from app.blueprints.scoring.forms.scores_and_justifications import ZeroToThreeScoreForm
from app.blueprints.services.data_services import get_scoring_system  # noqa


def get_scoring_class(round_id):
    scoring_system = get_scoring_system(round_id)

    try:
        class_mapping = {
            "ZeroToThree": ZeroToThreeScoreForm,
            "OneToFive": OneToFiveScoreForm,
        }
        scoring_form_class = class_mapping[scoring_system]
    except KeyError:
        current_app.logger.error(f"Scoring system '{scoring_system}' not found.")
        abort(
            500,
            description=f"Scoring system '{scoring_system}' for round {round_id} has not been configured.",
        )
    return scoring_form_class
