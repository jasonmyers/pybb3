# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pony.orm import db_session, Database

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

        # Need to define empty Database() here so that imported models have
        # access to db.Entity.  We'll bind it later to a provider in `init_app`
        self.db = Database()
        self.Entity = self.db.Entity
        self.session = db_session

    def init_app(self, app):
        app.config.setdefault('PONY_DATABASE_PROVIDER', 'sqlite')
        app.config.setdefault('PONY_DATABASE_URI', ':memory:')
        app.config.setdefault('PONY_DATABASE_USERNAME', '')
        app.config.setdefault('PONY_DATABASE_PASSWORD', '')
        app.config.setdefault('PONY_DATABASE_HOST', '')

        self.connect(app)

        app.db = self.db

        @app.after_request
        def merge_stats(response):
            if app.db.local_stats:
                app.db.merge_local_stats()
            return response

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
