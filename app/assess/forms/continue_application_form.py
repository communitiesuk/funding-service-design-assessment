from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import InputRequired


class ContinueApplicationForm(FlaskForm):
    reason = TextAreaField(
        "reason",
        validators=[InputRequired()],
    )
