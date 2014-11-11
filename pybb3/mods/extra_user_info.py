# -*- coding: utf-8 -*-
"""
Mod that adds extra info to user profiles (birthday, social media, etc)
"""
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import Optional, LongStr


@mod.extend('User')
class ExtraUserInfoModUser(object):
    birthday = Optional(str, 10, column='user_birthday')
    location = Optional(str, 100, column='user_from')
    icq = Optional(str, 15, column='user_icq')
    aim = Optional(str, column='user_aim')
    yim = Optional(str, column='user_yim')
    msnm = Optional(str, column='user_msnm')
    jabber = Optional(str, column='user_jabber')
    website = Optional(str, 200, column='user_website')
    occ = Optional(LongStr, column='user_occ')
    interests = Optional(LongStr, column='user_interests')
