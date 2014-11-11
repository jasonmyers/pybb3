# -*- coding: utf-8 -*-
"""
Mod to allow bookmarking of topics
"""
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import Set, table_name


@mod.extend('User')
class BookmarkTopicsModUser(object):
    bookmarked_topics = Set('BookmarkTopicsModTopic', table=table_name('bookmarks'), column='topic_id', reverse='user_bookmarks')


@mod.extend('Topic')
class BookmarkTopicsModTopic(object):
    user_bookmarks = Set('BookmarkTopicsModUser', table=table_name('bookmarks'), column='user_id', reverse='bookmarked_topics')
