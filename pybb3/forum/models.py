# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pony.orm import db_session

from pybb3 import mod
from pybb3.database import (
    db, Required, Optional, Set, PrimaryKey, LongStr, INT,
    Choices, table_name
)
from pybb3.extensions import bcrypt


@mod.extendable
class Forum(db.Entity):
    _table_ = table_name('forums')

    @mod.extendable
    class ForumType(Choices(int, INT.TINYINT)):
        FORUM_CAT = 0
        FORUM_POST = 1
        FORUM_LINK = 2

    @mod.extendable
    class ForumStatus(Choices(int, INT.TINYINT)):
        pass

    id = PrimaryKey(int, auto=True, column='forum_id')  # Forum id=0 (global) required
    parent = Optional(lambda: Forum, column='parent_id', reverse='children')
    children = Set(lambda: Forum, reverse='parent')

    name = Required(str, column='forum_name')
    desc = Required(LongStr, column='forum_desc')  # + Bitfields
    link = Optional(str, column='forum_link')
    password = Optional(str, 40, column='forum_password')
    image = Optional(str, column='forum_image')
    topics_per_page = Required(int, size=INT.TINYINT, column='forum_topics_per_page')

    type = Required(int, default=0, size=INT.TINYINT, py_check=ForumType.check, column='forum_type')
    status = Required(int, default=0, size=INT.TINYINT, py_check=ForumStatus.check, column='forum_status')

    flags = Required(int, size=INT.TINYINT, default=32, column='forum_flags')
    display_on_index = Required(bool, default=True, column='display_on_index')
    enable_indexing = Required(bool, default=True, column='enable_indexing')
    enable_icons = Required(bool, default=True, column='enable_icons')

    enable_prune = Required(bool, default=False, column='enable_prune')
    prune_next = Required(int, default=0, column='prune_next')
    prune_days = Required(int, size=INT.TINYINT, default=0, column='prune_days')
    prune_viewed = Required(int, size=INT.TINYINT, default=0, column='prune_viewed')
    prune_freq = Required(int, size=INT.TINYINT, default=0, column='prune_freq')

    def __new__(cls, password=None, **kwargs):
        return super(Forum, cls).__new__(cls, **kwargs)

    def __init__(self, password=None, **kwargs):
        if password:
            self.set_password(password)
        else:
            self.password = None

    def __repr__(self):
        return '<Forum({id}: {name!r})>'.format(id=self.id, name=self.name)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)



# Make sure we have a global forum at id=0
with db_session:
    if not Forum[0]:
        Forum(
            id=0,
            parent=None,
            name='Global',
            desc='Top level forum',
            topics_per_page=0,
        )
