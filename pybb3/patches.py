# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def debugger():
    """ Adds a 'debugger' command to builtins """
    try:
        import ipdb as pdb
    except ImportError:
        import pdb
    import inspect
    import sys

    try:
        trace_frame = inspect.stack()[1][0]
    except:
        trace_frame = sys._getframe().f_back

    pdb.set_trace(trace_frame)

__builtins__['debugger'] = debugger
