
const utils = require('./index');
const generateBreakpoints = require('./generateBreakpoints');
const Cache = require('../cache');

const isEmpty = utils.isEmpty;

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
function scaledUrl(public_id, width, transformation, options = {}) {
  let configParams = utils.extractUrlParams(options);
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
function getOrGenerateBreakpoints(public_id, srcset = {}, options = {}) {
  let breakpoints = [];
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
  return breakpoints.map(width => `${scaledUrl(public_id, width, transformation, options)} ${width}w`).join(', ');
}

/**
 * Helper function. Generates sizes attribute value of the HTML img tag
 * @private
 * @param {number[]} breakpoints An array of breakpoints.
 * @return {string} Resulting sizes attribute value
 */
function generateSizesAttribute(breakpoints = []) {
  return breakpoints.map(width => `(max-width: ${width}px) ${width}px`).join(', ');
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
function generateImageResponsiveAttributes(publicId, attributes = {}, srcsetData = {}, options = {}) {
  // Create both srcset and sizes here to avoid fetching breakpoints twice

  let responsiveAttributes = {};
  if (isEmpty(srcsetData)) {
    return responsiveAttributes;
  }

  const generateSizes = (!attributes.sizes && srcsetData.sizes === true);

  const generateSrcset = !attributes.srcset;
  if (generateSrcset || generateSizes) {
    let breakpoints = getOrGenerateBreakpoints(publicId, srcsetData, options);

    if (generateSrcset) {
      let transformation = srcsetData.transformation;
      let srcsetAttr = generateSrcsetAttribute(publicId, breakpoints, transformation, options);
      if (!isEmpty(srcsetAttr)) {
        responsiveAttributes.srcset = srcsetAttr;
      }
    }

    if (generateSizes) {
      let sizesAttr = generateSizesAttribute(breakpoints);
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
function generateMediaAttr(options = {}) {
  let mediaQuery = [];
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
