from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import length
from wtforms.validators import DataRequired


class CommentsForm(FlaskForm):

    comment = TextAreaField("Comment", validators=[length(max=100000), DataRequired()])
