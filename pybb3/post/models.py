# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from pybb3.mods import mod
from pybb3.database import (
    db, Required, Optional, PrimaryKey, LongStr, table_name
)


@mod.extendable
class Post(db.Entity):
    """ Subclass BasePost class to add fields to `Post` """
    _table_ = table_name('posts')

    id = PrimaryKey(int, auto=True, column='post_id')

    topic = Required('Topic', column='topic_id', reverse='posts')
    forum = Required('Forum', column='forum_id', reverse='posts')
    poster = Required('User', column='poster_id', reverse='posts')

    poster_ip = Optional(str, 40, column='poster_ip')
    time = Required(datetime.datetime, default=datetime.datetime.utcnow, column='post_time')
    enable_bbcode = Required(bool, default=True, column='enable_bbcode')
    enable_smilies = Required(bool, default=True, column='enable_smilies')
    enable_magic_url = Required(bool, default=True, column='enable_magic_url')
    enable_sig = Required(bool, default=True, column='enable_sig')

    username = Required(str, column='post_username')
    subject = Required(str, 100, column='post_subject')
    text = Required(LongStr, column='post_text')
    checksum = Required(str, 32, column='post_checksum')

    bbcode_bitfield = Required(str, column='bbcode_bitfield')
    bbcode_uid = Required(str, 5, column='bbcode_uid')

    def __repr__(self):
        return '<Post({id}: {subject!r})>'.format(id=self.id, name=self.subject)
