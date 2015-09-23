# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import partial

from pony.orm import select
import pytest

from pybb3.forum.models import Forum
from tests.factories import ForumFactory


def assert_positional_integrity():
    positions = [pos for leftright in select(
        (forum.left, forum.right) for forum in Forum
    ) for pos in leftright]
    try:
        assert sorted(positions) == list(range(len(positions)))  # No gaps, no overlap, 0-n
    except:
        raise


def flat_tree(tree):
    tree = tree or []
    for branch in tree:
        root, branches = branch[0], branch[1:]
        yield root
        for leaf in flat_tree(branches):
            yield leaf


def assert_branch(parents, node, branches):
    children = list(flat_tree(branches))
    assert parents == node.parents()[:]
    assert children == node.children()[:]


def assert_branches(tree, parents=[]):
    for branch in tree:
        root, branches = branch[0], branch[1:]
        assert_branch(parents, root, branches)
        parents = [root] + parents
        assert_branches(branches, parents)
        parents = parents[1:]


def assert_tree(tree):
    assert_positional_integrity()
    assert_branches(tree)


class TestForum:

    def test_creating_ordering(self, db):
        """ Tests for creating and ordering forums in the Nested Set hierarchy,
        including `Forum.move_after`, `Forum.move_before`, `Forum.move_into`,
        and `Forum.move_forum`

        Also tests `Forum.children` and `Forum.parents` methods
        """

        with db.session:
            a = ForumFactory(); db.commit()
            assert_tree([
                [a],
            ])

            b = ForumFactory(parent=a); db.commit()
            assert_tree([
                [a, [b]],
            ])

            c = ForumFactory(parent=b); db.commit()
            assert_tree([
                [a, [b, [c]]],
            ])

            d = ForumFactory(); db.commit()
            assert_tree([
                [a, [b, [c]]],
                [d],
            ])

            e = ForumFactory(parent=d); db.commit()
            assert_tree([
                [a, [b, [c]]],
                [d, [e]],
            ])

            f = ForumFactory(); db.commit()
            assert_tree([
                [a, [b, [c]]],
                [d, [e]],
                [f],
            ])

            g = ForumFactory(parent=f); db.commit()
            assert_tree([
                [a, [b, [c]]],
                [d, [e]],
                [f, [g]],
            ])

            h = ForumFactory(parent=f); db.commit()
            assert_tree([
                [a, [b, [c]]],
                [d, [e]],
                [f, [g], [h]],
            ])

            i = ForumFactory(); db.commit()
            assert_tree([
                [a, [b, [c]]],
                [d, [e]],
                [f, [g], [h]],
                [i],
            ])

            j = ForumFactory(parent=i); db.commit()
            assert_tree([
                [a, [b, [c]]],
                [d, [e]],
                [f, [g], [h]],
                [i, [j]],
            ])

            g.move_forum(to=h.right + 1)
            assert_tree([
                [a, [b, [c]]],
                [d, [e]],
                [f, [h], [g]],
                [i, [j]],
            ])

            b.move_after(h)
            assert_tree([
                [a],
                [d, [e]],
                [f, [h], [b, [c]], [g]],
                [i, [j]],
            ])

            a.move_after(i)
            assert_tree([
                [d, [e]],
                [f, [h], [b, [c]], [g]],
                [i, [j]],
                [a],
            ])

            a.move_before(d)
            assert_tree([
                [a],
                [d, [e]],
                [f, [h], [b, [c]], [g]],
                [i, [j]],
            ])

            b.move_into(a)
            assert_tree([
                [a, [b, [c]]],
                [d, [e]],
                [f, [h], [g]],
                [i, [j]],
            ])

            g.move_before(h)
            assert_tree([
                [a, [b, [c]]],
                [d, [e]],
                [f, [g], [h]],
                [i, [j]],
            ])

            b.move_before(a)
            assert_tree([
                [b, [c]],
                [a],
                [d, [e]],
                [f, [g], [h]],
                [i, [j]],
            ])

            b.move_into(a)
            assert_tree([
                [a, [b, [c]]],
                [d, [e]],
                [f, [g], [h]],
                [i, [j]],
            ])

            for error_case in [
                # Moving a forum to the same spot
                partial(a.move_forum, a.left),
                partial(a.move_forum, a.right),
                partial(h.move_before, h),
                partial(a.move_after, a),

                # Moving a forum inside itself or children
                partial(a.move_forum, b.left),
                partial(a.move_forum, b.right),
                partial(a.move_forum, c.left),
                partial(a.move_forum, c.right),
                partial(a.move_forum, d.left),
                partial(b.move_into, b),
                partial(a.move_into, b),
                partial(a.move_after, c),
                partial(b.move_before, c),
            ]:

                with pytest.raises(ValueError):
                    error_case()

                # Make sure tree is unchanged
                assert_tree([
                    [a, [b, [c]]],
                    [d, [e]],
                    [f, [g], [h]],
                    [i, [j]],
                ])

    def test_forum_choices(self, db):
        with db.session:
            a = ForumFactory(name='a'); db.commit()
            b = ForumFactory(name='b', parent=a); db.commit()
            c = ForumFactory(name='c', parent=b); db.commit()
            _ = ForumFactory(name='_', type=Forum.ForumType.LINK)  # Should be missing from output
            d = ForumFactory(name='d', ); db.commit()
            e = ForumFactory(name='e', parent=d); db.commit()
            f = ForumFactory(name='f'); db.commit()
            g = ForumFactory(name='g', parent=f); db.commit()
            h = ForumFactory(name='h', parent=f); db.commit()
            i = ForumFactory(name='i', type=Forum.ForumType.CATEGORY); db.commit()
            j = ForumFactory(name='j', parent=i); db.commit()

        forums = [a, b, c, d, e, f, g, h, i, j]

        assert '\n'.join(name for id, name in Forum.forum_choices(allow_empty=False)) == """
a
  b
    c
d
  e
f
  g
  h
i
  j""".strip()

        assert '\n'.join(name for id, name in Forum.forum_choices(indent_per_level=0, allow_empty=False)) == """
a
b
c
d
e
f
g
h
i
j""".strip()

        assert '\n'.join(name for id, name in Forum.forum_choices(allow_empty=True)) == """
(none)
a
  b
    c
d
  e
f
  g
  h
i
  j""".strip()

        assert '\n'.join(name for id, name in Forum.forum_choices(indent_per_level=0, allow_empty=True)) == """
(none)
a
b
c
d
e
f
g
h
i
j""".strip()
