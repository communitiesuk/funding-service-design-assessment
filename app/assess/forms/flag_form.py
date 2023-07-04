from config import Config
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms import SelectMultipleField
from wtforms import TextAreaField
from wtforms.validators import InputRequired
from wtforms.validators import length


class FlagApplicationForm(FlaskForm):
    justification = TextAreaField(
        "Reason for flagging",
        validators=[
            length(max=Config.TEXT_AREA_INPUT_MAX_CHARACTERS),
            InputRequired(
                message="Provide a justification for flagging this application"
            ),
        ],
    )
    section = SelectMultipleField(
        "Sections to flag",
        choices=None,
        validators=[
            length(max=Config.TEXT_AREA_INPUT_MAX_CHARACTERS),
            InputRequired(message="Provide which section(s) you are flagging"),
        ],
    )

    # TODO: Rework on the avialable teams after implemented in fundstore
    teams_available = RadioField(
        "teams_available",
        choices=None,
        # validators=[InputRequired(message="Select a team")],
        validate_choice=False,
    )

    def __init__(self, section_choices=None, team_choices=None):
        super().__init__()
        self.section.choices = section_choices
        self.teams_available.choices = team_choices
