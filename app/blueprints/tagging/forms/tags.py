from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms import SelectMultipleField
from wtforms import TextAreaField
from wtforms.validators import InputRequired
from wtforms.validators import Regexp
from wtforms.validators import length

from config import Config


class TagAssociationForm(FlaskForm):
    tags = SelectMultipleField(
        "Tags to associate",
        validators=[
            InputRequired(message="Provide which tag(s) you are associating"),
        ],
    )


tag_value_field = TextAreaField(
    "value",
    validators=[
        InputRequired(message="Provide a value for the tag."),
        length(max=Config.TEXT_AREA_INPUT_MAX_CHARACTERS),
        Regexp(r"^[A-Za-z0-9_' -]+$", message="Invalid characters in value."),
    ],
)


class NewTagForm(FlaskForm):
    value = tag_value_field

    type = RadioField(
        "type",
        validators=[InputRequired()],
    )


class EditTagForm(FlaskForm):
    value = tag_value_field


class DeactivateTagForm(FlaskForm):
    pass


class ReactivateTagForm(FlaskForm):
    pass
