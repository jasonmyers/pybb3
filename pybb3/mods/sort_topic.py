# -*- coding: utf-8 -*-
"""
Mod to enable sorting of topics and posts
"""
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import Choices, INT, Optional


@mod.extend('User')
class SortTopicMod(object):

    topic_show_days = Optional(int, size=INT.SMALLINT, unsigned=True, column='user_topic_show_days')
    post_show_days = Optional(int, size=INT.SMALLINT, unsigned=True, column='user_post_show_days')

    @mod.extendable
    class UserSortByType(Choices(str, 1)):
        TIME = 't'  # Default
        AUTHOR = 'a'
        SUBJECT = 's'
    topic_sortby_type = Optional(str, UserSortByType.size, py_check=UserSortByType.check, column='user_topic_sortby_type')
    post_sortby_type = Optional(str, UserSortByType.size, py_check=UserSortByType.check, column='user_post_sortby_type')

    @mod.extendable
    class UserSortByDir(Choices(str, 1)):
        ASCENDING = 'a'  # Default
        DESCENDING = 'd'
    topic_sortby_dir = Optional(str, UserSortByDir.size, py_check=UserSortByDir.check, column='user_topic_sortby_dir')
    post_sortby_dir = Optional(str, UserSortByDir.size, py_check=UserSortByDir.check, column='user_post_sortby_dir')

