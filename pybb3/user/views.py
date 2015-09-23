# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Blueprint, render_template
from flask.ext.login import login_required

blueprint = Blueprint(
    "user", __name__, url_prefix='/users',
    static_folder="../static", template_folder='../templates/users')

