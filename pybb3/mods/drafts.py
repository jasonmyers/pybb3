# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from pybb3.mods import mod
from pybb3.database import db, Optional, table_name, Required, PrimaryKey, Set


@mod.extendable
class Draft(db.Entity):
    _table_ = table_name('drafts')

    id = PrimaryKey(int, auto=True, column='draft_id')

    user = Required('User', column='user_id', reverse='drafts')
    topic = Optional('Topic', column='topic_id', reverse='draft')
    forum = Optional('Forum', column='forum_id', reverse='fraft')

    save_time = Required(datetime.datetime, default=datetime.datetime.utcnow, column='save_time')

    def __repr__(self):
        return '<Draft({id})>'.format(username=self.username)
