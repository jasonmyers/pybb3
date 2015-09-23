# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import (
    Blueprint, render_template, request, url_for, flash, redirect, abort)

from pony.orm import select

from .models import Forum
from .forms import NewCategoryForm, NewForumForm, NewLinkForm
from pybb3.topic.models import Topic
from pybb3.utils import flash_errors, as_context_processor, grouper, \
    nbsp_indent
from pybb3.database import db


blueprint = Blueprint(
    "forum", __name__, url_prefix='/forums',
    static_folder="../static", template_folder='../templates/forum')


@as_context_processor(blueprint)
def board_index_url():
    return url_for('forum.forums')


@blueprint.route('/')
@blueprint.arg('?show_empty_categories=<flag>')
def forums(show_empty_categories=False):
    forums = select(
        forum for forum in Forum if forum.parent is None
    ).order_by(Forum.left)  # .prefetch(Forum.children, recursive=False)

    return render_template(
        "forums.html",
        forum_groups=grouper(forums, lambda forum: not forum.is_category()),
        show_empty_categories=show_empty_categories,
    )


@blueprint.route('/new_category', methods=['GET', 'POST'])
@blueprint.arg('?parent=<Forum>', methods=['GET'])
def new_category(parent=None):
    form = NewCategoryForm(request.form, parent=parent and parent.id)
    form.parent.choices = list(Forum.forum_choices(name_format=nbsp_indent))

    if form.validate_on_submit():
        new = Forum.from_form(
            form,
            type=Forum.ForumType.CATEGORY,
        )
        db.commit()
        if parent:
            to = url_for('forum.forum', forum=parent)
        else:
            to = board_index_url()
        return redirect(to)
    else:
        flash_errors(form)
    return render_template('new_category.html', form=form)


@blueprint.route('/new_forum', methods=['GET', 'POST'])
@blueprint.arg('?parent=<Forum>', methods=['GET'])
def new_forum(parent=None):
    form = NewForumForm(request.form, parent=parent and parent.id)
    form.parent.choices = list(Forum.forum_choices(name_format=nbsp_indent))

    if form.validate_on_submit():
        new = Forum.from_form(
            form,
            type=Forum.ForumType.POST,
        )
        db.commit()
        if parent:
            to = url_for('forum.forum', forum=parent)
        else:
            to = board_index_url()

        return redirect(to)
    else:
        flash_errors(form)
    return render_template('new_forum.html', form=form)


@blueprint.route('/new_link', methods=['GET', 'POST'])
@blueprint.arg('?parent=<Forum>', methods=['GET'])
def new_link(parent=None):
    form = NewLinkForm(request.form, parent=parent and parent.id)
    form.parent.choices = list(Forum.forum_choices(name_format=nbsp_indent))

    if form.validate_on_submit():
        new = Forum.from_form(
            form,
            type=Forum.ForumType.LINK,
        )
        db.commit()
        if parent:
            to = url_for('forum.forum', forum=parent)
        else:
            to = board_index_url()

        return redirect(to)
    else:
        flash_errors(form)
    return render_template('new_link.html', form=form)


@blueprint.route('/<Forum:forum>')
@blueprint.arg('?page=<int>', preprocess=lambda page: max(page, 1))
def forum(forum, page=1):
    topics = select(
        topic for topic in Topic
        if topic.forum == forum
    ).page(page, pagesize=forum.topics_per_page or Forum.DEFAULT_TOPICS_PER_PAGE)
    return render_template('forum.html', forum=forum, topics=topics)


@blueprint.route('/categories/<Forum:category>')
def category(category):
    if category.type != Forum.ForumType.CATEGORY:
        return redirect(board_index_url())
    return render_template('category.html', category=category)

