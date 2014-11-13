# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

from pony.orm import *
import pony.options
pony.options.CUT_TRACEBACK = False

from .database import db

class app:
    class Config:
        INSTALLED_MODS = [
            'icons',
            'messages',
            '...',
            'person',  # warning, not found
            'recent_post',
        ]
        APP_DIR = os.path.abspath(os.path.dirname(__file__))

    config = dict(Config.__dict__)


from .extensions import mod
mod.init_app(app)

from .person import Person
from .post import Post

from .mods.icons import Icon
from .mods.messages import Message

sql_debug(True)
import pony.orm.core
import logging
pony.orm.core.orm_log_level = logging.DEBUG


db.generate_mapping(create_tables=True)

print(Person._columns_)
print(Post._columns_)

with db_session:
    person = Person(name='Jason', age=32, password='rabbit')
    post = Post(poster=person)

    print(Person.PersonType)

    if mod.installed('icons'):
        icon = Icon(picture='rabbit')
        message = Message(icon=icon, title='test')
