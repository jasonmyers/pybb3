# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pony.orm import *

from .. import mod


__version__ = '0.0.2'


from ..person import Person


@mod.extend('Person')
class NamedPerson(object):
    name = Required(str)
