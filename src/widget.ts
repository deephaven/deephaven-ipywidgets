/* eslint-disable camelcase */
/* eslint-disable max-classes-per-file */
// Copyright (c) Deephaven Data Labs LLC
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';
import {
  isMessage,
  LOGIN_OPTIONS_REQUEST,
  makeResponse,
} from '@deephaven/jsapi-utils';
import Log from '@deephaven/log';
import { MODULE_NAME, MODULE_VERSION } from './version';

// Import the CSS
import '../css/widget.css';

const log = Log.module('deephaven-ipywidgets.widget');

export class DeephavenModel extends DOMWidgetModel {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  defaults(): any {
    return {
      ...super.defaults(),
      _model_name: DeephavenModel.model_name,
      _model_module: DeephavenModel.model_module,
      _model_module_version: DeephavenModel.model_module_version,
      _view_name: DeephavenModel.view_name,
      _view_module: DeephavenModel.view_module,
      _view_module_version: DeephavenModel.view_module_version,
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    // Add any extra serializers here
  };

  static model_name = 'DeephavenModel';

  static model_module = MODULE_NAME;

  static model_module_version = MODULE_VERSION;

  static view_name = 'DeephavenView'; // Set to null if no view

  static view_module = MODULE_NAME; // Set to null if no view

  static view_module_version = MODULE_VERSION;
}

export class DeephavenView extends DOMWidgetView {
  private iframe: HTMLIFrameElement;

  sendAuthenticationResponse = (
    messageId: string,
    childWindow: WindowProxy,
    url: string
  ): void => {
    const token = this.model.get('token');

    const payload = {
      type: 'io.deephaven.proto.auth.Token',
      token,
    };

    try {
      log.info('Sending login options to iframe', url);
      childWindow.postMessage(makeResponse(messageId, payload), url);
    } catch (e) {
      log.error(e);
    }
  };

  handleAuthentication = (event: MessageEvent<unknown>): void => {
    const { data, source, origin } = event;

    if (
      source == null ||
      source instanceof MessagePort ||
      source instanceof ServiceWorker ||
      source !== this.iframe.contentWindow
    ) {
      log.debug('Ignore message, invalid event source', source);
      return;
    }

    if (!isMessage(data)) {
      log.debug('Ignore unsupported message', data);
      return;
    }

    switch (data.message) {
      case LOGIN_OPTIONS_REQUEST:
        this.sendAuthenticationResponse(data.id, source, origin);
        break;
      default: {
        log.debug('Ignore unsupported message', data.message);
      }
    }
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  render(): any {
    const iframeUrl = this.model.get('iframe_url');
    const width = this.model.get('width');
    const height = this.model.get('height');

    window.addEventListener('message', this.handleAuthentication);

    log.info('init_element for widget', iframeUrl, width, height);

    this.iframe = document.createElement('iframe');
    this.iframe.src = iframeUrl;
    if (width > 0) {
      this.iframe.width = width;
      this.iframe.style.width = `${width}px`;
    }
    if (height > 0) {
      this.iframe.height = height;
      this.iframe.style.height = `${height}px`;
    }
    this.el.className = 'deephaven-ipywidgets-widget';
    this.el.appendChild(this.iframe);
  }
}
