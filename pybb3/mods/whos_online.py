# -*- coding: utf-8 -*-
"""
Mod to add Who's Online to Forum display
"""
from __future__ import unicode_literals

from pybb3 import mod
from pybb3.database import Required


@mod.extend('User')
class WhosOnlineModUser(object):
    allow_viewonline = Required(bool, default=True, column='user_allow_viewonline')

