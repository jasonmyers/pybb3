# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from .. import mod
from ..database import db, Optional, Set


@mod.extendable
class Message(db.Entity):
    title = Optional(str)


@mod.extend('Message')
def extend(base):
    if mod.installed('icons'):
        class MessageModIconMessage(base):
            icon = Optional('MessageModIcon', reverse='messages')
        return MessageModIconMessage


@mod.extend('Icon')
def extend(base):
    if mod.installed('icons'):
        class MessageModIcon(base):
            messages = Set('MessageModIconMessage', reverse='icon')

        return MessageModIcon

