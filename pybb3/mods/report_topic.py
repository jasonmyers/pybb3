# -*- coding: utf-8 -*-
"""
Mod to allow reporting topics and posts
"""
from __future__ import unicode_literals

import datetime

from pybb3 import mod
from pybb3.database import (
    db, Required, PrimaryKey, Optional, LongStr, Set, table_name, INT
)


@mod.extend('Topic')
class ReportTopicModTopic(object):
    reported = Required(bool, default=False, column='topic_reported')
    reports = Set('Report', reverse='topic')


@mod.extend('Post')
class ReportTopicModPost(object):
    reported = Required(bool, default=False, column='post_reported')
    reports = Set('Report', reverse='post')


@mod.extend('User')
class ReportTopicModUser(object):
    reports = Set('Report', reverse='user')


@mod.extendable
class Report(db.Entity):
    _table_ = table_name('reports')
    id = PrimaryKey(int, auto=True, column='report_id')

    reason = Optional('Reason', column='reason_id', reverse='report')
    post = Required('ReportTopicModPost', column='post_id', reverse='reports')
    user = Required('ReportTopicModUser', column='user_id', reverse='reports')

    user_notify = Required(bool, default=False, column='user_notify')
    closed = Required(bool, default=False, column='report_closed')
    time = Required(datetime.datetime, default=datetime.datetime.utcnow, column='time')
    text = Optional(LongStr, column='report_text')

    def __repr__(self):
        return '<Report({id})>'.format(id=self.id)


@mod.extendable
class ReportReason(db.Entity):
    _table_ = table_name('reports_reasons')

    id = PrimaryKey(int, auto=True, column='reason_id')

    title = Optional(str, column='reason_title')
    description = Optional(str, column='reason_description')
    order = Optional(int, size=INT.SMALLINT, column='reason_order')

    def __repr__(self):
        return '<ReportReason({id})>'.format(id=self.id)
