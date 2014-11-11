# -*- coding: utf-8 -*-
"""
Mod to enable approvals before new topics become visible
"""
from __future__ import unicode_literals

from pybb3.mods import mod
from pybb3.database import Required


@mod.extend('Topic')
class ApproveTopicModTopic(object):
    approved = Required(bool, default=True, column='topic_approved')


@mod.extend('Post')
class ApproveTopicModPost(object):
    approved = Required(bool, default=True, column='post_approved')
