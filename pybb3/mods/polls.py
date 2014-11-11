# -*- coding: utf-8 -*-
"""
Mod to add polls
"""
from __future__ import unicode_literals

import datetime

from pybb3.mods import mod
from pybb3.database import (
    db, Optional, INT, Required, LongStr, PrimaryKey, table_name, Set,
)


@mod.extend('Topic')
class PollsModTopic(object):
    title = Optional(str, 100, column='poll_title')
    start = Optional(datetime.datetime, column='poll_start')
    length = Optional(int, default=0, column='poll_length')
    max_options = Optional(int, size=INT.TINYINT, default=1, column='poll_max_options')
    last_vote = Optional(datetime.datetime, size=INT.TINYINT, column='poll_last_vote')
    vote_change = Required(bool, default=False, column='poll_vote_change')

    poll_options = Set('PollOptions', reverse='topic')
    poll_votes = Set('PollVotes', reverse='topic')


@mod.extend('User')
class PollsModUser(object):
    poll_votes = Set('PollVotes', reverse='user')


@mod.extendable
class PollOption(db.Entity):
    _table_ = table_name('poll_options')

    id = PrimaryKey(int, auto=True, column='poll_option_id')

    topic = Required('PollsModTopic', column='topic_id', reverse='poll_options')

    text = Optional(LongStr, column='poll_option_text')
    total = Required(int, INT.MEDIUMINT, default=0, column='poll_option_total')
    votes = Set('PollVotes', reverse='poll_option')

    def __repr__(self):
        return '<PollOptions({id}: {text!r})>'.format(
            id=self.id, text=self.text)


@mod.extendable
class PollVotes(db.Entity):
    _table_ = table_name('poll_votes')

    topic = Required('Topic', column='topic_id', reverse='poll_votes')
    poll_option = Required('PollOption', column='poll_option_id', reverse='votes')
    user = Required('PollsModUser', column='user_id', reverse='poll_votes')
    user_ip = Required(str, 40, column='user_ip')

    def __repr__(self):
        return '<PollVotes({id})>'.format(
            id=self.id, text=self.text)
