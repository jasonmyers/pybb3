# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from pybb3.mods import mod
from pybb3.database import (
    db, Required, Optional, PrimaryKey, INT, Choices, table_name, Set
)


@mod.extendable
class Topic(db.Entity):
    _table_ = table_name('topics')

    id = PrimaryKey(int, auto=True, column='topic_id')

    forum = Required('Forum', column='forum_id', reverse='topics')
    poster = Required('User', column='topic_poster', reverse='topics')
    posts = Set('Post', reverse='topic')
    posters = Set('User', table=table_name('topics_posted'), column='user_id', reverse='topics_posted_in')

    title = Required(str, 100, column='topic_title')

    time = Required(datetime.datetime, default=datetime.datetime.utcnow, column='topic_time')
    time_limit = Required(int, default=0, column='topic_time_limit')

    @mod.extendable
    class TopicStatus(Choices(int, INT.TINYINT)):
        ITEM_UNLOCKED = 0
        ITEM_LOCKED = 1
        ITEM_MOVED = 2
    status = Required(int, size=TopicStatus.size, default=0, py_check=TopicStatus.check, column='topic_status')

    @mod.extendable
    class TopicType(Choices(int, INT.TINYINT)):
        POST_NORMAL = 0
        POST_STICKY = 1
        POST_ANNOUNCE = 2
        POST_GLOBAL = 3
    type = Required(int, size=TopicType.size, default=0, py_check=TopicType.check, column='topic_type')

    moved = Optional('Topic', column='topic_moved_id', reverse='moved_from')
    moved_from = Optional('Topic', reverse='moved')
    bumped = Required(bool, default=False, column='topic_bumped')
    bumper = Optional('User', column='topic_bumper', reverse='bumped_topics')

    logs = Set('Log', reverse='topic')

    def __repr__(self):
        return '<Topic({id}: {title!r})>'.format(id=self.id, name=self.title)

    def validate(self):
        if self.topic_type == Topic.TopicType.POST_GLOBAL:
            assert self.forum.id == 0

        if self.topic_status == Topic.TopicStatus.ITEM_MOVED:
            assert self.moved

    def before_insert(self):
        self.validate()

    def before_update(self):
        self.validate()
