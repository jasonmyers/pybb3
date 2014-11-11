# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pony.orm import *

from .. import mod


mod.require('named_person', '0.0.2')

from ..person import Person


@mod.extend(Person)
def extend(base):
    from ..database import INT
    class AgedPerson(base):
        age = Required(int, size=INT.TINYINT)

    return AgedPerson


@mod.extend(Person.PersonType)
class AgedPersonPersonType(object):
    ANIMAL = 2
