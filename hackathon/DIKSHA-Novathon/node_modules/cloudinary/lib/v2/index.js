const v1 = require('../cloudinary');
const api = require('./api');
const uploader = require('./uploader');
const search = require('./search');
const search_folders = require('./search_folders');

const v2 = {
  ...v1,
  api,
  uploader,
  search,
  search_folders
};
module.exports = v2;
