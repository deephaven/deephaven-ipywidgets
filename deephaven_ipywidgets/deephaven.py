#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2016-2022 Deephaven Data Labs and Patent Pending
#

"""
Module for displaying Deephaven widgets within interactive python environments.
"""
from __future__ import annotations

import __main__
from typing import Any

from ipywidgets import DOMWidget
from traitlets import Unicode, Integer, Bytes, Bool
from uuid import uuid4
from ._frontend import module_name, module_version
import os
import base64
import atexit

TABLE_TYPES = {"deephaven.table.Table", "pandas.core.frame.DataFrame", "pydeephaven.table.Table"}
FIGURE_TYPES = {"deephaven.plot.figure.Figure"}


def _str_object_type(obj):
    """Returns the object type as a string value"""
    return f"{obj.__class__.__module__}.{obj.__class__.__name__}"


def _path_for_object(obj):
    """Return the iframe path for the specified object. Inspects the class name to determine."""
    name = _str_object_type(obj)

    if name in TABLE_TYPES:
        return "table"
    if name in FIGURE_TYPES:
        return "chart"

    # No special handling for this type, just try it as a widget
    return "widget"


def _cleanup(widget: DeephavenWidget):
    """
    Remove the widget when the kernel is shutdown

    Args:
        widget (DeephavenWidget): The widget to remove
    """
    widget.set_trait("kernel_active", False)


def _check_session(session: Any, params: dict):
    """
    Check the session for a session manager and set the parameters for the widget

    Args:
        session: The session to check
        params: The parameters to set

    Returns:
        str, str: The server URL and token to use

    """

    token = ""

    port = session.port
    server_url = f"http://{session.host}:{port}/"

    if hasattr(session, "_extra_headers") and b"envoy-prefix" in session._extra_headers:
        params["envoyPrefix"] = session._extra_headers[b"envoy-prefix"].decode(
            "ascii"
        )

    if hasattr(session, "session_manager"):
        params["authProvider"] = "parent"
        # We have a DnD session, and we can get the authentication and connection details from the session manager
        token = base64.b64encode(
            session.session_manager.auth_client.get_token(
                "RemoteQueryProcessor"
            ).SerializeToString()
        ).decode("us-ascii")
        server_url = (
            session.pqinfo().state.connectionDetails.staticUrl
        )

    return server_url, token


class DeephavenWidget(DOMWidget):
    """A wrapper for viewing DeephavenWidgets in IPython"""

    _model_name = Unicode("DeephavenModel").tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode("DeephavenView").tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    server_url = Unicode().tag(sync=True)
    iframe_url = Unicode().tag(sync=True)
    width = Integer().tag(sync=True)
    height = Integer().tag(sync=True)
    token = Unicode().tag(sync=True)
    kernel_active = Bool().tag(sync=True)

    def __init__(self, deephaven_object, height=600, width=0, session=None):
        """Create a Deephaven widget for displaying in an interactive Python console.

        Args:
            deephaven_object (deephaven.table.Table | pandas.core.frame.DataFrame | pydeephaven.table.Table | str): the Deephaven object to display, or the name of the object if using pydeephaven
            height (int): the height of the table
            width (int): the width of the table. Set to 0 to take up full width of notebook.
            session (pydeephaven.session.Session): the session to load the table from. Required only if using a remote pydeephaven object by name.
        """
        super(DeephavenWidget, self).__init__()

        # Generate a new table ID using a UUID prepended with a `t_` prefix
        object_id = (
            deephaven_object
            if isinstance(deephaven_object, str)
            else f"_{str(uuid4()).replace('-', '_')}"
        )

        params = {"name": object_id}
        port = 10000
        token = ""

        if isinstance(deephaven_object, str):
            if session is None:
                raise ValueError(
                    "session must be specified when using a remote pydeephaven object by name"
                )

            server_url, token = _check_session(session, params)

        elif _str_object_type(deephaven_object) == "pydeephaven.table.Table":
            session = deephaven_object.session

            server_url, token = _check_session(session, params)

            session.bind_table(object_id, deephaven_object)
        else:
            from deephaven_server import Server
            port = Server.instance.port
            server_url = f"http://localhost:{port}/"

            # Add the table to the main modules globals list so it can be retrieved by the iframe
            __main__.__dict__[object_id] = deephaven_object

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
        iframe_url = (
            f"{server_url}iframe/{_path_for_object(deephaven_object)}/{param_string}"
        )

        self.set_trait("server_url", server_url)
        self.set_trait("iframe_url", iframe_url)
        self.set_trait("width", width)
        self.set_trait("height", height)
        self.set_trait("token", token)
        self.set_trait("kernel_active", True)

        atexit.register(_cleanup, self)
