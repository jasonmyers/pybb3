# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import db, table_name, PrimaryKey, Required


@mod.extendable
class Disallow(db.Entity):
    _table_ = table_name('disallow')

    id = PrimaryKey(int, auto=True, column='disallow_id')
    username = Required(str, column='disallow_username')

    def __repr__(self):
        return '<Disallow({id}: {username!r})>'.format(
            id=self.id, username=self.username)
