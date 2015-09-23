# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import url_for

from pony.orm import db_session, select, desc, max

from pybb3.mods import mod
from pybb3.database import (
    db, Required, Optional, Set, PrimaryKey, LongStr, INT,
    Choices, table_name
)
from pybb3.extensions import bcrypt
from pybb3.utils import pony_entity_from_form


@mod.extendable
class Forum(db.Entity):
    _table_ = table_name('forums')

    id = PrimaryKey(int, auto=True, column='forum_id')  # Forum id=0 (global) required
    parent = Optional('Forum', column='parent_id', reverse='forums')
    forums = Set('Forum', reverse='parent')

    left = Optional(int, column='left_id')  # Left position in Nested Set hierarchy
    right = Optional(int, column='right_id')  # Right position in Nested Set hierarchy

    forum_parents = Optional(LongStr, column='forum_parents')  # Serialized string of parents

    topics = Set('Topic', reverse='forum')
    posts = Set('Post', reverse='forum')

    name = Required(str, column='forum_name')
    desc = Required(LongStr, column='forum_desc')  # + Bitfields
    link = Optional(str, column='forum_link')
    password = Optional(str, 40, column='forum_password')
    image = Optional(str, column='forum_image')
    topics_per_page = Required(int, size=INT.TINYINT, default=0, py_check=lambda v: v >= 0, column='forum_topics_per_page')
    DEFAULT_TOPICS_PER_PAGE = 25

    @mod.extendable
    class ForumType(Choices(int, INT.TINYINT)):
        CATEGORY = 0    # FORUM_CATEGORY: Category
        POST = 1        # FORUM_POST: Forum
        LINK = 2        # FORUM_LINK: Link
    type = Required(int, size=ForumType.size, default=0, py_check=ForumType.check, column='forum_type')

    @mod.extendable
    class ForumStatus(Choices(int, INT.TINYINT)):
        DEFAULT = 0  # ???
    status = Required(int, size=ForumStatus.size, default=0, py_check=ForumStatus.check, column='forum_status')

    flags = Required(int, size=INT.TINYINT, default=32, column='forum_flags')
    display_on_index = Required(bool, default=True, column='display_on_index')
    enable_indexing = Required(bool, default=True, column='enable_indexing')
    enable_icons = Required(bool, default=True, column='enable_icons')

    enable_prune = Required(bool, default=False, column='enable_prune')
    prune_next = Required(int, default=0, column='prune_next')
    prune_days = Required(int, size=INT.TINYINT, default=0, column='prune_days')
    prune_viewed = Required(int, size=INT.TINYINT, default=0, column='prune_viewed')
    prune_freq = Required(int, size=INT.TINYINT, default=0, column='prune_freq')

    logs = Set('Log', reverse='forum')

    def __new__(cls, password='', **kwargs):
        password = password and cls.encrypt_password(password)
        return super(mod.extendable(Forum), cls).__new__(cls, password=password, **kwargs)

    def __repr__(self):
        if self.type == self.ForumType.CATEGORY:
            return '<Forum Category({id}: {name!r})>'.format(id=self.id, name=self.name)
        elif self.type == self.ForumType.LINK:
            return '<Forum Link({id}: {name!r})>'.format(id=self.id, name=self.name)
        return '<Forum({id}: {name!r})>'.format(id=self.id, name=self.name)

    def before_insert(self):
        if self.parent is None:
            # New global forum, put at the end
            rightmost = max(forum.right for forum in Forum)
            if rightmost is not None:
                self.move_forum(to=rightmost + 1)
            else:
                # First forum
                self.move_forum(to=0)

        else:
            # New sub forum
            self.move_into(self.parent)

    def move_before(self, forum):
        """ Move a forum before another forum """
        self.move_forum(to=forum.left)

    def move_after(self, forum):
        """ Move a forum after another forum """
        self.move_forum(to=forum.right + 1)

    def move_into(self, forum):
        """ Move a forum inside another forum (appended to the end) """
        self.move_forum(to=forum.right)

    @db_session
    def move_forum(self, to):
        """ Move a forum's left postionional node to a new position in the forum hierarchy, shifting
        other forums around it.  This is used to re-order the forum display, or nest a forum in another

        Forum order and parent/child relationship are stored as a Nested Set
        http://en.wikipedia.org/wiki/Nested_set_model

        `Forum.parent` stores the direct parent forum id
        `Forum.left` and `Forum.right` store the Nested Set left/right node values, for calculating
        all parents or all children, and forum display order

        `to`:  Move the current forum's `left` postion to the `to` (adjusting others)

        Note::  The new node can't be the same as the current `forum`'s (a no-op),
            or any of its children (self-nesting)

        """
        if self.left is not None and self.right is not None:
            # Moving an existing forum

            # "Size" if this forum, including all children.
            # This is the number of nodes in the Nested Set this forum spans
            # We will shift other forums by this amount when this one moves.
            size = self.right - self.left + 1

            if to < self.left:
                # Forum is moving in this direction (other forums adjusted in opposite direction)
                direction = -1

                # "Distance" this forum is moving.
                # We will shift this forum and children by this amount.
                distance = self.left - to

                # Other forums between left_bound and right_bound will need to be adjusted
                left_bound = to
                right_bound = self.right

            elif to == self.left:
                raise ValueError('Tried to move a forum before itself')
            elif to <= self.right:  # to > self.left
                raise ValueError('Tried to move a forum inside itself')
            elif to == self.right + 1:
                raise ValueError('Tried to move a forum after itself')

            else:  # to > self.right + 1
                direction = 1
                distance = to - self.left - size
                left_bound = self.left
                right_bound = to - 1

        else:
            # Inserting a new forum
            size = 2
            direction = -1
            distance = 0
            left_bound = to
            right_bound = to + 1
            self.left = left_bound
            self.right = right_bound

        # Find all forums with nodes between left_bound and right_bound, and adjust
        # to new positions
        for forum in select(
            forum for forum in Forum
            if (forum.right >= left_bound and forum.right <= right_bound)
            or (forum.left >= left_bound and forum.left <= right_bound)
        ).for_update():
            if forum.id == self.id:
                # Skip self, since we're updating it directly below
                continue

            if forum.left > self.left and forum.right < self.right:
                # Adjust mover's children
                forum.left += distance * direction
                forum.right += distance * direction

            else:
                # Adjust sibling/parent forums
                if forum.left >= left_bound:
                    forum.left += size * -direction
                if forum.right <= right_bound:
                    forum.right += size * -direction

        if direction == -1:
            self.left = left_bound
            self.right = left_bound + size - 1
        else:
            self.left = right_bound - size + 1
            self.right = right_bound

    def parents(self):
        return select(
            forum for forum in Forum
            if forum.left < self.left and forum.right > self.right
        ).order_by(desc(Forum.left))

    def children(self):
        return select(
            forum for forum in Forum
            if forum.left > self.left and forum.right < self.right
        ).order_by(Forum.left)

    @property
    def ordered_forums(self):
        return sorted(self.forums, key=lambda forum: forum.left)

    @classmethod
    def forum_choices(cls, indent_per_level=2, name_format=None, allow_empty=True):
        """ Yields `(forum.id, forum.name)` tuples according to forum hierarchy,
        for use in building a html select field for choosing a forum

        If `indent_per_level` is > 0, forum names will be intented with
        that many spaces according to their nested level

        If `allow_empty` is true, the choices will be prepended with an empty
        choice

        Names will be passed through the `name_format` function if provided

        Only forums of type ForumType.FORUM and ForumType.CATEGORY are returned
        """
        forums = select(
            (f.id, f.name, f.left, f.right)
            for f in Forum if f.type != Forum.ForumType.LINK
        ).order_by(lambda id, name, left, right: left)

        if allow_empty:
            yield None, '(none)'

        parents = []
        for id, name, left, right in forums:
            parents = [r for r in parents if r > left]

            label = '{indent}{name}'.format(
                indent=indent_per_level * ' ' * len(parents), name=name
            )

            if name_format is not None:
                label = name_format(label)

            parents.append(right)
            yield id, label

    @classmethod
    def encrypt_password(cls, password):
        return bcrypt.generate_password_hash(password)

    def set_password(self, password):
        self.password = self.encrypt_password(password)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    def is_category(self):
        return self.type == Forum.ForumType.CATEGORY

    def is_forum(self):
        return self.type == Forum.ForumType.POST

    def is_link(self):
        return self.type == Forum.ForumType.LINK

    def url(self):
        if self.is_link():
            return self.link
        elif self.is_forum():
            return url_for('forum.forum', forum=self)
        elif self.is_category():
            return url_for('forum.category', category=self)

    @classmethod
    def from_form(cls, form, **kwargs):
        return pony_entity_from_form(cls, form, **kwargs)
