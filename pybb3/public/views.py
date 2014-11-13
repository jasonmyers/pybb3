# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from __future__ import unicode_literals

from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session)
from flask.ext.login import login_user, login_required, logout_user

from pybb3.extensions import login_manager
from pybb3.user.models import User
from pybb3.public.forms import LoginForm
from pybb3.user.forms import RegisterForm
from pybb3.utils import flash_errors
from pybb3.database import db

blueprint = Blueprint(
    'public', __name__,
    static_folder="../static", template_folder='../templates/public'
)


@login_manager.user_loader
def load_user(id):
    return User[id]


@blueprint.route("/", methods=["GET", "POST"])
def home():
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", 'success')
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("home.html", form=form)


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True
        )
        flash("Thank you for registering. You can now log in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('register.html', form=form)


@blueprint.route("/about")
@db.nosession
def about():
    form = LoginForm(request.form)
    return render_template("about.html", form=form)
