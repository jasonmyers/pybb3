# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from pybb3.mods import mod
from pybb3.database import (
    db, PrimaryKey, Choices, INT, Required, Optional, table_name, LongStr,
)


@mod.extendable
class Log(db.Entity):
    _table_ = table_name('logs')
    id = PrimaryKey(int, auto=True, column='log_id')

    @mod.extendable
    class LogType(Choices(int, INT.TINYINT)):
        DEFAULT = 0  # ???
    type = Required(int, size=LogType.size, default=0, py_check=LogType.check, column='log_type')

    user = Optional('User', column='user_id', reverse='logs')
    forum = Optional('Forum', column='forum_id', reverse='logs')
    topic = Optional('Topic', column='topic_id', reverse='logs')
    reportee = Optional('User', column='reportee_id', reverse='reportee_logs')

    ip = Optional(str, 40, column='log_ip')
    time = Required(datetime.datetime, default=datetime.datetime.utcnow, column='log_time')
    operation = Optional(LongStr, column='log_operation')
    data = Optional(LongStr, column='log_data')
