# -*- coding: utf-8 -*-
"""
Mod to enable new user activation
"""
from __future__ import unicode_literals

from pybb3 import mod
from pybb3.database import Optional


@mod.extend('User')
class UserActivationModUser(object):
    actkey = Optional(str, 32, column='user_actkey')
