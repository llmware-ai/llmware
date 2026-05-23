const _ = require('lodash');
exports.config = require("./config");
exports.utils = require("./utils");
exports.uploader = require("./uploader");
exports.api = require("./api");
let account = require("./provisioning/account");

exports.provisioning = {
  account: account
};
exports.PreloadedFile = require("./preloaded_file");
exports.Cache = require('./cache');

const cloudinary = module.exports;

const optionConsume = cloudinary.utils.option_consume;

exports.url = function url(public_id, options) {
  options = _.extend({}, options);
  return cloudinary.utils.url(public_id, options);
};

const { generateImageResponsiveAttributes, generateMediaAttr } = require('./utils/srcsetUtils');

/**
 * Helper function, allows chaining transformation to the end of transformation list
 *
 * @private
 * @param {object} options Original options
 * @param {object|object[]} transformation Transformations to chain at the end
 *
 * @return {object} Resulting options
 */
function chainTransformations(options, transformation = []) {
  // preserve url options
  let urlOptions = cloudinary.utils.extractUrlParams(options);
  let currentTransformation = cloudinary.utils.extractTransformationParams(options);
  transformation = cloudinary.utils.build_array(transformation);
  urlOptions.transformation = [currentTransformation, ...transformation];
  return urlOptions;
}

/**
 * Generate an HTML img tag with a Cloudinary URL
 * @param {string} source A Public ID or a URL
 * @param {object} options Configuration options
 * @param {srcset} options.srcset srcset options
 * @param {object} options.attributes HTML attributes
 * @param {number} options.html_width (deprecated) The HTML tag width
 * @param {number} options.html_height (deprecated) The HTML tag height
 * @param {boolean} options.client_hints Don't implement the client side responsive function.
 *                  This argument can override the the same option in the global configuration.
 * @param {boolean} options.responsive Setup the tag for the client side responsive function.
 * @param {boolean} options.hidpi Setup the tag for the client side auto dpr function.
 * @param {boolean} options.responsive_placeholder A place holder image URL to use with.
 *                  the client side responsive function
 * @return {string} An HTML img tag
 */
exports.image = function image(source, options) {
  let localOptions = _.extend({}, options);
  let srcsetParam = optionConsume(localOptions, 'srcset');
  let attributes = optionConsume(localOptions, 'attributes', {});
  let src = cloudinary.utils.url(source, localOptions);
  if ("html_width" in localOptions) localOptions.width = optionConsume(localOptions, "html_width");
  if ("html_height" in localOptions) localOptions.height = optionConsume(localOptions, "html_height");

  let client_hints = optionConsume(localOptions, "client_hints", cloudinary.config().client_hints);
  let responsive = optionConsume(localOptions, "responsive");
  let hidpi = optionConsume(localOptions, "hidpi");

  if ((responsive || hidpi) && !client_hints) {
    localOptions["data-src"] = src;
    let classes = [responsive ? "cld-responsive" : "cld-hidpi"];
    let current_class = optionConsume(localOptions, "class");
    if (current_class) classes.push(current_class);
    localOptions.class = classes.join(" ");
    src = optionConsume(localOptions, "responsive_placeholder", cloudinary.config().responsive_placeholder);
    if (src === "blank") {
      src = cloudinary.BLANK;
    }
  }
  let html = "<img ";
  if (src) html += "src='" + src + "' ";
  let responsiveAttributes = {};
  if (cloudinary.utils.isString(srcsetParam)) {
    responsiveAttributes.srcset = srcsetParam;
  } else {
    responsiveAttributes = generateImageResponsiveAttributes(source, attributes, srcsetParam, options);
  }
  if (!cloudinary.utils.isEmpty(responsiveAttributes)) {
    delete localOptions.width;
    delete localOptions.height;
  }
  html += cloudinary.utils.html_attrs(_.extend(localOptions, responsiveAttributes, attributes)) + "/>";
  return html;
};

/**
 * Creates an HTML video tag for the provided public_id
 * @param {String} public_id the resource public ID
 * @param {Object} [options] options for the resource and HTML tag
 * @param {(String|Array<String>)} [options.source_types] Specify which
 *        source type the tag should include. defaults to webm, mp4 and ogv.
 * @param {String} [options.source_transformation] specific transformations
 *        to use for a specific source type.
 * @param {(String|Object)} [options.poster] image URL or
 *        poster options that may include a <tt>public_id</tt> key and
 *        poster-specific transformations
 * @example <caption>Example of generating a video tag:</caption>
 * cloudinary.video("mymovie.mp4");
 * cloudinary.video("mymovie.mp4", {source_types: 'webm'});
 * cloudinary.video("mymovie.ogv", {poster: "myspecialplaceholder.jpg"});
 * cloudinary.video("mymovie.webm", {source_types: ['webm', 'mp4'], poster: {effect: 'sepia'}});
 * @return {string} HTML video tag
 */
exports.video = function video(public_id, options) {
  options = _.extend({}, options);
  public_id = public_id.replace(/\.(mp4|ogv|webm)$/, '');
  let source_types = optionConsume(options, 'source_types', []);
  let source_transformation = optionConsume(options, 'source_transformation', {});
  let sources = optionConsume(options, 'sources', []);
  let fallback = optionConsume(options, 'fallback_content', '');

  if (source_types.length === 0) source_types = cloudinary.utils.DEFAULT_VIDEO_SOURCE_TYPES;
  let video_options = _.cloneDeep(options);

  if (video_options.hasOwnProperty('poster')) {
    if (_.isPlainObject(video_options.poster)) {
      if (video_options.poster.hasOwnProperty('public_id')) {
        video_options.poster = cloudinary.utils.url(video_options.poster.public_id, video_options.poster);
      } else {
        video_options.poster = cloudinary.utils.url(public_id, _.extend({}, cloudinary.utils.DEFAULT_POSTER_OPTIONS, video_options.poster));
      }
    }
  } else {
    video_options.poster = cloudinary.utils.url(public_id, _.extend({}, cloudinary.utils.DEFAULT_POSTER_OPTIONS, options));
  }

  if (!video_options.poster) delete video_options.poster;

  let html = '<video ';

  if (!video_options.hasOwnProperty('resource_type')) video_options.resource_type = 'video';
  let multi_source_types = _.isArray(source_types) && source_types.length > 1;
  let has_sources = _.isArray(sources) && sources.length > 0;
  let source = public_id;
  if (!multi_source_types && !has_sources) {
    source = source + '.' + cloudinary.utils.build_array(source_types)[0];
  }
  let src = cloudinary.utils.url(source, video_options);
  if (!multi_source_types && !has_sources) video_options.src = src;
  if (video_options.hasOwnProperty("html_width")) video_options.width = optionConsume(video_options, 'html_width');
  if (video_options.hasOwnProperty("html_height")) video_options.height = optionConsume(video_options, 'html_height');
  html = html + cloudinary.utils.html_attrs(video_options) + '>';
  if (multi_source_types && !has_sources) {
    sources = source_types.map(source_type => ({
      type: source_type,
      transformations: source_transformation[source_type] || {}
    }));
  }
  if (_.isArray(sources) && sources.length > 0) {
    html += sources.map((source_data) => {
      let source_type = source_data.type;
      let codecs = source_data.codecs;
      let transformation = source_data.transformations || {};
      src = cloudinary.utils.url(source + "." + source_type, _.extend({ resource_type: 'video' }, _.cloneDeep(options), _.cloneDeep(transformation)));
      return cloudinary.utils.create_source_tag(src, source_type, codecs);
    }).join('');
  }
  return `${html}${fallback}</video>`;
};


/**
 * Generate a <code>source</code> tag.
 * @param {string} public_id
 * @param {object} options
 * @param {srcset} options.srcset arguments required to generate the srcset attribute.
 * @param {object} options.attributes HTML tag attributes
 * @return {string}
 */
exports.source = function source(public_id, options = {}) {
  let srcsetParam = cloudinary.utils.extend({}, options.srcset, cloudinary.config().srcset);
  let attributes = options.attributes || {};

  cloudinary.utils.extend(attributes, generateImageResponsiveAttributes(public_id, attributes, srcsetParam, options));
  if (!attributes.srcset) {
    attributes.srcset = cloudinary.url(public_id, options);
  }
  if (!attributes.media && options.media) {
    attributes.media = generateMediaAttr(options.media);
  }
  return `<source ${cloudinary.utils.html_attrs(attributes)}>`;
};

/**
 * Generate a <code>picture</code> HTML tag.<br>
 *   The sources argument defines different transformations to apply for each
 *   media query.
 * @param {string}public_id
 * @param {object} options
 * @param {object[]} options.sources a list of source arguments. A source tag will be rendered for each item
 * @param {number} options.sources.min_width a minimum width query
 * @param {number} options.sources.max_width a maximum width query
 * @param {number} options.sources.transformation the transformation to apply to the source tag.
 * @return {string} A picture HTML tag
 * @example
 *
 * cloudinary.picture("sample", {
 *   sources: [
 *     {min_width: 1600, transformation: {crop: 'fill', width: 800, aspect_ratio: 2}},
 *     {min_width: 500, transformation: {crop: 'fill', width: 600, aspect_ratio: 2.3}},
 *     {transformation: {crop: 'crop', width: 400, gravity: 'auto'}},
 *     ]}
 * );
 */
exports.picture = function picture(public_id, options = {}) {
  let sources = options.sources || [];
  options = cloudinary.utils.clone(options);
  delete options.sources;
  cloudinary.utils.patchFetchFormat(options);
  return "<picture>"
    + sources.map((source) => {
      let sourceOptions = chainTransformations(options, source.transformation);
      sourceOptions.media = source;
      return cloudinary.source(public_id, sourceOptions);
    }).join('')
    + cloudinary.image(public_id, options)
    + "</picture>";
};

exports.cloudinary_js_config = cloudinary.utils.cloudinary_js_config;
exports.CF_SHARED_CDN = cloudinary.utils.CF_SHARED_CDN;
exports.AKAMAI_SHARED_CDN = cloudinary.utils.AKAMAI_SHARED_CDN;
exports.SHARED_CDN = cloudinary.utils.SHARED_CDN;
exports.BLANK = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
exports.v2 = require('./v2');
