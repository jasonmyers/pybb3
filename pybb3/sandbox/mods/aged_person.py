# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pony.orm import *

from .. import mod


@mod.extend('Person')
def extend(base):
    from ..database import INT
    class AgedPerson(base):
        age = Required(int, size=INT.TINYINT)

    return AgedPerson


@mod.extend('PersonType', 'Choices')
def extend(base):
    class AgedPersonPersonType(base):
        ANIMAL = 2

    return AgedPersonPersonType
