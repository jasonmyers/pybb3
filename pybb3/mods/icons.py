# -*- coding: utf-8 -*-
"""
Mod to add icons to topics and posts
"""
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import (
    db, Required, Optional, PrimaryKey, INT, table_name, Set
)
from pybb3 import mod


@mod.extend('Topic')
class IconsModTopic(object):
    icon = Optional('TopicIconsModIcon', column='icon_id', reverse='topics')


@mod.extend('Post')
class IconsModPost(object):
    icon = Optional('TopicIconsModIcon', column='icon_id', reverse='posts')


@mod.extendable
class Icon(db.Entity):
    _table_ = table_name('icons')

    id = PrimaryKey(int, auto=True, column='icon_id')

    topics = Set('TopicIconsModTopic', reverse='icons')
    posts = Set('TopicIconsModPosts', reverse='icons')

    url = Optional(str, column='icon_url')
    width = Required(int, size=INT.TINYINT, default=0, column='icon_width')
    height = Required(int, size=INT.TINYINT, default=0, column='icon_height')
    order = Required(int, size=INT.MEDIUMINT, default=0, column='icon_order')

    display_on_posting = Required(bool, default=True, column='display_on_posting')

    def __repr__(self):
        return '<Icon({id}: {url!r})>'.format(id=self.id, name=self.url)
