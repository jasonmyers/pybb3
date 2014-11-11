# -*- coding: utf-8 -*-
"""
Mod to ban users, ips and emails
"""
from __future__ import unicode_literals

import datetime

from pybb3.mods import mod
from pybb3.database import (
    db, Optional, PrimaryKey, Required, LongStr, table_name, Set,
)


@mod.extendable
class BanList(db.Entity):
    _table_ = table_name('banlist')
    id = PrimaryKey(int, auto=True, column='ban_id')

    userid = Optional('User', column='ban_userid', reverse='ban')
    ip = Optional(str, 40, column='ban_ip')
    email = Optional(str, 100, column='ban_email')

    start = Optional(datetime.datetime, column='ban_start')
    end = Optional(datetime.datetime, column='ban_end')

    exclude = Required(bool, default=False, column='ban_exclude')
    reason = Optional(LongStr, column='ban_reason')
    ban_give_reason = Optional(LongStr, column='ban_give_reason')

    def __repr__(self):
        return '<Banlist({id}: {name!r})>'.format(
            id=self.id, name=self.userid or self.ip or self.email
        )
