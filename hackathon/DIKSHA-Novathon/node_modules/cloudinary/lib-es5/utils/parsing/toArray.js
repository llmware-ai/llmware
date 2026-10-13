'use strict';

var isArray = require('lodash/isArray');

/**
 * @desc Turns arguments that aren't arrays into arrays
 * @param arg
 * @returns { any | any[] }
 */
function toArray(arg) {
  switch (true) {
    case arg == null:
      return [];
    case isArray(arg):
      return arg;
    default:
      return [arg];
  }
}

module.exports = toArray;