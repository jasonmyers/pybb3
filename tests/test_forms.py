# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pybb3.public.forms import LoginForm
from pybb3.user.forms import RegisterForm
from pybb3.user.models import User


class TestRegisterForm:

    def test_validate_user_already_registered(self, user):
        # Enters username that is already registered
        form = RegisterForm(
            username=user.username, email='foo@bar.com',
            password='password', confirm='password')

        assert form.validate() is False
        assert 'Username already registered' in form.username.errors

    def test_validate_email_already_registered(self, user):
        # enters email that is already registered
        form = RegisterForm(
            username='unique', email=user.email,
            password='password', confirm='password')

        assert form.validate() is False
        assert 'Email already registered' in form.email.errors

    def test_validate_success(self, db):
        form = RegisterForm(
            username='newusername', email='new@test.test',
            password='password', confirm='password')
        with db.session:
            assert form.validate() is True


class TestLoginForm:

    def test_validate_success(self, db, user):
        user.set_password('password')

        form = LoginForm(username=user.username, password='password')
        assert form.validate() is True
        assert form.user == user

    def test_validate_unknown_username(self, db):
        form = LoginForm(username='unknown', password='password')

        with db.session:
            assert form.validate() is False

        assert 'Invalid username or password' in form.username.errors
        assert form.user is None

    def test_validate_invalid_password(self, db, user):
        user.set_password('password')

        db.commit()

        form = LoginForm(username=user.username, password='wrongpassword')

        assert form.validate() is False
        assert 'Invalid username or password' in form.username.errors
