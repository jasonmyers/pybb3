# -*- coding: utf-8 -*-
"""
Mod to add rules page to forums
"""
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import Optional, LongStr


@mod.extend('Forum')
class ForumRulesModForum(object):
    rules = Optional(LongStr, column='forum_rules')  # + Bitfields
    rules_link = Optional(str, column='forum_rules_link')
