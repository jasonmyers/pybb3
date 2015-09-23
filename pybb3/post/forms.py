from __future__ import unicode_literals

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class NewPostForm(Form):
    subject = StringField('Post Subject', validators=[DataRequired(), Length(max=255)])
    text = StringField('Post Text')
