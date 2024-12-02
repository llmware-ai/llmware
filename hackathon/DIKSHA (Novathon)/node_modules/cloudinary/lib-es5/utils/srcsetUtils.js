'use strict';

var utils = require('./index');
var generateBreakpoints = require('./generateBreakpoints');
var Cache = require('../cache');

var isEmpty = utils.isEmpty;

/**
 * Options used to generate the srcset attribute.
 * @typedef {object} srcset
 * @property {(number[]|string[])}   [breakpoints] An array of breakpoints.
 * @property {number}                [min_width]   Minimal width of the srcset images.
 * @property {number}                [max_width]   Maximal width of the srcset images.
 * @property {number}                [max_images]  Number of srcset images to generate.
 * @property {object|string}         [transformation] The transformation to use in the srcset urls.
 * @property {boolean}               [sizes] Whether to calculate and add the sizes attribute.
 */

/**
 * Helper function. Generates a single srcset item url
 *
 * @private
 * @param {string} public_id  Public ID of the resource.
 * @param {number} width      Width in pixels of the srcset item.
 * @param {object|string} transformation
 * @param {object} options    Additional options.
 *
 * @return {string} Resulting URL of the item
 */
function scaledUrl(public_id, width, transformation) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var configParams = utils.extractUrlParams(options);
  transformation = transformation || options;
  configParams.raw_transformation = utils.generate_transformation_string([utils.extend({}, transformation), { crop: 'scale', width: width }]);

  return utils.url(public_id, configParams);
}

/**
 * If cache is enabled, get the breakpoints from the cache. If the values were not found in the cache,
 * or cache is not enabled, generate the values.
 * @param {srcset} srcset The srcset configuration parameters
 * @param {string} public_id
 * @param {object} options
 * @return {*|Array}
 */
function getOrGenerateBreakpoints(public_id) {
  var srcset = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var breakpoints = [];
  if (srcset.useCache) {
    breakpoints = Cache.get(public_id, options);
    if (!breakpoints) {
      breakpoints = [];
    }
  } else {
    breakpoints = generateBreakpoints(srcset);
  }
  return breakpoints;
}

/**
 * Helper function. Generates srcset attribute value of the HTML img tag
 * @private
 *
 * @param {string} public_id  Public ID of the resource
 * @param {number[]} breakpoints An array of breakpoints (in pixels)
 * @param {object} transformation The transformation
 * @param {object} options Includes html tag options, transformation options
 * @return {string} Resulting srcset attribute value
 */
function generateSrcsetAttribute(public_id, breakpoints, transformation, options) {
  options = utils.clone(options);
  utils.patchFetchFormat(options);
  return breakpoints.map(function (width) {
    return `${scaledUrl(public_id, width, transformation, options)} ${width}w`;
  }).join(', ');
}

/**
 * Helper function. Generates sizes attribute value of the HTML img tag
 * @private
 * @param {number[]} breakpoints An array of breakpoints.
 * @return {string} Resulting sizes attribute value
 */
function generateSizesAttribute() {
  var breakpoints = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];

  return breakpoints.map(function (width) {
    return `(max-width: ${width}px) ${width}px`;
  }).join(', ');
}

/**
 * Helper function. Generates srcset and sizes attributes of the image tag
 *
 * Generated attributes are added to attributes argument
 *
 * @private
 * @param {string}    publicId  The public ID of the resource
 * @param {object}    attributes Existing HTML attributes.
 * @param {srcset}    srcsetData
 * @param {object}    options    Additional options.
 *
 * @return array The responsive attributes
 */
function generateImageResponsiveAttributes(publicId) {
  var attributes = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var srcsetData = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  // Create both srcset and sizes here to avoid fetching breakpoints twice

  var responsiveAttributes = {};
  if (isEmpty(srcsetData)) {
    return responsiveAttributes;
  }

  var generateSizes = !attributes.sizes && srcsetData.sizes === true;

  var generateSrcset = !attributes.srcset;
  if (generateSrcset || generateSizes) {
    var breakpoints = getOrGenerateBreakpoints(publicId, srcsetData, options);

    if (generateSrcset) {
      var transformation = srcsetData.transformation;
      var srcsetAttr = generateSrcsetAttribute(publicId, breakpoints, transformation, options);
      if (!isEmpty(srcsetAttr)) {
        responsiveAttributes.srcset = srcsetAttr;
      }
    }

    if (generateSizes) {
      var sizesAttr = generateSizesAttribute(breakpoints);
      if (!isEmpty(sizesAttr)) {
        responsiveAttributes.sizes = sizesAttr;
      }
    }
  }
  return responsiveAttributes;
}

/**
 * Generate a media query
 *
 * @private
 * @param {object} options configuration options
 * @param {number|string} options.min_width
 * @param {number|string} options.max_width
 * @return {string} a media query string
 */
function generateMediaAttr() {
  var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

  var mediaQuery = [];
  if (options.min_width != null) {
    mediaQuery.push(`(min-width: ${options.min_width}px)`);
  }
  if (options.max_width != null) {
    mediaQuery.push(`(max-width: ${options.max_width}px)`);
  }
  return mediaQuery.join(' and ');
}

module.exports = {
  srcsetUrl: scaledUrl,
  generateSrcsetAttribute,
  generateSizesAttribute,
  generateMediaAttr,
  generateImageResponsiveAttributes
};