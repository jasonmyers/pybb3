# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pony.orm import *

from .. import mod


@mod.extend('Person')
class NamedPerson(object):
    name = Required(str)
