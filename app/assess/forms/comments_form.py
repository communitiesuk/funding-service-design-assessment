from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import InputRequired
from wtforms.validators import length


class CommentsForm(FlaskForm):

    comment = TextAreaField(
        "Comment", validators=[length(max=100000), InputRequired()]
    )
