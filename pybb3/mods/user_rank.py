# -*- coding: utf-8 -*-
"""
Mod to enable user rankings
"""
from __future__ import unicode_literals


from pybb3 import mod
from pybb3.database import db, Optional, PrimaryKey, Set, Required, INT, table_name


@mod.extend('User')
class UserRankModUser(object):
    rank = Optional('Rank', column='user_rank', reverse='users')


class Rank(db.Entity):
    _table_ = table_name('ranks')
    id = PrimaryKey(int, auto=True, column='rank_id')
    users = Set('UserRankModUser')
    title = Optional(str, column='rank_title')
    min = Required(int, INT.MEDIUMINT, default=0, column='rank_min')
    special = Required(bool, default=False, column='rank_special')
    image = Optional(str, column='rank_image')
