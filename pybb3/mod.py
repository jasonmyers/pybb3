# -*- coding: utf-8 -*-
""" Utilities for installed modifications to pybb3 """
from __future__ import unicode_literals

import os
import glob

from collections import defaultdict

from pony.orm.core import EntityMeta


INSTALLED_MODS_DIR = os.path.join(os.path.dirname(__file__), "mods", "*.py")
EXTENSION_SUFFIX = 'Extended'

# {'Base': {'Class': {extensions...}}}
model_extension_registry = defaultdict(lambda: defaultdict(set))


def extendable(cls):
    """ Class decorator to mark a class as extendable with `mod.extend`

    Usage::

        from pybb3 import mod

        @mod.extendable
        class Topic(db.Entity):
            ...

        @mod.extend('Topic')
        def extend(base):
            class ExtendedTopic(base):
                ...
            return ExtendedTopic

    Note:: It is recommended to perform register all extensions with `mod.extend` before
    defining any custom `mod.extendable` classes.  Classes cannot be extended further
    once they have been defined.

    """
    return cls.__class__(cls.__name__ + EXTENSION_SUFFIX, load_extended_models(cls), {})


def extend(model, cls=None):
    """ Decorator to extend a pybb3 class with additional fields and
    methods

    `name`: the name (string) of the class to extend
    `cls`: the base class of the class, e.g. `db.Entity` (default),
        `Choices`, etc.  The given class must be decorated by `mod.extendable`

    Your decorated function will be passed a base class, and you should return
    a subclass of it with your custom fields and methods, which will be added
    to the final constructed class.

    e.g., given a Topic model structure of::

        class BaseTopic(db.Entity):
            ... core Topic fields / methods ...

        class Topic(BaseTopic):
            # Final constructed Topic model for use in queries
            pass

    The model class you return from your decorated function will be inserted
    as a base class before `Topic`, e.g.::

        class BaseTopic(db.Entity):
            ... core topic fields / methods ...

        class YourTopicMod(BaseTopic):
            ... your custom topic fields / methods ...

        class Topic(YourTopicMod):
            # Final constructed Topic model for use in queries
            pass

    Example usage::

        from pybb3 import mod

        @mod.extend('Topic')
        def extend(base):
            class MyTopicMod(base):
                ... my custom topic fields / methods ...

            return MyTopicMod

    Note:: It is recommended to define your custom class in-line in the
    function to avoid import issues

    Note:: If you add a relationship field, you need to also extend the other
    model to provide the reverse relationship.

    Note:: It is recommended to perform register all extensions with `mod.extend` before
    defining any custom `mod.extendable` classes.  Classes cannot be extended further
    once they have been defined.

    """
    if cls is None:
        from pybb3.database import db
        cls = db.Entity

    def wrapper(func):
        model_extension_registry[cls][model].add(func)
        return func
    return wrapper


def generate_extended_base(cls, extension):
    if isinstance(extension, type):
        # If a class, convert it into a db.Entity
        return EntityMeta(extension.__name__, (cls,), dict(extension.__dict__))
    else:
        # Otherwise assume a callable and pass in the base class
        return extension(cls)


def installed(mod, version=None):
    """
    Checks if a given mod is installed and enabled with the given minimum
    version (`None` for any version).
    """
    return True


def require(mod, version=None):
    """
    Fails if the given mod is not installed and enabled
    """
    return True


def load_extended_models(cls):
    """ Return a list of extensions for a given base class, based on
    installed mods decorating with `mod.extend`
    """
    # Import mods to load model_extension_registry
    files = glob.glob(INSTALLED_MODS_DIR)
    modules = [os.path.basename(f)[:-3] for f in files]
    mods = [module for module in modules if module != '__init__']
    __import__('pybb3.mods', fromlist=mods)

    name = extended_class_name_pretty(cls)

    extensions = model_extension_registry[cls.__base__.__name__][name]
    extended_bases = tuple(generate_extended_base(cls, extension) for extension in extensions)
    return extended_bases or (cls,)


def extended_class_name(cls):
    """ Returns the class's name with the EXTENSION_SUFFIX added """
    try:
        return cls.__name__ + EXTENSION_SUFFIX
    except AttributeError:
        # cls is a string
        return cls + EXTENSION_SUFFIX


def extended_class_name_pretty(cls):
    """ Returns the class's name with the EXTENSION_SUFFIX removed """
    try:
        return cls.__name__.rsplit(EXTENSION_SUFFIX, 1)[0]
    except AttributeError:
        # cls is a string
        return cls.rsplit(EXTENSION_SUFFIX, 1)[0]
