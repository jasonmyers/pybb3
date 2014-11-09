# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    #from flash.ext.pony import Pony
    from ....ext.pony import Pony
    from pony.orm import db_session
    from pony.orm.dbproviders.sqlite import SQLiteProvider

    pony_available = True
except ImportError:
    Pony = None
    SQLiteProvider = None
    db_session = None
    pony_available = False

from flask import request, current_app, abort, json_available, g, \
    render_template
# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from flask_debugtoolbar import module
from flask_debugtoolbar.panels import DebugPanel
from flask_debugtoolbar.utils import format_fname, format_sql as debugtoolbar_format_sql
import itsdangerous


_ = lambda x: x


def query_signer():
    return itsdangerous.URLSafeSerializer(current_app.config['SECRET_KEY'],
                                          salt='fdt-sql-query')


def sign_query(statement):
    if not statement.lower().strip().startswith('select'):
        return None

    try:
        return query_signer().dumps(statement)
    except TypeError:
        return None


def load_query(data):
    try:
        statement = query_signer().loads(request.args['query'])
    except (itsdangerous.BadSignature, TypeError):
        abort(406)

    # Make sure it is a select statement
    if not statement.lower().strip().startswith('select'):
        abort(406)

    return statement


class PonyDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'Pony'

    def __init__(self, jinja_env, *args, **kwargs):
        # Only needed while this lives in app/ext/flask_debugtoolbar instead of flask_debugtoolbar.*
        import os
        embedded_template_path = os.path.join(current_app.config['APP_DIR'], 'ext/flask_debugtoolbar/templates/')
        if embedded_template_path not in current_app.jinja_loader.searchpath:
            current_app.jinja_loader.searchpath.append(embedded_template_path)

        super(PonyDebugPanel, self).__init__(jinja_env=current_app.jinja_env, *args, **kwargs)

    @property
    def has_content(self):
        if not json_available or not pony_available:
            return True  # will display an error message
        return bool(self.debug_queries)

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def nav_title(self):
        return _('Pony')

    def nav_subtitle(self):
        if not json_available or not pony_available:
            return 'Unavailable'

        count = len(self.debug_queries)
        return "%d %s" % (count, "query" if count == 1 else "queries")

    def title(self):
        return _('Pony queries')

    def url(self):
        return ''

    def content(self):
        if not json_available or not pony_available:
            msg = ['Missing required libraries:', '<ul>']
            if not json_available:
                msg.append('<li>simplejson</li>')
            if not pony_available:
                msg.append('<li>Flask-Pony</li>')
            msg.append('</ul>')
            return '\n'.join(msg)

        queries = []
        for query in sorted(self.debug_queries.values(), key=lambda q: q.sum_time, reverse=True):
            queries.append({
                'db_hits': query.db_count,
                'cache_hits': query.cache_count,
                'min_time': query.min_time,
                'avg_time': query.avg_time,
                'max_time': query.max_time,
                'sum_time': query.sum_time,
                'sql': format_sql(query.sql, []),
                'signed_query': sign_query(query.sql),

                'context_long': '',#query.context,
                'context': '',#format_fname(query.context)
            })
        return self.render('panels/pony.html', {'queries': queries})

    @property
    def debug_queries(self):
        if self._debug_queries is None:
            try:
                self._debug_queries = current_app.db.local_stats.copy()
            except AttributeError:
                self._debug_queries = []
            else:
                current_app.db.merge_local_stats()  # Clear stats

        return self._debug_queries
    _debug_queries = None


@module.route('/pony/sql_select', methods=['GET', 'POST'])
def sql_select():
    statement = load_query(request.args['query'])

    db = current_app.db

    with db_session:
        cursor = db.execute(statement)
        result = cursor.fetchall()
        headers = [header[0] for header in cursor.description]

    #return g.debug_toolbar.render('panels/pony_select.html', {
    return render_template('panels/pony_select.html', **{
        'result': result,
        'headers': headers,
        'sql': format_sql(statement, []),
        'duration': float(request.args['duration']),
    })


@module.route('/pony/sql_explain', methods=['GET', 'POST'])
def sql_explain():
    statement = load_query(request.args['query'])
    db = current_app.db

    if isinstance(db.provider, SQLiteProvider):
        query = 'EXPLAIN QUERY PLAN %s' % statement
    else:
        query = 'EXPLAIN %s' % statement

    with db_session:
        cursor = db.execute(query)
        result = cursor.fetchall()
        headers = [header[0] for header in cursor.description]

    #return g.debug_toolbar.render('panels/pony_explain.html', {
    return render_template('panels/pony_explain.html', **{
        'result': result,
        'headers': headers,
        'sql': format_sql(statement, []),
        'duration': float(request.args['duration']),
    })


def format_sql(query, args):
    query = query.replace('"', '')
    return debugtoolbar_format_sql(query, args).decode('utf-8')
