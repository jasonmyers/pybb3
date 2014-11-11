# -*- coding: utf-8 -*-
"""
Mod to add avatars to users profiles and posts
"""
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import Choices, INT, Optional


@mod.extendable
class AvatarType(Choices(int, INT.TINYINT)):
    """
    REMOTE = ?
    GALLERY = ?
    UPLOADED = ?
    """
    pass


@mod.extend('User')
class AvatarsModUser(object):

    avatar = Optional(str, column='user_avatar')

    avatar_type = Optional(int, size=AvatarType.size, py_check=AvatarType.check, column='user_avatar_type')

    avatar_width = Optional(int, size=INT.SMALLINT, unsigned=True, column='user_avatar_width')
    avatar_height = Optional(int, size=INT.SMALLINT, unsigned=True, column='user_avatar_height')


@mod.extend('Group')
class AvatarsModGroup(object):
    avatar = Optional(str, column='group_avatar')

    avatar_type = Optional(int, size=AvatarType.size, py_check=AvatarType.check, column='group_avatar_type')

    avatar_width = Optional(int, size=INT.SMALLINT, unsigned=True, column='group_avatar_width')
    avatar_height = Optional(int, size=INT.SMALLINT, unsigned=True, column='group_avatar_height')
