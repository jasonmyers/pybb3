# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from pony.orm import Required
from flask_wtf import Form
from wtforms import StringField

from pybb3.utils import (
    grouper, nbsp_indent, optional_string_id, pony_entity_from_form,
)


class TestUtils:

    def test_grouper(self):
        assert list(grouper([], lambda item: True)) == []
        assert list(grouper([], lambda item: False)) == []

        assert list(grouper([0], lambda item: True)) == [[0]]
        assert list(grouper([0], lambda item: False)) == [[0]]

        assert list(grouper([1, 2, 3, 4, 5], lambda item: True)) == [
            [1, 2, 3, 4, 5]
        ]
        assert list(grouper([1, 2, 3, 4, 5], lambda item: False)) == [
            [1], [2], [3], [4], [5]
        ]

        assert list(grouper([0, 0, 1, 2, 0, 2, 1], lambda item: item > 0)) == [
            [0], [0], [1, 2], [0], [2, 1]
        ]
        assert list(grouper([0, 0, 1, 2, 0, 2, 1], lambda item: item == 0)) == [
            [0, 0], [1], [2], [0], [2], [1]
        ]

    def test_nbsp_indent(self):
        assert nbsp_indent('') == ''
        assert nbsp_indent(' ') == '&nbsp;'
        assert nbsp_indent('  ') == '&nbsp;&nbsp;'
        assert nbsp_indent('a') == 'a'
        assert nbsp_indent(' a') == '&nbsp;a'
        assert nbsp_indent('  a') == '&nbsp;&nbsp;a'
        assert nbsp_indent('  a a') == '&nbsp;&nbsp;a a'
        assert nbsp_indent('a\n') == 'a\n'
        assert nbsp_indent('a\n ') == 'a\n&nbsp;'
        assert nbsp_indent('a a\n b b\n  c c') == 'a a\n&nbsp;b b\n&nbsp;&nbsp;c c'

    def test_optional_string_id(self):
        assert optional_string_id(0) == 0
        assert optional_string_id(1) == 1
        assert optional_string_id('1') == 1
        assert optional_string_id('None') is None
        assert optional_string_id(None) is None
        assert optional_string_id('') is None
        with pytest.raises(ValueError):
            optional_string_id('a')

    def test_pony_entity_from_form(self, newdb):
        db = newdb

        class Topic(db.Entity):
            name = Required(str)

            @classmethod
            def from_form(cls, form, **kwargs):
                return pony_entity_from_form(cls, form, **kwargs)

        db.generate_mapping(create_tables=True)

        class TopicForm(Form):
            name = StringField('Name')

        form = TopicForm(name='topic')

        with db.session:
            with pytest.raises(ValueError):
                topic = Topic()
                topic.name = 'topic'

            with pytest.raises(ValueError):
                topic = Topic()
                topic = form.populate_obj(topic)

        with db.session:
            topic = pony_entity_from_form(Topic, form)

        assert topic.name == 'topic'
        assert topic.id is not None

        with db.session:
            topic = Topic.from_form(form)

        assert topic.name == 'topic'
        assert topic.id is not None
