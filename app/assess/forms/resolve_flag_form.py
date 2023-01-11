from flask_wtf import FlaskForm
from wtforms import TextAreaField, RadioField
from wtforms.validators import DataRequired

# TODO
# add data required validators

class ResolveFlagForm(FlaskForm):
    resolution_flag = RadioField(
        "resolve", 
        choices=["RESOLVED", "STOPPED"], 
        validators=[DataRequired()]
    )
    justification = TextAreaField(
        "justification",
        validators=[DataRequired()],
    )
