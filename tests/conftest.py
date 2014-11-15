# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
from __future__ import unicode_literals
import functools

import pytest
from webtest import TestApp

from pybb3.settings import TestConfig
from pybb3.app import create_app
from pybb3.ext.pony import Pony
from pybb3.ext.mod import Mod

from .factories import UserFactory


@pytest.yield_fixture
def app():
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


def pytest_runtest_call(item):
    if 'db' in item.funcargs:
        db = item.funcargs['db']

        original_runtest = item.runtest

        # If `db` fixture is used, automatically wrap the test in a `db.session`
        # Also re-load any Entity fixtures (e.g. `user`) into this
        # session so that they are immediately usable in the test (otherwise,
        # you would get an 'expired session' error, and have to re-load the
        # entity once inside the test)
        @functools.wraps(original_runtest)
        @db.session
        def session_runtest():
            for key, value in item.funcargs.items():
                if isinstance(value, db.Entity):
                    item.funcargs[key] = value.__class__[value.id]
            return original_runtest()

        item.runtest = session_runtest


@pytest.yield_fixture(scope='session')
def db_schema():
    from pybb3.extensions import db
    if not db.schema:
        db.generate_mapping(create_tables=False, check_tables=False)
    yield db


@pytest.yield_fixture
def db(app, db_schema):
    """ This fixture provides access to the real app's database and models

    It is automatically wiped before and after your test runs

    Tests using this fixture are also automatically wrapped in a `db.session`
    """
    db = db_schema
    db.drop_all_tables(with_all_data=True)

    db.create_tables(check_tables=False)
    yield db

    db.drop_all_tables(with_all_data=True)


@pytest.yield_fixture
def udb(app):
    """ This fixture provides access to an empty, unmapped database, which you
    can use to define entities during your test

    Note::  You must call `udb.generate()` after defining your entities,
    and before running any queries, e.g.

    def unmapped_test(udb):
        db = udb
        class Topic(db.Entity):
            ...

        db.generate()

        with db.session:
            topic = Topic(...)
            ...

    """
    db = Pony(app=app)
    yield db
    db.drop_all_tables(with_all_data=True)


@pytest.fixture
def mod(app):
    return Mod(app=app)


@pytest.fixture
def user(db):
    with db.session:
        return UserFactory(password='myprecious')
