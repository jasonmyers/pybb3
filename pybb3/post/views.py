# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Blueprint, render_template, request, url_for, flash, redirect, current_app

from .models import Post
from .forms import NewPostForm
from pybb3.utils import flash_errors, as_context_processor
from pybb3.database import db


blueprint = Blueprint(
    "post", __name__, url_prefix='/post',
    static_folder="../static", template_folder='../templates/post')


@as_context_processor(blueprint)
def board_index_url():
    return url_for('forum.forums')


@blueprint.route('/new_post')
@blueprint.arg('?topic=<Topic>', required=True)
def new_post(topic):
    form = NewPostForm(request.form)
    if form.validate_on_submit():
        new_post = Post(
            subject=form.subject.data,
            text=form.text.data,
            topic=topic,
            forum=topic.forum,
        )
        db.commit()
        return redirect(url_for('topic.topic', topic=topic))
    else:
        flash_errors(form)
    return render_template('new_post.html', form=form, topic=topic)
