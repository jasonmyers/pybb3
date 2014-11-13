# -*- coding: utf-8 -*-
"""Model unit tests."""
from __future__ import unicode_literals

import datetime

from pybb3.database import db
from pybb3.user.models import User
from .factories import UserFactory


class TestUser:

    def test_get_by_id(self):
        with db.session:
            user = User(username='foo', email='foo@bar.com')

        assert user.id == User[user.id].id

    def test_created_at_defaults_to_datetime(self):
        with db.session:
            user = User(username='foo', email='foo@bar.com')

        assert bool(user.created_at)
        assert isinstance(user.created_at, datetime.datetime)

    def test_password_is_nullable(self):
        with db.session:
            user = User(username='foo', email='foo@bar.com')

        assert user.password is None

    def test_factory(self):
        with db.session:
            user = UserFactory(password='myprecious')

        assert bool(user.username)
        assert bool(user.email)
        assert bool(user.created_at)
        assert user.is_admin is False
        assert user.active is True
        assert user.check_password('myprecious')

    def test_check_password(self):
        with db.session:
            user = User.create(
                username='foo', email='foo@bar.com',
                password='foobarbaz123')

        assert user.check_password('foobarbaz123') is True
        assert user.check_password('barfoobaz') is False

    def test_full_name(self):
        with db.session:
            user = UserFactory(first_name='Foo', last_name='Bar')

        assert user.full_name == 'Foo Bar'
