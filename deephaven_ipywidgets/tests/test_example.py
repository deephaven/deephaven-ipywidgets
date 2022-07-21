#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mike Bender.
# Distributed under the terms of the Modified BSD License.

import pytest

from ..deephaven import DeephavenWidget


def test_example_creation_blank():
    w = DeephavenWidget()
    assert w.value == 'Hello World'
