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

    password = Optional(str)

    def __new__(cls, password=None, **kwargs):
        print('Person.__new__(password={}, **kwargs={})'.format(password, kwargs))
        password = cls.encrypt_password(password)
        return super(mod.extendable(Person), cls).__new__(cls, password=password, **kwargs)

    @classmethod
    def encrypt_password(cls, password):
        return password[::-1]

    def check_password(self, value):
        return self.password and value == self.passwprd[::-1]

