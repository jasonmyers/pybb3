# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from __future__ import unicode_literals

from flask import url_for

from pony.orm import *

from pybb3.user.models import User
from .factories import UserFactory


class TestLoggingIn:

    def test_can_log_in_returns_200(self, user, testapp):
        # Goes to homepage
        res = testapp.get('/')
        # Fills out login form in navbar
        form = res.forms['loginForm']
        form['username'] = user.username
        form['password'] = 'myprecious'
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200

    def test_sees_alert_on_log_out(self, user, testapp):
        res = testapp.get('/')
        # Fills out login form in navbar
        form = res.forms['loginForm']
        form['username'] = user.username
        form['password'] = 'myprecious'
        # Submits
        res = form.submit().follow()
        res = testapp.get(url_for('public.logout')).follow()
        # sees alert
        assert 'You are logged out.' in res

    def test_sees_error_message_if_password_is_incorrect(self, user, testapp):
        # Goes to homepage
        res = testapp.get('/')
        # Fills out login form, password incorrect
        form = res.forms['loginForm']
        form['username'] = user.username
        form['password'] = 'wrong'
        # Submits
        res = form.submit()
        # sees error
        assert 'Invalid username or password' in res

    def test_sees_error_message_if_username_doesnt_exist(self, user, testapp):
        # Goes to homepage
        res = testapp.get('/')
        # Fills out login form, password incorrect
        form = res.forms['loginForm']
        form['username'] = 'unknown'
        form['password'] = 'myprecious'
        # Submits
        res = form.submit()
        # sees error
        assert 'Invalid username or password' in res


class TestRegistering:

    def test_can_register(self, db, user, testapp):
        with db.session:
            old_count = count(u for u in User)
        # Goes to homepage
        res = testapp.get('/')
        # Clicks Create Account button
        res = res.click('Create account')
        # Fills out the form
        form = res.forms['registerForm']
        form['username'] = 'foobar'
        form['email'] = 'foo@bar.com'
        form['password'] = 'password'
        form['confirm'] = 'password'
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200
        # A new user was created
        with db.session:
            assert count(u for u in User) == old_count + 1

    def test_sees_error_message_if_passwords_dont_match(self, user, testapp):
        # Goes to registration page
        res = testapp.get(url_for('public.register'))
        # Fills out form, but passwords don't match
        form = res.forms['registerForm']
        form['username'] = 'foobar'
        form['email'] = 'foo@bar.com'
        form['password'] = 'password'
        form['confirm'] = 'passwords'
        # Submits
        res = form.submit()
        # sees error message
        assert 'Passwords must match' in res

    def test_sees_error_message_if_password_too_short(self, user, testapp):
        # Goes to registration page
        res = testapp.get(url_for('public.register'))
        # Fills out form, but passwords don't match
        form = res.forms['registerForm']
        form['username'] = 'foobar'
        form['email'] = 'foo@bar.com'
        form['password'] = 'pass'
        form['confirm'] = 'pass'
        # Submits
        res = form.submit()
        # sees error message
        assert 'between 8 and 256' in res

    def test_sees_error_message_if_user_already_registered(self, db, user, testapp):
        with db.session:
            user = UserFactory()  # A registered user

        # Goes to registration page
        res = testapp.get(url_for('public.register'))
        # Fills out form, but username is already registered
        form = res.forms['registerForm']
        form['username'] = user.username
        form['email'] = 'foo@bar.com'
        form['password'] = 'password'
        form['confirm'] = 'password'
        # Submits
        res = form.submit()
        # sees error
        assert 'Username already registered' in res
