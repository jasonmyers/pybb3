# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pony.orm import *

from .database import db
from . import mod


@mod.extendable
class Post(db.Entity):
    id = PrimaryKey(int, auto=True)
    final_property = Optional(str)

    posters = Set('Person', column='person_id')
