from __future__ import unicode_literals

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class NewTopicForm(Form):
    title = StringField('Forum Name', validators=[DataRequired(), Length(max=255)])
