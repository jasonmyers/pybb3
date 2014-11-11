# -*- coding: utf-8 -*-
"""
Mod to enable private messages
"""
from __future__ import unicode_literals

import datetime

from pybb3.mods import mod
from pybb3.database import (
    db, Choices, INT, Required, Optional, PrimaryKey, LongStr, Set, table_name
)


@mod.extendable
class Message(db.Entity):
    _table_ = table_name('privmsgs')

    id = PrimaryKey(int, auto=True, column='msg_id')

    root_level = Optional('Message', column='root_level', reverse='reply_tree')
    reply_tree = Set('Message', reverse='root_level')
    author = Required('PrivateMessageModUser', column='author_id', reverse='sent_messages')

    author_ip = Optional(str, 40, column='author_ip')
    time = Required(datetime.datetime, default=datetime.datetime.utcnow, column='message_time')

    to_address = Required(LongStr, column='message_to_address')
    bcc_address = Required(LongStr, column='bcc_address')

    enable_bbcode = Required(bool, default=True, column='enable_bbcode')
    enable_smilies = Required(bool, default=True, column='enable_smilies')
    enable_magic_url = Required(bool, default=True, column='enable_magic_url')
    enable_sig = Required(bool, default=True, column='enable_sig')

    subject = Optional(str, 100, column='message_subject')
    text = Optional(LongStr, column='message_text')
    bbcode_bitfield = Optional(str, column='bbcode_bitfield')
    bbcode_uid = Optional(str, 5, column='bbcode_uid')

    edit_reason = Optional(str, column='message_edit_reason')
    edit_user = Optional('PrivateMessageModUser', reverse='edited_messages')
    edit_time = Optional(datetime.datetime, column='message_edit_time')
    edit_count = Optional(int, size=INT.SMALLINT, column='message_edit_count')

    def __repr__(self):
        return '<Message({id}: {subject!r})>'.format(id=self.id, subject=self.subject)


@mod.extendable
class MessageFolder(db.Entity):
    _table_ = table_name('privmsgs_folder')

    id = PrimaryKey(int, auto=True, column='folder_id')

    user = Required('PrivateMessageModUser', column='user_id', reverse='message_folders')
    name = Optional(str, column='folder_name')
    pm_count = Required(int, size=INT.MEDIUMINT, default=0, column='pm_count')

    messages = Set('MessageTo', reverse='folder')

    def __repr__(self):
        return '<MessageFolder({id}: {name!r})>'.format(id=self.id, name=self.name)


@mod.extendable
class MessageTo(db.Entity):
    _table_ = table_name('privmsgs_to')

    id = PrimaryKey(int, auto=True, column='msg_id')

    user = Required('PrivateMessageModUser', column='user_id', reverse='received_messages')
    author = Required('PrivateMessageModUser', column='author_id', reverse='author_messages')

    deleted = Required(bool, default=False, column='pm_deleted')
    new = Required(bool, default=True, column='pm_new')
    unread = Required(bool, default=True, column='pm_unread')
    replied = Required(bool, default=False, column='pm_replied')
    marked = Required(bool, default=False, column='pm_marked')
    forwarded = Required(bool, default=False, column='pm_forwarded')

    folder = Optional('MessageFolder', column='folder_id', reverse='messages')

    def __repr__(self):
        return '<MessageTo({id}: {author} -> {user})>'.format(
            id=self.id, author=self.author, user=self.user)


@mod.extend('User')
class PrivateMessageModUser(object):

    new_privmsg = Required(int, size=INT.TINYINT, default=0, column='user_new_privmsg')
    unread_privmsg = Required(int, size=INT.TINYINT, default=0, column='user_unread_privmsg')
    last_privmsg = Optional(datetime.datetime, column='user_last_privmsg')
    message_rules = Required(bool, default=False, column='user_message_rules')

    @mod.extendable
    class UserFullFolder(Choices(int, INT.INTEGER)):
        pass
    full_folder = Optional(int, size=INT.INTEGER, py_check=UserFullFolder.check, column='user_full_folder')

    allow_pm = Required(bool, default=True, column='user_allow_pm')

    sent_messages = Set('Message', reverse='author')
    author_messages = Set('MessageTo', reverse='author')
    received_messages = Set('MessageTo', reverse='user')
    edited_messages = Set('Message', reverse='edit_user')
    message_folders = Set('MessageFolder', reverse='user')


@mod.extend('Group')
class PrivateMessageModGroup(object):
    receive_pm = Required(bool, default=False, column='group_receive_pm')
    message_limit = Required(int, size=INT.MEDIUMINT, default=0, column='group_message_limit')


@mod.installed('icons')
def icons_installed():
    @mod.extend('Icon')
    class PrivateMessageModIcon(object):
        messages = Optional('PrivateMessageModMessageIcon', reverse='icon')

    @mod.extend('Message')
    class PrivateMessageModMessageIcon(object):
        icon = Optional('PrivateMessageModIcon', column='icon_id', reverse='messages')


@mod.installed('attachments')
def attachments_installed():
    @mod.extend('Message')
    class PrivateMessageModMessageAttachment(object):
        attachment = Required(bool, default=False, column='message_attachment')

    @mod.extend('Attachment')
    class PrivateMessageModAttachment(object):
        in_message = Required(bool, default=False, column='in_message')


@mod.installed('drafts')
def drafts_installed():
    @mod.extend('Draft')
    class PrivateMessageModDraft(object):
        subject = Optional(str, 100, column='draft_subject')
        message = Optional(LongStr, column='draft_message')
