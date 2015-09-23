# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import werkzeug.routing
from flask import abort


class FlagConverter(werkzeug.routing.BaseConverter):
    """ Url converter for boolean flags, (e.g. ``?setting=true``)

    Presence of the flag is considered `True` (e.g., ``?setting=``)

    Flags set to "falsy string values" '0' or 'false' will return `False`

    Any other value (including '1' or 'true') will return `True`

    e.g. given::

        app.route('?show=<flag:show>')

    These will resolve to `show=False`::

        ?show=0
        ?show=false
        ?show=False

    These will resolve to `show=True`::

        ?show
        ?show=
        ?show=1
        ?show=true
        ?show=True
        ?show=<anything else>

    When generating urls with this converter, `1` and `0` will be used for `True`
    and `False` parameters respectively

    """

    def to_python(self, value):
        if value == '':
            # Presence of the parameter indicates True
            return True
        if value is None or str(value).lower() in ('0', 'false'):
            return False
        return True

    def to_url(self, value):
        if value == '':
            return '1'
        if str(value).lower() in ('0', 'false'):
            return '0'

        if value:
            return '1'
        else:
            return '0'


class EntityLoader(werkzeug.routing.BaseConverter):
    """ Base class for url converters that load entities from the database

        For routes, tries to load an entity with the given id, e.g. given an
        `EntityLoader` subclass that loads `Forum` entities::

            /forums/1

        will match this route::

            @app.route('/forums/<Forum:forum>')
            def forums(forum):
                ...

        Where the `forum` argument is a loaded `Forum[1]` instance, roughly
        equivalent to::

            @app.route('/forums/<int:forum>')
            def forums(forum):
                forum = Forum[forum]

        For `url_for`, either the `Forum` instance or an id can be used, e.g.::

            url_for('forums', forum=1) -> /forums/1
            url_for('forums', forum=Forum[1]) -> /forums/1

    """
    entity_class = None

    def to_python(self, value):
        entity = self.entity_class[value]
        if entity is None:
            abort(404)
        return entity

    def to_url(self, value):
        try:
            return str(value.id)  # TODO, more thorough pk support?
        except:
            return str(value)

    @classmethod
    def from_class(cls, entity_class):
        """ Generates a subclass of EntityLoader for a specific Entity class """
        return type('{}Loader'.format(entity_class.__name__), (cls,), {'entity_class': entity_class})
