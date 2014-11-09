# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .. import mod
from ..database import db, Optional


@mod.extendable
class Icon(db.Entity):
    picture = Optional(str)
