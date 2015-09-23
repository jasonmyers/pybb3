# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from pybb3 import converters


class TestConverters:

    def test_flag_converter(self):
        converter = converters.FlagConverter(map={})

        # Convert url parameters to python
        assert converter.to_python('0') is False
        assert converter.to_python('false') is False
        assert converter.to_python('False') is False
        assert converter.to_python(None) is False

        assert converter.to_python('') is True
        assert converter.to_python('1') is True
        assert converter.to_python('true') is True
        assert converter.to_python('True') is True
        assert converter.to_python('anything else') is True

        # Convert python to url parameters
        assert converter.to_url(0) is '0'
        assert converter.to_url('0') is '0'
        assert converter.to_url(False) is '0'
        assert converter.to_url('false') is '0'
        assert converter.to_url('False') is '0'
        assert converter.to_url(None) is '0'

        assert converter.to_url('') is '1'
        assert converter.to_url(1) is '1'
        assert converter.to_url('1') is '1'
        assert converter.to_url(True) is '1'
        assert converter.to_url('true') is '1'
        assert converter.to_url('True') is '1'
        assert converter.to_url('anything else') is '1'

    def test_entity_converter(self):
        pass
