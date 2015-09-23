from __future__ import unicode_literals

from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length

from pybb3.utils import optional_string_id


class NewCategoryForm(Form):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=255)])
    desc = StringField('Category Description', validators=[DataRequired()])
    parent = SelectField('Parent', coerce=optional_string_id)


class NewForumForm(Form):
    name = StringField('Forum Name', validators=[DataRequired(), Length(max=255)])
    desc = StringField('Forum Description', validators=[DataRequired()])
    parent = SelectField('Parent', coerce=optional_string_id)


class NewLinkForm(Form):
    name = StringField('Link Name', validators=[DataRequired(), Length(max=255)])
    desc = StringField('Link Description', validators=[DataRequired()])
    parent = SelectField('Parent', coerce=optional_string_id)
    url = StringField('Url', validators=[DataRequired()])
