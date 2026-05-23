"use strict";

// eslint-disable-next-line import/order
var config = require("../config");
var utils = require("../utils");
var ensureOption = require('../utils/ensureOption').defaults(config());
var execute_request = require('./execute_request');

var ensurePresenceOf = utils.ensurePresenceOf;


function call_account_api(method, uri, params, callback, options) {
  ensurePresenceOf({ method, uri });
  var cloudinary = ensureOption(options, "upload_prefix", "https://api.cloudinary.com");
  var account_id = ensureOption(options, "account_id");
  var api_url = [cloudinary, "v1_1", "provisioning", "accounts", account_id].concat(uri).join("/");
  var auth = {
    key: ensureOption(options, "provisioning_api_key"),
    secret: ensureOption(options, "provisioning_api_secret")
  };

  return execute_request(method, params, auth, api_url, callback, options);
}

module.exports = call_account_api;