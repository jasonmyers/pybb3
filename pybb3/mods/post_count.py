# -*- coding: utf-8 -*-
"""
Mod to add post/topic/view counts to Forum/Topic views
"""
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import Required, INT


@mod.extend('Forum')
class PostCountModForum(object):
    post_count = Required(int, size=INT.MEDIUMINT, default=0, unsigned=True, column='forum_posts')
    topic_count = Required(int, size=INT.MEDIUMINT, default=0, unsigned=True, column='forum_topics')
    topic_count_real = Required(int, size=INT.MEDIUMINT, default=0, unsigned=True, column='forum_topics_real')


@mod.extend('Post')
class PostCountModPost(object):
    post_count = Required(bool, default=True, column='post_postcount')


@mod.extend('Topic')
class PostCountModTopic(object):
    view_count = Required(int, size=INT.MEDIUMINT, default=0, column='topic_views')
    reply_count = Required(int, size=INT.MEDIUMINT, default=0, column='topic_replies')
    reply_count_real = Required(int, size=INT.MEDIUMINT, default=0, column='topic_replies_real')
