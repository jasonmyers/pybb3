# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import functools
import re
import six

from pony.orm import db_session, Database

from flask import Blueprint

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class Pony(object):

    def __init__(self, app=None):
        self.app = app

        # Need to instantiate empty Database() here so that imported models have
        # access to db.Entity.  We'll bind it later to a provider in `init_app`
        self.db = Database()
        self.Entity = self.db.Entity

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('PONY_DATABASE_PROVIDER', 'sqlite')
        app.config.setdefault('PONY_DATABASE_URI', ':memory:')
        app.config.setdefault('PONY_DATABASE_USERNAME', '')
        app.config.setdefault('PONY_DATABASE_PASSWORD', '')
        app.config.setdefault('PONY_DATABASE_HOST', '')

        # If `True`, wraps all requests in a `@db_session`
        app.config.setdefault('PONY_AUTO_SESSION_VIEWS', True)

        # Url regex patterns to be `match`ed, for urls to bypass auto
        # `@db_session` wrapping
        app.config.setdefault('PONY_AUTO_SESSION_EXEMPT_URLS', ())

        # Combined compiled regex from `PONY_AUTO_SESSION_EXEMPT_URLS`
        app.config.setdefault(
            'PONY_AUTO_SESSION_EXEMPT_RE',
            re.compile('|'.join(app.config['PONY_AUTO_SESSION_EXEMPT_URLS']))
            if app.config['PONY_AUTO_SESSION_EXEMPT_URLS'] else None
        )

        self.connect(app)

        app.db = self.db

        @app.after_request
        def merge_stats(response):
            if app.db.local_stats:
                app.db.merge_local_stats()
            return response

        # Automatically wrap flask routes in `@db_session`
        self.wrap_requests_with_session(app)

    def connect(self, app):
        if self.schema or self.provider:
            return self.db

        provider = app.config['PONY_DATABASE_PROVIDER']
        uri = app.config['PONY_DATABASE_URI']
        username = app.config['PONY_DATABASE_USERNAME']
        password = app.config['PONY_DATABASE_PASSWORD']
        host = app.config['PONY_DATABASE_HOST']

        if provider == 'sqlite':
            self.db.bind('sqlite', uri, create_db=uri != ':memory:')
        else:
            raise ValueError('PONY_DATABASE_PROVIDER {!r} not supported'.format(provider))

        #db.bind('postgres', user='', password='', host='', database='')
        #db.bind('mysql', host='', user='', passwd='', db='')
        #db.bind('oracle', 'user/password@dsn')
        if not app.config['TESTING']:
            self.generate()
        return self.db

    @property
    def session(self, *args, **kwargs):
        """ Wrapper around the `@db_session` decorator.  Usage::

            @app.route(...)
            @db.session
            def myview(...):
                ... db session enabled here ...

        Note:: app.config setting `'PONY_AUTO_DB_SESSION_VIEWS'` controls
        automatic `@db_session` wrapping of all views (default `True`), so
        this is only required if that setting is disabled

        """
        return db_session

    @property
    def drop_all_tables(self):
        return self.db.drop_all_tables

    @property
    def create_tables(self):
        return self.db.create_tables

    @property
    def generate_mapping(self):
        return self.db.generate_mapping

    def generate(self):
        return self.generate_mapping(create_tables=True, check_tables=True)

    @property
    def commit(self):
        return self.db.commit

    @property
    def schema(self):
        return self.db.schema

    @property
    def provider(self):
        return self.db.provider

    def wrap_requests_with_session(self, app):
        """ Patch `Flask.wsgi_app` to wrap all routes in a `@db_session`
        if `app.config['PONY_AUTO_SESSION_VIEWS']` is enabled and the route
        is not opted-out with `app.config['PONY_AUTO_SESSION_EXEMPT_URLS']`
        """
        original_wsgi_app = app.wsgi_app

        @functools.wraps(original_wsgi_app)
        def wsgi_app(environ, start_response):
            if app.config['PONY_AUTO_SESSION_VIEWS']:
                exempt_re = app.config['PONY_AUTO_SESSION_EXEMPT_RE']
                if not exempt_re or not exempt_re.match(environ['PATH_INFO']):
                    return self.session(original_wsgi_app)(environ, start_response)
            return original_wsgi_app(environ, start_response)

        app.wsgi_app = wsgi_app
