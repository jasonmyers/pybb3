# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
from __future__ import unicode_literals

import pytest
from webtest import TestApp

from pybb3.settings import TestConfig
from pybb3.app import create_app
from pybb3.ext.pony import Pony
from pybb3.ext.mod import Mod

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
    db = Pony(app=app)

    with app.app_context():
        db.create_tables()

    yield db

    db.drop_all_tables(with_all_data=True)


@pytest.fixture(scope='function')
def mod(app):
    return Mod(app=app)


@pytest.yield_fixture
def user(db):
    """ Using this fixture wraps your test in a db_session """
    with db.session:
        yield UserFactory(password='myprecious')
