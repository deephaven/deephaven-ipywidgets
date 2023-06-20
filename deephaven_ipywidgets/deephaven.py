#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2016-2022 Deephaven Data Labs and Patent Pending
#

"""
Module for displaying Deephaven widgets within interactive python environments.
"""

import __main__
from ipywidgets import DOMWidget
from traitlets import Unicode, Integer, Bytes
from deephaven_server import Server
from uuid import uuid4
from ._frontend import module_name, module_version
import os
import base64
import json


def _str_object_type(obj):
    """Returns the object type as a string value"""
    return f"{obj.__class__.__module__}.{obj.__class__.__name__}"


def _path_for_object(obj):
    """Return the iframe path for the specified object. Inspects the class name to determine."""
    name = _str_object_type(obj)

    if name in ('deephaven.table.Table', 'pandas.core.frame.DataFrame', 'pydeephaven.table.Table'):
        return 'table'
    if name == 'deephaven.plot.figure.Figure':
        return 'chart'
    raise TypeError(f"Unknown object type: {name}")



class DeephavenWidget(DOMWidget):
    """A wrapper for viewing DeephavenWidgets in IPython
    """
    _model_name = Unicode('DeephavenModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('DeephavenView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    object_id = Unicode().tag(sync=True)
    object_type = Unicode().tag(sync=True)
    server_url = Unicode().tag(sync=True)
    iframe_url = Unicode().tag(sync=True)
    width = Integer().tag(sync=True)
    height = Integer().tag(sync=True)
    token = Unicode().tag(sync=True)

    def __init__(self, deephaven_object, height=600, width=0):
        """Create a Deephaven widget for displaying in an interactive Python console.

        Args:
            deephaven_object (Table): the Deephaven object to display
            height (int): the height of the table
            width (int): the width of the table. Set to 0 to take up full width of notebook.
        """
        super(DeephavenWidget, self).__init__()

        # Generate a new table ID using a UUID prepended with a `t_` prefix
        object_id = f"t_{str(uuid4()).replace('-', '_')}"

        params = {
            "name": object_id
        }

        token = ''

        if _str_object_type(deephaven_object) == 'pydeephaven.table.Table':
            session = deephaven_object.session

            envoy_prefix = session._extra_headers[
                b'envoy-prefix'].decode('ascii')

            token = base64.b64encode(
                session.session_manager.auth_client.get_token("RemoteQueryProcessor").SerializeToString()
            ).decode('us-ascii')

            params.update({
                "authProvider": "parent",
                "envoyPrefix": envoy_prefix
            })

            port = deephaven_object.session.port
            server_url = f"https://{deephaven_object.session.host}:{port}"

            session.bind_table(object_id, deephaven_object)
        else:
            port = Server.instance.port
            server_url = f"http://localhost:{port}/"

        param_values = [f"{k}={v}" for k, v in params.items()]
        param_string = "?" + "&".join(param_values)

        if "DEEPHAVEN_IPY_URL" in os.environ:
            server_url = os.environ["DEEPHAVEN_IPY_URL"]

        try:
            from google.colab.output import eval_js
            server_url = eval_js(f"google.colab.kernel.proxyPort({port})")
        except ImportError:
            pass

        if not server_url.endswith("/"):
            server_url = f"{server_url}/"

        # Generate the iframe_url from the object type
        iframe_url = f"{server_url}iframe/{_path_for_object(deephaven_object)}/{param_string}"
        # Add the table to the main modules globals list so it can be retrieved by the iframe
        __main__.__dict__[object_id] = deephaven_object

        self.set_trait('server_url', server_url)
        self.set_trait('iframe_url', iframe_url)
        self.set_trait('object_id', object_id)
        self.set_trait('object_type', _str_object_type(deephaven_object))
        self.set_trait('width', width)
        self.set_trait('height', height)
        self.set_trait('token', token)
