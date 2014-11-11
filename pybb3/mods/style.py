# -*- coding: utf-8 -*-
"""
Mod to allow forum styles
"""
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import db, Optional, PrimaryKey, table_name


@mod.extendable
class Style(db.Entity):
    _table_ = table_name('styles')

    id = PrimaryKey(int, auto=True, column='style_id')
    name = Optional(str, column='style_name')

    users = Optional('StyleModUser', reverse='style')

    def __repr__(self):
        return '<Style({id}: {name!r})>'.format(id=self.id, name=self.name)


@mod.extend('User')
class StyleModUser(object):
    style = Optional('Style', column='user_style', reverse='users')
