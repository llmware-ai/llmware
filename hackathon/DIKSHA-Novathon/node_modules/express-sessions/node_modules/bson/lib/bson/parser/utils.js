'use strict';

/**
 * Normalizes our expected stringified form of a function across versions of node
 * @param {Function} fn The function to stringify
 */
function normalizedFunctionString(fn) {
  return fn.toString().replace(/function *\(/, 'function (');
}

module.exports = {
  normalizedFunctionString: normalizedFunctionString
};

