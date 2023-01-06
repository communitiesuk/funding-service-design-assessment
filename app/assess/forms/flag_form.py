from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import length


class FlagApplicationForm(FlaskForm):
    reason = TextAreaField(
        "Reason for flagging",
        validators=[
            length(max=10000),
            DataRequired(
                message="Provide a reason for flagging this application"
            ),
        ],
    )
    section = StringField(
        "Section to flag",
        validators=[
            length(max=10000),
            DataRequired(message="Provide which section you are flagging"),
        ],
    )
