# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pony.orm import *

from . import mod
from .extensions import db


class INT:
    TINYINT = 8         # 8 bit - TINYINT in MySQL
    SMALLINT = 16       # 16 bit - SMALLINT in MySQL
    MEDIUMINT = 24      # 24 bit - MEDIUMINT in MySQL
    INTEGER = 32        # 32 bit - INTEGER in MySQL
    BIGINT = 64         # 64 bit - BIGINT in MySQL


table_prefix = 'pybb3'


def table_name(table):
    return '{table_prefix}_{table_name}'.format(
        table_prefix=table_prefix,
        table_name=table_name,
    )


class ChoicesMeta(type):

    def __new__(mcs, name, bases, cls_dict):
        """ Do some validation on the keys and values in the Choices class

            All values should be of the same type
            All keys should be unique among base classes
            All values should be unique among base classes
            All values should comply with the given constraints (if any)

        """
        choices = [(key, value) for key, value in cls_dict.items() if ChoicesMeta.valid_choices_key(key)]
        if choices:
            keys, values = zip(*choices)
            keys_set, values_set = set(keys), set(values)

            # Enforce that all values are of the same base type (or None) among all base classes
            value_types_set = {value.__class__.__mro__[-2] for value in values if value is not None}
            if len(value_types_set) > 1:
                raise ValueError('All Choices values for {} must be of the same type. Found: {}'.format(
                    mod.extended_class_name_pretty(name),
                    ', '.join(t.__name__ for t in value_types_set)
                ))

            # Check for value collisions in the given class
            collision_errors = []

            if len(values) != len(values_set):
                value_collisions = {value for value in values if values.count(value) > 1}
                collision_errors.append(
                    'Choices value collision: {values} defined twice in {cls}'.format(
                        values=', '.join(repr(v) for v in value_collisions),
                        cls=mod.extended_class_name_pretty(name),
                    ))

            for base in bases:
                # Enforce that keys and values are unique among all base classes
                base_choices = [(key, value) for key, value in base.__dict__.items() if ChoicesMeta.valid_choices_key(key)]
                if not base_choices:
                    continue
                base_keys, base_values = zip(*base_choices)
                base_keys_set, base_values_set = set(base_keys), set(base_values)

                base_value_types_set = {value.__class__.__mro__[-2] for value in base_values if value is not None}

                if len(value_types_set | base_value_types_set) > 1:
                    raise ValueError('All Choices values for {}({}) must be of the same type. Found: {}'.format(
                        mod.extended_class_name_pretty(name),
                        mod.extended_class_name_pretty(base),
                        ', '.join(t.__name__ for t in value_types_set | base_value_types_set)
                    ))

                # Check for key collisions between given class and base classes
                key_collisions = keys_set & base_keys_set
                if key_collisions:
                    collision_errors.append(
                        'Choices key collision: {keys} defined in both {cls} and {base}'.format(
                            keys=', '.join(repr(k) for k in key_collisions),
                            cls=mod.extended_class_name_pretty(name),
                            base=base.__name__,
                        ))

                # Check for value collisions between given class and base classes
                value_collisions = values_set & base_values_set
                if value_collisions:
                    collision_errors.append(
                        'Choices value collision: {values} defined in both {cls} and {base}'.format(
                            values=', '.join(repr(v) for v in value_collisions),
                            cls=mod.extended_class_name_pretty(name),
                            base=base.__name__,
                        ))

            if collision_errors:
                raise ValueError('Found collisions among Choices classes:\n' + '\n'.join(error for error in collision_errors))

        new_class = super(ChoicesMeta, mcs).__new__(mcs, name, bases, cls_dict)

        if choices:
            # Validate any constraints
            for value in values:
                new_class.validate_constraints(value)

        return new_class

    def __str__(cls):
        constraints = [
            constraint for constraint in [
                cls._type and cls._type.__name__,
                cls._size,
                'unsigned' if cls._unsigned else None,
            ] if constraint is not None]
        constraint_display = ''
        if constraints:
            constraint_display = '({})'.format(' '.join(str(c) for c in constraints))
        try:
            options = ', '.join('{}={}'.format(key, value) for key, value in cls.options())
        except TypeError:
            options = ''
        return "<{name}{constraints}: {options}>".format(
            name=mod.extended_class_name_pretty(cls),
            constraints=constraint_display,
            options=options
        )

    _type = None
    _size = None
    _unsigned = False

    @staticmethod
    def valid_choices_key(key):
        return key and key.isupper() and not key.startswith('_')

    def options(cls):
        if cls.__options is None:
            cls.__options = [
                (key, value)
                for base in cls.__mro__
                for key, value in base.__dict__.items()
                if ChoicesMeta.valid_choices_key(key)
            ]
            if cls.__sort_key:
                cls.__options = sorted(cls.__options, key=cls.__sort_key)

        return cls.__options
    __sort_key = lambda self, kv: kv[1]
    __options = None

    def keys(cls):
        if cls.__keys is None:
            cls.__keys = [key for key, value in cls.options()]
        return cls.__keys
    __keys = None

    def values(cls):
        if cls.__values is None:
            cls.__values = [value for key, value in cls.options()]
        return cls.__values
    __values = None

    def values_set(cls):
        if cls.__values_set is None:
            cls.__values_set = frozenset(cls.values())
        return cls.__values_set
    __values_set = None

    def check(cls, value):
        return value in cls.values_set()

    def validate_constraints(cls, value):
        if value is None:
            return
        if cls._type is not None:
            if not isinstance(value, cls._type):
                raise ValueError('{} requires {} values, found {!r}'.format(
                    cls, cls._type.__name__, value))
        if cls._size is not None:
            cls.validate_size_constraint(value)

    def validate_size_constraint(cls, value):
        if cls._type is str:
            if not len(value) <= cls._size:
                raise ValueError('Max length for {} is {}, found {!r} (len={})'.format(
                    cls, cls._size, value, len(value)
                ))
        if cls._type is int:
            bits = cls._size * 2 if cls._unsigned else cls._size
            if not value.bit_length() < bits:
                raise ValueError('Max bits for {} is {}, found {!r} (bits={})'.format(
                    cls, bits, value, value.bit_length()
                ))


class Choices(metaclass=ChoicesMeta):

    def __new__(cls, type=None, size=None, unsigned=False):
        """ If you instantiate `Choices`, you'll get back another `Choices` class
            (not instance!) with the type/size/unsigned values set.

            Usage::

                >>> Choices
                <class Choices>
                >>> Choices(int)
                <class Choices(int)>
                >>> Choices(int, 16)
                <class Choices(int 16)>
        """
        if type is None:
            size = None
            unsigned = False
        if type is int and size is None:
            size = INT.INTEGER
        if type is str and size is None:
            size = 255

        cls_dict = dict(cls.__dict__)
        cls_dict['_type'] = type
        cls_dict['_size'] = size
        cls_dict['_unsigned'] = unsigned

        return ChoicesMeta(cls.__name__, cls.__bases__, cls_dict)
