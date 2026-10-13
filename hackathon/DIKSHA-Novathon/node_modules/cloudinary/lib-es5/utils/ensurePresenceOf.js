"use strict";

/**
 * Validate that the given values are defined
 * @private
 * @param {object} parameters where each key value pair is the name and value of the argument to validate.
 *
 * @example
 *
 *    function foo(bar){
 *      ensurePresenceOf({bar});
 *      // ...
 *    }
 */
function ensurePresenceOf(parameters) {
  var missing = Object.keys(parameters).filter(function (key) {
    return parameters[key] === undefined;
  });
  if (missing.length) {
    console.error(missing.join(',') + " cannot be undefined");
  }
}

module.exports = ensurePresenceOf;