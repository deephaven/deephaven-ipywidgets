#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Deephaven Data Labs LLC.
# Distributed under the terms of the Modified BSD License.

import pytest

from unittest.mock import patch
from deephaven_server import Server
from ..deephaven import DeephavenWidget

server = Server(port=9876)
server.start()

@patch('deephaven.table.Table')
def test_example_creation_blank(MockTableClass):
    mock_table = MockTableClass()
    mock_table.__class__.__module__ = 'deephaven.table'
    mock_table.__class__.__name__ = 'Table'
    w = DeephavenWidget(mock_table)
    assert w.server_url == 'http://localhost:9876/'
    assert str(w.iframe_url).startswith('http://localhost:9876/iframe/table/?name=t_')
