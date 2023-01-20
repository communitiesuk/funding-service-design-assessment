from config import Config
from flask_wtf import FlaskForm
from wtforms import StringField
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
    section = StringField(
        "Section to flag",
        validators=[
            length(max=Config.TEXT_AREA_INPUT_MAX_CHARACTERS),
            InputRequired(message="Provide which section you are flagging"),
        ],
    )
