# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from pybb3.mods import mod
from pybb3.database import Optional


@mod.extend('User')
class UserColourModUser(object):
    colour = Optional(str, 6, column='user_colour')


@mod.extend('Group')
class UserColourModGroup(object):
    colour = Optional(str, 6, column='group_colour')
