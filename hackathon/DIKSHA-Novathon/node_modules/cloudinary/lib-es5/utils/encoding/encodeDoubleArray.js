'use strict';

var isArray = require('lodash/isArray');
var toArray = require('../parsing/toArray');

/**
 * Serialize an array of arrays into a string
 * @param {string[] | Array.<Array.<string>>} array - An array of arrays.
 *                          If the first element is not an array the argument is wrapped in an array.
 * @returns {string} A string representation of the arrays.
 */
function encodeDoubleArray(array) {
  array = toArray(array);
  if (!isArray(array[0])) {
    array = [array];
  }
  return array.map(function (e) {
    return toArray(e).join(",");
  }).join("|");
}

module.exports = encodeDoubleArray;