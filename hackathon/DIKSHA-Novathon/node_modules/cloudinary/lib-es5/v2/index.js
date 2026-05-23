'use strict';

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var v1 = require('../cloudinary');
var api = require('./api');
var uploader = require('./uploader');
var search = require('./search');
var search_folders = require('./search_folders');

var v2 = _extends({}, v1, {
  api,
  uploader,
  search,
  search_folders
});
module.exports = v2;