import Transformation from './transformation';

import {
  ACCESSIBILITY_MODES,
  DEFAULT_IMAGE_PARAMS,
  OLD_AKAMAI_SHARED_CDN,
  PLACEHOLDER_IMAGE_MODES,
  SHARED_CDN,
  SEO_TYPES
} from './constants';

import {
  defaults,
  compact,
  isPlainObject
} from './util';

import crc32 from './crc32';
import getSDKAnalyticsSignature from "./sdkAnalytics/getSDKAnalyticsSignature";
import getAnalyticsOptions from "./sdkAnalytics/getAnalyticsOptions";


/**
 * Adds protocol, host, pathname prefixes to given string
 * @param str
 * @returns {string}
 */
function makeUrl(str) {
    let prefix = document.location.protocol + '//' + document.location.host;
    if (str[0] === '?') {
      prefix += document.location.pathname;
    } else if (str[0] !== '/') {
      prefix += document.location.pathname.replace(/\/[^\/]*$/, '/');
    }
    return prefix + str;
}

/**
 * Check is given string is a url
 * @param str
 * @returns {boolean}
 */
function isUrl(str){
  return str ? !!str.match(/^https?:\//) : false;
}

// Produce a number between 1 and 5 to be used for cdn sub domains designation
function cdnSubdomainNumber(publicId) {
  return crc32(publicId) % 5 + 1;
}

/**
 * Removes signature from options and returns the signature
 * Makes sure signature is empty or of this format: s--signature--
 * @param {object} options
 * @returns {string} the formatted signature
 */
function handleSignature(options) {
  const {signature} = options;
  const isFormatted = !signature || (signature.indexOf('s--') === 0 && signature.substr(-2) === '--');
  delete options.signature;

  return isFormatted ? signature : `s--${signature}--`;
}

/**
 * Create the URL prefix for Cloudinary resources.
 * @param {string} publicId the resource public ID
 * @param {object} options additional options
 * @param {string} options.cloud_name - the cloud name.
 * @param {boolean} [options.cdn_subdomain=false] - Whether to automatically build URLs with
 *  multiple CDN sub-domains.
 * @param {string} [options.private_cdn] - Boolean (default: false). Should be set to true for Advanced plan's users
 *  that have a private CDN distribution.
 * @param {string} [options.protocol="http://"] - the URI protocol to use. If options.secure is true,
 *  the value is overridden to "https://"
 * @param {string} [options.secure_distribution] - The domain name of the CDN distribution to use for building HTTPS URLs.
 *  Relevant only for Advanced plan's users that have a private CDN distribution.
 * @param {string} [options.cname] - Custom domain name to use for building HTTP URLs.
 *  Relevant only for Advanced plan's users that have a private CDN distribution and a custom CNAME.
 * @param {boolean} [options.secure_cdn_subdomain=true] - When options.secure is true and this parameter is false,
 *  the subdomain is set to "res".
 * @param {boolean} [options.secure=false] - Force HTTPS URLs of images even if embedded in non-secure HTTP pages.
 *  When this value is true, options.secure_distribution will be used as host if provided, and options.protocol is set
 *  to "https://".
 * @returns {string} the URL prefix for the resource.
 * @private
 */
function handlePrefix(publicId, options) {
  if (options.cloud_name && options.cloud_name[0] === '/') {
    return '/res' + options.cloud_name;
  }
  // defaults
  let protocol = "http://";
  let cdnPart = "";
  let subdomain = "res";
  let host = ".cloudinary.com";
  let path = "/" + options.cloud_name;
  // modifications
  if (options.protocol) {
    protocol = options.protocol + '//';
  }
  if (options.private_cdn) {
    cdnPart = options.cloud_name + "-";
    path = "";
  }
  if (options.cdn_subdomain) {
    subdomain = "res-" + cdnSubdomainNumber(publicId);
  }
  if (options.secure) {
    protocol = "https://";
    if (options.secure_cdn_subdomain === false) {
      subdomain = "res";
    }
    if ((options.secure_distribution != null) && options.secure_distribution !== OLD_AKAMAI_SHARED_CDN && options.secure_distribution !== SHARED_CDN) {
      cdnPart = "";
      subdomain = "";
      host = options.secure_distribution;
    }
  } else if (options.cname) {
    protocol = "http://";
    cdnPart = "";
    subdomain = options.cdn_subdomain ? 'a' + ((crc32(publicId) % 5) + 1) + '.' : '';
    host = options.cname;
  }
  return [protocol, cdnPart, subdomain, host, path].join("");
}

/**
 * Return the resource type and action type based on the given configuration
 * @function Cloudinary#handleResourceType
 * @param {Object|string} resource_type
 * @param {string} [type='upload']
 * @param {string} [url_suffix]
 * @param {boolean} [use_root_path]
 * @param {boolean} [shorten]
 * @returns {string} resource_type/type
 * @ignore
 */
function handleResourceType({resource_type = "image", type = "upload", url_suffix, use_root_path, shorten}) {
  let options, resourceType = resource_type;

  if (isPlainObject(resourceType)) {
    options = resourceType;
    resourceType = options.resource_type;
    type = options.type;
    shorten = options.shorten;
  }
  if (type == null) {
    type = 'upload';
  }
  if (url_suffix != null) {
    resourceType = SEO_TYPES[`${resourceType}/${type}`];
    type = null;
    if (resourceType == null) {
      throw new Error(`URL Suffix only supported for ${Object.keys(SEO_TYPES).join(', ')}`);
    }
  }
  if (use_root_path) {
    if (resourceType === 'image' && type === 'upload' || resourceType === "images") {
      resourceType = null;
      type = null;
    } else {
      throw new Error("Root path only supported for image/upload");
    }
  }
  if (shorten && resourceType === 'image' && type === 'upload') {
    resourceType = 'iu';
    type = null;
  }
  return [resourceType, type].join("/");
}

/**
 * Encode publicId
 * @param publicId
 * @returns {string} encoded publicId
 */
function encodePublicId(publicId) {
  return encodeURIComponent(publicId).replace(/%3A/g, ':').replace(/%2F/g, '/');
}

/**
 * Encode and format publicId
 * @param publicId
 * @param options
 * @returns {string} publicId
 */
function formatPublicId(publicId, options) {
  if (isUrl(publicId)){
    publicId = encodePublicId(publicId);
  } else {
    try {
      // Make sure publicId is URI encoded.
      publicId = decodeURIComponent(publicId);
    } catch (error) {}

    publicId = encodePublicId(publicId);

    if (options.url_suffix) {
      publicId = publicId + '/' + options.url_suffix;
    }
    if (options.format) {
      if (!options.trust_public_id) {
        publicId = publicId.replace(/\.(jpg|png|gif|webp)$/, '');
      }
      publicId = publicId + '.' + options.format;
    }
  }
  return publicId;
}

/**
 * Get any error with url options
 * @param options
 * @returns {string} if error, otherwise return undefined
 */
function validate(options) {
  const {cloud_name, url_suffix} = options;

  if (!cloud_name) {
    return 'Unknown cloud_name';
  }

  if (url_suffix && url_suffix.match(/[\.\/]/)) {
    return 'url_suffix should not include . or /';
  }
}

/**
 * Get version part of the url
 * @param publicId
 * @param options
 * @returns {string}
 */
function handleVersion(publicId, options) {
  // force_version param means to make sure there is a version in the url (Default is true)
  const isForceVersion = (options.force_version || typeof options.force_version === 'undefined');

  // Is version included in publicId or in options, or publicId is a url (doesn't need version)
  const isVersionExist = (publicId.indexOf('/') < 0 || publicId.match(/^v[0-9]+/) || isUrl(publicId)) || options.version;

  if (isForceVersion && !isVersionExist) {
    options.version = 1;
  }

  return options.version ? `v${options.version}` : '';
}

/**
 * Get final transformation component for url string
 * @param options
 * @returns {string}
 */
function handleTransformation(options) {
  let {placeholder, accessibility, ...otherOptions} = options || {};
  const result = new Transformation(otherOptions);

  // Append accessibility transformations
  if (accessibility && ACCESSIBILITY_MODES[accessibility]) {
    result.chain().effect(ACCESSIBILITY_MODES[accessibility]);
  }

  // Append placeholder transformations
  if (placeholder) {
    if (placeholder === "predominant-color" && result.getValue('width') && result.getValue('height')) {
      placeholder += '-pixel';
    }
    const placeholderTransformations = PLACEHOLDER_IMAGE_MODES[placeholder] || PLACEHOLDER_IMAGE_MODES.blur;
    placeholderTransformations.forEach(t => result.chain().transformation(t));
  }

  return result.serialize();
}

/**
 * If type is 'fetch', update publicId to be a url
 * @param publicId
 * @param type
 * @returns {string}
 */
function preparePublicId(publicId, {type}){
  return (!isUrl(publicId) && type === 'fetch') ? makeUrl(publicId) : publicId;
}

/**
 * Generate url string
 * @param publicId
 * @param options
 * @returns {string} final url
 */
function urlString(publicId, options) {
  if (isUrl(publicId) && (options.type === 'upload' || options.type === 'asset')) {
    return publicId;
  }

  const version = handleVersion(publicId, options);
  const transformationString = handleTransformation(options);
  const prefix = handlePrefix(publicId, options);
  const signature = handleSignature(options);
  const resourceType = handleResourceType(options);

  publicId = formatPublicId(publicId, options);

  return compact([prefix, resourceType, signature, transformationString, version, publicId])
    .join('/')
    .replace(/([^:])\/+/g, '$1/') // replace '///' with '//'
    .replace(' ', '%20');
}

/**
 * Merge options and config with defaults
 * update options fetch_format according to 'type' param
 * @param options
 * @param config
 * @returns {*} updated options
 */
function prepareOptions(options, config) {
  if (options instanceof Transformation) {
    options = options.toOptions();
  }

  options = defaults({}, options, config, DEFAULT_IMAGE_PARAMS);

  if (options.type === 'fetch') {
    options.fetch_format = options.fetch_format || options.format;
  }

  return options;
}

/**
 * Generates a URL for any asset in your Media library.
 * @function url
 * @ignore
 * @param {string} publicId - The public ID of the media asset.
 * @param {Object} [options={}] - The {@link Transformation} parameters to include in the URL.
 * @param {object} [config={}] - URL configuration parameters
 * @param {type} [options.type='upload'] - The asset's storage type.
 *  For details on all fetch types, see
 * <a href="https://cloudinary.com/documentation/image_transformations#fetching_images_from_remote_locations"
 *  target="_blank">Fetch types</a>.
 * @param {Object} [options.resource_type='image'] - The type of asset. <p>Possible values:<br/>
 *  - `image`<br/>
 *  - `video`<br/>
 *  - `raw`
 * @param {signature} [options.signature='s--12345678--'] - The signature component of a
 *  signed delivery URL of the format: /s--SIGNATURE--/.
 *  For details on signatures, see
 * <a href="https://cloudinary.com/documentation/signatures" target="_blank">Signatures</a>.
 * @return {string} The media asset URL.
 * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
 *  Available image transformations</a>
 * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
 *  Available video transformations</a>
 */
export default function url(publicId, options = {}, config = {}) {
  if (!publicId) {
    return publicId;
  }
  options = prepareOptions(options, config);
  publicId = preparePublicId(publicId, options);

  const error = validate(options);

  if (error) {
    throw error;
  }
  let resultUrl = urlString(publicId, options);
  if(options.urlAnalytics) {
    let analyticsOptions = getAnalyticsOptions(options);
    let sdkAnalyticsSignature = getSDKAnalyticsSignature(analyticsOptions);
    // url might already have a '?' query param
    let appender = '?';
    if (resultUrl.indexOf('?') >= 0) {
      appender = '&';
    }
    resultUrl = `${resultUrl}${appender}_a=${sdkAnalyticsSignature}`;
  }
  if (options.auth_token) {
    let appender = resultUrl.indexOf('?') >= 0 ? '&' : '?';
    resultUrl = `${resultUrl}${appender}__cld_token__=${options.auth_token}`;
  }
  return resultUrl;
};
