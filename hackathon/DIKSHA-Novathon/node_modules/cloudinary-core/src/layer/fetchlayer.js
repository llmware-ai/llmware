import Layer from './layer';

import {
  base64EncodeURL,
  isString
} from '../util';

class FetchLayer extends Layer {
  /**
   * @class FetchLayer
   * @classdesc Creates an image layer using a remote URL.
   * @param {Object|string} options - layer parameters or a url
   * @param {string} options.url the url of the image to fetch
   */
  constructor(options) {
    super(options);
    if (isString(options)) {
      this.options.url = options;
    } else if (options != null ? options.url : void 0) {
      this.options.url = options.url;
    }
  }

  url(url) {
    this.options.url = url;
    return this;
  }

  /**
   * generate the string representation of the layer
   * @function FetchLayer#toString
   * @return {String}
   */
  toString() {
    return `fetch:${base64EncodeURL(this.options.url)}`;
  }

}

export default FetchLayer;
