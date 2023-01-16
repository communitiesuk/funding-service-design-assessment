from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms import TextAreaField
from wtforms.validators import InputRequired


class ScoreForm(FlaskForm):
    """
    Given class is a form class model for search fund
    """

    score = RadioField(
        "Score", choices=[1, 2, 3, 4, 5], validators=[InputRequired()]
    )
    justification = TextAreaField(
        "Justification", validators=[InputRequired()]
    )
