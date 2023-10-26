import app.blueprints.scoring.forms.scores_and_justifications as scoring_form_classes
from app.blueprints.services.data_services import get_scoring_system  # noqa
from flask import abort
from flask import current_app


def get_scoring_class(round_id):
    # scoring systems:
    # - OneToFive
    # - ZeroToThree
    # TODO: Add endpoint to assessment store to retrieve scoring system
    # scoring_system  = get_scoring_system()
    scoring_system = "OneToFive"
    try:
        scoring_form_class = getattr(
            scoring_form_classes, f"{scoring_system}ScoreForm"
        )
    except AttributeError:
        current_app.logger.error(
            f"Scoring system '{scoring_system}' not found."
        )
        abort(500, description="Scoring system not found.")
    return scoring_form_class
