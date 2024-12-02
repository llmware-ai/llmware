const uploader = require('../uploader');
const v1_adapters = require('../utils').v1_adapters;

v1_adapters(exports, uploader, {
  unsigned_upload_stream: 1,
  upload_stream: 0,
  unsigned_upload: 2,
  upload: 1,
  upload_large_part: 0,
  upload_large: 1,
  upload_chunked: 1,
  upload_chunked_stream: 0,
  explicit: 1,
  destroy: 1,
  rename: 2,
  text: 1,
  generate_sprite: 1,
  multi: 1,
  explode: 1,
  add_tag: 2,
  remove_tag: 2,
  remove_all_tags: 1,
  add_context: 2,
  remove_all_context: 1,
  replace_tag: 2,
  create_archive: 0,
  create_zip: 0,
  update_metadata: 2
});

exports.direct_upload = uploader.direct_upload;
exports.upload_tag_params = uploader.upload_tag_params;
exports.upload_url = uploader.upload_url;
exports.image_upload_tag = uploader.image_upload_tag;
exports.unsigned_image_upload_tag = uploader.unsigned_image_upload_tag;
exports.create_slideshow = uploader.create_slideshow;
exports.download_generated_sprite = uploader.download_generated_sprite;
exports.download_multi = uploader.download_multi;
