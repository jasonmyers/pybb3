# -*- coding: utf-8 -*-
"""
Mod to add avatars to users profiles and posts
"""
from __future__ import unicode_literals

from pybb3 import mod
from pybb3.database import Choices, INT, Optional


@mod.extend('User')
class AvatarsModUser(object):

    @mod.extendable
    class UserAvatarType(Choices(int, INT.TINYINT)):
        REMOTE = '?'
        GALLERY = '?'
        UPLOADED = '?'

    avatar = Optional(str, column='user_avatar')
    avatar_type = Optional(int, size=INT.TINYINT, py_check=UserAvatarType.check, column='user_avatar_type')
    avatar_width = Optional(int, size=INT.SMALLINT, unsigned=True, column='user_avatar_width')
    avatar_height = Optional(int, size=INT.SMALLINT, unsigned=True, column='user_avatar_height')
