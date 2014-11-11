# -*- coding: utf-8 -*-
"""
Mod that allows editing of posts
"""
from __future__ import unicode_literals

import datetime

from pybb3.mods import mod
from pybb3.database import Set, Optional, INT, Required


@mod.extend('Post')
class EditPostModPost(object):
    edit_time = Optional(datetime.datetime, column='post_edit_time')
    edit_reason = Optional(str, column='post_edit_reson')
    edit_user = Optional('EditPostModUser', column='post_edit_user', reverse='edited_posts')
    edit_count = Optional(int, size=INT.TINYINT, column='post_edit_count')
    edit_locked = Required(bool, default=False, column='post_edit_locked')


@mod.extend('User')
class EditPostModUser(object):
    edited_posts = Set('EditPostModPost', reverse='edit_user')
