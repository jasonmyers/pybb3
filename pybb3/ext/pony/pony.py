# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import functools

import six

from pony.orm import db_session, Database

from flask import Blueprint, request
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
        if app is not None:
            self.init_app(app)

        # Need to instantiate empty Database() here so that imported models have
        # access to db.Entity.  We'll bind it later to a provider in `init_app`
        self.db = Database()
        self.Entity = self.db.Entity

        self._exempt_db_session_views = set()
        self._exempt_db_session_blueprints = set()

    def init_app(self, app):
        app.config.setdefault('PONY_DATABASE_PROVIDER', 'sqlite')
        app.config.setdefault('PONY_DATABASE_URI', ':memory:')
        app.config.setdefault('PONY_DATABASE_USERNAME', '')
        app.config.setdefault('PONY_DATABASE_PASSWORD', '')
        app.config.setdefault('PONY_DATABASE_HOST', '')

        app.config.setdefault('PONY_AUTO_DB_SESSION_VIEWS', True)

        self.connect(app)

        app.db = self.db

        @app.after_request
        def merge_stats(response):
            if app.db.local_stats:
                app.db.merge_local_stats()
            return response

        # Automatically wrap flask routes in `@db_session`
        app.add_url_rule = self.patch_add_url_rule(app)

    def connect(self, app):
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

        self.db.generate_mapping(check_tables=True, create_tables=True)
        return self.db

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
        return db_session(*args, **kwargs)

    def exempt(self, view):
        """ Decorator to disable the automatic `@db_session` wrapping on a
        particular route.  Usage::

            @app.route(...)
            @db.exempt
            def myview(...):
                ... no automatic db session ...

        Note::  You can still use `db_session` inside such a view (as a
        context manager, for example).  This just disables the automatic
        wrapping.

        """
        if isinstance(view, Blueprint):
            self._exempt_db_session_blueprints.add(view.name)
            return view
        if isinstance(view, six.string_types):
            view_location = view
        else:
            view_location = '%s.%s' % (view.__module__, view.__name__)
        self._exempt_db_session_views.add(view_location)
        return view

    def patch_add_url_rule(self, app):
        """ Patch `Flask.add_url_rule` to wrap all routes in a `@db_session`
        if app.config['PONY_AUTO_DB_SESSION_VIEWS'] is enabled and the route
        is not opted-out with `@db.exempt`
        """
        original_add_url_rule = app.add_url_rule

        @functools.wraps(original_add_url_rule)
        def add_url_rule(rule, endpoint=None, view_func=None, **options):
            clean = functools.partial(original_add_url_rule, rule, endpoint=endpoint, view_func=view_func, **options)
            wrapped = functools.partial(original_add_url_rule, rule, endpoint=endpoint, view_func=self.session(view_func), **options)

            enable_auto_session = app.config['PONY_AUTO_DB_SESSION_VIEWS']

            if not enable_auto_session:
                return clean()

            if self._exempt_db_session_views or self._exempt_db_session_blueprints:
                if not request.endpoint:
                    return clean()

                view = app.view_functions.get(request.endpoint)
                if not view:
                    return clean()

                dest = '%s.%s' % (view.__module__, view.__name__)
                if dest in self._exempt_db_session_views:
                    return clean()
                if request.blueprint in self._exempt_db_session_blueprints:
                    return clean()

            return wrapped()

        return add_url_rule
