#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from flask.ext.script import Manager, Shell, Server

from pybb3.app import create_app
from pybb3.user.models import User
from pybb3.settings import DevConfig, ProdConfig
from pybb3.database import db

if os.environ.get("PYBB3_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

manager = Manager(app)
TEST_CMD = "py.test tests"


def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User}


@manager.option('-k', '--tests', help='Only run tests matching this pytest string expression')
@manager.option('-d', '--pdb', action='store_true', help='Break to pdb on failure')
@manager.option('-x', action='store_true', help='Stop after first failed test')
def test(tests=None, pdb=False, x=False):
    """Run the tests."""
    import pytest
    command = ['tests', '--verbose']
    if tests:
        command.extend(['-k', tests])
    if pdb:
        command.extend(['--pdb'])
    if x:
        command.extend(['-x'])
    exit_code = pytest.main(command)
    return exit_code


manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
