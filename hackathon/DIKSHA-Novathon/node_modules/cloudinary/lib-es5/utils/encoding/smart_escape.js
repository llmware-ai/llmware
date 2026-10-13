"use strict";

// Based on CGI::unescape. In addition does not escape / :
// smart_escape = (string) => encodeURIComponent(string).replace(/%3A/g, ":").replace(/%2F/g, "/")
function smart_escape(string) {
  var unsafe = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : /([^a-zA-Z0-9_.\-\/:]+)/g;

  return string.replace(unsafe, function (match) {
    return match.split("").map(function (c) {
      return "%" + c.charCodeAt(0).toString(16).toUpperCase();
    }).join("");
  });
}

module.exports = smart_escape;