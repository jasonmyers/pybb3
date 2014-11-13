# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import functools

import logging
logger = logging.getLogger(__name__)


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


from flask_wtf.form import Form
original_validate_on_submit = Form.validate_on_submit


@functools.wraps(original_validate_on_submit)
def log_form_errors(self, *args, **kwargs):
    try:
        return original_validate_on_submit(self, *args, **kwargs)
    finally:
        if self.errors:
            logger.debug("Errors in {form}: {errors}".format(
                form=self, errors=self.errors))

Form.validate_on_submit = log_form_errors
