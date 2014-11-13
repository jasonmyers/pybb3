# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
from __future__ import unicode_literals

import pytest
from webtest import TestApp

from pybb3.settings import TestConfig
from pybb3.app import create_app
from pybb3.database import db as _db

from .factories import UserFactory


@pytest.yield_fixture(scope='function')
def app():
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.yield_fixture(scope='function')
def db(app):
    _db.app = app
    with app.app_context():
        _db.create_tables()

    yield _db

    _db.drop_all_tables(with_all_data=True)


@pytest.yield_fixture
def user(db):
    """ Using this fixture wraps your test in a db_session """
    with db.session:
        yield UserFactory(password='myprecious')
