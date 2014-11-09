# -*- coding: utf-8 -*-
"""
Mod to send notifications to users for replies

If Private Message Mod isinstalled, also allows notifications for PMs
"""
from __future__ import unicode_literals

from pybb3 import mod
from pybb3.database import (
    db, Choices, INT, Required, Optional, Set, table_name,
)


@mod.extend('User')
class NotifyUsersModUser(object):

    @mod.extendable
    class UserNotifyType(Choices(int, INT.TINYINT)):
        pass

    notify = Required(bool, default=False, column='user_notify')
    notify_type = Optional(int, size=INT.TINYINT, py_check=UserNotifyType.check, column='user_notify_type')

    watch_forums = Set('NotifyUsersModForum', table=table_name('forums_watch'), column='forum_id', reverse='watchers')
    watch_topics = Set('NotifyUserModTopic', table=table_name('topics_watch'), column='topic_id', reverse='watchers')


@mod.extend('Forum')
class NotifyUsersModForum(object):
    watchers = Set('NotifyUsersModUser', table=table_name('forums_watch'), column='user_id', reverse='watch_forums')


@mod.extend('Topic')
class NotifyUsersModTopic(object):
    watchers = Set('NotifyUsersModUser', table=table_name('topics_watch'), column='user_id', reverse='watch_topics')


if mod.installed('private_message'):
    @mod.extend('User')
    class NotifyUsersModUserPrivateMessage(object):
        notify_pm = Required(bool, default=True, column='user_notify_pm')
