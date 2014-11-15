# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from pony.orm import Set, Required, Optional, select, get

from pybb3.ext.mod import ClassExtensionError


class TestExtendable:

    @pytest.fixture
    def extendable_class_with_root(self, mod):

        class ExtendableClass(object):
            inherited_attribute = 'ExtendableClass'
            overridden_attribute = 'ExtendableClass'

            def inherited_instance_method(self):
                return 'ExtendableClass'

            def overridden_instance_method(self):
                return 'ExtendableClass'

            def chained_instance_method(self):
                return 'ExtendableClass'

            @classmethod
            def inherited_class_method(cls):
                return 'ExtendableClass'

            @classmethod
            def overridden_class_method(cls):
                return 'ExtendableClass'

            @classmethod
            def chained_class_method(cls):
                return 'ExtendableClass'

        Root = ExtendableClass
        Class = mod.extendable(ExtendableClass)

        assert Class._root_ is Root
        assert mod.extendable(Class) is Root
        assert Class.__bases__ == (Root,)
        assert Class.inherited_attribute == 'ExtendableClass'
        assert Class.overridden_attribute == 'ExtendableClass'
        assert Class.inherited_class_method() == 'ExtendableClass'
        assert Class.overridden_class_method() == 'ExtendableClass'
        assert Class.chained_class_method() == 'ExtendableClass'
        assert Class().inherited_instance_method() == 'ExtendableClass'
        assert Class().overridden_instance_method() == 'ExtendableClass'
        assert Class().chained_instance_method() == 'ExtendableClass'

        return Class, Root

    @pytest.fixture
    def extendable_class(self, extendable_class_with_root):
        Class, _ = extendable_class_with_root
        return Class

    def test_extendable(self, mod):

        class Topic(object):
            pass

        BaseTopic = Topic
        Topic = mod.extendable(Topic)

        assert mod.extendable(Topic) is BaseTopic
        assert Topic._root_ is BaseTopic
        assert Topic.__base__ is BaseTopic
        assert Topic in mod.extendable_roots
        assert 'Topic' in mod.extendable_registry
        assert mod.extendable_registry['Topic'] is Topic

    def test_extendable_custom_name(self, mod):

        @mod.extendable('CustomTopic')
        class Topic(object):
            pass

        assert 'CustomTopic' in mod.extendable_registry
        assert mod.extendable_registry['CustomTopic'] is Topic

    def test_extendable_classmethod(self, mod):

        @mod.extendable
        class Topic(object):
            def __new__(cls, *args, **kwargs):
                assert super(Topic, cls).__new__ is Topic.__new__
                assert super(mod.extendable(Topic)).__new__ is not Topic.__new__

        Topic()

    def test_extendable_already_registered(self, mod):

        @mod.extendable
        class Topic(object):
            pass

        with pytest.raises(ClassExtensionError):
            @mod.extendable
            class Topic(object):
                pass

        with pytest.raises(ClassExtensionError):
            @mod.extendable('Topic')
            class CustomTopic(object):
                pass

    def test_extend_not_found(self, mod):

        @mod.extendable
        class Topic(object):
            pass

        class Post(object):
            pass

        with pytest.raises(ClassExtensionError):
            @mod.extend(Post)
            def CustomPost(object):
                pass

        with pytest.raises(ClassExtensionError):
            @mod.extend('Post')
            def CustomPost(object):
                pass

    def test_extended_object_name(self, mod):

        @mod.extendable
        class Topic(object):
            pass

        assert Topic.__base__.__name__ == 'Topic'
        assert Topic.__name__ == 'Topic'

        assert mod.extended_object_name('Topic') == 'Topic' + mod.EXTENDED_OBJECT_SUFFIX
        assert mod.extended_object_name(Topic) == 'Topic' + mod.EXTENDED_OBJECT_SUFFIX
        assert mod.extended_object_name(Topic.__base__) == 'Topic' + mod.EXTENDED_OBJECT_SUFFIX

        assert mod.extended_object_name_pretty('Topic') == 'Topic'
        assert mod.extended_object_name_pretty('TopicExtended') == 'Topic'
        assert mod.extended_object_name_pretty(Topic) == 'Topic'
        assert mod.extended_object_name_pretty(Topic.__base__) == 'Topic'

    def test_no_extensions(self, mod):

        class BaseTopic(object):
            a = 1

        Topic = mod.extendable(BaseTopic)

        mod.extend_objects()

        assert mod.extendable(Topic) is BaseTopic
        assert Topic._root_ is BaseTopic
        assert Topic.__base__ is BaseTopic
        assert Topic.__bases__ == (BaseTopic,)

    def test_extension_by_name(self, mod, extendable_class_with_root):
        Class, Root = extendable_class_with_root

        @mod.extend('ExtendableClass')
        class Extension(object):
            overridden_attribute = 'Extension'

            def overridden_instance_method(self):
                return 'Extension'

            def chained_instance_method(self):
                return 'Extension ' + super(Extension, self).chained_instance_method()

            @classmethod
            def overridden_class_method(cls):
                return 'Extension'

            @classmethod
            def chained_class_method(cls):
                return 'Extension ' + super(Extension, cls).chained_class_method()

        assert Class._root_ is Root
        assert mod.extendable(Class) is Root
        assert Class.__bases__ == (Extension,)
        assert Class.inherited_attribute == 'ExtendableClass'
        assert Class.overridden_attribute == 'Extension'
        assert Class.inherited_class_method() == 'ExtendableClass'
        assert Class.overridden_class_method() == 'Extension'
        assert Class.chained_class_method() == 'Extension ExtendableClass'
        assert Class().inherited_instance_method() == 'ExtendableClass'
        assert Class().overridden_instance_method() == 'Extension'
        assert Class().chained_instance_method() == 'Extension ExtendableClass'

    def test_one_extension(self, mod, extendable_class_with_root):
        Class, Root = extendable_class_with_root

        @mod.extend(Class)
        class Extension(object):
            overridden_attribute = 'Extension'

            def overridden_instance_method(self):
                return 'Extension'

            def chained_instance_method(self):
                return 'Extension ' + super(Extension, self).chained_instance_method()

            @classmethod
            def overridden_class_method(cls):
                return 'Extension'

            @classmethod
            def chained_class_method(cls):
                return 'Extension ' + super(Extension, cls).chained_class_method()

            def extension_only_method(self):
                try:
                    return 'Extension ' + super(Extension, self).extension_only_method()
                except AttributeError:
                    return 'Extension'

        assert Class._root_ is Root
        assert mod.extendable(Class) is Root
        assert Class.__bases__ == (Extension,)
        assert Class.inherited_attribute == 'ExtendableClass'
        assert Class.overridden_attribute == 'Extension'
        assert Class.inherited_class_method() == 'ExtendableClass'
        assert Class.overridden_class_method() == 'Extension'
        assert Class.chained_class_method() == 'Extension ExtendableClass'
        assert Class().inherited_instance_method() == 'ExtendableClass'
        assert Class().overridden_instance_method() == 'Extension'
        assert Class().chained_instance_method() == 'Extension ExtendableClass'
        assert Class().extension_only_method() == 'Extension'

    def test_one_extension_by_callback(self, mod, extendable_class_with_root):
        Class, Root = extendable_class_with_root

        @mod.extend(Class)
        def extend(base):
            class Extension(base):
                overridden_attribute = 'Extension'

                def overridden_instance_method(self):
                    return 'Extension'

                def chained_instance_method(self):
                    return 'Extension ' + super(Extension, self).chained_instance_method()

                @classmethod
                def overridden_class_method(cls):
                    return 'Extension'

                @classmethod
                def chained_class_method(cls):
                    return 'Extension ' + super(Extension, cls).chained_class_method()

            return Extension

        # After @extend but before extend_objects is called
        assert Class._root_ is Root
        assert mod.extendable(Class) is Root
        assert Class.__bases__ == (Root,)
        assert Class.inherited_attribute == 'ExtendableClass'
        assert Class.overridden_attribute == 'ExtendableClass'
        assert Class.inherited_class_method() == 'ExtendableClass'
        assert Class.overridden_class_method() == 'ExtendableClass'
        assert Class.chained_class_method() == 'ExtendableClass'
        assert Class().inherited_instance_method() == 'ExtendableClass'
        assert Class().overridden_instance_method() == 'ExtendableClass'
        assert Class().chained_instance_method() == 'ExtendableClass'

        mod.extend_objects()

        # After extend_objects
        assert Class._root_ is Root
        assert mod.extendable(Class) is Root
        assert Class.__bases__[0].__name__ == 'Extension'
        assert Class.inherited_attribute == 'ExtendableClass'
        assert Class.overridden_attribute == 'Extension'
        assert Class.inherited_class_method() == 'ExtendableClass'
        assert Class.overridden_class_method() == 'Extension'
        assert Class.chained_class_method() == 'Extension ExtendableClass'
        assert Class().inherited_instance_method() == 'ExtendableClass'
        assert Class().overridden_instance_method() == 'Extension'
        assert Class().chained_instance_method() == 'Extension ExtendableClass'

    def test_two_extensions(self, mod, extendable_class_with_root):
        Class, Root = extendable_class_with_root

        @mod.extend(Class)
        class Extension(object):
            overridden_attribute = 'Extension'

            def overridden_instance_method(self):
                return 'Extension'

            def chained_instance_method(self):
                return 'Extension ' + super(Extension, self).chained_instance_method()

            @classmethod
            def overridden_class_method(cls):
                return 'Extension'

            @classmethod
            def chained_class_method(cls):
                return 'Extension ' + super(Extension, cls).chained_class_method()

            def extension_only_method(self):
                try:
                    return 'Extension ' + super(Extension, self).extension_only_method()
                except AttributeError:
                    return 'Extension'

        @mod.extend(Class)
        class Extension2(object):
            overridden_attribute = 'Extension2'

            def overridden_instance_method(self):
                return 'Extension2'

            def chained_instance_method(self):
                return 'Extension2 ' + super(Extension2, self).chained_instance_method()

            @classmethod
            def overridden_class_method(cls):
                return 'Extension2'

            @classmethod
            def chained_class_method(cls):
                return 'Extension2 ' + super(Extension2, cls).chained_class_method()

            def extension_only_method(self):
                try:
                    return 'Extension2 ' + super(Extension2, self).extension_only_method()
                except AttributeError:
                    return 'Extension2'

        assert Class._root_ is Root
        assert mod.extendable(Class) is Root
        assert Class.__bases__ == (Extension, Extension2)
        assert Class.inherited_attribute == 'ExtendableClass'
        assert Class.overridden_attribute == 'Extension'
        assert Class.inherited_class_method() == 'ExtendableClass'
        assert Class.overridden_class_method() == 'Extension'
        assert Class.chained_class_method() == 'Extension Extension2 ExtendableClass'
        assert Class().inherited_instance_method() == 'ExtendableClass'
        assert Class().overridden_instance_method() == 'Extension'
        assert Class().chained_instance_method() == 'Extension Extension2 ExtendableClass'
        assert Class().extension_only_method() == 'Extension Extension2'


class TestModPonyEntity:

    @pytest.fixture
    def extendable_model(self, udb, mod):
        db = udb

        @mod.extendable
        class User(db.Entity):
            username = Required(str)
            password = Optional(str)

            def __new__(cls, password=None, **kwargs):
                password = cls.encrypt_password(password)
                return super(mod.extendable(User), cls).__new__(cls, password=password, **kwargs)

            @staticmethod
            def encrypt_password(password):
                return password[::-1]

        return User

    def test_no_extensions(self, udb, extendable_model):
        db = udb
        db.generate()

        User = extendable_model
        with db.session:
            user = User(username='test', password='password')

        assert set(User._columns_) == {'id', 'username', 'password'}
        assert user.username == 'test'
        assert user.password == 'drowssap'
        with db.session:
            assert get(u for u in User if u.username == 'test').id == user.id

    def test_one_extension(self, udb, mod, extendable_model):
        db = udb
        User = extendable_model

        @mod.extend(User)
        class EmailUser(object):
            email = Required(str)

            @classmethod
            def encrypt_password(cls, password):
                return password.upper()

        db.generate()

        with db.session:
            with pytest.raises(ValueError):
                # Extension introduced a required field
                user = User(username='test', password='password')

            user = User(username='test', password='password', email='test@test')

        assert set(User._columns_) == {'id', 'username', 'password', 'email'}
        assert user.username == 'test'
        assert user.password == 'PASSWORD'
        assert user.email == 'test@test'
        with db.session:
            assert get(u for u in User if u.email == 'test@test').id == user.id

    def test_two_extensions(self, udb, mod, extendable_model):
        db = udb
        User = extendable_model

        @mod.extend(User)
        class EmailUser(object):
            email = Required(str)

            @classmethod
            def encrypt_password(cls, password):
                return password.upper()

        @mod.extend('User')
        class AdminUser(object):
            role = Optional(str)

            def is_admin(self):
                return self.role == 'admin'

        db.generate()

        with db.session:
            user = User(username='test', password='password', email='test@test')

        assert set(User._columns_) == {'id', 'username', 'password', 'email', 'role'}
        assert user.username == 'test'
        assert user.password == 'PASSWORD'
        assert user.email == 'test@test'

        with db.session:
            user = User[user.id]
            user.role = 'admin'
            assert user.is_admin()

        with db.session:
            assert get(u for u in User if u.email == 'test@test').id == user.id
            assert get(u for u in User if u.role == 'admin').id == user.id

        with db.session:
            user = User[user.id]
            user.role = 'moderator'
            assert not user.is_admin()

    def test_discriminator_disabled(self, udb, mod, extendable_model):
        db = udb
        User = extendable_model

        @mod.extend(User)
        class EmailUser(object):
            email = Required(str)

        db.generate()

        assert 'classtype' not in User._columns_
        assert User._discriminator_ is None
        assert 'classtype' not in EmailUser._columns_
        assert EmailUser._discriminator_ is None

        with db.session:
            users = select(u for u in User)[:]

        assert 'classtype' not in db.db.last_sql


class TestMods:
    pass
