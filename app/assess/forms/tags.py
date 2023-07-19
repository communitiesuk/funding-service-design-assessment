from config import Config
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms import SelectMultipleField
from wtforms import TextAreaField
from wtforms.validators import InputRequired
from wtforms.validators import length


class TagAssociationForm(FlaskForm):
    tags = SelectMultipleField(
        "Tags to associate",
        validators=[
            InputRequired(message="Provide which tag(s) you are associating"),
        ],
    )


class NewTagForm(FlaskForm):
    value = TextAreaField(
        "value",
        validators=[
            InputRequired(message="Provide a value for the tag."),
            length(max=Config.TEXT_AREA_INPUT_MAX_CHARACTERS),
        ],
    )

    type = RadioField(
        "type",
        validators=[InputRequired()],
    )
