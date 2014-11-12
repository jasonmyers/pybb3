# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest

from pybb3.database import table_name, table_prefix, Choices, INT


class TestChoices:

    def test_choices(self):

        assert Choices.valid_choices_key('GET')
        assert not Choices.valid_choices_key('get')
        assert not Choices.valid_choices_key('Get')

        class Method(Choices):
            GET = 1
            POST = 2
            not_a_choice = 3

        assert Method.GET == 1
        assert Method.check(1)
        assert Method.check(Method.POST)
        assert not Method.check(4)

    def test_choices_collections(self):

        class Method(Choices):
            GET = 1
            POST = 2
            not_a_choice = 3

        assert Method.items() == [('GET', 1), ('POST', 2)]
        assert Method.keys() == ['GET', 'POST']
        assert Method.values() == [1, 2]
        assert Method.values_set() == {1, 2}

        class Method(Choices):
            GET = 2
            POST = 1
            not_a_choice = 3

        assert Method.items() == [('POST', 1), ('GET', 2)]
        assert Method.keys() == ['POST', 'GET']
        assert Method.values() == [1, 2]
        assert Method.values_set() == {1, 2}

        class Method(Choices):
            GET = 2
            POST = 1
            not_a_choice = 3

            @staticmethod
            def sort_key(kv):
                return kv[0]

        assert Method.items() == [('GET', 2), ('POST', 1)]
        assert Method.keys() == ['GET', 'POST']
        assert Method.values() == [2, 1]
        assert Method.values_set() == {2, 1}

    def test_choices_subclass(self):
        class Method(Choices):
            GET = 1
            POST = 2

        class ExtraMethod(Method):
            HEAD = 3

        assert ExtraMethod.items() == [('GET', 1), ('POST', 2), ('HEAD', 3)]
        assert ExtraMethod.keys() == ['GET', 'POST', 'HEAD']
        assert ExtraMethod.values() == [1, 2, 3]
        assert ExtraMethod.values_set() == {1, 2, 3}

        with pytest.raises(ValueError):
            class RedefinedKey(Method):
                GET = 3

        with pytest.raises(ValueError):
            class RedefinedValue(Method):
                HEAD = 1

    def test_choices_instance(self):
        assert Choices.__class__ is Choices().__class__
        assert not isinstance(Choices(), Choices)

        str_choices = Choices(str, 10, unsigned=True)
        assert str_choices.type == str
        assert str_choices.size == 10
        assert str_choices.unsigned is None

        int_choices = Choices(int, 4, unsigned=True)
        assert int_choices.type == int
        assert int_choices.size == 4
        assert int_choices.unsigned is True

        with pytest.raises(ValueError):
            Choices(size=10)

        with pytest.raises(ValueError):
            Choices(unsigned=True)

    def test_choices_type_constraint(self):

        class Method(Choices(int)):
            GET = 1
            POST = 2

        with pytest.raises(ValueError):
            class Method(Choices(int)):
                GET = '1'
                POST = 2

        with pytest.raises(ValueError):
            class Method(Choices(str)):
                GET = 1
                POST = 2

        class Method(Choices(int)):
            GET = 1
            POST = 2

        with pytest.raises(ValueError):
            class ExtraMethod(Method):
                HEAD = '1'

    def test_choices_size_constraint(self):

        assert Choices.size is None
        assert Choices().size is None
        assert Choices(int).size == INT.INTEGER
        assert Choices(str).size == 255

        class Method(Choices(str, 4)):
            GET = 'get'
            POST = 'post'

        with pytest.raises(ValueError):
            class Method(Choices(str, 4)):
                GET = 'get'
                POST = 'post'
                OPTION = 'option'

        class Method(Choices(int, 2)):  # 2 bits
            GET = 1
            POST = 2

        with pytest.raises(ValueError):
            class ExtraMethod(Method):
                OPTION = 4

        with pytest.raises(ValueError):
            class Method(Choices(int, 2)):  # 2 bits
                GET = 4

    def test_choices_size_constraint_unsigned(self):
        class Method(Choices(int, 2, unsigned=True)):
            GET = 6
            POST = 7

        with pytest.raises(ValueError):
            class Method(Choices(int, 2, unsigned=True)):
                GET = 7
                POST = 8


class TestDatabase:

    def test_table_name(self):
        assert table_name('foo') == table_prefix + 'foo'
