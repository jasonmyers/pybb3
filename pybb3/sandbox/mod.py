# -*- coding: utf-8 -*-

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

    """
    bases = load_extended_models(cls)
    try:
        return cls.__class__(cls.__name__ + EXTENSION_SUFFIX, bases, {})
    except Exception as e:
        raise e.__class__('Error constructing {} from bases {}:\n{}'.format(cls, bases, e))


def extend(name, cls='Entity'):
    """ Decorator to extend a pybb3 table/model with additional fields and
    methods

    `name`: the class name (string) of the model to extend
    `cls`: the name of the type of the class, for disambiguation

    You can decorate a plain class, or a function that receives a base class
    and must return a subclass.  Example (these two are equivalent)::

        from pybb3 import mod

        @mod.extend('Topic')
        class CustomTopic(object):
            ... custom topic fields ...

        @mod.extend('Topic')
        def extend(base):
            class CustomTopic(base):
                ... custom topic fields ...

            return CustomTopic

    The class you decorate/return will be added as a parent class to the final
    model.  e.g., given a Topic model structure of::

        class BaseTopic(db.Entity):
            ... core Topic fields / methods ...

        class Topic(BaseTopic):
            # Final constructed Topic model for use in queries
            pass

    The model class you return from your decorated class/function will be inserted
    as a base class before `Topic`, e.g.::

        class BaseTopic(db.Entity):
            ... core topic fields / methods ...

        class CustomTopic(BaseTopic):
            ... your custom topic fields ...

        class Topic(YourTopicMod):
            # Final constructed Topic model for use in queries
            pass

    Note:: It is recommended to define your custom models in-line in the
    function to avoid import issues

    Note:: If you add a relationship field, you need to also extend the other
    model to provide the reverse relationship.  Relationships added here are
    queryable between your custom models and the core pybb3 models, but not among
    other installed mods (currently)

    """
    def wrapper(func):
        model_extension_registry[cls][name].add(func)
        return func
    return wrapper


def generate_extended_base(cls, extension):
    if isinstance(extension, type):
        # If a class, convert it into a db.Entity
        return EntityMeta(extension.__name__, (cls,), dict(extension.__dict__))
    else:
        # Otherwise assum a callable and pass in the base class
        return extension(cls)


def installed(mod, version=None):
    """ True if the named mode is installed at the minimum given version """
    return True


installed_mods = set()


def load_mods():
    global installed_mods
    # Import mods to load model_extension_registry
    files = glob.glob(INSTALLED_MODS_DIR)
    modules = [os.path.basename(f)[:-3] for f in files]
    mods = [module for module in modules if module != '__init__']
    installed_mods = __import__('sandbox.mods', fromlist=mods)
    return installed_mods


def load_extended_models(cls):
    load_mods()
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
