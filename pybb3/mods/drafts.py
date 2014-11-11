# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from pybb3.mods import mod
from pybb3.database import db, Optional, table_name, Required, PrimaryKey, Set


@mod.extendable
class Draft(db.Entity):
    _table_ = table_name('drafts')

    id = PrimaryKey(int, auto=True, column='draft_id')

    user = Required('DraftsModUser', column='user_id', reverse='drafts')
    topic = Optional('DraftsModTopic', column='topic_id', reverse='drafts')
    forum = Optional('DraftsModForum', column='forum_id', reverse='drafts')

    save_time = Required(datetime.datetime, default=datetime.datetime.utcnow, column='save_time')

    def __repr__(self):
        return '<Draft({id})>'.format(username=self.username)


@mod.extend('User')
class DraftsModUser(object):
    drafts = Set('Draft', reverse='user')


@mod.extend('Topic')
class DraftsModTopic(object):
    drafts = Set('Draft', reverse='topic')


@mod.extend('Forum')
class DraftsModForum(object):
    drafts = Set('Draft', reverse='forum')
