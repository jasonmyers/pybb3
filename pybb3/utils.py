# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
from __future__ import unicode_literals
import functools
import re

from flask import flash, request, current_app, abort
from pony.orm import db_session
import werkzeug.routing


try:
    from types import SimpleNamespace
except ImportError:
    class SimpleNamespace(object):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def __repr__(self):
            keys = sorted(self.__dict__)
            items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
            return "{}({})".format(type(self).__name__, ", ".join(items))

        def __eq__(self, other):
            return self.__dict__ == other.__dict__


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0} - {1}".format(
                getattr(form, field).label.text, error), category
            )


def as_context_processor(app, name=None):
    """ Adds the decorated function to the app/blueprint's context_processors
     under the given name

     If `name` is not provided, uses `func.__name__`
    """
    def wrapper(func):
        processor_name = name
        if name is None:
            processor_name = func.__name__

        @app.context_processor
        def processor():
            return {
                processor_name: func
            }

        return func
    return wrapper


def grouper(iterable, predicate):
    """ Yields lists of items from `iterable`, with adjacent items grouped
    together while `predicate(item)` is `True`

    Example::

        >>> items = [0, 0, 1, 2, 0, 2, 1]
        >>> predicate = lambda item: item > 0   # Group all non-zero items
        >>> list(grouper(items, predicate))
        [[0], [0], [1, 2], [0], [2, 1]]

    """
    group = []
    for item in iterable:
        if predicate(item):
            group.append(item)
        else:
            if group:
                yield group
                group = []
            yield [item]
    if group:
        yield group


def nbsp_indent(text):
    """ Replace spaces at the start of lines with `&nbsp;`s

    Example::

        >>> text = '''
        a a
          b b
            c c
        '''

        >>> print(nbsp_indent(text))
        a a
        &nbsp;&nbsp;b b
        &nbsp;&nbsp;&nbsp;&nbsp;c c

    """
    pattern = re.compile('^ +', re.M)

    def replacer(match):
        return '&nbsp;' * len(match.group())

    return re.sub(pattern, replacer, text)


def optional_string_id(value):
    """ Coerces a string id into an int, converting falsy values (except 0)
    into None

    Example::

        >>> optional_string_id(0)
        0
        >>> optional_string_id(1)
        1
        >>> optional_string_id('1')
        1
        >>> optional_string_id('None')
        None
        >>> optional_string_id(None)
        None
        >>> optional_string_id('')
        None
        >>> optional_string_id('a')
        ValueError

    Useful for coercing optional db `ids` from strings to ints, where the input
    id may be coming from a url query string, and `None` may be specified as
    a falsy-string, such as `''` or `'None'`

    """
    try:
        return int(value)
    except (TypeError, ValueError):
        if value in (None, 'None', ''):
            return None
        raise


def pony_entity_from_form(cls, form, **kwargs):
    """ Given a pony Entity class and a wtform instance, returns a new pony
    entity using `form.populate_obj`

    Any `kwargs` provided will override any form data on the final entity

    Note:: We can't use `form.populate_obj(pony_entity)` directly, since pony
    entities require all required attributes to be specified in the initial
    constructor, and `populate_obj` uses `setattr` after instantiation.
    So we build a temporary object first, and finally pass that object's
    attributes into the pony entity constructor

    Note:: This performs no form validation, so make sure the form is validated
    before use

    """
    temp = SimpleNamespace()
    form.populate_obj(temp)
    temp.__dict__.update(kwargs)
    return cls(**temp.__dict__)
