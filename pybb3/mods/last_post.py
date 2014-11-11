# -*- coding: utf-8 -*-
"""
Mod to display last post in Forum and Topic views
"""
from __future__ import unicode_literals

import datetime

from pybb3.mods import mod
from pybb3.database import Optional, Set


@mod.extend('Forum')
class LastPostModForum(object):
    last_post = Optional('LastPostModPost', column='forum_last_post_id')
    last_post_subject = Optional(str, column='forum_last_post_subject')
    last_post_time = Optional(datetime.datetime, column='forum_last_post_time')

    last_poster = Optional('LastPostModUser', column='forum_last_poster_id')
    last_poster_name = Optional(str, column='forum_last_poster_name')
    last_poster_colour = Optional(str, 6, column='forum_last_poster_colour')


@mod.extend('User')
class LastPostModUser(object):
    last_poster_for_forums = Set('LastPostModForum', reverse='last_poster')
    last_poster_for_topics = Set('LastPostModTopic', reverse='last_poster')


@mod.extend('Post')
class LastPostModPost(object):
    last_post_for_forum = Optional('LastPostModForum', reverse='last_post')
    last_post_for_topic = Optional('LastPostModTopic', reverse='last_post')
    first_post_for_topic = Optional('LastPostModTopic', reverse='first_post')


@mod.extend('Topic')
class LastPostModTopic(object):
    first_post = Optional('LastPostModPost', column='topic_first_post_id', reverse='first_post_for_topic')
    first_poster_name = Optional(str, column='topic_first_poster_name')
    first_poster_colour = Optional(str, 6, column='topic_first_poster_colour')

    last_post = Optional('LastPostModPost', column='topic_last_post_id', reverse='last_post_for_topic')
    last_poster = Optional('LastPostModUser', column='topic_last_poster_id', reverse='last_poster_for_topics')
    last_poster_name = Optional(str, column='topic_last_poster_name')
    last_poster_colour = Optional(str, 6, column='topic_last_post_colour')
    last_post_subject = Optional(str, 100, column='topic_last_post_subject')
    last_post_time = Optional(datetime.datetime, column='topic_last_post_time')
    last_post_view_time = Optional(datetime.datetime, column='topic_last_post_view_time')
