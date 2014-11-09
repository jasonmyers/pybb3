# -*- coding: utf-8 -*-
"""
Mod to allow marking as read
"""
from __future__ import unicode_literals

import datetime

from pybb3 import mod
from pybb3.database import Optional, Set, Required, PrimaryKey, table_name


mod.require('last_post')


@mod.extend('User')
class MarkAsReadModUser(object):
    lastmark = Optional(datetime.datetime, column='user_lastmark')

    tracked_forums = Set('ForumTrack', reverse='user')
    tracked_topics = Set('ForumTrack', reverse='user')


@mod.extend('Forum')
class MarkAsReadModForum(object):
    trackers = Set('ForumTrack', reverse='forum')
    topic_trackers = Set('TopicTrack', reverse='forum')


@mod.extend('Topic')
class MarkAsReadModTopic(object):
    trackers = Set('TopicTrack', reverse='topic')


@mod.extendable
class ForumTrack(object):
    _table_ = table_name('forums_track')

    user = Required('MarkAsReadModUser', column='user_id', reverse='tracked_forums')
    forum = Required('MarkAsReadModForum', column='forum_id', reverse='trackers')
    PrimaryKey(user, forum)

    mark_time = Required(datetime.datetime, default=datetime.datetime.utcnow, column='mark_time')

    def __repr__(self):
        return '<ForumTrack({id})>'.format(id=self.id)


@mod.extendable
class TopicTrack(object):
    _table_ = table_name('topics_track')

    user = Required('MarkAsReadModUser', column='user_id', reverse='tracked_topics')
    topic = Required('MarkAsReadModTopic', column='topic_id', reverse='trackers')
    PrimaryKey(user, topic)

    forum = Required('MarkAsReadModForum', column='forum_id', reverse='topic_trackers')

    mark_time = Required(datetime.datetime, default=datetime.datetime.utcnow, column='mark_time')

    def __repr__(self):
        return '<TopicTrack({id})>'.format(id=self.id)
