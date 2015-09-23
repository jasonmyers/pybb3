# -*- coding: utf-8 -*-
"""
Flask extension to provide automatic extraction and conversion of query params
and request data from `request.args`, `request.form`, `request.files` and
json data.

This extension allows you to specify parameters to extract from
the request in the same manner that you can extract values from flask url
routes, for example if you have ever wanted to write:

    @app.route('/?page=<int:page>')
    def show(page=1):
        ...

Example usage, showing equivalents between routes without and with this extension::

    # Basic usage
    @app.route('/old')
    def old():
        arg = request.args.get('arg', None)

    @app.route('/new')
    @app.arg('arg')
    def new(arg=None):
        ...

    # Conversion
    @app.route('/old')
    def old():
        arg = int(request.args.get('arg', 0))

    @app.route('/new')
    @app.arg('<int:arg>')
    def new(arg=0):
        ...

    # Required
    @app.route('/old')
    def old():
        arg = request.args.get('arg', None)
        if arg is None:
            abort(404)

    @app.route('/new')
    @arg('arg', required=True)
        ...

    # Methods
    @app.route('/old', methods=['GET', 'POST'])
    def old():
        arg = None
        if request.method == 'GET':
            arg = request.args.get('arg', None)

    @app.route('/new', methods=['GET', 'POST'])
    @app.arg('arg', methods=['GET'])
    def new(arg=None):
        ...

    # Preprocessing
    @app.route('/old')
    def old():
        arg = int(request.args.get('arg', 0))
        if arg < 0:
            arg = 0

    @app.route('/new')
    @app.arg('<int:arg>', preprocess=lambda arg: 0 of arg < 0 else arg)
    def new(arg=0):
        ...


See `:func:arg` for more usage.

"""
from __future__ import unicode_literals

from collections import defaultdict
import re
from flask.helpers import _endpoint_from_view_func

import werkzeug.routing
import werkzeug.exceptions

from flask import request, Flask, Blueprint


def arg(app, rule, **options):
    """ View decorator to provide automatic extraction and conversion of
    request data from `request.args`, `request.form`, `request.files` and json
    data.

    `app`:  The app or blueprint to register this request arg with
    `rule`:  The name of the arg, using the same format as capturing and
        converting args in a `route` decorator (e.g. `'<int:name>'`)
    `**options`:
        `required`:  If `True`, this arg is required and will raise 404 for
            routes and a `BuildError` for `url_for` if not present or if
            conversion fails (similar to required parameters in regular
            routes).  (default `False`)
        `methods`:  Restrict argument extraction to only these http methods
            (defaults to the allowed methods for this view)
        `file`:  Argument is a file, and found in `request.files` (default `False`)
        `json`:  Request is json, and argument is found in `request.get_json()` (default `False`)
        `json_loader`:  Function to load json given a request (default `request.get_json()`)
        `converter`:  Argument converter (usually parsed from `rule`).  Should implement
            `to_python()` and `to_url()` methods.  See `werkzeug.routing.BaseConverter`
        `preprocess`:  Function to preprocess the arg value before being
            passed to the view (after any conversion)

    Tip:: This decorator is added as a method on both `Flask` and `Blueprint`,
    and is to be used as you would the `route` decorator.

    Basic usage, given a url like `/forums/1?page=5`, instead of::

        @app.route('/forums/<int:id>')
        def forum(id):
            page = int(request.args.get('page', 0))
            ...

    you can register the `page` query param to be extracted with::

        @app.route('/forums/<int:id>')
        @app.arg('<int:page>')
        def forum(id, page=0):
            ...

    and it will be passed into your view as a keyword arg, and (optionally)
    converted using the specified converter (`IntegerConverter` in this example).
    The following syntax is also supported::

        @app.arg('?page=<int>')

    Which may give clearer intent when reading routes.

    Important:: Make sure any `@app.arg` decorators come after (below)
    any `@app.route` decorators.

    Note::  If you specify a converter and the conversion fails (e.g. sending
    a non-int to `<int:arg>`), the original value will be retained in
    e.g. `request.args`, however no value will be sent to your view.  This is
    different from the behaviour of routes where conversion fails, and a 404
    is raised.

    You may specify unconverted params with any of::

        @arg('<page>')  # Same as @route sytax
        @arg('page')    # Just the name
        @arg('?page=')  # Query param syntax omitting converter

    By default, `arg` will look for the parameters in any `method` that
    your route supports.  For example, if your `@route` specifies
    `methods=['GET', 'POST']`, `arg` will look in `request.args` (for
    `GET`) and `request.form` (for `POST`).  You can supply a `methods` param
    to `arg` to restrict it to only extract parameters for certain
    methods, and skip others.

    If the arg is a file, you should use `@arg(..., file=True)` to tell
    `arg` to get the data from `request.files`.

    If the request is json, you should use `@arg(..., json=True)` to tell
    `arg` to get the data from `request.get_json()`  The json data
    must be a dictionary with the arg being one of the keys..

    Note:: If you need to customize the `request.get_json()` call, you can
    specify a `json_loader` callback that takes the request and returns the
    loaded json.

    Tip:: `url_for` is also aware of any converters registered with this
    decorator, and constructed urls will pass through the converter's `to_url`
    function.  e.g. given the above route, this will fail with a `ValueError`::

        url_for('forum', id=5, page="a")

    """
    def inner(view):
        if isinstance(app, Blueprint):
            app.record(lambda state: register_requestarg_on_view(state.app, view, rule, **options))
        else:
            register_requestarg_on_view(app, view, rule, **options)
        return view
    return inner

Flask.arg = arg
Blueprint.arg = arg


def default_json_loader(req):
    return req.get_json()


def register_requestarg_on_view(app, view, rule, **options):
    # Parse the given param rule, extracting any converter specified
    # '<int:page>' -> ('int', None, 'page')
    rule = parse_rule(rule)
    converter_name, converter_args, param_name = next(werkzeug.routing.parse_rule(rule))

    converter = options.get('converter')
    if converter:
        # Specified a custom converter
        try:
            # Check if is a class
            converter_name = converter.__name__
            try:
                converter = converter(map=app.url_map)
            except TypeError:
                converter = converter()
        except AttributeError:
            converter_name = converter.__class__.__name__

        if converter_name not in app.url_map.converters:
            app.url_map.converters[converter_name] = converter
    else:
        if converter_name:
            # 'int' -> <class IntegerConverter>
            Converter = app.url_map.converters[converter_name]
            if converter_args:
                c_args, c_kwargs = werkzeug.routing.parse_converter_args(converter_args)
                converter = Converter(app.url_map, *c_args, **c_kwargs)
            else:
                converter = Converter(app.url_map)

    options['converter'] = converter

    # Register this param/options on the view directly, so we can pull
    # if off later during `add_url_rule`
    try:
        view._requestargs[param_name] = options
    except AttributeError:
        view._requestargs = {param_name: options}


def parse_rule(qs):
    """ Covert `'?page=<int>'` to `'<int:page>'`

    """
    original = qs

    if qs.startswith('<'):
        # Assume already formatted as `'<int:page>'`
        return qs

    qs = qs.strip('?&=')

    if not qs:
        raise Exception('Arg name required, got "{}"'.format(original))

    try:
        arg, converter = qs.split('=', 1)
        converter = converter.strip('<>')
    except ValueError:
        arg, converter = qs, None

    if not py_identifier_re.match(arg):
        raise Exception(
            'Arg name must be a valid Python identifier, got "{}"'.format(arg))

    fmt = "<{arg}>"
    if converter:
        fmt = "<{converter}:{arg}>"

    return fmt.format(converter=converter, arg=arg)

py_identifier_re = re.compile(r"^[^\d\W]\w*\Z")


class RequestArg(object):

    def __init__(self, app=None):
        self.app = app

        # {'view.endpoint': {'param': dict(options)}}
        self.endpoints = defaultdict(dict)

        self.patch_add_url_rule(Flask)
        self.patch_add_url_rule(Blueprint)

        if app is not None:
            self.init_app(app)

    def patch_add_url_rule(self, cls):
        """ Intercept `add_url_rule` to pull the requestargs options off the
        decorated view, and store it under the given endpoint """
        original_add_url_rule = cls.add_url_rule

        def add_url_rule(_self, rule, endpoint=None, view_func=None, **options):
            requestargs = getattr(view_func, '_requestargs', None)

            if requestargs:
                requestargs_endpoint = endpoint
                if requestargs_endpoint is None:
                    requestargs_endpoint = _endpoint_from_view_func(view_func)
                if requestargs_endpoint not in self.endpoints:
                    self.endpoints[requestargs_endpoint] = requestargs

                self.check_for_requestarg_conflicts(requestargs, rule, requestargs_endpoint)

            return original_add_url_rule(_self, rule, endpoint=endpoint, view_func=view_func, **options)

        cls.add_url_rule = add_url_rule

    def check_for_requestarg_conflicts(self, args, rule, endpoint):
        """ Make sure any registered request args don't conflict with a
        captured parameter name in the given `@route` rule, e.g. this should
        fail::

            @app.route('/post/<int:id>')
            @app.arg('<int:id>')
            def post(id):
                ...

        Because this would be ambiguous: `/post/1?id=2`

        """
        route_params = {
            param_name
            for converter_name, converter_args, param_name
            in werkzeug.routing.parse_rule(rule)
        }
        conflicting_args = set(args) & route_params

        if conflicting_args:
            raise ValueError(
                '@arg {!r} conflicts with a parameter in @route({!r}) '
                'for endpoint {!r}'.format(
                    conflicting_args.pop(), rule, endpoint
                )
            )

    def init_app(self, app):
        app.url_defaults(self.url_defaults)
        app.url_value_preprocessor(self.url_value_preprocessor)

    def url_defaults(self, endpoint, values):
        """ Intercept `url_for` kwargs and pass params through any converters """
        if endpoint not in self.endpoints:
            return

        args = self.endpoints[endpoint]

        extracted_kwargs = {}

        for arg, options in args.items():
            arg_value = values.get(arg)

            if arg_value is not None:
                converter = options.get('converter')
                if converter:
                    arg_value = converter.to_url(arg_value)

                extracted_kwargs[arg] = arg_value

            if options.get('required', False) and extracted_kwargs.get(arg) is None:
                raise werkzeug.routing.BuildError(endpoint, values, None)

        values.update(extracted_kwargs)

    def url_value_preprocessor(self, endpoint, values):
        """ Preprocess view kwargs and inject any converted args """
        if endpoint not in self.endpoints:
            return

        args = self.endpoints[endpoint]

        extracted_kwargs = {}

        for arg, options in args.items():
            # Make sure we're not overwriting a keyword arg to the view with an extracted request arg
            assert arg not in values

            if options.get('methods') is not None and request.method not in options.get('methods'):
                continue

            if options.get('file', False):
                data = request.files
            elif options.get('json', False):
                data = options.get('json_loader', default_json_loader)(request)
                if not isinstance(data, dict):
                    # Skip if they're sending a json structure or value other than a dictionary
                    data = {}
            else:
                data = request.values

            arg_value = data.get(arg)

            if arg_value is not None:
                converter = options.get('converter')
                if converter:
                    try:
                        extracted_kwargs[arg] = converter.to_python(arg_value)
                    except:
                        # Incorrect type in url, leave the arg in `request.args`, but don't send as a kwargs
                        pass
                else:
                    extracted_kwargs[arg] = arg_value

                preprocessor = options.get('preprocess')
                if preprocessor and arg in extracted_kwargs:
                    extracted_kwargs[arg] = preprocessor(extracted_kwargs[arg])

            if options.get('required', False) and extracted_kwargs.get(arg) is None:
                raise werkzeug.exceptions.NotFound()

        values.update(extracted_kwargs)
