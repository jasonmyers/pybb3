# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pony.orm import *

from .database import db
from .person import Person
from .post import Post
from . import mod
from .mods.icons import Icon
from .mods.messages import Message

sql_debug(True)

db.generate_mapping(create_tables=True)

print(Person._columns_)
print(Post._columns_)

with db_session:
    person = Person(name='Jason', age=32)
    post = Post(poster=person)

    print(Person.PersonType)

    if mod.installed('icons'):
        icon = Icon(picture='rabbit')
        message = Message(icon=icon, title='test')
