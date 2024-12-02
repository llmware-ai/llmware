"use strict";

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

function _toConsumableArray(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } else { return Array.from(arr); } }

/**
 * Utilities
 * @module utils
 * @borrows module:auth_token as generate_auth_token
 */

var crypto = require("crypto");
var querystring = require("querystring");
var urlParse = require("url").parse;

// Functions used internally
var compact = require("lodash/compact");
var first = require("lodash/first");
var isFunction = require("lodash/isFunction");
var isPlainObject = require("lodash/isPlainObject");
var last = require("lodash/last");
var map = require("lodash/map");
var take = require("lodash/take");
var at = require("lodash/at");

// Exposed by the module
var clone = require("lodash/clone");
var extend = require("lodash/extend");
var filter = require("lodash/filter");
var includes = require("lodash/includes");
var isArray = require("lodash/isArray");
var isEmpty = require("lodash/isEmpty");
var isNumber = require("lodash/isNumber");
var isObject = require("lodash/isObject");
var isString = require("lodash/isString");
var isUndefined = require("lodash/isUndefined");

var smart_escape = require("./encoding/smart_escape");
var consumeOption = require('./parsing/consumeOption');
var toArray = require('./parsing/toArray');

var _require = require('./encoding/base64EncodeURL'),
    base64EncodeURL = _require.base64EncodeURL;

var encodeDoubleArray = require('./encoding/encodeDoubleArray');

var config = require("../config");
var generate_token = require("../auth_token");
var crc32 = require('./crc32');
var ensurePresenceOf = require('./ensurePresenceOf');
var ensureOption = require('./ensureOption').defaults(config());
var entries = require('./entries');
var isRemoteUrl = require('./isRemoteUrl');
var getSDKVersions = require('./encoding/sdkAnalytics/getSDKVersions');

var _require$Util = require('cloudinary-core').Util,
    getAnalyticsOptions = _require$Util.getAnalyticsOptions,
    getSDKAnalyticsSignature = _require$Util.getSDKAnalyticsSignature;

exports = module.exports;
var utils = module.exports;

try {
  // eslint-disable-next-line global-require
  utils.VERSION = require('../../package.json').version;
} catch (error) {
  utils.VERSION = '';
}

function generate_auth_token(options) {
  var token_options = Object.assign({}, config().auth_token, options);
  return generate_token(token_options);
}

exports.CF_SHARED_CDN = "d3jpl91pxevbkh.cloudfront.net";
exports.OLD_AKAMAI_SHARED_CDN = "cloudinary-a.akamaihd.net";
exports.AKAMAI_SHARED_CDN = "res.cloudinary.com";
exports.SHARED_CDN = exports.AKAMAI_SHARED_CDN;
exports.USER_AGENT = `CloudinaryNodeJS/${exports.VERSION} (Node ${process.versions.node})`;

// Add platform information to the USER_AGENT header
// This is intended for platform information and not individual applications!
exports.userPlatform = "";

function getUserAgent() {
  return isEmpty(utils.userPlatform) ? `${utils.USER_AGENT}` : `${utils.userPlatform} ${utils.USER_AGENT}`;
}

var _require2 = require('./consts'),
    DEFAULT_RESPONSIVE_WIDTH_TRANSFORMATION = _require2.DEFAULT_RESPONSIVE_WIDTH_TRANSFORMATION,
    DEFAULT_POSTER_OPTIONS = _require2.DEFAULT_POSTER_OPTIONS,
    DEFAULT_VIDEO_SOURCE_TYPES = _require2.DEFAULT_VIDEO_SOURCE_TYPES,
    CONDITIONAL_OPERATORS = _require2.CONDITIONAL_OPERATORS,
    PREDEFINED_VARS = _require2.PREDEFINED_VARS,
    LAYER_KEYWORD_PARAMS = _require2.LAYER_KEYWORD_PARAMS,
    TRANSFORMATION_PARAMS = _require2.TRANSFORMATION_PARAMS,
    SIMPLE_PARAMS = _require2.SIMPLE_PARAMS,
    UPLOAD_PREFIX = _require2.UPLOAD_PREFIX,
    SUPPORTED_SIGNATURE_ALGORITHMS = _require2.SUPPORTED_SIGNATURE_ALGORITHMS,
    DEFAULT_SIGNATURE_ALGORITHM = _require2.DEFAULT_SIGNATURE_ALGORITHM;

function textStyle(layer) {
  var keywords = [];
  var style = "";

  if (!isEmpty(layer.text_style)) {
    return layer.text_style;
  }
  Object.keys(LAYER_KEYWORD_PARAMS).forEach(function (attr) {
    var default_value = LAYER_KEYWORD_PARAMS[attr];
    var attr_value = layer[attr] || default_value;
    if (attr_value !== default_value) {
      keywords.push(attr_value);
    }
  });

  Object.keys(layer).forEach(function (attr) {
    if (attr === "letter_spacing" || attr === "line_spacing") {
      keywords.push(`${attr}_${layer[attr]}`);
    }
    if (attr === "font_hinting") {
      keywords.push(`${attr.split("_").pop()}_${layer[attr]}`);
    }
    if (attr === "font_antialiasing") {
      keywords.push(`antialias_${layer[attr]}`);
    }
  });

  if (layer.hasOwnProperty("font_size" || "font_family") || !isEmpty(keywords)) {
    if (!layer.font_size) throw new Error('Must supply font_size for text in overlay/underlay');
    if (!layer.font_family) throw new Error('Must supply font_family for text in overlay/underlay');
    keywords.unshift(layer.font_size);
    keywords.unshift(layer.font_family);
    style = compact(keywords).join("_");
  }
  return style;
}

/**
 * Normalize an expression string, replace "nice names" with their coded values and spaces with "_"
 * e.g. `width > 0` => `w_lt_0`
 *
 * @param {String} expression An expression to be normalized
 * @return {Object|String} A normalized String of the input value if possible otherwise the value itself
 */
function normalize_expression(expression) {
  if (!isString(expression) || expression.length === 0 || expression.match(/^!.+!$/)) {
    return expression;
  }

  var operators = "\\|\\||>=|<=|&&|!=|>|=|<|/|-|\\^|\\+|\\*";
  var operatorsPattern = "((" + operators + ")(?=[ _]))";
  var operatorsReplaceRE = new RegExp(operatorsPattern, "g");
  expression = expression.replace(operatorsReplaceRE, function (match) {
    return CONDITIONAL_OPERATORS[match];
  });

  // Duplicate PREDEFINED_VARS to also include :{var_name} as well as {var_name}
  // Example:
  // -- PREDEFINED_VARS = ['foo']
  // -- predefinedVarsPattern = ':foo|foo'
  // It is done like this because node 6 does not support regex lookbehind
  var predefinedVarsPattern = "(" + Object.keys(PREDEFINED_VARS).map(function (v) {
    return `:${v}|${v}`;
  }).join("|") + ")";
  var userVariablePattern = '(\\$_*[^_ ]+)';
  var variablesReplaceRE = new RegExp(`${userVariablePattern}|${predefinedVarsPattern}`, "g");
  expression = expression.replace(variablesReplaceRE, function (match) {
    return PREDEFINED_VARS[match] || match;
  });

  return expression.replace(/[ _]+/g, '_');
}

/**
 * Parse custom_function options
 * @private
 * @param {object|*} customFunction a custom function object containing function_type and source values
 * @return {string|*} custom_function transformation string
 */
function process_custom_function(customFunction) {
  if (!isObject(customFunction)) {
    return customFunction;
  }
  if (customFunction.function_type === "remote") {
    var encodedSource = base64EncodeURL(customFunction.source);

    return [customFunction.function_type, encodedSource].join(":");
  }
  return [customFunction.function_type, customFunction.source].join(":");
}

/**
 * Parse custom_pre_function options
 * @private
 * @param {object|*} customPreFunction a custom function object containing function_type and source values
 * @return {string|*} custom_pre_function transformation string
 */
function process_custom_pre_function(customPreFunction) {
  var result = process_custom_function(customPreFunction);
  return utils.isString(result) ? `pre:${result}` : null;
}

/**
 * Parse "if" parameter
 * Translates the condition if provided.
 * @private
 * @return {string} "if_" + ifValue
 */
function process_if(ifValue) {
  return ifValue ? "if_" + normalize_expression(ifValue) : ifValue;
}

/**
 * Parse layer options
 * @private
 * @param {object|*} layer The layer to parse.
 * @return {string} layer transformation string
 */
function process_layer(layer) {
  if (isString(layer)) {
    var resourceType = null;
    var layerUrl = '';

    var fetchLayerBegin = 'fetch:';
    if (layer.startsWith(fetchLayerBegin)) {
      layerUrl = layer.substring(fetchLayerBegin.length);
    } else if (layer.indexOf(':fetch:', 0) !== -1) {
      var parts = layer.split(':', 3);
      resourceType = parts[0];
      layerUrl = parts[2];
    } else {
      return layer;
    }

    layer = {
      url: layerUrl,
      type: 'fetch'
    };

    if (resourceType) {
      layer.resource_type = resourceType;
    }
  }

  if (typeof layer !== 'object') {
    return layer;
  }

  var _layer = layer,
      resource_type = _layer.resource_type,
      text = _layer.text,
      type = _layer.type,
      public_id = _layer.public_id,
      format = _layer.format,
      fetchUrl = _layer.url;

  var components = [];

  if (!isEmpty(text) && isEmpty(resource_type)) {
    resource_type = 'text';
  }

  if (!isEmpty(fetchUrl) && isEmpty(type)) {
    type = 'fetch';
  }

  if (!isEmpty(public_id) && !isEmpty(format)) {
    public_id = `${public_id}.${format}`;
  }

  if (isEmpty(public_id) && resource_type !== 'text' && type !== 'fetch') {
    throw new Error('Must supply public_id for non-text overlay');
  }

  if (!isEmpty(resource_type) && resource_type !== 'image') {
    components.push(resource_type);
  }

  if (!isEmpty(type) && type !== 'upload') {
    components.push(type);
  }

  if (resource_type === 'text' || resource_type === 'subtitles') {
    if (isEmpty(public_id) && isEmpty(text)) {
      throw new Error('Must supply either text or public_in in overlay');
    }

    var textOptions = textStyle(layer);

    if (!isEmpty(textOptions)) {
      components.push(textOptions);
    }

    if (!isEmpty(public_id)) {
      public_id = public_id.replace('/', ':');
      components.push(public_id);
    }

    if (!isEmpty(text)) {
      var variablesRegex = new RegExp(/(\$\([a-zA-Z]\w+\))/g);
      var textDividedByVariables = text.split(variablesRegex).filter(function (x) {
        return x;
      });
      var encodedParts = textDividedByVariables.map(function (subText) {
        var matches = variablesRegex[Symbol.match](subText);
        var isVariable = matches ? matches.length > 0 : false;
        if (isVariable) {
          return subText;
        }
        return encodeCurlyBraces(encodeURIComponent(smart_escape(subText, new RegExp(/([,\/])/g))));
      });
      components.push(encodedParts.join(''));
    }
  } else if (type === 'fetch') {
    var encodedUrl = base64EncodeURL(fetchUrl);
    components.push(encodedUrl);
  } else {
    public_id = public_id.replace('/', ':');
    components.push(public_id);
  }

  return components.join(':');
}

function replaceAllSubstrings(string, search) {
  var replacement = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : '';

  return string.split(search).join(replacement);
}

function encodeCurlyBraces(input) {
  return replaceAllSubstrings(replaceAllSubstrings(input, '(', '%28'), ')', '%29');
}

/**
 * Parse radius options
 * @private
 * @param {Array<string|number>|string|number} radius The radius to parse
 * @return {string} radius transformation string
 */
function process_radius(radius) {
  if (!radius) {
    return radius;
  }
  if (!isArray(radius)) {
    radius = [radius];
  }
  if (radius.length === 0 || radius.length > 4) {
    throw new Error("Radius array should contain between 1 and 4 values");
  }
  if (radius.findIndex(function (x) {
    return x === null;
  }) >= 0) {
    throw new Error("Corner: Cannot be null");
  }
  return radius.map(normalize_expression).join(':');
}

function build_multi_and_sprite_params(tagOrOptions, options) {
  var tag = null;
  if (typeof tagOrOptions === 'string') {
    tag = tagOrOptions;
  } else {
    if (isEmpty(options)) {
      options = tagOrOptions;
    } else {
      throw new Error('First argument must be a tag when additional options are passed');
    }
    tag = null;
  }
  if (!options && !tag) {
    throw new Error('Either tag or urls are required');
  }
  if (!options) {
    options = {};
  }
  var urls = options.urls;
  var transformation = generate_transformation_string(extend({}, options, {
    fetch_format: options.format
  }));
  return {
    tag,
    transformation,
    urls,
    timestamp: utils.timestamp(),
    async: options.async,
    notification_url: options.notification_url
  };
}

function build_upload_params(options) {
  var params = {
    access_mode: options.access_mode,
    allowed_formats: options.allowed_formats && toArray(options.allowed_formats).join(","),
    asset_folder: options.asset_folder,
    async: utils.as_safe_bool(options.async),
    backup: utils.as_safe_bool(options.backup),
    callback: options.callback,
    cinemagraph_analysis: utils.as_safe_bool(options.cinemagraph_analysis),
    colors: utils.as_safe_bool(options.colors),
    display_name: options.display_name,
    discard_original_filename: utils.as_safe_bool(options.discard_original_filename),
    eager: utils.build_eager(options.eager),
    eager_async: utils.as_safe_bool(options.eager_async),
    eager_notification_url: options.eager_notification_url,
    eval: options.eval,
    exif: utils.as_safe_bool(options.exif),
    faces: utils.as_safe_bool(options.faces),
    folder: options.folder,
    format: options.format,
    filename_override: options.filename_override,
    image_metadata: utils.as_safe_bool(options.image_metadata),
    media_metadata: utils.as_safe_bool(options.media_metadata),
    invalidate: utils.as_safe_bool(options.invalidate),
    moderation: options.moderation,
    notification_url: options.notification_url,
    overwrite: utils.as_safe_bool(options.overwrite),
    phash: utils.as_safe_bool(options.phash),
    proxy: options.proxy,
    public_id: options.public_id,
    public_id_prefix: options.public_id_prefix,
    quality_analysis: utils.as_safe_bool(options.quality_analysis),
    responsive_breakpoints: utils.generate_responsive_breakpoints_string(options.responsive_breakpoints),
    return_delete_token: utils.as_safe_bool(options.return_delete_token),
    timestamp: options.timestamp || exports.timestamp(),
    transformation: utils.generate_transformation_string(clone(options)),
    type: options.type,
    unique_filename: utils.as_safe_bool(options.unique_filename),
    upload_preset: options.upload_preset,
    use_filename: utils.as_safe_bool(options.use_filename),
    use_filename_as_display_name: utils.as_safe_bool(options.use_filename_as_display_name),
    quality_override: options.quality_override,
    accessibility_analysis: utils.as_safe_bool(options.accessibility_analysis),
    use_asset_folder_as_public_id_prefix: utils.as_safe_bool(options.use_asset_folder_as_public_id_prefix),
    visual_search: utils.as_safe_bool(options.visual_search),
    on_success: options.on_success
  };
  return utils.updateable_resource_params(options, params);
}

function encode_key_value(arg) {
  if (!isObject(arg)) {
    return arg;
  }
  return entries(arg).map(function (_ref) {
    var _ref2 = _slicedToArray(_ref, 2),
        k = _ref2[0],
        v = _ref2[1];

    return `${k}=${v}`;
  }).join('|');
}

/**
 * @description Escape = and | with two backslashes \\
 * @param {string|number} value
 * @return {string}
 */
function escapeMetadataValue(value) {
  return value.toString().replace(/([=|])/g, '\\$&');
}

/**
 *
 * @description Encode metadata fields based on incoming value.
 *              If array, escape as color_id=[\"green\",\"red\"]
 *              If string/number, escape as in_stock_id=50
 *
 *              Joins resulting values with a pipe:
 *              in_stock_id=50|color_id=[\"green\",\"red\"]
 *
 *              = and | and escaped by default (this can't be turned off)
 *
 * @param metadataObj
 * @return {string}
 */
function encode_context(metadataObj) {
  if (!isObject(metadataObj)) {
    return metadataObj;
  }

  return entries(metadataObj).map(function (_ref3) {
    var _ref4 = _slicedToArray(_ref3, 2),
        key = _ref4[0],
        value = _ref4[1];

    // if string, simply parse the value and move on
    if (isString(value)) {
      return `${key}=${escapeMetadataValue(value)}`;

      // If array, parse each item individually
    } else if (isArray(value)) {
      var values = value.map(function (innerVal) {
        return `\"${escapeMetadataValue(innerVal)}\"`;
      }).join(',');
      return `${key}=[${values}]`;
      // if number, convert to string
    } else if (Number.isInteger(value)) {
      return `${key}=${escapeMetadataValue(String(value))}`;
      // if unknown, return the value as string
    } else {
      return value.toString();
    }
  }).join('|');
}

function build_eager(transformations) {
  return toArray(transformations).map(function (transformation) {
    var transformationString = utils.generate_transformation_string(clone(transformation));
    var format = transformation.format;
    return format == null ? transformationString : `${transformationString}/${format}`;
  }).join('|');
}

/**
 * Build the custom headers for the request
 * @private
 * @param headers
 * @return {Array<string>|object|string} An object of name and value,
 *         an array of header strings, or a string of headers
 */
function build_custom_headers(headers) {
  switch (true) {
    case headers == null:
      return void 0;
    case isArray(headers):
      return headers.join("\n");
    case isObject(headers):
      return entries(headers).map(function (_ref5) {
        var _ref6 = _slicedToArray(_ref5, 2),
            k = _ref6[0],
            v = _ref6[1];

        return `${k}:${v}`;
      }).join("\n");
    default:
      return headers;
  }
}

function generate_transformation_string(options) {
  if (utils.isString(options)) {
    return options;
  }
  if (isArray(options)) {
    return options.map(function (t) {
      return utils.generate_transformation_string(clone(t));
    }).filter(utils.present).join('/');
  }

  var responsive_width = consumeOption(options, "responsive_width", config().responsive_width);
  var width = options.width;
  var height = options.height;
  var size = consumeOption(options, "size");
  if (size) {
    var _size$split = size.split("x");

    var _size$split2 = _slicedToArray(_size$split, 2);

    width = _size$split2[0];
    height = _size$split2[1];
    var _ref7 = [width, height];
    options.width = _ref7[0];
    options.height = _ref7[1];
  }
  var has_layer = options.overlay || options.underlay;
  var crop = consumeOption(options, "crop");
  var angle = toArray(consumeOption(options, "angle")).join(".");
  var no_html_sizes = has_layer || utils.present(angle) || crop === "fit" || crop === "limit" || responsive_width;
  if (width && (width.toString().indexOf("auto") === 0 || no_html_sizes || parseFloat(width) < 1)) {
    delete options.width;
  }
  if (height && (no_html_sizes || parseFloat(height) < 1)) {
    delete options.height;
  }
  var background = consumeOption(options, "background");
  background = background && background.replace(/^#/, "rgb:");
  var color = consumeOption(options, "color");
  color = color && color.replace(/^#/, "rgb:");
  var base_transformations = toArray(consumeOption(options, "transformation", []));
  var named_transformation = [];
  if (base_transformations.some(isObject)) {
    base_transformations = base_transformations.map(function (tr) {
      return utils.generate_transformation_string(isObject(tr) ? clone(tr) : { transformation: tr });
    });
  } else {
    named_transformation = base_transformations.join(".");
    base_transformations = [];
  }
  var effect = consumeOption(options, "effect");
  if (isArray(effect)) {
    effect = effect.join(":");
  } else if (isObject(effect)) {
    effect = entries(effect).map(function (_ref8) {
      var _ref9 = _slicedToArray(_ref8, 2),
          key = _ref9[0],
          value = _ref9[1];

      return `${key}:${value}`;
    });
  }
  var border = consumeOption(options, "border");
  if (isObject(border)) {
    border = `${border.width != null ? border.width : 2}px_solid_${(border.color != null ? border.color : "black").replace(/^#/, 'rgb:')}`;
  } else if (/^\d+$/.exec(border)) {
    // fallback to html border attributes
    options.border = border;
    border = void 0;
  }
  var flags = toArray(consumeOption(options, "flags")).join(".");
  var dpr = consumeOption(options, "dpr", config().dpr);
  if (options.offset != null) {
    var _split_range = split_range(consumeOption(options, "offset"));

    var _split_range2 = _slicedToArray(_split_range, 2);

    options.start_offset = _split_range2[0];
    options.end_offset = _split_range2[1];
  }
  if (options.start_offset) {
    options.start_offset = normalize_expression(options.start_offset);
  }
  if (options.end_offset) {
    options.end_offset = normalize_expression(options.end_offset);
  }
  var overlay = process_layer(consumeOption(options, "overlay"));
  var radius = process_radius(consumeOption(options, "radius"));
  var underlay = process_layer(consumeOption(options, "underlay"));
  var ifValue = process_if(consumeOption(options, "if"));
  var custom_function = process_custom_function(consumeOption(options, "custom_function"));
  var custom_pre_function = process_custom_pre_function(consumeOption(options, "custom_pre_function"));
  var fps = consumeOption(options, 'fps');
  if (isArray(fps)) {
    fps = fps.join('-');
  }
  var params = {
    a: normalize_expression(angle),
    ar: normalize_expression(consumeOption(options, "aspect_ratio")),
    b: background,
    bo: border,
    c: crop,
    co: color,
    dpr: normalize_expression(dpr),
    e: normalize_expression(effect),
    fl: flags,
    fn: custom_function || custom_pre_function,
    fps: fps,
    h: normalize_expression(height),
    ki: normalize_expression(consumeOption(options, "keyframe_interval")),
    l: overlay,
    o: normalize_expression(consumeOption(options, "opacity")),
    q: normalize_expression(consumeOption(options, "quality")),
    r: radius,
    t: named_transformation,
    u: underlay,
    w: normalize_expression(width),
    x: normalize_expression(consumeOption(options, "x")),
    y: normalize_expression(consumeOption(options, "y")),
    z: normalize_expression(consumeOption(options, "zoom"))
  };

  SIMPLE_PARAMS.forEach(function (_ref10) {
    var _ref11 = _slicedToArray(_ref10, 2),
        name = _ref11[0],
        short = _ref11[1];

    var value = consumeOption(options, name);
    if (value !== undefined) {
      params[short] = value;
    }
  });
  if (params.vc != null) {
    params.vc = process_video_params(params.vc);
  }
  ["so", "eo", "du"].forEach(function (short) {
    if (params[short] !== undefined) {
      params[short] = norm_range_value(params[short]);
    }
  });

  var variablesParam = consumeOption(options, "variables", []);
  var variables = entries(options).filter(function (_ref12) {
    var _ref13 = _slicedToArray(_ref12, 2),
        key = _ref13[0],
        value = _ref13[1];

    return key.startsWith('$');
  }).map(function (_ref14) {
    var _ref15 = _slicedToArray(_ref14, 2),
        key = _ref15[0],
        value = _ref15[1];

    delete options[key];
    return `${key}_${normalize_expression(value)}`;
  }).sort().concat(variablesParam.map(function (_ref16) {
    var _ref17 = _slicedToArray(_ref16, 2),
        name = _ref17[0],
        value = _ref17[1];

    return `${name}_${normalize_expression(value)}`;
  })).join(',');

  var transformations = entries(params).filter(function (_ref18) {
    var _ref19 = _slicedToArray(_ref18, 2),
        key = _ref19[0],
        value = _ref19[1];

    return utils.present(value);
  }).map(function (_ref20) {
    var _ref21 = _slicedToArray(_ref20, 2),
        key = _ref21[0],
        value = _ref21[1];

    return key + '_' + value;
  }).sort().join(',');

  var raw_transformation = consumeOption(options, 'raw_transformation');
  transformations = compact([ifValue, variables, transformations, raw_transformation]).join(",");
  base_transformations.push(transformations);
  transformations = base_transformations;
  if (responsive_width) {
    var responsive_width_transformation = config().responsive_width_transformation || DEFAULT_RESPONSIVE_WIDTH_TRANSFORMATION;

    transformations.push(utils.generate_transformation_string(clone(responsive_width_transformation)));
  }
  if (String(width).startsWith("auto") || responsive_width) {
    options.responsive = true;
  }
  if (dpr === "auto") {
    options.hidpi = true;
  }
  return filter(transformations, utils.present).join("/");
}

function updateable_resource_params(options) {
  var params = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  if (options.access_control != null) {
    params.access_control = utils.jsonArrayParam(options.access_control);
  }
  if (options.auto_tagging != null) {
    params.auto_tagging = options.auto_tagging;
  }
  if (options.background_removal != null) {
    params.background_removal = options.background_removal;
  }
  if (options.categorization != null) {
    params.categorization = options.categorization;
  }
  if (options.context != null) {
    params.context = utils.encode_context(options.context);
  }
  if (options.metadata != null) {
    params.metadata = utils.encode_context(options.metadata);
  }
  if (options.custom_coordinates != null) {
    params.custom_coordinates = encodeDoubleArray(options.custom_coordinates);
  }
  if (options.detection != null) {
    params.detection = options.detection;
  }
  if (options.face_coordinates != null) {
    params.face_coordinates = encodeDoubleArray(options.face_coordinates);
  }
  if (options.headers != null) {
    params.headers = utils.build_custom_headers(options.headers);
  }
  if (options.notification_url != null) {
    params.notification_url = options.notification_url;
  }
  if (options.ocr != null) {
    params.ocr = options.ocr;
  }
  if (options.raw_convert != null) {
    params.raw_convert = options.raw_convert;
  }
  if (options.similarity_search != null) {
    params.similarity_search = options.similarity_search;
  }
  if (options.tags != null) {
    params.tags = toArray(options.tags).join(",");
  }
  if (options.quality_override != null) {
    params.quality_override = options.quality_override;
  }
  if (options.asset_folder != null) {
    params.asset_folder = options.asset_folder;
  }
  if (options.display_name != null) {
    params.display_name = options.display_name;
  }
  if (options.unique_display_name != null) {
    params.unique_display_name = options.unique_display_name;
  }
  if (options.visual_search != null) {
    params.visual_search = options.visual_search;
  }
  return params;
}

/**
 * A list of keys used by the url() function.
 * @private
 */
var URL_KEYS = ['api_secret', 'auth_token', 'cdn_subdomain', 'cloud_name', 'cname', 'format', 'long_url_signature', 'private_cdn', 'resource_type', 'secure', 'secure_cdn_subdomain', 'secure_distribution', 'shorten', 'sign_url', 'ssl_detected', 'type', 'url_suffix', 'use_root_path', 'version'];

/**
 * Create a new object with only URL parameters
 * @param {object} options The source object
 * @return {Object} An object containing only URL parameters
 */

function extractUrlParams(options) {
  return pickOnlyExistingValues.apply(undefined, [options].concat(URL_KEYS));
}

/**
 * Create a new object with only transformation parameters
 * @param {object} options The source object
 * @return {Object} An object containing only transformation parameters
 */

function extractTransformationParams(options) {
  return pickOnlyExistingValues.apply(undefined, [options].concat(_toConsumableArray(TRANSFORMATION_PARAMS)));
}

/**
 * Handle the format parameter for fetch urls
 * @private
 * @param options url and transformation options. This argument may be changed by the function!
 */

function patchFetchFormat() {
  var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

  if (options.type === "fetch") {
    if (options.fetch_format == null) {
      options.fetch_format = consumeOption(options, "format");
    }
  }
}

function build_distribution_domain(source, options) {
  var cloud_name = consumeOption(options, 'cloud_name', config().cloud_name);
  if (!cloud_name) {
    throw new Error('Must supply cloud_name in tag or in configuration');
  }

  var secure = consumeOption(options, 'secure', null);
  var ssl_detected = consumeOption(options, 'ssl_detected', config().ssl_detected);
  if (secure === null) {
    secure = ssl_detected || config().secure;
  }

  var private_cdn = consumeOption(options, 'private_cdn', config().private_cdn);
  var cname = consumeOption(options, 'cname', config().cname);
  var secure_distribution = consumeOption(options, 'secure_distribution', config().secure_distribution);
  var cdn_subdomain = consumeOption(options, 'cdn_subdomain', config().cdn_subdomain);
  var secure_cdn_subdomain = consumeOption(options, 'secure_cdn_subdomain', config().secure_cdn_subdomain);

  return unsigned_url_prefix(source, cloud_name, private_cdn, cdn_subdomain, secure_cdn_subdomain, cname, secure, secure_distribution);
}

function url(public_id) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var signature = void 0,
      source_to_sign = void 0;
  utils.patchFetchFormat(options);
  var type = consumeOption(options, "type", null);
  var transformation = utils.generate_transformation_string(options);

  var resource_type = consumeOption(options, "resource_type", "image");
  var version = consumeOption(options, "version");
  var force_version = consumeOption(options, "force_version", config().force_version);
  if (force_version == null) {
    force_version = true;
  }
  var long_url_signature = !!consumeOption(options, "long_url_signature", config().long_url_signature);
  var format = consumeOption(options, "format");
  var shorten = consumeOption(options, "shorten", config().shorten);
  var sign_url = consumeOption(options, "sign_url", config().sign_url);
  var api_secret = consumeOption(options, "api_secret", config().api_secret);
  var url_suffix = consumeOption(options, "url_suffix");
  var use_root_path = consumeOption(options, "use_root_path", config().use_root_path);
  var signature_algorithm = consumeOption(options, "signature_algorithm", config().signature_algorithm || DEFAULT_SIGNATURE_ALGORITHM);
  if (long_url_signature) {
    signature_algorithm = 'sha256';
  }
  var auth_token = consumeOption(options, "auth_token");
  if (auth_token !== false) {
    auth_token = exports.merge(config().auth_token, auth_token);
  }
  var preloaded = /^(image|raw)\/([a-z0-9_]+)\/v(\d+)\/([^#]+)$/.exec(public_id);
  if (preloaded) {
    resource_type = preloaded[1];
    type = preloaded[2];
    version = preloaded[3];
    public_id = preloaded[4];
  }
  var original_source = public_id;
  if (public_id == null) {
    return original_source;
  }
  public_id = public_id.toString();
  if (type === null && public_id.match(/^https?:\//i)) {
    return original_source;
  }

  var _finalize_resource_ty = finalize_resource_type(resource_type, type, url_suffix, use_root_path, shorten);

  var _finalize_resource_ty2 = _slicedToArray(_finalize_resource_ty, 2);

  resource_type = _finalize_resource_ty2[0];
  type = _finalize_resource_ty2[1];

  var _finalize_source = finalize_source(public_id, format, url_suffix);

  var _finalize_source2 = _slicedToArray(_finalize_source, 2);

  public_id = _finalize_source2[0];
  source_to_sign = _finalize_source2[1];


  if (version == null && force_version && source_to_sign.indexOf("/") >= 0 && !source_to_sign.match(/^v[0-9]+/) && !source_to_sign.match(/^https?:\//)) {
    version = 1;
  }
  if (version != null) {
    version = `v${version}`;
  } else {
    version = null;
  }

  transformation = transformation.replace(/([^:])\/\//g, '$1/');
  if (sign_url && isEmpty(auth_token)) {
    var to_sign = [transformation, source_to_sign].filter(function (part) {
      return part != null && part !== '';
    }).join('/');

    var signatureConfig = {};
    if (long_url_signature) {
      signatureConfig.algorithm = 'sha256';
      signatureConfig.signatureLength = 32;
    } else {
      signatureConfig.algorithm = signature_algorithm;
      signatureConfig.signatureLength = 8;
    }

    var truncated = compute_hash(to_sign + api_secret, signatureConfig.algorithm, 'base64').slice(0, signatureConfig.signatureLength).replace(/\//g, '_').replace(/\+/g, '-');
    signature = `s--${truncated}--`;
  }

  var prefix = build_distribution_domain(public_id, options);
  var resultUrl = [prefix, resource_type, type, signature, transformation, version, public_id].filter(function (part) {
    return part != null && part !== '';
  }).join('/').replace(/ /g, '%20');
  if (sign_url && !isEmpty(auth_token)) {
    auth_token.url = urlParse(resultUrl).path;
    var token = generate_token(auth_token);
    resultUrl += `?${token}`;
  }

  var urlAnalytics = ensureOption(options, 'urlAnalytics', false);

  if (urlAnalytics === true) {
    var _getSDKVersions = getSDKVersions(),
        sdkCode = _getSDKVersions.sdkCode,
        sdkSemver = _getSDKVersions.sdkSemver,
        techVersion = _getSDKVersions.techVersion;

    var sdkVersions = {
      sdkCode: ensureOption(options, 'sdkCode', sdkCode),
      sdkSemver: ensureOption(options, 'sdkSemver', sdkSemver),
      techVersion: ensureOption(options, 'techVersion', techVersion)
    };

    var analyticsOptions = getAnalyticsOptions(Object.assign({}, options, sdkVersions));

    var sdkAnalyticsSignature = getSDKAnalyticsSignature(analyticsOptions);

    // url might already have a '?' query param
    var appender = '?';
    if (resultUrl.indexOf('?') >= 0) {
      appender = '&';
    }
    resultUrl = `${resultUrl}${appender}_a=${sdkAnalyticsSignature}`;
  }

  return resultUrl;
}

function video_url(public_id, options) {
  options = extend({
    resource_type: 'video'
  }, options);
  return utils.url(public_id, options);
}

function finalize_source(source, format, url_suffix) {
  var source_to_sign = void 0;
  source = source.replace(/([^:])\/\//g, '$1/');
  if (source.match(/^https?:\//i)) {
    source = smart_escape(source);
    source_to_sign = source;
  } else {
    source = encodeURIComponent(decodeURIComponent(source)).replace(/%3A/g, ":").replace(/%2F/g, "/");
    source_to_sign = source;
    if (url_suffix) {
      if (url_suffix.match(/[\.\/]/)) {
        throw new Error('url_suffix should not include . or /');
      }
      source = source + '/' + url_suffix;
    }
    if (format != null) {
      source = source + '.' + format;
      source_to_sign = source_to_sign + '.' + format;
    }
  }
  return [source, source_to_sign];
}

function video_thumbnail_url(public_id, options) {
  options = extend({}, DEFAULT_POSTER_OPTIONS, options);
  return utils.url(public_id, options);
}

function finalize_resource_type(resource_type, type, url_suffix, use_root_path, shorten) {
  if (type == null) {
    type = 'upload';
  }
  if (url_suffix != null) {
    if (resource_type === 'image' && type === 'upload') {
      resource_type = "images";
      type = null;
    } else if (resource_type === 'image' && type === 'private') {
      resource_type = 'private_images';
      type = null;
    } else if (resource_type === 'image' && type === 'authenticated') {
      resource_type = 'authenticated_images';
      type = null;
    } else if (resource_type === 'raw' && type === 'upload') {
      resource_type = 'files';
      type = null;
    } else if (resource_type === 'video' && type === 'upload') {
      resource_type = 'videos';
      type = null;
    } else {
      throw new Error("URL Suffix only supported for image/upload, image/private, image/authenticated, video/upload and raw/upload");
    }
  }
  if (use_root_path) {
    if (resource_type === 'image' && type === 'upload' || resource_type === 'images' && type == null) {
      resource_type = null;
      type = null;
    } else {
      throw new Error("Root path only supported for image/upload");
    }
  }
  if (shorten && resource_type === 'image' && type === 'upload') {
    resource_type = 'iu';
    type = null;
  }
  return [resource_type, type];
}

// cdn_subdomain and secure_cdn_subdomain
// 1) Customers in shared distribution (e.g. res.cloudinary.com)
//    if cdn_domain is true uses res-[1-5].cloudinary.com for both http and https.
//    Setting secure_cdn_subdomain to false disables this for https.
// 2) Customers with private cdn
//    if cdn_domain is true uses cloudname-res-[1-5].cloudinary.com for http
//    if secure_cdn_domain is true uses cloudname-res-[1-5].cloudinary.com for https
//      (please contact support if you require this)
// 3) Customers with cname
//    if cdn_domain is true uses a[1-5].cname for http.
//    For https, uses the same naming scheme as 1 for shared distribution and as 2 for private distribution.

function unsigned_url_prefix(source, cloud_name, private_cdn, cdn_subdomain, secure_cdn_subdomain, cname, secure, secure_distribution) {
  var prefix = void 0;
  if (cloud_name.indexOf("/") === 0) {
    return '/res' + cloud_name;
  }
  var shared_domain = !private_cdn;
  if (secure) {
    if (secure_distribution == null || secure_distribution === exports.OLD_AKAMAI_SHARED_CDN) {
      secure_distribution = private_cdn ? cloud_name + "-res.cloudinary.com" : exports.SHARED_CDN;
    }
    if (shared_domain == null) {
      shared_domain = secure_distribution === exports.SHARED_CDN;
    }
    if (secure_cdn_subdomain == null && shared_domain) {
      secure_cdn_subdomain = cdn_subdomain;
    }
    if (secure_cdn_subdomain) {
      secure_distribution = secure_distribution.replace('res.cloudinary.com', 'res-' + (crc32(source) % 5 + 1 + '.cloudinary.com'));
    }
    prefix = 'https://' + secure_distribution;
  } else if (cname) {
    var subdomain = cdn_subdomain ? 'a' + (crc32(source) % 5 + 1) + '.' : '';
    prefix = 'http://' + subdomain + cname;
  } else {
    var cdn_part = private_cdn ? cloud_name + '-' : '';
    var subdomain_part = cdn_subdomain ? '-' + (crc32(source) % 5 + 1) : '';
    var host = [cdn_part, 'res', subdomain_part, '.cloudinary.com'].join('');
    prefix = 'http://' + host;
  }
  if (shared_domain) {
    prefix += '/' + cloud_name;
  }
  return prefix;
}

function base_api_url() {
  var path = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var cloudinary = ensureOption(options, "upload_prefix", UPLOAD_PREFIX);
  var cloud_name = ensureOption(options, "cloud_name");
  var encode_path = function encode_path(unencoded_path) {
    return encodeURIComponent(unencoded_path).replace("'", '%27');
  };
  var encoded_path = Array.isArray(path) ? path.map(encode_path) : encode_path(path);
  return [cloudinary, "v1_1", cloud_name].concat(encoded_path).join("/");
}

function api_url() {
  var action = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 'upload';
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var resource_type = options.resource_type || "image";
  return base_api_url([resource_type, action], options);
}

function random_public_id() {
  return crypto.randomBytes(12).toString('base64').replace(/[^a-z0-9]/g, "");
}

function signed_preloaded_image(result) {
  return `${result.resource_type}/upload/v${result.version}/${filter([result.public_id, result.format], utils.present).join(".")}#${result.signature}`;
}

function api_sign_request(params_to_sign, api_secret) {
  var to_sign = entries(params_to_sign).filter(function (_ref22) {
    var _ref23 = _slicedToArray(_ref22, 2),
        k = _ref23[0],
        v = _ref23[1];

    return utils.present(v);
  }).map(function (_ref24) {
    var _ref25 = _slicedToArray(_ref24, 2),
        k = _ref25[0],
        v = _ref25[1];

    return `${k}=${toArray(v).join(",")}`;
  }).sort().join("&");
  return compute_hash(to_sign + api_secret, config().signature_algorithm || DEFAULT_SIGNATURE_ALGORITHM, 'hex');
}

/**
 * Computes hash from input string using specified algorithm.
 * @private
 * @param {string} input string which to compute hash from
 * @param {string} signature_algorithm algorithm to use for computing hash
 * @param {string} encoding type of encoding
 * @return {string} computed hash value
 */
function compute_hash(input, signature_algorithm, encoding) {
  if (!SUPPORTED_SIGNATURE_ALGORITHMS.includes(signature_algorithm)) {
    throw new Error(`Signature algorithm ${signature_algorithm} is not supported. Supported algorithms: ${SUPPORTED_SIGNATURE_ALGORITHMS.join(', ')}`);
  }
  var hash = crypto.createHash(signature_algorithm).update(input).digest();
  return Buffer.from(hash).toString(encoding);
}

function clear_blank(hash) {
  var filtered_hash = {};
  entries(hash).filter(function (_ref26) {
    var _ref27 = _slicedToArray(_ref26, 2),
        k = _ref27[0],
        v = _ref27[1];

    return utils.present(v);
  }).forEach(function (_ref28) {
    var _ref29 = _slicedToArray(_ref28, 2),
        k = _ref29[0],
        v = _ref29[1];

    filtered_hash[k] = v.filter ? v.filter(function (x) {
      return x;
    }) : v;
  });
  return filtered_hash;
}

function sort_object_by_key(object) {
  return Object.keys(object).sort().reduce(function (obj, key) {
    obj[key] = object[key];
    return obj;
  }, {});
}

function merge(hash1, hash2) {
  return _extends({}, hash1, hash2);
}

function sign_request(params) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var apiKey = ensureOption(options, 'api_key');
  var apiSecret = ensureOption(options, 'api_secret');
  params = exports.clear_blank(params);
  params.signature = exports.api_sign_request(params, apiSecret);
  params.api_key = apiKey;
  return params;
}

function webhook_signature(data, timestamp) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  ensurePresenceOf({
    data,
    timestamp
  });

  var api_secret = ensureOption(options, 'api_secret');
  var signature_algorithm = ensureOption(options, 'signature_algorithm', DEFAULT_SIGNATURE_ALGORITHM);
  return compute_hash(data + timestamp + api_secret, signature_algorithm, 'hex');
}

/**
 * Verifies the authenticity of a notification signature
 *
 * @param {string} body JSON of the request's body
 * @param {number} timestamp Unix timestamp in seconds. Can be retrieved from the X-Cld-Timestamp header
 * @param {string} signature Actual signature. Can be retrieved from the X-Cld-Signature header
 * @param {number} [valid_for=7200] The desired time in seconds for considering the request valid
 *
 * @return {boolean}
 */
function verifyNotificationSignature(body, timestamp, signature) {
  var valid_for = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : 7200;

  // verify that signature is valid for the given timestamp
  if (timestamp < Math.round(Date.now() / 1000) - valid_for) {
    return false;
  }
  var payload_hash = utils.webhook_signature(body, timestamp, {
    api_secret: config().api_secret,
    signature_algorithm: config().signature_algorithm
  });
  return signature === payload_hash;
}

function process_request_params(params, options) {
  if (options.unsigned != null && options.unsigned) {
    params = exports.clear_blank(params);
    delete params.timestamp;
  } else if (options.oauth_token || config().oauth_token) {
    params = exports.clear_blank(params);
  } else if (options.signature) {
    params = exports.clear_blank(options);
  } else {
    params = exports.sign_request(params, options);
  }

  return params;
}

function private_download_url(public_id, format) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = exports.sign_request({
    timestamp: options.timestamp || exports.timestamp(),
    public_id: public_id,
    format: format,
    type: options.type,
    attachment: options.attachment,
    expires_at: options.expires_at
  }, options);
  return exports.api_url("download", options) + "?" + querystring.stringify(params);
}

/**
 * Utility method that uses the deprecated ZIP download API.
 * @deprecated Replaced by {download_zip_url} that uses the more advanced and robust archive generation and download API
 */

function zip_download_url(tag) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var params = exports.sign_request({
    timestamp: options.timestamp || exports.timestamp(),
    tag: tag,
    transformation: utils.generate_transformation_string(options)
  }, options);
  return exports.api_url("download_tag.zip", options) + "?" + hashToQuery(params);
}

/**
 * The returned url should allow downloading the backedup asset based on the
 * version and asset id
 * asset and version id are returned with resource(<PUBLIC_ID1>, { versions: true })
 * @param asset_id
 * @param version_id
 * @param options
 * @returns {string }
 */
function download_backedup_asset(asset_id, version_id) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = exports.sign_request({
    timestamp: options.timestamp || exports.timestamp(),
    asset_id: asset_id,
    version_id: version_id
  }, options);
  return exports.base_api_url(['download_backup'], options) + "?" + hashToQuery(params);
}

/**
 * Utility method to create a signed URL for specified resources.
 * @param action
 * @param params
 * @param options
 */
function api_download_url(action, params, options) {
  var download_params = _extends({}, params, {
    mode: "download"
  });
  var cloudinary_params = exports.sign_request(download_params, options);
  return exports.api_url(action, options) + "?" + hashToQuery(cloudinary_params);
}

/**
 * Returns a URL that when invokes creates an archive and returns it.
 * @param {object} options
 * @param {string} [options.resource_type="image"] The resource type of files to include in the archive.
 *   Must be one of :image | :video | :raw
 * @param {string} [options.type="upload"] The specific file type of resources: :upload|:private|:authenticated
 * @param {string|Array} [options.tags] list of tags to include in the archive
 * @param {string|Array<string>} [options.public_ids] list of public_ids to include in the archive
 * @param {string|Array<string>} [options.prefixes]  list of prefixes of public IDs (e.g., folders).
 * @param {string|Array<string>} [options.fully_qualified_public_ids] list of fully qualified public_ids to include
 *   in the archive.
 * @param {string|Array<string>} [options.transformations]  list of transformations.
 *   The derived images of the given transformations are included in the archive. Using the string representation of
 *   multiple chained transformations as we use for the 'eager' upload parameter.
 * @param {string} [options.mode="create"] return the generated archive file or to store it as a raw resource and
 *   return a JSON with URLs for accessing the archive. Possible values: :download, :create
 * @param {string} [options.target_format="zip"]
 * @param {string} [options.target_public_id]  public ID of the generated raw resource.
 *   Relevant only for the create mode. If not specified, random public ID is generated.
 * @param {boolean} [options.flatten_folders=false] If true, flatten public IDs with folders to be in the root
 *   of the archive. Add numeric counter to the file name in case of a name conflict.
 * @param {boolean} [options.flatten_transformations=false] If true, and multiple transformations are given,
 *   flatten the folder structure of derived images and store the transformation details on the file name instead.
 * @param {boolean} [options.use_original_filename] Use the original file name of included images
 *   (if available) instead of the public ID.
 * @param {boolean} [options.async=false] If true, return immediately and perform archive creation in the background.
 *   Relevant only for the create mode.
 * @param {string} [options.notification_url] URL to send an HTTP post request (webhook) to when the
 *   archive creation is completed.
 * @param {string|Array<string>} [options.target_tags=] Allows assigning one or more tags to the generated archive file
 *   (for later housekeeping via the admin API).
 * @param {string} [options.keep_derived=false] keep the derived images used for generating the archive
 * @return {String} archive url
 */
function download_archive_url() {
  var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

  var params = exports.archive_params(merge(options, {
    mode: "download"
  }));
  return api_download_url("generate_archive", params, options);
}

/**
 * Returns a URL that when invokes creates an zip archive and returns it.
 * @see download_archive_url
 */

function download_zip_url() {
  var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

  return exports.download_archive_url(merge(options, {
    target_format: "zip"
  }));
}

/**
 * Creates and returns a URL that when invoked creates an archive of a folder
 * @param {string} folder_path Full path (from the root) of the folder to download
 * @param {object} options Additional options
 * @returns {string} Url for downloading an archive of a folder
 */
function download_folder(folder_path) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  options.resource_type = options.resource_type || "all";
  options.prefixes = folder_path;
  var cloudinary_params = exports.sign_request(exports.archive_params(merge(options, {
    mode: "download"
  })), options);
  return exports.api_url("generate_archive", options) + "?" + hashToQuery(cloudinary_params);
}

/**
 * Render the key/value pair as an HTML tag attribute
 * @private
 * @param {string} key
 * @param {string|boolean|number} [value]
 * @return {string} A string representing the HTML attribute
 */
function join_pair(key, value) {
  if (!value) {
    return void 0;
  }
  return value === true ? key : key + "='" + value + "'";
}

/**
 * If the given value is a string, replaces single or double quotes with character entities
 * @private
 * @param {*} value The string to encode quotes in
 * @return {*} Encoded string or original value if not a string
 */
function escapeQuotes(value) {
  return isString(value) ? value.replace(/\"/g, '&#34;').replace(/\'/g, '&#39;') : value;
}

/**
 *
 * @param attrs
 * @return {*}
 */
exports.html_attrs = function html_attrs(attrs) {
  return filter(map(attrs, function (value, key) {
    return join_pair(key, escapeQuotes(value));
  })).sort().join(" ");
};

var CLOUDINARY_JS_CONFIG_PARAMS = ['api_key', 'cloud_name', 'private_cdn', 'secure_distribution', 'cdn_subdomain'];

function cloudinary_js_config() {
  var params = pickOnlyExistingValues.apply(undefined, [config()].concat(CLOUDINARY_JS_CONFIG_PARAMS));
  return `<script type='text/javascript'>\n$.cloudinary.config(${JSON.stringify(params)});\n</script>`;
}

function v1_result_adapter(callback) {
  if (callback == null) {
    return undefined;
  }
  return function (result) {
    if (result.error != null) {
      return callback(result.error);
    }
    return callback(void 0, result);
  };
}

function v1_adapter(name, num_pass_args, v1) {
  return function () {
    for (var _len = arguments.length, args = Array(_len), _key = 0; _key < _len; _key++) {
      args[_key] = arguments[_key];
    }

    var pass_args = take(args, num_pass_args);
    var options = args[num_pass_args];
    var callback = args[num_pass_args + 1];
    if (callback == null && isFunction(options)) {
      callback = options;
      options = {};
    }
    callback = v1_result_adapter(callback);
    args = pass_args.concat([callback, options]);
    return v1[name].apply(this, args);
  };
}

function v1_adapters(exports, v1, mapping) {
  return Object.keys(mapping).map(function (name) {
    var num_pass_args = mapping[name];
    exports[name] = v1_adapter(name, num_pass_args, v1);
    return exports[name];
  });
}

function as_safe_bool(value) {
  if (value == null) {
    return void 0;
  }
  if (value === true || value === 'true' || value === '1') {
    value = 1;
  }
  if (value === false || value === 'false' || value === '0') {
    value = 0;
  }
  return value;
}

var NUMBER_PATTERN = "([0-9]*)\\.([0-9]+)|([0-9]+)";

var OFFSET_ANY_PATTERN = `(${NUMBER_PATTERN})([%pP])?`;
var RANGE_VALUE_RE = RegExp(`^${OFFSET_ANY_PATTERN}$`);
var OFFSET_ANY_PATTERN_RE = RegExp(`(${OFFSET_ANY_PATTERN})\\.\\.(${OFFSET_ANY_PATTERN})`);

// Split a range into the start and end values
function split_range(range) {
  // :nodoc:
  switch (range.constructor) {
    case String:
      if (!OFFSET_ANY_PATTERN_RE.test(range)) {
        return range;
      }
      return range.split("..");
    case Array:
      return [first(range), last(range)];
    default:
      return [null, null];
  }
}

function norm_range_value(value) {
  // :nodoc:
  var offset = String(value).match(RANGE_VALUE_RE);
  if (offset) {
    var modifier = offset[5] ? 'p' : '';
    value = `${offset[1] || offset[4]}${modifier}`;
  }
  return value;
}

/**
 * A video codec parameter can be either a String or a Hash.
 * @param {Object} param <code>vc_<codec>[ : <profile> : [<level>]]</code>
 *                       or <code>{ codec: 'h264', profile: 'basic', level: '3.1' }</code>
 * @return {String} <code><codec> : <profile> : [<level>]]</code> if a Hash was provided
 *                   or the param if a String was provided.
 *                   Returns null if param is not a Hash or String
 */
function process_video_params(param) {
  switch (param.constructor) {
    case Object:
      {
        var video = "";
        if ('codec' in param) {
          video = param.codec;
          if ('profile' in param) {
            video += ":" + param.profile;
            if ('level' in param) {
              video += ":" + param.level;
            }
          }
        }
        return video;
      }
    case String:
      return param;
    default:
      return null;
  }
}

/**
 * Returns a Hash of parameters used to create an archive
 * @private
 * @param {object} options
 * @return {object} Archive API parameters
 */

function archive_params() {
  var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

  return {
    allow_missing: exports.as_safe_bool(options.allow_missing),
    async: exports.as_safe_bool(options.async),
    expires_at: options.expires_at,
    flatten_folders: exports.as_safe_bool(options.flatten_folders),
    flatten_transformations: exports.as_safe_bool(options.flatten_transformations),
    keep_derived: exports.as_safe_bool(options.keep_derived),
    mode: options.mode,
    notification_url: options.notification_url,
    prefixes: options.prefixes && toArray(options.prefixes),
    fully_qualified_public_ids: options.fully_qualified_public_ids && toArray(options.fully_qualified_public_ids),
    public_ids: options.public_ids && toArray(options.public_ids),
    skip_transformation_name: exports.as_safe_bool(options.skip_transformation_name),
    tags: options.tags && toArray(options.tags),
    target_format: options.target_format,
    target_public_id: options.target_public_id,
    target_tags: options.target_tags && toArray(options.target_tags),
    timestamp: options.timestamp || exports.timestamp(),
    transformations: utils.build_eager(options.transformations),
    type: options.type,
    use_original_filename: exports.as_safe_bool(options.use_original_filename)
  };
}

exports.process_layer = process_layer;

exports.create_source_tag = function create_source_tag(src, source_type) {
  var codecs = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;

  var video_type = source_type === 'ogv' ? 'ogg' : source_type;
  var mime_type = `video/${video_type}`;
  if (!isEmpty(codecs)) {
    var codecs_str = isArray(codecs) ? codecs.join(', ') : codecs;
    mime_type += `; codecs=${codecs_str}`;
  }
  return `<source ${utils.html_attrs({
    src,
    type: mime_type
  })}>`;
};

function build_explicit_api_params(public_id) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return [exports.build_upload_params(extend({}, { public_id }, options))];
}

function generate_responsive_breakpoints_string(breakpoints) {
  if (breakpoints == null) {
    return null;
  }
  breakpoints = clone(breakpoints);
  if (!isArray(breakpoints)) {
    breakpoints = [breakpoints];
  }
  for (var j = 0; j < breakpoints.length; j++) {
    var breakpoint_settings = breakpoints[j];
    if (breakpoint_settings != null) {
      if (breakpoint_settings.transformation) {
        breakpoint_settings.transformation = utils.generate_transformation_string(clone(breakpoint_settings.transformation));
      }
    }
  }
  return JSON.stringify(breakpoints);
}

function build_streaming_profiles_param() {
  var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

  var params = pickOnlyExistingValues(options, "display_name", "representations");
  if (isArray(params.representations)) {
    params.representations = JSON.stringify(params.representations.map(function (r) {
      return {
        transformation: utils.generate_transformation_string(r.transformation)
      };
    }));
  }
  return params;
}

function hashToParameters(hash) {
  return entries(hash).reduce(function (parameters, _ref30) {
    var _ref31 = _slicedToArray(_ref30, 2),
        key = _ref31[0],
        value = _ref31[1];

    if (isArray(value)) {
      key = key.endsWith('[]') ? key : key + '[]';
      var items = value.map(function (v) {
        return [key, v];
      });
      parameters = parameters.concat(items);
    } else {
      parameters.push([key, value]);
    }
    return parameters;
  }, []);
}

/**
 * Convert a hash of values to a URI query string.
 * Array values are spread as individual parameters.
 * @param {object} hash Key-value parameters
 * @return {string} A URI query string.
 */
function hashToQuery(hash) {
  return hashToParameters(hash).map(function (_ref32) {
    var _ref33 = _slicedToArray(_ref32, 2),
        key = _ref33[0],
        value = _ref33[1];

    return `${querystring.escape(key)}=${querystring.escape(value)}`;
  }).join('&');
}

/**
 * Verify that the parameter `value` is defined and it's string value is not zero.
 * <br>This function should not be confused with `isEmpty()`.
 * @private
 * @param {string|number} value The value to check.
 * @return {boolean} True if the value is defined and not empty.
 */

function present(value) {
  return value != null && ("" + value).length > 0;
}

/**
 * Returns a new object with key values from source based on the keys.
 * `null` or `undefined` values are not copied.
 * @private
 * @param {object} source The object to pick values from.
 * @param {...string} keys One or more keys to copy from source.
 * @return {object} A new object with the required keys and values.
 */

function pickOnlyExistingValues(source) {
  var result = {};
  if (source) {
    for (var _len2 = arguments.length, keys = Array(_len2 > 1 ? _len2 - 1 : 0), _key2 = 1; _key2 < _len2; _key2++) {
      keys[_key2 - 1] = arguments[_key2];
    }

    keys.forEach(function (key) {
      if (source[key] != null) {
        result[key] = source[key];
      }
    });
  }
  return result;
}

/**
 * Returns a JSON array as String.
 * Yields the array before it is converted to JSON format
 * @private
 * @param {object|String|Array<object>} data
 * @param {function(*):*} [modifier] called with the array before the array is stringified
 * @return {String|null} a JSON array string or `null` if data is `null`
 */

function jsonArrayParam(data, modifier) {
  if (!data) {
    return null;
  }
  if (isString(data)) {
    data = JSON.parse(data);
  }
  if (!isArray(data)) {
    data = [data];
  }
  if (isFunction(modifier)) {
    data = modifier(data);
  }
  return JSON.stringify(data);
}

/**
 * Empty function - do nothing
 *
 */
exports.NOP = function () {};
exports.generate_auth_token = generate_auth_token;
exports.getUserAgent = getUserAgent;
exports.build_upload_params = build_upload_params;
exports.build_multi_and_sprite_params = build_multi_and_sprite_params;
exports.api_download_url = api_download_url;
exports.timestamp = function () {
  return Math.floor(new Date().getTime() / 1000);
};
exports.option_consume = consumeOption; // for backwards compatibility
exports.build_array = toArray; // for backwards compatibility
exports.encode_double_array = encodeDoubleArray;
exports.encode_key_value = encode_key_value;
exports.encode_context = encode_context;
exports.build_eager = build_eager;
exports.build_custom_headers = build_custom_headers;
exports.generate_transformation_string = generate_transformation_string;
exports.updateable_resource_params = updateable_resource_params;
exports.extractUrlParams = extractUrlParams;
exports.extractTransformationParams = extractTransformationParams;
exports.patchFetchFormat = patchFetchFormat;
exports.url = url;
exports.video_url = video_url;
exports.video_thumbnail_url = video_thumbnail_url;
exports.api_url = api_url;
exports.random_public_id = random_public_id;
exports.signed_preloaded_image = signed_preloaded_image;
exports.api_sign_request = api_sign_request;
exports.clear_blank = clear_blank;
exports.merge = merge;
exports.sign_request = sign_request;
exports.webhook_signature = webhook_signature;
exports.verifyNotificationSignature = verifyNotificationSignature;
exports.process_request_params = process_request_params;
exports.private_download_url = private_download_url;
exports.zip_download_url = zip_download_url;
exports.download_archive_url = download_archive_url;
exports.download_zip_url = download_zip_url;
exports.cloudinary_js_config = cloudinary_js_config;
exports.v1_adapters = v1_adapters;
exports.as_safe_bool = as_safe_bool;
exports.archive_params = archive_params;
exports.build_explicit_api_params = build_explicit_api_params;
exports.generate_responsive_breakpoints_string = generate_responsive_breakpoints_string;
exports.build_streaming_profiles_param = build_streaming_profiles_param;
exports.hashToParameters = hashToParameters;
exports.present = present;
exports.only = pickOnlyExistingValues; // for backwards compatibility
exports.pickOnlyExistingValues = pickOnlyExistingValues;
exports.jsonArrayParam = jsonArrayParam;
exports.download_folder = download_folder;
exports.base_api_url = base_api_url;
exports.download_backedup_asset = download_backedup_asset;
exports.compute_hash = compute_hash;
exports.build_distribution_domain = build_distribution_domain;
exports.sort_object_by_key = sort_object_by_key;

// was exported before, so kept for backwards compatibility
exports.DEFAULT_POSTER_OPTIONS = DEFAULT_POSTER_OPTIONS;
exports.DEFAULT_VIDEO_SOURCE_TYPES = DEFAULT_VIDEO_SOURCE_TYPES;

Object.assign(module.exports, {
  normalize_expression,
  at,
  clone,
  extend,
  filter,
  includes,
  isArray,
  isEmpty,
  isNumber,
  isObject,
  isRemoteUrl,
  isString,
  isUndefined,
  keys: function keys(source) {
    return Object.keys(source);
  },
  ensurePresenceOf
});