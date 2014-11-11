# -*- coding: utf-8 -*-
"""
Flask extension to allow installed mods to override views, templates and models
in order to customize behavior
"""
from __future__ import unicode_literals

import importlib
import inspect
import os
import glob
import functools
from collections import defaultdict, OrderedDict
from distutils.version import StrictVersion
import itertools

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import six

from pony.orm.core import EntityMeta


class ModError(Exception): pass
class ModRequiredError(ModError): pass
class ModInstallError(ModError): pass
class ClassExtensionError(ModError): pass


class Mod(object):
    EXTENDED_OBJECT_SUFFIX = 'Extended'

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

        # Have the mods all been imported yet
        self.mods_loaded = False

        # Holds which classes have been decorated with `@mod.extendable`
        #     {'registered name': <class>}
        self.extendable_registry = OrderedDict()

        # A set of the objects that are extendable.  Equivalent to:
        #     set(self.extendable_registry.values())
        self.extendable_objects = set()

        # For each extendable class, holds which classes have been
        # decorated with `@mod.extend`
        #     {'registered name': [extensions, ...],
        #      <class>: [extensions, ...]}
        self.extend_registry = defaultdict(list)

        # Holds the list of installed mod names with their version
        #     {'mod name': 'mod version'}
        self.installed_registry = {}

        # Holds a mapping of the dependencies for each mod
        #     {'mod name': {'required mod name': 'required version'}}
        self.required_registry = defaultdict(dict)

    def init_app(self, app):
        # If True, a `ModRequiredError` will be raised when mod.require('mod') fails
        # If False, the mod will will be skipped (not installed)
        app.config.setdefault('MODS_FAIL_ON_MISSING_REQUIRED', False)

        # Directory where local mods are installed.  Defaults to APP_DIR/mods
        app.config.setdefault('INSTALLED_MODS_DIR', os.path.join(app.config['APP_DIR'], "mods"))

        """ List of mods to load

        Use string ellipses ('...') to separate mods that should be loaded
        first and last.

        If ellipses is found, all mods found in `INSTALLED_MODS_DIR` will
        be loaded then.  Remove the ellipses to disable this auto-loading of
        those mods (and only load the ones you explicitely state here).

        You can also use `DISABLED_MODS` to specifically disable some mods.

        Example::

            INSTALLED_MODS = [
                'mod_a',   # Loaded first
                'mod_b',   # Loaded second
                '...',     # Load other mods found in INSTALLED_MODS_DIR, except
                'mod_y',   # Loaded second to last
                'mod_z',   # Loaded last
            ]

        Default is `['...']` which auto loads all mods found in
        `INSTALLED_MODS_DIR`, in any order
        """
        app.config.setdefault('INSTALLED_MODS', ['...'])

        # Mods that are present in `INSTALLED_MODS_DIR` but shouldn't be installed
        app.config.setdefault('DISABLED_MODS', [])

        self.install_mods(app)

    def extendable(self, obj, name=None):
        """ Decorator to register an class as extendable

        `obj`:  The class to be extended
        `name`:  The name to register this class under.  If omitted, the
            `__name__` of the class is used

        For classes, extending the class inserts your custom class as a base class
        in the hierarchy (at the same level as any other mods extending this class)

        Example::

                     Topic       <- @extendable
                /      |     \
               ModA  ModB  ModC  <- @extend('Topic')
                \     |     /
                 ExtendedTopic   <- import Topic

        The final `ExtendedTopic` is the one that will be imported and used,
        using the same name as the initial class (`import Topic`).

        Your custom class should inherit from `object`, and can override properties
        and methods as is normal for Python multiple inheritance.

        Usage::

            from pybb3.mods import mod

            @mod.extendable
            class Topic(db.Entity):
                ...

            @mod.extend('Topic')
            class CustomizeTopic(object):
                ... add properties/methods ...

        Caution:: Other mods may be extending the same class, so be careful about
        modifying return values, not calling `super` when appropriate, choosing
        method names that may conflict with other mods, etc.  All caveats of
        multiple inheritance apply.

        Important:: If you add a relationship column, you need to also @extend the
        other model to provide the reverse relationship.

        Example adding a `moderator` field to the above `Topic` model::

            @mod.extend('Topic')
            class ModeratorModTopic(object):
                moderator = Required('ModeratorModUser`, reverse='moderated_topics')

            @mod.extend('User'):
            class ModeratorModUser(object):
                moderated_topics = Set('ModeratorModTopic', reverse='moderator')

        (Note that we link the FKs to our customized models, not to core models)

        """
        if isinstance(obj, six.string_types):
            # @mod.extendable('name')
            return functools.partial(self.extendable, name=obj)

        if name is None:
            name = self.extended_object_name_pretty(obj)

        # @mod.extendable
        empty_subclass = obj.__class__(self.extended_object_name(obj), (obj,), {})
        if name in self.extendable_registry:
            raise ClassExtensionError(
                '{} attempted to register as extendable under {!r}, but {} is'
                'already registered under that name.  Change the name under'
                '@extend and @extendable decorations for one or the other'.format(
                    obj, name, self.extendable_registry[name]
                ))
        empty_subclass.__name__ = name
        self.extendable_registry[name] = empty_subclass
        self.extendable_objects.add(empty_subclass)

        # We return an "empty" subclass of the decorated class, so that
        # it is usable in the immediate file.  Later we will replace the
        # __bases__ of this temporary class with any mod-installed custom
        # classes registered via `mod.extend`
        return empty_subclass

    def extend(self, name):
        """ Decorator to extend a `@mod.extendable` class with additional
        fields and/or methods

        `name`: the object or registered name of the object you wish to extend,
            as registered by `@mod.extendable('name')`

        You can provide the actual object, or the name (to resolve import issues)

        See `mod.extendable` for usage

        In addition to decorating a class, you can provide a function that
        receives a base class and must return a subclass.  Example
        (these two are equivalent)::

            from pybb3.mods import mod
            from pybb3.topic.models import Topic

            # Decorate a class
            @mod.extend(Topic)
            class CustomTopic(object):
                ... custom topic fields ...

            # Decorate a callback
            @mod.extend('Topic')
            def extend(base):
                class CustomTopic(base):
                    ... custom topic fields ...

                return CustomTopic

        The callback version may be useful to resolve import issues or otherwise
        move your class definition inside a function
        """
        if name not in self.extendable_registry and name not in self.extendable_objects:
            raise ClassExtensionError(
                'No @mod.extendable objects found under: {!r}'.format(name))

        def wrapper(func):
            self.extend_registry[name].append(func)
            return func
        return wrapper

    def install_check_factory(self):
        """ Constructs a class-scoped (to `Mod`) version of `IsModInstalled`

        Used by `Mod.installed` to check if a given mod is installed or not
        """
        extension = self

        class IsModInstalled(object):
            callback_registry = {}

            def __init__(self, name, version=None):
                # Name / minimum version of the mod
                self.name = name
                self.version = version

            def __nonzero__(self):
                return self.__bool__()

            def __bool__(self):
                """ When evaluated in a boolean expression, return
                 True if the given mod is installed

                 If we haven't loaded all mods yet, raise a `ModInstallError`
                 """
                if not extension.mods_loaded:
                    raise ModInstallError(
                        'mod.installed({!r}, version={!r}) evaluated before all mods have '
                        'been loaded. Either move this check out of the main import '
                        'path of your module or use @mod.installed() as a decorator to '
                        'register a callback once all mods are loaded'.format(
                            self.name, self.version))

                if self.name not in extension.installed_registry:
                    return False

                if self.version is None:
                    return True

                installed_version = extension.installed_registry[self.name]

                if installed_version is None:
                    return True

                return StrictVersion(installed_version) >= StrictVersion(self.version)

            def __call__(self, func):
                """ When used as a decorator, register the given callback
                to be called once all mods are loaded (if the given mod is
                installed)
                """
                IsModInstalled.callback_registry[self] = func
                return func

            @classmethod
            def execute_callbacks(cls):
                for check, callback in IsModInstalled.callback_registry.items():
                    if check:
                        callback()

                IsModInstalled.callback_registry = {}

        return IsModInstalled

    def installed(self, name, version=None):
        """ Evaluates to True if the named mod is installed at the minimum
        given `version`, based on `mod.__version__`

        `version` should be in a format
            comparable by `distutils.version.StrictVersion`

        If the version is omitted (from `version` or from the
            mod's `__version__`), any version is allowed

        Usage::

            from pybb3.mods import mod

            if mod.installed('some_other_mod'):
                ... some_other_mod specific code ...

        Note::  This function can't be used at the top level of your mod, because
        during import of your mod other mods may not have been imported yet, so we
        don't have a full list of the installed mods yet.

        To mitigate this, you can also use `installed` as a decorator, which
        registers your function to be called later once all mods are loaded.

        For example::

            from pybb3.mods import mod

            @mod.installed('some_other_mod')
            def other_mod_code():
                # called after all mods have been loaded, and only if
                # some_other_mod is installed

        """
        return self.install_check(name, version=version)

    @property
    def install_check(self):
        if self._install_check is None:
            self._install_check = self.install_check_factory()
        return self._install_check
    _install_check = None

    def require(self, required, version=None):
        """ Raises an error if the named mod is not installed at the minimum given `version`

        `version` should be in the format comparable by `distutils.version.StrictVersion`

        If `version` is omitted, any version is allowed
        """
        frame = inspect.stack()[1]
        mod = inspect.getmodule(frame[0])
        self.required_registry[mod][required] = version

    def validate_required_mods(self):
        for mod, required_mods in self.required_registry.items():
            for required, version in required_mods.items():
                if not self.installed(required, version=version):
                    raise ModRequiredError('{mod} requires {required!r}{atversion}, which was not found.'.format(
                        mod=mod,
                        required=required,
                        atversion='' if version is None else ' with minimum version {!r}'.format(version)
                    ))
                logger.debug('    Mod {} requires {!r} (version: {!r}) ...ok'.format(
                    mod, required, 'any' if version is None else version
                ))

    def extended_object_name(self, obj):
        """ Returns the class's name with the EXTENDED_OBJECT_SUFFIX added """
        try:
            return obj.__name__ + self.EXTENDED_OBJECT_SUFFIX
        except AttributeError:
            # cls is a string
            return obj + self.EXTENDED_OBJECT_SUFFIX

    def extended_object_name_pretty(self, obj):
        """ Returns the class's name with the EXTENSION_SUFFIX removed """
        try:
            return obj.__name__.rsplit(self.EXTENDED_OBJECT_SUFFIX, 1)[0]
        except AttributeError:
            # cls is a string
            return obj.rsplit(self.EXTENDED_OBJECT_SUFFIX, 1)[0]

    def generate_extended_base(self, cls, extension):
        if isinstance(extension, type):
            # If a class, convert it into a db.Entity
            return cls.__class__(extension.__name__, (cls,), dict(extension.__dict__))
        else:
            # Otherwise assume a callable and pass in the base class
            return extension(cls)

    def load_model_extensions(self, name, obj):
        base = obj.__base__

        # objects can be registered by name or by reference
        extensions = self.extend_registry[name] + self.extend_registry[obj]
        extended_bases = (self.generate_extended_base(base, extension) for extension in extensions)
        filtered_bases = tuple(base for base in extended_bases if base is not None)
        if filtered_bases:
            return filtered_bases, extensions
        else:
            return (base,), (None,)

    def extend_objects(self):
        """ The registry contains "empty subclass" objects in the form::

                @mod.extendable
                class Topic(...):
                    ...

                class EmptyTopic(Topic):
                    pass

            In order to extend these classes, we will load any custom classes
            from installed mods and insert them in the hierarchy::

                @mod.extendable
                class Topic(...):
                    ...

                class CustomModA(Topic):
                    ...

                class CustomModB(Topic):
                    ...

                class EmptyTopic(CustomModA, CustomModB):
                    pass

            By changing `EmptyTopic.__bases__` to `(CustomModA, CustomModB, ...)`
        """
        for name, obj in self.extendable_registry.items():
            base = obj.__base__

            # Load all bases generated by installed mods, to be inserted
            bases, extensions = self.load_model_extensions(name, obj)
            if bases[0] is base:
                logger.debug('No extensions found for {}'.format(str(base)))
                continue

            try:
                logger.debug('Extending {} with:\n    {}'.format(
                    obj.__base__, '\n    '.join(map(str, bases))))
                # Switch `EmptyTopic` bases from `Topic` to the list of mod bases
                obj.__bases__ = bases

                if isinstance(obj, EntityMeta):
                    # When extending pony orm `db.Entity`, we need to monkey patch
                    # some properties that are set in `EntityMeta.__new__` that
                    # depend on the entity's current `__bases__`.  Since we
                    # change `__bases__` after `__new__` has run, some properties
                    # are incorrect (for example parent class table fields, etc)
                    #
                    # To fix this, we create a temporary subclass so that
                    # EntityMeta.__new__ is called with all mod base clases,
                    # and then copy over those properties to our Empty class
                    #
                    # We can't just use the temporary subclass, because our
                    # Empty class is a live reference to the object back in
                    # the original module, so we need to mutate it.
                    tempobj_name = obj.__name__ + '_TEMP'
                    tempobj = obj.__class__(tempobj_name, bases, {})

                    # _id_ holds a creation counter.  `obj` was created before
                    # the mod classes, so it's `_id_` is lower, but we need it to
                    # be greater so that it is initialized after them, since
                    # we are moving it from above to below them in the class
                    # hierarchy
                    obj._id_ = tempobj._id_

                    # Set the correct columns
                    obj._adict_ = tempobj._adict_
                    obj._attrs_ = tempobj._attrs_
                    obj._base_attrs_ = tempobj._base_attrs_

                    # Fix base classes of our new class
                    obj._all_bases_ = tempobj._all_bases_
                    obj._direct_bases_ = tempobj._direct_bases_

                    # Add our new subclass to all parent classes
                    for parent_class in tempobj.__mro__:
                        if hasattr(parent_class, '_subclasses_'):
                            parent_class._subclasses_.discard(tempobj)
                            parent_class._subclasses_.add(obj)

                    # Clean up traces of our temporary class
                    # Should be no more references to tempobj after this
                    del obj._database_.entities[tempobj_name]
                    del obj._database_.__dict__[tempobj_name]
                    del obj._discriminator_attr_.code2cls[tempobj_name]

            except Exception as e:
                raise e.__class__(
                    '{}\n'
                    'when constructing {} from bases:\n'
                    '{}:'.format(
                        e, obj, '\n'.join('{}'.format(base) for extension, base in zip(extensions, bases))
                    )
                )

    def register_core_models(self):
        """ Ensure that core models are imported and registered as `extendable` """
        from ...person import Person
        from ...post import Post



        logger.debug('Loaded core models: {}'.format(
            ', '.join(c.__name__ for c in [Person, Post])))

    def load_mod(self, mod_name, fail_on_missing_required=False):
        mod_path = 'sandbox.mods.{}'.format(mod_name)
        logger.debug('    Installing {}'.format(mod_path))
        try:
            imported = importlib.import_module(mod_path)
        except ModRequiredError as e:
            if fail_on_missing_required:
                raise
            else:
                logger.warning(str(e))
                return
        mod_version = getattr(imported, '__version__', None)
        self.installed_registry[mod_name] = mod_version

    def populate_mod_cache(self, installed_mods_dir=None, installed_mods=None,
                           disabled_mods=None, fail_on_missing_required=False):
        if self.installed_registry:
            return

        if installed_mods is None:
            isntalled_mods = []

        if disabled_mods is None:
            disabled_mods = []

        # Import mods to load object_extension_registry
        files = glob.glob(
            os.path.join(installed_mods_dir, '*.py')
        )
        modules = [os.path.basename(f)[:-3] for f in files]
        mod_names = set(module for module in modules if module != '__init__')

        installed_mods_iter = iter(installed_mods)
        load_first = list(itertools.takewhile(lambda m: m != '...', installed_mods_iter))
        load_last = list(installed_mods_iter)

        # These mods are found in `INSTALLED_MOD_DIR` but not specified
        # in `INSTALLED_MODS`.  Only loaded if '...' is present in `INSTALLED_MODS`
        unordered_mods = set(mod_names) - set(load_first) - set(load_last)

        # First install any mods listed first in the `mod_load_order` configuration
        for first_mod in load_first:
            if first_mod not in mod_names:
                logger.warning('Mod {!r} in mod_load_order list not found, skipping'.format(first_mod))
                continue
            self.load_mod(first_mod, fail_on_missing_required=fail_on_missing_required)

        # If ellipses is present, load all mods in `INSTALLED_MOD_DIR`
        # Sorted by name for consistency
        if '...' in installed_mods:
            for mod in sorted(unordered_mods):
                self.load_mod(mod, fail_on_missing_required=fail_on_missing_required)

        # Finally install any mods listed last in the `mod_load_order` configuration
        for last_mod in load_last:
            if last_mod not in mod_names:
                logger.warning('Mod {!r} in mod_load_order list not found, skipping'.format(last_mod))
                continue
            self.load_mod(last_mod, fail_on_missing_required=fail_on_missing_required)

    def install_mods(self, app):
        logger.debug('Importing core models')
        self.register_core_models()

        logger.debug('Installing mods')
        self.populate_mod_cache(
            installed_mods_dir=app.config['INSTALLED_MODS_DIR'],
            installed_mods=app.config['INSTALLED_MODS'],
            disabled_mods=app.config['DISABLED_MODS'],
            fail_on_missing_required=app.config['MODS_FAIL_ON_MISSING_REQUIRED'],
        )

        self.mods_loaded = True

        logger.debug('Validating required mods')
        self.validate_required_mods()

        self.install_check.execute_callbacks()

        logger.debug('Extending objects')
        self.extend_objects()
