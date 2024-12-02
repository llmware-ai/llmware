'use strict';

/**
 * Authorization Token
 * @module auth_token
 */

var crypto = require('crypto');
var smart_escape = require('./utils/encoding/smart_escape');

var unsafe = /([ "#%&'/:;<=>?@[\]^`{|}~]+)/g;

function digest(message, key) {
  return crypto.createHmac("sha256", Buffer.from(key, "hex")).update(message).digest('hex');
}

/**
 * Escape url using lowercase hex code
 * @param {string} url a url string
 * @return {string} escaped url
 */
function escapeToLower(url) {
  var safeUrl = smart_escape(url, unsafe);
  return safeUrl.replace(/%../g, function (match) {
    return match.toLowerCase();
  });
}

/**
 * Auth token options
 * @typedef {object} authTokenOptions
 * @property {string} [token_name="__cld_token__"] The name of the token.
 * @property {string} key The secret key required to sign the token.
 * @property {string} ip The IP address of the client.
 * @property {number} start_time=now The start time of the token in seconds from epoch.
 * @property {string} expiration The expiration time of the token in seconds from epoch.
 * @property {string} duration The duration of the token (from start_time).
 * @property {string|Array<string>} acl The ACL(s) for the token.
 * @property {string} url The URL to authentication in case of a URL token.
 *
 */

/**
 * Generate an authorization token
 * @param {authTokenOptions} options
 * @returns {string} the authorization token
 */
module.exports = function (options) {
  var tokenName = options.token_name ? options.token_name : "__cld_token__";
  var tokenSeparator = "~";
  if (options.expiration == null) {
    if (options.duration != null) {
      var start = options.start_time != null ? options.start_time : Math.round(Date.now() / 1000);
      options.expiration = start + options.duration;
    } else {
      throw new Error("Must provide either expiration or duration");
    }
  }
  var tokenParts = [];
  if (options.ip != null) {
    tokenParts.push(`ip=${options.ip}`);
  }
  if (options.start_time != null) {
    tokenParts.push(`st=${options.start_time}`);
  }
  tokenParts.push(`exp=${options.expiration}`);
  if (options.acl != null) {
    if (Array.isArray(options.acl) === true) {
      options.acl = options.acl.join("!");
    }
    tokenParts.push(`acl=${escapeToLower(options.acl)}`);
  }
  var toSign = [].concat(tokenParts);
  if (options.url != null && options.acl == null) {
    var url = escapeToLower(options.url);
    toSign.push(`url=${url}`);
  }
  var auth = digest(toSign.join(tokenSeparator), options.key);
  tokenParts.push(`hmac=${auth}`);

  if (!options.url && !options.acl) {
    throw 'authToken must contain either an acl or a url property';
  }

  return `${tokenName}=${tokenParts.join(tokenSeparator)}`;
};