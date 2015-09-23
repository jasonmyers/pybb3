# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from factory import Sequence, PostGenerationMethodCall
from .pony_factory import PonyModelFactory

from pybb3.user.models import User
from pybb3.forum.models import Forum
from pybb3.database import db


class BaseFactory(PonyModelFactory):

    class Meta:
        abstract = True
        pony_session = db.session


class UserFactory(BaseFactory):
    username = Sequence(lambda n: "user{0}".format(n))
    email = Sequence(lambda n: "user{0}@example.com".format(n))
    password = PostGenerationMethodCall('set_password', 'example')

    class Meta:
        model = User


class ForumFactory(BaseFactory):
    name = Sequence(lambda n: "Forum {0}".format(n))
    desc = Sequence(lambda n: "Description {0}".format(n))

    class Meta:
        model = Forum
