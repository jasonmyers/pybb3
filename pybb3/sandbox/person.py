# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pony.orm import *

from .database import db, Choices, INT
from . import mod


class PersonMixin(object):
    is_authenticated = False

    def logged_in(self):
        return True


@mod.extendable
class Person(PersonMixin, db.Entity):

    @mod.extendable
    class PersonType(Choices(int, INT.TINYINT)):
        HUMAN = 0
        MINERAL = 1

    person_id = PrimaryKey(int, auto=True)
    final_property = Optional(str)

    posted_in = Set('Post', column='post_id')
