# -*- coding: utf-8 -*-
"""
Mod to convert passwords over to a new encryption scheme

Passwords are converted as users log in
"""
from __future__ import unicode_literals

from pybb3 import mod
from pybb3.database import Required


@mod.extend('User')
class ConvertPasswordsModUser(object):
    # Whether this password needs to be converted
    pass_convert = Required(bool, default=False, column='user_pass_convert')
