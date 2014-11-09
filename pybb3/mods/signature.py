# -*- coding: utf-8 -*-
"""
Mod to enable signatures
"""
from __future__ import unicode_literals

from pybb3 import mod
from pybb3.database import Optional, LongStr


@mod.extend('User')
class SignatureModUser(object):
    sig = Optional(LongStr, column='user_sig')
    sig_bbcode_uid = Optional(str, 5, column='user_sig_bbcode_uid')
    sig_bbcode_bitfield = Optional(str, column='user_sig_bbcode_bitfield')
