# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .. import mod
from ..database import db, Optional


__version__ = '0.0.1'


@mod.extendable
class Icon(db.Entity):
    picture = Optional(str)
