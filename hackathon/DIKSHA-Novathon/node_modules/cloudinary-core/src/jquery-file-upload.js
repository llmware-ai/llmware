/**
 * This module extends CloudinaryJquery to support jQuery File Upload
 * Depends on 'jquery', 'util', 'cloudinaryjquery', 'jquery.ui.widget', 'jquery.iframe-transport','jquery.fileupload'
 */
import CloudinaryJQuery from './cloudinaryjquery';
import * as Util from './util';

/**
 * Delete a resource using the upload token
 * @function CloudinaryJQuery#delete_by_token
 * @param {string} delete_token - the delete token
 * @param {Object} [options]
 * @param {string} [options.url] - an alternative URL to use for the API
 * @param {string} [options.cloud_name] - an alternative cloud_name to use. This parameter is ignored if `options.url` is provided.
 */
CloudinaryJQuery.prototype.delete_by_token = function(delete_token, options) {
  var cloud_name, dataType, url;
  options = options || {};
  url = options.url;
  if (!url) {
    cloud_name = options.cloud_name || jQuery.cloudinary.config().cloud_name;
    url = 'https://api.cloudinary.com/v1_1/' + cloud_name + '/delete_by_token';
  }
  dataType = jQuery.support.xhrFileUpload ? 'json' : 'iframe json';
  return jQuery.ajax({
    url: url,
    method: 'POST',
    data: {
      token: delete_token
    },
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    },
    dataType: dataType
  });
};

/**
 * Creates an `input` tag and sets it up to upload files to cloudinary
 * @function CloudinaryJQuery#unsigned_upload_tag
 * @param {string}
 */
CloudinaryJQuery.prototype.unsigned_upload_tag = function(upload_preset, upload_params, options) {
  return jQuery('<input/>').attr({
    type: 'file',
    name: 'file'
  }).unsigned_cloudinary_upload(upload_preset, upload_params, options);
};

/**
 * Initialize the jQuery File Upload plugin to upload to Cloudinary
 * @function jQuery#cloudinary_fileupload
 * @param {Object} options
 * @returns {jQuery}
 */
jQuery.fn.cloudinary_fileupload = function(options) {
  var cloud_name, initializing, resource_type, type, upload_url;
  if (!Util.isFunction(jQuery.fn.fileupload)) {
    return this;
  }
  initializing = !this.data('blueimpFileupload');
  if (initializing) {
    options = jQuery.extend({
      maxFileSize: 20000000,
      dataType: 'json',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    }, options);
  }
  this.fileupload(options);
  if (initializing) {
    this.bind('fileuploaddone', function(e, data) {
      var add_field, field, multiple, upload_info;
      if (data.result.error) {
        return;
      }
      data.result.path = ['v', data.result.version, '/', data.result.public_id, data.result.format ? '.' + data.result.format : ''].join('');
      if (data.cloudinaryField && data.form.length > 0) {
        upload_info = [data.result.resource_type, data.result.type, data.result.path].join('/') + '#' + data.result.signature;
        multiple = jQuery(e.target).prop('multiple');
        add_field = function() {
          return jQuery('<input/>').attr({
            type: 'hidden',
            name: data.cloudinaryField
          }).val(upload_info).appendTo(data.form);
        };
        if (multiple) {
          add_field();
        } else {
          field = jQuery(data.form).find('input[name="' + data.cloudinaryField + '"]');
          if (field.length > 0) {
            field.val(upload_info);
          } else {
            add_field();
          }
        }
      }
      return jQuery(e.target).trigger('cloudinarydone', data);
    });
    this.bind('fileuploadsend', function(e, data) {
      // add a common unique ID to all chunks of the same uploaded file
      data.headers = jQuery.extend({}, data.headers, {
        'X-Unique-Upload-Id': (Math.random() * 10000000000).toString(16)
      });
      return true;
    });
    this.bind('fileuploadstart', function(e) {
      return jQuery(e.target).trigger('cloudinarystart');
    });
    this.bind('fileuploadstop', function(e) {
      return jQuery(e.target).trigger('cloudinarystop');
    });
    this.bind('fileuploadprogress', function(e, data) {
      return jQuery(e.target).trigger('cloudinaryprogress', data);
    });
    this.bind('fileuploadprogressall', function(e, data) {
      return jQuery(e.target).trigger('cloudinaryprogressall', data);
    });
    this.bind('fileuploadfail', function(e, data) {
      return jQuery(e.target).trigger('cloudinaryfail', data);
    });
    this.bind('fileuploadalways', function(e, data) {
      return jQuery(e.target).trigger('cloudinaryalways', data);
    });
    if (!this.fileupload('option').url) {
      cloud_name = options.cloud_name || jQuery.cloudinary.config().cloud_name;
      resource_type = options.resource_type || 'auto';
      type = options.type || 'upload';
      upload_url = 'https://api.cloudinary.com/v1_1/' + cloud_name + '/' + resource_type + '/' + type;
      this.fileupload('option', 'url', upload_url);
    }
  }
  return this;
};

/**
 * Add a file to upload
 * @function jQuery#cloudinary_upload_url
 * @param {string} remote_url - the url to add
 * @returns {jQuery}
 */
jQuery.fn.cloudinary_upload_url = function(remote_url) {
  if (!Util.isFunction(jQuery.fn.fileupload)) {
    return this;
  }
  this.fileupload('option', 'formData').file = remote_url;
  this.fileupload('add', {
    files: [remote_url]
  });
  delete this.fileupload('option', 'formData').file;
  return this;
};

/**
 * Initialize the jQuery File Upload plugin to upload to Cloudinary using unsigned upload
 * @function jQuery#unsigned_cloudinary_upload
 * @param {string} upload_preset - the upload preset to use
 * @param {Object} [upload_params] - parameters that should be past to the server
 * @param {Object} [options]
 * @returns {jQuery}
 */
jQuery.fn.unsigned_cloudinary_upload = function(upload_preset, upload_params = {}, options = {}) {
  var attr, attrs_to_move, html_options, i, key, value;
  upload_params = Util.cloneDeep(upload_params);
  options = Util.cloneDeep(options);
  attrs_to_move = ['cloud_name', 'resource_type', 'type'];
  i = 0;
  while (i < attrs_to_move.length) {
    attr = attrs_to_move[i];
    if (upload_params[attr]) {
      options[attr] = upload_params[attr];
      delete upload_params[attr];
    }
    i++;
  }
// Serialize upload_params
  for (key in upload_params) {
    value = upload_params[key];
    if (Util.isPlainObject(value)) {
      upload_params[key] = jQuery.map(value, function(v, k) {
        if (Util.isString(v)) {
          v = v.replace(/[\|=]/g, "\\$&");
        }
        return k + '=' + v;
      }).join('|');
    } else if (Util.isArray(value)) {
      if (value.length > 0 && Array.isArray(value[0])) {
        upload_params[key] = jQuery.map(value, function(array_value) {
          return array_value.join(',');
        }).join('|');
      } else {
        upload_params[key] = value.join(',');
      }
    }
  }
  if (!upload_params.callback) {
    upload_params.callback = '/cloudinary_cors.html';
  }
  upload_params.upload_preset = upload_preset;
  options.formData = upload_params;
  if (options.cloudinary_field) {
    options.cloudinaryField = options.cloudinary_field;
    delete options.cloudinary_field;
  }
  html_options = options.html || {};
  html_options.class = Util.trim(`cloudinary_fileupload ${html_options.class || ''}`);
  if (options.multiple) {
    html_options.multiple = true;
  }
  this.attr(html_options).cloudinary_fileupload(options);
  return this;
};

jQuery.cloudinary = new CloudinaryJQuery();

export default CloudinaryJQuery;
