/**
 * Image Tag
 * Depends on 'tags/htmltag', 'cloudinary'
 */
import {generateImageResponsiveAttributes, generateMediaAttr} from "../util/srcsetUtils";
import {merge} from '../util';
import url from '../url';
import HtmlTag from './htmltag';

/**
 * Creates an HTML (DOM) Image tag using Cloudinary as the source.
 * @constructor SourceTag
 * @extends HtmlTag
 * @param {string} [publicId]
 * @param {Object} [options]
 */
class SourceTag extends HtmlTag {
  constructor(publicId, options = {}) {
    super("source", publicId, options);
  }

  /** @override */
  closeTag() {
    return "";
  }

  /** @override */
  attributes() {
    let srcsetParam = this.getOption('srcset');
    let attr = super.attributes() || {};
    let options = this.getOptions();
    merge(attr, generateImageResponsiveAttributes(this.publicId, attr, srcsetParam, options));
    if(!attr.srcset){
      attr.srcset = url(this.publicId, options);
    }
    if(!attr.media && options.media){
      attr.media = generateMediaAttr(options.media);
    }

    return attr;
  }

};

export default SourceTag;
