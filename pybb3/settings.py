# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

os_env = os.environ


class Config(object):
    SECRET_KEY = os_env.get('PYBB3_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    DEBUG_TB_PANELS = (
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        #'flask_debugtoolbar.panels.pony.PonyDebugPanel',
        'pybb3.ext.flask_debugtoolbar.panels.pony.PonyDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
    )
    PONY_AUTO_SESSION_EXEMPT_URLS = (
        '/static',
        '/_debug_toolbar/static/',
    )


class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False
    PONY_DATABASE_URI = 'postgresql://localhost/example'  # TODO: Change me
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True
    DEBUG_TB_ENABLED = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    PONY_DATABASE_URI = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    WTF_CSRF_ENABLED = True


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    DEBUG_TB_ENABLED = True
    PONY_DATABASE_URI = ':memory:'
    BCRYPT_LOG_ROUNDS = 1  # For faster tests
    WTF_CSRF_ENABLED = False  # Allows form testing
