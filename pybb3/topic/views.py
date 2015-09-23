# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Blueprint, render_template, request, url_for, flash, redirect, current_app
from pony.orm import select

from .models import Topic
from .forms import NewTopicForm
from pybb3.post.models import Post
from pybb3.utils import flash_errors, as_context_processor
from pybb3.database import db


blueprint = Blueprint(
    "topic", __name__, url_prefix='/topic',
    static_folder="../static", template_folder='../templates/topic')


@as_context_processor(blueprint)
def board_index_url():
    return url_for('forum.forums')


@blueprint.route('/new_topic')
@blueprint.arg('?forum=<Forum>', required=True)
def new_topic(forum):
    form = NewTopicForm(request.form)
    if form.validate_on_submit():
        new_topic = Topic(
            title=form.title.data,
            forum=forum,
        )
        db.commit()
        return redirect(url_for('topic.topic', topic=new_topic))
    else:
        flash_errors(form)
    return render_template('new_topic.html', form=form, forum=forum)


@blueprint.route('/<Topic:topic>')
@blueprint.arg('?page=<int>', preprocess=lambda page: max(page, 1))
def topic(topic, page=1):
    posts = select(
        post for post in Post
        if post.topic == topic
    ).page(page, pagesize=25)
    return render_template('topic.html', topic=topic, posts=posts)
