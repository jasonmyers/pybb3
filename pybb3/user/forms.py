from __future__ import unicode_literals

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from .models import User
from ..database import exists


class RegisterForm(Form):
    username = StringField(
        'Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField(
        'Email', validators=[DataRequired(), Email(), Length(min=6, max=40)])
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField(
        'Verify password',
        [DataRequired(), EqualTo('password', message='Passwords must match')])

    def validate(self):
        if not super(RegisterForm, self).validate():
            return False

        if exists(u for u in User if u.username == self.username.data):
            self.username.errors.append("Username already registered")
            return False
        if exists(u for u in User if u.email == self.email.data):
            self.email.errors.append("Email already registered")
            return False
        return True
