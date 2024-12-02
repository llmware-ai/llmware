"use strict";

/**
 * Deletes `option_name` from `options` and return the value if present.
 * If `options` doesn't contain `option_name` the default value is returned.
 * @param {Object} options a collection
 * @param {String} option_name the name (key) of the desired value
 * @param {*} [default_value] the value to return is option_name is missing
 */

function consumeOption(options, option_name, default_value) {
  var result = options[option_name];
  delete options[option_name];
  return result != null ? result : default_value;
}

module.exports = consumeOption;