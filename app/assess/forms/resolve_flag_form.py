from config import Config
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms import TextAreaField
from wtforms.validators import InputRequired
from wtforms.validators import length


class ResolveFlagForm(FlaskForm):
    resolution_flag = RadioField(
        "resolve",
        choices=["RESOLVED", "STOPPED"],
        validators=[InputRequired()],
    )
    justification = TextAreaField(
        "justification",
        validators=[
            InputRequired(),
            length(max=Config.TEXT_AREA_INPUT_MAX_CHARACTERS),
        ],
    )
