# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from pony.orm import *

from .. import mod


@mod.extend('Post')
def extend(base):
    class RecentPostModPost(base):
        poster = Required('RecentPostModPerson', reverse='recent_poster_for')
    return RecentPostModPost


@mod.extend('Person')
def extend(base):
    class RecentPostModPerson(base):
        recent_poster_for = Optional('RecentPostModPost', reverse='poster')
    return RecentPostModPerson
