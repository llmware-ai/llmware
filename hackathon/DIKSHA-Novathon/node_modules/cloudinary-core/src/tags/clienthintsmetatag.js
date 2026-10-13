/**
 * Image Tag
 * Depends on 'tags/htmltag', 'cloudinary'
 */

import HtmlTag from './htmltag';

import {
  assign
} from '../util';

/**
 * Creates an HTML (DOM) Meta tag that enables Client-Hints for the HTML page. <br/>
 *  See
 *  <a href="https://cloudinary.com/documentation/responsive_images#automating_responsive_images_with_client_hints"
 *  target="_new">Automating responsive images with Client Hints</a> for more details.
 * @constructor ClientHintsMetaTag
 * @extends HtmlTag
 * @param {object} options
 * @example
 * tag = new ClientHintsMetaTag()
 * //returns: <meta http-equiv="Accept-CH" content="DPR, Viewport-Width, Width">
 */
class ClientHintsMetaTag extends HtmlTag {
  constructor(options) {
    super('meta', void 0, assign({
      "http-equiv": "Accept-CH",
      content: "DPR, Viewport-Width, Width"
    }, options));
  }

  /** @override */
  closeTag() {
    return "";
  }

};

export default ClientHintsMetaTag;
