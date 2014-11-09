# -*- coding: utf-8 -*-
"""
Mod to enable user warnings
"""
from __future__ import unicode_literals

import datetime

from pybb3 import mod
from pybb3.database import (
    db, Required, INT, Optional, PrimaryKey, table_name, Set,
)


@mod.extend('User')
class WarnUserModUser(object):
    warning_count = Required(int, size=INT.TINYINT, default=0, column='user_warnings')
    last_warning = Optional(datetime.datetime, column='user_last_warning')

    warnings = Set('Warning', reverse='user')


@mod.extend('Post')
class WarnUserModPost(object):
    warning = Optional('Warning', reverse='post')


@mod.extend('Log')
class WarnUserModLog(object):
    warnings = Set('Warning', reverse='log')


@mod.extendable
class Warning(db.Entity):
    _table_ = table_name('warnings')

    id = PrimaryKey(int, auto=True, column='warning_id')

    user = Required('WarnUserModUser', column='user_id', reverse='warnings')
    post = Required('WarnUserModPost', column='post_id', reverse='warning')
    log = Optional('WarnUserModLog', column='log_id', reverse='warnings')

    time = Required(datetime.datetime, default=datetime.datetime.utcnow, column='warning_time')
