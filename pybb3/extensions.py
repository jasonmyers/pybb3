# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located
in app.py
"""

from .ext.mod import Mod
mod = Mod()

from flask.ext.bcrypt import Bcrypt
bcrypt = Bcrypt()

from flask.ext.login import LoginManager
login_manager = LoginManager()

from .ext.pony import Pony
db = Pony()

from flask.ext.cache import Cache
cache = Cache()

from flask.ext.wtf import CsrfProtect
csrf = CsrfProtect

from flask.ext.debugtoolbar import DebugToolbarExtension
debug_toolbar = DebugToolbarExtension()
