
var assert = require('assert')
var env = require('../').env;

console.log('environment: %s', env.type);

var col;
switch (env.type) {
  case 'node':
    col = require('./collection/node');
    break;
  case 'mongo':
    col = require('./collection/mongo');
  case 'browser':
    col = require('./collection/browser');
  default:
    throw new Error('missing collection implementation for environment: ' + env.type);
}

module.exports = exports = col;
