'use strict';

/**
 * Returns an ensureOption function that relies on the provided `defaultOptions` argument
 * for default values.
 * @private
 * @param {object} defaultOptions
 * @return {function(*, *, *=): *}
 */
function defaults(defaultOptions) {
  return function ensureOption(options, name, defaultValue) {
    var value = void 0;

    if (typeof options[name] !== 'undefined') {
      value = options[name];
    } else if (typeof defaultOptions[name] !== 'undefined') {
      value = defaultOptions[name];
    } else if (typeof defaultValue !== 'undefined') {
      value = defaultValue;
    } else {
      throw `Must supply ${name}`;
    }

    return value;
  };
}

/**
 * Get the option `name` from options, the global config, or the default value.
 * If the value is not defined and no default value was provided,
 * the method will throw an error.
 * @private
 * @param {object} options
 * @param {string} name
 * @param {*} [defaultValue]
 * @return {*} the value associated with the provided `name` or the default.
 *
 */
module.exports = defaults({});

module.exports.defaults = defaults;