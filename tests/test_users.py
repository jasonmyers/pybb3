# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from pybb3.user.models import User
from .factories import UserFactory


class TestUser:

    def test_get_by_id(self, db):
        user = User(username='foo', email='foo@bar.com')
        db.commit()

        assert user.id == User[user.id].id

    def test_created_at_defaults_to_datetime(self, db):
        user = User(username='foo', email='foo@bar.com')
        db.commit()

        assert bool(user.regdate)
        assert isinstance(user.regdate, datetime.datetime)

    def test_password_is_nullable(self, db):
        user = User(username='foo', email='foo@bar.com')
        db.commit()

        assert user.password == ''

    def test_factory(self, db):
        user = UserFactory(password='myprecious')
        db.commit()

        assert bool(user.username)
        assert bool(user.email)
        assert bool(user.regdate)
        assert user.is_active()
        assert user.check_password('myprecious')

    def test_check_password(self, db):
        user = User(
            username='foo', email='foo@bar.com',
            password='foobarbaz123')
        db.commit()

        assert user.password != 'foobarbaz123'
        assert user.check_password('foobarbaz123') is True
        assert user.check_password('barfoobaz') is False
