from flask_wtf import FlaskForm
from wtforms import SelectMultipleField
from wtforms.validators import InputRequired


class TagAssociationForm(FlaskForm):
    tags = SelectMultipleField(
        "Tags to associate",
        validators=[
            InputRequired(message="Provide which tag(s) you are associating"),
        ],
    )
