// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

// Add any needed widget imports here (or from controls)
// import {} from '@jupyter-widgets/base';

import { createTestModel } from './utils';

import { DeephavenModel } from '..';

describe('Basic Tests', () => {
  describe('DeephavenModel', () => {
    it('should be createable with a value', () => {
      const iframeUrl = 'http://localhost:8080/test';
      const state = { iframe_url: iframeUrl };
      const model = createTestModel(DeephavenModel, state);
      expect(model).toBeInstanceOf(DeephavenModel);
      expect(model.get('iframe_url')).toEqual(iframeUrl);
    });
  });
});
