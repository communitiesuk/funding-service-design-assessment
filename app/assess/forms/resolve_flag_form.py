from flask_wtf import FlaskForm
from wtforms import TextAreaField, RadioField
from wtforms.validators import InputRequired

class ResolveFlagForm(FlaskForm):
    resolution_flag = RadioField(
        "resolve", 
        choices=["RESOLVED", "STOPPED"], 
        validators=[InputRequired()]
    )
    justification = TextAreaField(
        "justification",
        validators=[InputRequired()],
    )
