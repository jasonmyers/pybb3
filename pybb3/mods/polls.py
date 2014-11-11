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


@mod.extendable
class PollOption(db.Entity):
    _table_ = table_name('poll_options')

    id = PrimaryKey(int, auto=True, column='poll_option_id')

    topic = Required('PollsModTopic', column='topic_id', reverse='poll_options')

    text = Optional(LongStr, column='poll_option_text')
    total = Required(int, size=INT.MEDIUMINT, default=0, column='poll_option_total')
    votes = Set('PollVote', reverse='poll_option')

    def __repr__(self):
        return '<PollOptions({id}: {text!r})>'.format(
            id=self.id, text=self.text)


@mod.extendable
class PollVote(db.Entity):
    _table_ = table_name('poll_votes')

    topic = Required('PollsModTopic', column='topic_id', reverse='poll_votes')
    poll_option = Required('PollOption', column='poll_option_id', reverse='votes')
    user = Required('PollsModUser', column='user_id', reverse='poll_votes')
    user_ip = Required(str, 40, column='user_ip')

    def __repr__(self):
        return '<PollVotes({id})>'.format(
            id=self.id, text=self.text)


@mod.extend('Topic')
class PollsModTopic(object):
    poll_title = Optional(str, 100, column='poll_title')
    poll_start = Optional(datetime.datetime, column='poll_start')
    poll_length = Optional(int, default=0, column='poll_length')
    poll_max_options = Optional(int, size=INT.TINYINT, default=1, column='poll_max_options')
    poll_last_vote = Optional(datetime.datetime, column='poll_last_vote')
    poll_vote_change = Required(bool, default=False, column='poll_vote_change')

    poll_options = Set('PollOption', reverse='topic')
    poll_votes = Set('PollVote', reverse='topic')


@mod.extend('User')
class PollsModUser(object):
    poll_votes = Set('PollVote', reverse='user')


