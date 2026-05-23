/**
 * Video Tag
 * Depends on 'tags/htmltag', 'util', 'cloudinary'
 */

import {
  DEFAULT_VIDEO_PARAMS,
  DEFAULT_IMAGE_PARAMS
} from '../constants';

import url from '../url';

import {
  defaults,
  isPlainObject,
  isArray,
  isEmpty,
  omit
} from '../util';

import HtmlTag from './htmltag';


const VIDEO_TAG_PARAMS = ['source_types', 'source_transformation', 'fallback_content', 'poster', 'sources'];

const DEFAULT_VIDEO_SOURCE_TYPES = ['webm', 'mp4', 'ogv'];

const DEFAULT_POSTER_OPTIONS = {
  format: 'jpg',
  resource_type: 'video'
};

/**
 * Creates an HTML (DOM) Video tag using Cloudinary as the source.
 * @constructor VideoTag
 * @extends HtmlTag
 * @param {string} [publicId]
 * @param {Object} [options]
 */
class VideoTag extends HtmlTag {
  constructor(publicId, options = {}) {
    options = defaults({}, options, DEFAULT_VIDEO_PARAMS);
    super("video", publicId.replace(/\.(mp4|ogv|webm)$/, ''), options);
  }

  /**
   * Set the transformation to apply on each source
   * @function VideoTag#setSourceTransformation
   * @param {Object} an object with pairs of source type and source transformation
   * @returns {VideoTag} Returns this instance for chaining purposes.
   */
  setSourceTransformation(value) {
    this.transformation().sourceTransformation(value);
    return this;
  }

  /**
   * Set the source types to include in the video tag
   * @function VideoTag#setSourceTypes
   * @param {Array<string>} an array of source types
   * @returns {VideoTag} Returns this instance for chaining purposes.
   */
  setSourceTypes(value) {
    this.transformation().sourceTypes(value);
    return this;
  }

  /**
   * Set the poster to be used in the video tag
   * @function VideoTag#setPoster
   * @param {string|Object} value
   * - string: a URL to use for the poster
   * - Object: transformation parameters to apply to the poster. May optionally include a public_id to use instead of the video public_id.
   * @returns {VideoTag} Returns this instance for chaining purposes.
   */
  setPoster(value) {
    this.transformation().poster(value);
    return this;
  }

  /**
   * Set the content to use as fallback in the video tag
   * @function VideoTag#setFallbackContent
   * @param {string} value - the content to use, in HTML format
   * @returns {VideoTag} Returns this instance for chaining purposes.
   */
  setFallbackContent(value) {
    this.transformation().fallbackContent(value);
    return this;
  }

  content() {
    let sourceTypes = this.transformation().getValue('source_types');
    const sourceTransformation = this.transformation().getValue('source_transformation');
    const fallback = this.transformation().getValue('fallback_content');
    let sources = this.getOption('sources');
    let innerTags = [];
    if (isArray(sources) && !isEmpty(sources)) {
      innerTags = sources.map(source => {
        let src = url(this.publicId, defaults(
            {},
            source.transformations || {},
            {resource_type: 'video', format: source.type}
            ), this.getOptions());
        return  this.createSourceTag(src, source.type, source.codecs);
      });
    } else {
      if (isEmpty(sourceTypes)) {
        sourceTypes = DEFAULT_VIDEO_SOURCE_TYPES;
      }
      if (isArray(sourceTypes)) {
        innerTags = sourceTypes.map(srcType => {
          let src = url(this.publicId, defaults(
              {},
              sourceTransformation[srcType] || {},
              {resource_type: 'video', format: srcType}
          ), this.getOptions());
          return  this.createSourceTag(src, srcType);
        });
      }
    }
    return innerTags.join('') + fallback;
  }

  attributes() {
    let sourceTypes = this.getOption('source_types');
    let poster = this.getOption('poster');
    if (poster === undefined) {
      poster = {};
    }
    if (isPlainObject(poster)) {
      let defaultOptions = poster.public_id != null ? DEFAULT_IMAGE_PARAMS : DEFAULT_POSTER_OPTIONS;
      poster = url(poster.public_id || this.publicId, defaults({}, poster, defaultOptions, this.getOptions()));
    }
    let attr = super.attributes() || {};
    attr = omit(attr, VIDEO_TAG_PARAMS);
    const sources = this.getOption('sources');
    // In case of empty sourceTypes - fallback to default source types is used.
    const hasSourceTags = !isEmpty(sources) || isEmpty(sourceTypes) || isArray(sourceTypes);
    if (!hasSourceTags) {
      attr["src"] = url(this.publicId, this.getOptions(), {
        resource_type: 'video',
        format: sourceTypes
      });
    }
    if (poster != null) {
      attr["poster"] = poster;
    }
    return attr;
  }

  createSourceTag(src, sourceType, codecs = null) {
    let mimeType = null;
    if (!isEmpty(sourceType)) {
      let videoType = sourceType === 'ogv' ? 'ogg' : sourceType;
      mimeType = 'video/' + videoType;
      if (!isEmpty(codecs)) {
        let codecsStr = isArray(codecs) ? codecs.join(', ') : codecs;
        mimeType += '; codecs=' + codecsStr;
      }
    }
    return "<source " + (this.htmlAttrs({
      src: src,
      type: mimeType
    })) + ">";
  }


}

export default VideoTag;
