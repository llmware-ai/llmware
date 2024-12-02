"use strict";

var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

/**
 * Assign a value to a nested object
 * @function putNestedValue
 * @param params the parent object - this argument will be modified!
 * @param key key in the form nested[innerkey]
 * @param value the value to assign
 * @return the modified params object
 */
var url = require('url');
var extend = require("lodash/extend");
var isObject = require("lodash/isObject");
var isString = require("lodash/isString");
var isUndefined = require("lodash/isUndefined");
var isEmpty = require("lodash/isEmpty");
var entries = require('./utils/entries');

var cloudinary_config = void 0;

/**
 * Sets a value in an object using a nested key
 * @param {object} params The object to assign the value in.
 * @param {string} key The key of the value. A period is used to denote inner keys.
 * @param {*} value The value to set.
 * @returns {object} The params argument.
 * @example
 *     let o = {foo: {bar: 1}};
 *     putNestedValue(o, 'foo.bar', 2); // {foo: {bar: 2}}
 *     putNestedValue(o, 'foo.inner.key', 'this creates an inner object');
 *     // {{foo: {bar: 2}, inner: {key: 'this creates an inner object'}}}
 */
function putNestedValue(params, key, value) {
  var chain = key.split(/[\[\]]+/).filter(function (i) {
    return i.length;
  });
  var outer = params;
  var lastKey = chain.pop();
  for (var j = 0; j < chain.length; j++) {
    var innerKey = chain[j];
    var inner = outer[innerKey];
    if (inner == null) {
      inner = {};
      outer[innerKey] = inner;
    }
    outer = inner;
  }
  outer[lastKey] = value;
  return params;
}

function parseCloudinaryConfigFromEnvURL(ENV_STR) {
  var conf = {};

  var uri = url.parse(ENV_STR, true);

  if (uri.protocol === 'cloudinary:') {
    conf = Object.assign({}, conf, {
      cloud_name: uri.host,
      api_key: uri.auth && uri.auth.split(":")[0],
      api_secret: uri.auth && uri.auth.split(":")[1],
      private_cdn: uri.pathname != null,
      secure_distribution: uri.pathname && uri.pathname.substring(1)
    });
  } else if (uri.protocol === 'account:') {
    conf = Object.assign({}, conf, {
      account_id: uri.host,
      provisioning_api_key: uri.auth && uri.auth.split(":")[0],
      provisioning_api_secret: uri.auth && uri.auth.split(":")[1]
    });
  }

  return conf;
}

function extendCloudinaryConfigFromQuery(ENV_URL) {
  var confToExtend = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var uri = url.parse(ENV_URL, true);
  if (uri.query != null) {
    entries(uri.query).forEach(function (_ref) {
      var _ref2 = _slicedToArray(_ref, 2),
          key = _ref2[0],
          value = _ref2[1];

      return putNestedValue(confToExtend, key, value);
    });
  }
}

function extendCloudinaryConfig(parsedConfig) {
  var confToExtend = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  entries(parsedConfig).forEach(function (_ref3) {
    var _ref4 = _slicedToArray(_ref3, 2),
        key = _ref4[0],
        value = _ref4[1];

    if (value !== undefined) {
      confToExtend[key] = value;
    }
  });

  return confToExtend;
}

module.exports = function (new_config, new_value) {
  if (cloudinary_config == null || new_config === true) {
    if (cloudinary_config == null) {
      cloudinary_config = {};
    } else {
      Object.keys(cloudinary_config).forEach(function (key) {
        return delete cloudinary_config[key];
      });
    }

    var CLOUDINARY_ENV_URL = process.env.CLOUDINARY_URL;
    var CLOUDINARY_ENV_ACCOUNT_URL = process.env.CLOUDINARY_ACCOUNT_URL;
    var CLOUDINARY_API_PROXY = process.env.CLOUDINARY_API_PROXY;

    if (CLOUDINARY_ENV_URL && !CLOUDINARY_ENV_URL.toLowerCase().startsWith('cloudinary://')) {
      throw new Error("Invalid CLOUDINARY_URL protocol. URL should begin with 'cloudinary://'");
    }
    if (CLOUDINARY_ENV_ACCOUNT_URL && !CLOUDINARY_ENV_ACCOUNT_URL.toLowerCase().startsWith('account://')) {
      throw new Error("Invalid CLOUDINARY_ACCOUNT_URL protocol. URL should begin with 'account://'");
    }
    if (!isEmpty(CLOUDINARY_API_PROXY)) {
      extendCloudinaryConfig({ api_proxy: CLOUDINARY_API_PROXY }, cloudinary_config);
    }

    [CLOUDINARY_ENV_URL, CLOUDINARY_ENV_ACCOUNT_URL].forEach(function (ENV_URL) {
      if (ENV_URL) {
        var parsedConfig = parseCloudinaryConfigFromEnvURL(ENV_URL);
        extendCloudinaryConfig(parsedConfig, cloudinary_config);
        // Provide Query support in ENV url cloudinary://key:secret@test123?foo[bar]=value
        // expect(cloudinary_config.foo.bar).to.eql('value')
        extendCloudinaryConfigFromQuery(ENV_URL, cloudinary_config);
      }
    });
  }
  if (!isUndefined(new_value)) {
    cloudinary_config[new_config] = new_value;
  } else if (isString(new_config)) {
    return cloudinary_config[new_config];
  } else if (isObject(new_config)) {
    extend(cloudinary_config, new_config);
  }
  return cloudinary_config;
};