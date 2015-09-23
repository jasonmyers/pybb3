# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import url_for

import pytest
from werkzeug.datastructures import FileStorage
from werkzeug.routing import BuildError

from pybb3.ext.requestarg import RequestArg, parse_rule


class TestRequestArg:

    @pytest.fixture(autouse=True)
    def requestarg(self, newapp):
        """ Make sure RequestArg is loaded and initialized """
        return RequestArg(newapp)

    def test_requestarg_get_simple(self, newapp):
        app = newapp

        @app.route('/')
        @app.arg('arg')
        def route(arg=None):
            route.arg = arg
            return ''

        app.client.get('/')
        assert route.arg is None

        app.client.get('/?arg=1')
        assert route.arg == '1'

    def test_requestarg_get_multiple(self, newapp):
        app = newapp

        @app.route('/')
        @app.arg('arg1')
        @app.arg('<arg2>')
        def route(arg1=None, arg2='default'):
            route.arg1 = arg1
            route.arg2 = arg2
            return ''

        app.client.get('/')
        assert route.arg1 is None
        assert route.arg2 is 'default'

        app.client.get('/?arg1=1')
        assert route.arg1 == '1'
        assert route.arg2 == 'default'

        app.client.get('/?arg2=custom')
        assert route.arg1 is None
        assert route.arg2 == 'custom'

        app.client.get('/?arg1=1&arg2=custom')
        assert route.arg1 == '1'
        assert route.arg2 == 'custom'

    def test_requestarg_post(self, newapp):
        app = newapp

        @app.route('/', methods=['POST'])
        @app.arg('arg')
        def route(arg=None):
            route.arg = arg
            return ''

        app.client.post('/')
        assert route.arg is None

        app.client.post('/?arg=1', {'arg': '1'})
        assert route.arg == '1'

    def test_requestarg_methods(self, newapp):
        app = newapp

        @app.route('/', methods=['GET', 'POST'])
        @app.arg('arg', methods=['GET'])
        def route(arg=None):
            route.arg = arg
            return ''

        app.client.get('/')
        assert route.arg is None

        app.client.get('/?arg=1')
        assert route.arg == '1'

        app.client.post('/')
        assert route.arg is None

        app.client.post('/', {'arg': '1'})
        assert route.arg is None

    def test_requestarg_file(self, newapp):
        app = newapp

        @app.route('/', methods=['POST'])
        @app.arg('arg', file=True)
        def route(arg=None):
            route.arg = arg
            return ''

        app.client.post('/')
        assert route.arg is None

        app.client.post('/', upload_files=[('arg', 'arg.txt', b'arg text')])
        assert isinstance(route.arg, FileStorage)
        assert route.arg.filename == 'arg.txt'

    def test_requestarg_json(self, newapp):
        app = newapp

        @app.route('/', methods=['POST'])
        @app.arg('arg', json=True)
        def route(arg=None):
            route.arg = arg
            return ''

        app.client.post_json('/', 1)
        assert route.arg is None

        app.client.post_json('/', [1])
        assert route.arg is None

        app.client.post_json('/', {'arg': 1})
        assert route.arg == 1

        app.client.post_json('/', {'arg': '1'})
        assert route.arg == '1'

    def test_requestarg_json_loader(self, newapp):
        app = newapp

        def json_loader(request):
            return {'arg': 'custom'}

        @app.route('/', methods=['POST'])
        @app.arg('arg', json=True, json_loader=json_loader)
        def route(arg=None):
            route.arg = arg
            return ''

        app.client.post_json('/', {'arg': '1'})
        assert route.arg == 'custom'

    def test_requestarg_converter(self, newapp):
        app = newapp

        @app.route('/', methods=['POST'])
        @app.arg('<int:arg>', json=True)
        def route(arg=None):
            route.arg = arg
            return ''

        app.client.post_json('/', {'arg': '1'})
        assert route.arg == 1

        app.client.post_json('/', {'arg': 1})
        assert route.arg == 1

        app.client.post_json('/', {'arg': None})
        assert route.arg is None

        app.client.post_json('/', {'arg': 'a'})
        assert route.arg is None

    def test_requestarg_custom_converter(self, newapp):
        app = newapp

        entity = {'id': 1}

        database = {
            1: entity,
        }

        class EntityLoader:
            def to_python(self, value):
                return database.get(int(value))

            def to_url(self, value):
                return value['id']

        @app.route('/')
        @app.arg('arg', converter=EntityLoader)
        def route(arg=None):
            route.arg = arg
            return ''

        app.client.get('/?arg=1')
        assert route.arg == entity

        assert url_for('route') == '/'

        with pytest.raises(TypeError):
            assert url_for('route', arg=1) == '/'

        assert url_for('route', arg=entity) == '/?arg=1'

    def test_requestarg_conflict(self, newapp):
        app = newapp

        with pytest.raises(ValueError):
            @app.route('/<int:id>')
            @app.arg('<int:id>')
            def index(id=None):
                pass

    def test_url_for(self, newapp):
        app = newapp

        @app.route('/')
        @app.arg('<float:arg>')
        def route(arg=None):
            route.arg = arg
            return ''

        assert url_for('route') == '/'
        assert url_for('route', arg=1) == '/?arg=1.0'
        assert url_for('route', arg=1.0) == '/?arg=1.0'
        with pytest.raises(ValueError):
            url_for('route', arg='a')

        assert url_for('route', arg=None) == '/'

    def test_requestarg_required(self, newapp):
        app = newapp

        @app.route('/')
        @app.arg('<int:arg>', required=True)
        def route(arg):
            route.arg = arg
            return ''

        assert app.client.get('/?arg=1').status_code == 200
        assert app.client.get('/', expect_errors=True).status_code == 404
        assert app.client.get('/?arg=a', expect_errors=True).status_code == 404

        assert url_for('route', arg=1) == '/?arg=1'

        with pytest.raises(BuildError):
            url_for('route')

        with pytest.raises(BuildError):
            url_for('route', arg=None)

        with pytest.raises(ValueError):
            url_for('route', arg='a')

    def test_convert_query_string_to_route_syntax(self):
        parser = parse_rule

        with pytest.raises(Exception):
            parser('')
        with pytest.raises(Exception):
            parser('&')
        with pytest.raises(Exception):
            parser('?')

        assert parser('arg') == '<arg>'
        assert parser('&arg') == '<arg>'
        assert parser('&arg=') == '<arg>'

        assert parser('?arg') == '<arg>'
        assert parser('?arg=') == '<arg>'
        assert parser('?arg=<') == '<arg>'
        assert parser('?arg=<>') == '<arg>'
        assert parser('?arg=<int') == '<int:arg>'
        assert parser('?arg=int>') == '<int:arg>'
        assert parser('?arg=int') == '<int:arg>'
        assert parser('?arg=<int>') == '<int:arg>'
        assert parser('?arg=string(length=2)') == '<string(length=2):arg>'
        assert parser('?arg=<string(length=2)>') == '<string(length=2):arg>'

        with pytest.raises(Exception):
            parser('?2arg')

        with pytest.raises(Exception):
            parser('?test**')

        with pytest.raises(Exception):
            parser('?<int>')

    def test_requestarg_preprocess(self, newapp):
        app = newapp

        @app.route('/')
        @app.arg('<int:arg>', preprocess=lambda v: -v)
        def route(arg):
            route.arg = arg
            return ''

        assert url_for('route', arg=1) == '/?arg=1'

        app.client.get('/?arg=1')
        assert route.arg == -1
