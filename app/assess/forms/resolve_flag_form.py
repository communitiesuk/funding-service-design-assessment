from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms import TextAreaField
from wtforms.validators import InputRequired


class ResolveFlagForm(FlaskForm):
    resolution_flag = RadioField(
        "resolve",
        choices=["RESOLVED", "STOPPED"],
        validators=[InputRequired()],
    )
    justification = TextAreaField(
        "justification",
        validators=[InputRequired()],
    )
