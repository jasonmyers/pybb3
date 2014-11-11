# -*- coding: utf-8 -*-
"""
Mod to enable sorting of topics and posts
"""
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import Choices, INT, Optional


@mod.extend('User')
class SortTopicMod(object):

    @mod.extendable
    class UserSortByType(Choices(str, 1)):
        AUTHOR = 'a'
        SUBJECT = 's'
        TIME = 't'  # Default

    @mod.extendable
    class UserSortByDir(Choices(str, 1)):
        ASCENDING = 'a'  # Default
        DESCENDING = 'd'

    topic_show_days = Optional(int, INT.SMALLINT, unsigned=True, column='user_topic_show_days')
    topic_sortby_type = Optional(str, 1, py_check=UserSortByType.check, column='user_topic_sortby_type')
    topic_sortby_dir = Optional(str, 1, py_check=UserSortByDir.check, column='user_topic_sortby_dir')

    post_show_days = Optional(int, INT.SMALLINT, unsigned=True, column='user_post_show_days')
    post_sortby_type = Optional(str, 1, py_check=UserSortByType.check, column='user_post_sortby_type')
    post_sortby_dir = Optional(str, 1, py_check=UserSortByDir.check, column='user_post_sortby_dir')
