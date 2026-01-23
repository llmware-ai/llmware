"use strict";

// eslint-disable-next-line import/order
var config = require("../config");
var utils = require("../utils");
var ensureOption = require('../utils/ensureOption').defaults(config());
var execute_request = require('./execute_request');

var ensurePresenceOf = utils.ensurePresenceOf;


function call_api(method, uri, params, callback, options) {
  ensurePresenceOf({ method, uri });
  var api_url = utils.base_api_url(uri, options);
  var auth = {};
  if (options.oauth_token || config().oauth_token) {
    auth = {
      oauth_token: ensureOption(options, "oauth_token")
    };
  } else {
    auth = {
      key: ensureOption(options, "api_key"),
      secret: ensureOption(options, "api_secret")
    };
  }
  return execute_request(method, params, auth, api_url, callback, options);
}

module.exports = call_api;