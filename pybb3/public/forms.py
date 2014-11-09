from __future__ import unicode_literals

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from pybb3.user.models import User


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def validate(self):
        if not super(LoginForm, self).validate():
            return False

        if not self.user or not self.user.check_password(self.password.data):
            self.username.errors.append('Invalid username or password')
            return False

        if not self.user.active:
            self.username.errors.append('User not activated')
            return False
        return True

    @property
    def user(self):
        if self._user is False and self.username.data:
            self._user = User.get(username=self.username.data)

        return self._user
    _user = False  # False until checked then None or User()
