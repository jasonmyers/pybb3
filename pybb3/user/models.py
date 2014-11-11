# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal

from flask.ext.login import UserMixin

from pybb3.mods import mod
from pybb3.extensions import bcrypt
from pybb3.database import (
    db, Required, Optional, Set, PrimaryKey, Choices,
    INT, LongStr, table_name
)


@mod.extendable
class User(UserMixin, db.Entity):
    _table_ = table_name('users')

    id = PrimaryKey(int, auto=True, column='user_id')

    @mod.extendable
    class UserType(Choices(int, INT.TINYINT)):
        NORMAL = 0
        INACTIVE = 1
        IGNORED = 2
        FOUNDER = 3
    type = Required(int, size=UserType.size, default=0, py_check=UserType.check, column='user_type')

    group = Optional('Group', column='group_id', reverse='default_users')  # Default group
    groups = Set('Group', table=table_name('user_group'), column='group_id', reverse='users')
    topics = Set('Topic', reverse='poster')
    posts = Set('Post', reverse='poster')
    bumped_topics = Optional('Topic', reverse='bumper')
    post_count = Required(int, size=INT.MEDIUMINT, default=0, column='user_posts')

    permissions = Optional(LongStr, column='user_permissions')
    perm_from = Optional('User', column='user_perm_from', reverse='perm_to')
    perm_to = Set('User', reverse='perm_from')
    ip = Optional(str, 40, column='user_ip')
    regdate = Required(datetime.datetime, default=datetime.datetime.utcnow, column='user_regdate')
    username = Required(str, column='username')
    username_clean = Required(str, column='username_clean')
    email = Optional(str, 100, column='user_email')
    email_hash = Optional(int, size=INT.BIGINT, column='user_email_hash')
    password = Optional(str, 60, column='user_password')  # Bcrypt hash length is 60
    passchg = Optional(datetime.datetime, column='user_passchg')
    newpasswd = Optional(str, 32, column='user_newpasswd')

    lastvisit = Optional(datetime.datetime, column='user_lastvisit')
    lastpost_time = Optional(datetime.datetime, column='user_lastpost_time')
    lastpage = Optional(str, 200, column='user_lastpage')
    last_search = Optional(datetime.datetime, column='user_last_search')
    emailtime = Optional(datetime.datetime, column='user_emailtime')

    last_confirm_key = Optional(str, 10, column='user_last_confirm_key')
    options = Optional(int, size=INT.INTEGER, unsigned=True, column='user_options')

    login_attempts = Required(int, size=INT.TINYINT, default=0, column='user_login_attempts')

    @mod.extendable
    class UserInactiveReason(Choices(int, INT.TINYINT)):
        pass
    inactive_reason = Optional(int, size=UserInactiveReason.size, py_check=UserInactiveReason, column='user_inactive_reason')
    inactive_time = Optional(datetime.datetime, column='user_inactive_time')

    lang = Optional(str, 30, column='user_lang')
    timezone = Optional(Decimal, 5, 2, column='user_timezone')
    dst = Required(bool, default=False, column='user_dst')
    dateformat = Optional(str, 30, column='user_dateformat')

    allow_viewemail = Required(bool, default=True, column='user_allow_viewemail')
    allow_massemail = Required(bool, default=True, column='user_allow_massemail')

    topics_posted_in = Set('Topic', table=table_name('topics_posted'), column='topic_id', reverse='posters')

    logs = Set('Log', reverse='user')
    reportee_logs = Set('Log', reverse='reportee')

    def __new__(cls, password=None, **kwargs):
        # Don't send password, since we need to encrypt it
        return super(User, cls).__new__(cls, **kwargs)

    def __init__(self, password=None, **kwargs):
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    @property
    def get_dateformat(self):
        return self.dateformat or 'd M Y H:i'

    @property
    def get_timezone(self):
        return self.timezone or Decimal('0.00')

    def __repr__(self):
        return '<User({id}: {username!r})>'.format(
            id=self.id, username=self.username)


@mod.extendable
class Group(db.Entity):
    _table_ = table_name('groups')

    id = PrimaryKey(int, auto=True, column='group_id')

    users = Set('User', table=table_name('user_group'), column='user_id', reverse='groups')
    default_users = Set('User', reverse='group')

    @mod.extendable
    class GroupType(Choices(int, INT.TINYINT)):
        DEFAULT = 1  # ???
    type = Required(int, size=GroupType.size, default=GroupType.DEFAULT, py_check=GroupType.check, column='group_type')

    founder_manage = Required(bool, default=False, column='group_founder_manage')
    name = Optional(str, column='group_name')
    desc = Optional(LongStr, column='group_desc')
    desc_bitfield = Optional(str, column='group_desc_bitfield')
    desc_options = Required(int, size=INT.INTEGER, default=7, column='desc_options')
    desc_uid = Optional(str, 5, column='group_desc_uid')

    display = Required(bool, default=False, column='group_display')
    legend = Required(bool, default=True, column='group_legend')
