# -*- coding: utf-8 -*-
"""
Mod to enable signatures
"""
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import Optional, LongStr, Required, INT


@mod.extend('User')
class SignatureModUser(object):
    sig = Optional(LongStr, column='user_sig')
    sig_bbcode_uid = Optional(str, 5, column='user_sig_bbcode_uid')
    sig_bbcode_bitfield = Optional(str, column='user_sig_bbcode_bitfield')


@mod.extend('Group')
class SignatureModGroup(object):
    sig_chars = Required(int, size=INT.MEDIUMINT, default=0, column='group_sig_chars')
