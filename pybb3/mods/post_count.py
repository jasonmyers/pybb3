# -*- coding: utf-8 -*-
"""
Mod to add post/topic/view counts to Forum/Topic views
"""
from __future__ import unicode_literals

from pybb3 import mod
from pybb3.database import Required, INT


@mod.extend('Forum')
class PostCountModForum(object):
    posts = Required(int, default=0, size=INT.MEDIUMINT, unsigned=True, column='forum_posts')
    topics = Required(int, default=0, size=INT.MEDIUMINT, unsigned=True, column='forum_topics')
    topics_real = Required(int, default=0, size=INT.MEDIUMINT, unsigned=True, column='forum_topics_real')


@mod.extend('Post')
class PostCountModPost(object):
    postcount = Required(bool, default=True, column='post_postcount')


@mod.extend('Topic')
class PostCountModTopic(object):
    views = Required(int, size=INT.MEDIUMINT, default=0, column='topic_views')
    replies = Required(int, size=INT.MEDIUMINT, default=0, column='topic_replies')
    replies_real = Required(int, size=INT.MEDIUMINT, default=0, column='topic_replies_real')
