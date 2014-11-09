# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from pybb3 import mod
from pybb3.database import (
    db, Required, table_name, PrimaryKey, Optional, Set, INT, LongStr
)


@mod.extend('User')
class AttachmentsModUser(object):
    attachments = Set('Attachment', reverse='poster')


@mod.extend('Post')
class AttachmentsModPost(object):
    attachment = Required(bool, default=False, column='post_attachment')


@mod.extend('Topic')
class AttachmentsModTopic(object):
    attachment = Required(bool, default=False, column='topic_attachment')


@mod.extendable
class Attachment(db.Entity):
    _table_ = table_name('attachments')

    id = PrimaryKey(int, auto=True, column='attach_id')

    post = Optional('AttachmentsModPost', column='post_msg_id', reverse='attachments')
    topic = Optional('AttachmentsModTopic', column='topic_id', reverse='attachments')
    poster = Required('AttachmentModUser', column='poster_id', reverse='attachments')

    is_orphan = Required(bool, default=True, column='is_orphan')
    physical_filename = Required(str, column='physical_filename')
    real_filename = Required(str, column='real_filename')

    download_count = Required(int, INT.MEDIUMINT, default=0, column='download_count')
    attach_comment = Optional(LongStr, column='attach_comment')
    extension = Optional(str, 100, column='extension')
    mimetype = Optional(str, 100, column='mimetype')
    filesize = Optional(int, size=INT.MEDIUMINT, column='filesize')
    filetime = Optional(datetime.datetime, default=datetime.datetime.utcnow, column='filetime')
    thumbnail = Required(bool, default=False, column='thumbnail')

    def __repr__(self):
        return '<Attachment({id}: {filename!r})>'.format(
            id=self.id, filename=self.physical_filename)
