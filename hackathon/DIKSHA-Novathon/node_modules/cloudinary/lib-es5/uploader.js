'use strict';

var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var fs = require('fs');

var _require = require('path'),
    extname = _require.extname,
    basename = _require.basename;

var Q = require('q');
var Writable = require("stream").Writable;
var urlLib = require('url');

// eslint-disable-next-line import/order

var _require2 = require("./config")(),
    upload_prefix = _require2.upload_prefix;

var isSecure = !(upload_prefix && upload_prefix.slice(0, 5) === 'http:');
var https = isSecure ? require('https') : require('http');

var Cache = require('./cache');
var utils = require("./utils");
var UploadStream = require('./upload_stream');
var config = require("./config");
var ensureOption = require('./utils/ensureOption').defaults(config());

var agent = config.api_proxy ? new https.Agent(config.api_proxy) : null;

var build_upload_params = utils.build_upload_params,
    extend = utils.extend,
    includes = utils.includes,
    isEmpty = utils.isEmpty,
    isObject = utils.isObject,
    isRemoteUrl = utils.isRemoteUrl,
    merge = utils.merge,
    pickOnlyExistingValues = utils.pickOnlyExistingValues;


exports.unsigned_upload_stream = function unsigned_upload_stream(upload_preset, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return exports.upload_stream(callback, merge(options, {
    unsigned: true,
    upload_preset: upload_preset
  }));
};

exports.upload_stream = function upload_stream(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return exports.upload(null, callback, extend({
    stream: true
  }, options));
};

exports.unsigned_upload = function unsigned_upload(file, upload_preset, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  return exports.upload(file, callback, merge(options, {
    unsigned: true,
    upload_preset: upload_preset
  }));
};

exports.upload = function upload(file, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("upload", callback, options, function () {
    var params = build_upload_params(options);
    return isRemoteUrl(file) ? [params, { file: file }] : [params, {}, file];
  });
};

exports.upload_large = function upload_large(path, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  if (path != null && isRemoteUrl(path)) {
    // upload a remote file
    return exports.upload(path, callback, options);
  }
  if (path != null && !options.filename) {
    options.filename = path.split(/(\\|\/)/g).pop().replace(/\.[^/.]+$/, "");
  }
  return exports.upload_chunked(path, callback, extend({
    resource_type: 'raw'
  }, options));
};

exports.upload_chunked = function upload_chunked(path, callback, options) {
  var file_reader = fs.createReadStream(path);
  var out_stream = exports.upload_chunked_stream(callback, options);
  return file_reader.pipe(out_stream);
};

var Chunkable = function (_Writable) {
  _inherits(Chunkable, _Writable);

  function Chunkable(options) {
    _classCallCheck(this, Chunkable);

    var _this = _possibleConstructorReturn(this, (Chunkable.__proto__ || Object.getPrototypeOf(Chunkable)).call(this, options));

    _this.chunk_size = options.chunk_size != null ? options.chunk_size : 20000000;
    _this.buffer = Buffer.alloc(0);
    _this.active = true;
    _this.on('finish', function () {
      if (_this.active) {
        _this.emit('ready', _this.buffer, true, function () {});
      }
    });
    return _this;
  }

  _createClass(Chunkable, [{
    key: '_write',
    value: function _write(data, encoding, done) {
      var _this2 = this;

      if (!this.active) {
        done();
      }
      if (this.buffer.length + data.length <= this.chunk_size) {
        this.buffer = Buffer.concat([this.buffer, data], this.buffer.length + data.length);
        done();
      } else {
        var grab = this.chunk_size - this.buffer.length;
        this.buffer = Buffer.concat([this.buffer, data.slice(0, grab)], this.buffer.length + grab);
        this.emit('ready', this.buffer, false, function (active) {
          _this2.active = active;
          if (_this2.active) {
            _this2.buffer = data.slice(grab);
            done();
          }
        });
      }
    }
  }]);

  return Chunkable;
}(Writable);

exports.upload_large_stream = function upload_large_stream(_unused_, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return exports.upload_chunked_stream(callback, extend({
    resource_type: 'raw'
  }, options));
};

exports.upload_chunked_stream = function upload_chunked_stream(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  options = extend({}, options, {
    stream: true
  });
  options.x_unique_upload_id = utils.random_public_id();
  var params = build_upload_params(options);
  var chunk_size = options.chunk_size != null ? options.chunk_size : options.part_size;
  var chunker = new Chunkable({
    chunk_size: chunk_size
  });
  var sent = 0;
  chunker.on('ready', function (buffer, is_last, done) {
    var chunk_start = sent;
    sent += buffer.length;
    options.content_range = `bytes ${chunk_start}-${sent - 1}/${is_last ? sent : -1}`;
    params.timestamp = utils.timestamp();
    var finished_part = function finished_part(result) {
      var errorOrLast = result.error != null || is_last;
      if (errorOrLast && typeof callback === "function") {
        callback(result);
      }
      return done(!errorOrLast);
    };
    var stream = call_api("upload", finished_part, options, function () {
      return [params, {}, buffer];
    });
    return stream.write(buffer, 'buffer', function () {
      return stream.end();
    });
  });
  return chunker;
};

exports.explicit = function explicit(public_id, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("explicit", callback, options, function () {
    return utils.build_explicit_api_params(public_id, options);
  });
};

// Creates a new archive in the server and returns information in JSON format
exports.create_archive = function create_archive(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var target_format = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;

  return call_api("generate_archive", callback, options, function () {
    var opt = utils.archive_params(options);
    if (target_format) {
      opt.target_format = target_format;
    }
    return [opt];
  });
};

// Creates a new zip archive in the server and returns information in JSON format
exports.create_zip = function create_zip(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return exports.create_archive(callback, options, "zip");
};

exports.create_slideshow = function create_slideshow(options, callback) {
  options.resource_type = ensureOption(options, "resource_type", "video");
  return call_api("create_slideshow", callback, options, function () {
    // Generate a transformation from the manifest_transformation key, which should be a valid transformation
    var manifest_transformation = utils.generate_transformation_string(extend({}, options.manifest_transformation));

    // Try to use {options.transformation} to generate a transformation (Example: options.transformation.width, options.transformation.height)
    var transformation = utils.generate_transformation_string(extend({}, ensureOption(options, 'transformation', {})));

    return [{
      timestamp: utils.timestamp(),
      manifest_transformation: manifest_transformation,
      upload_preset: options.upload_preset,
      overwrite: options.overwrite,
      public_id: options.public_id,
      notification_url: options.notification_url,
      manifest_json: options.manifest_json,
      tags: options.tags,
      transformation: transformation
    }];
  });
};

exports.destroy = function destroy(public_id, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("destroy", callback, options, function () {
    return [{
      timestamp: utils.timestamp(),
      type: options.type,
      invalidate: options.invalidate,
      public_id: public_id
    }];
  });
};

exports.rename = function rename(from_public_id, to_public_id, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  return call_api("rename", callback, options, function () {
    return [{
      timestamp: utils.timestamp(),
      type: options.type,
      from_public_id: from_public_id,
      to_public_id: to_public_id,
      overwrite: options.overwrite,
      invalidate: options.invalidate,
      to_type: options.to_type,
      context: options.context,
      metadata: options.metadata
    }];
  });
};

var TEXT_PARAMS = ["public_id", "font_family", "font_size", "font_color", "text_align", "font_weight", "font_style", "background", "opacity", "text_decoration", "font_hinting", "font_antialiasing"];

exports.text = function text(content, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("text", callback, options, function () {
    var textParams = pickOnlyExistingValues.apply(undefined, [options].concat(TEXT_PARAMS));
    var params = _extends({
      timestamp: utils.timestamp(),
      text: content
    }, textParams);

    return [params];
  });
};

/**
 * Generate a sprite by merging multiple images into a single large image for reducing network overhead and bypassing
 * download limitations.
 *
 * The process produces 2 files as follows:
 * - A single image file containing all the images with the specified tag (PNG by default).
 * - A CSS file that includes the style class names and the location of the individual images in the sprite.
 *
 * @param {String|Object} tag     A string specifying a tag that indicates which images to include or an object
 *                                which includes options and image URLs.
 * @param {Function}     callback   Callback function
 * @param {Object}       options  Configuration options. If options are passed as the first parameter, this parameter
 *                                should be empty
 *
 * @return {Object}
 */
exports.generate_sprite = function generate_sprite(tag, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("sprite", callback, options, function () {
    return [utils.build_multi_and_sprite_params(tag, options)];
  });
};

/**
 * Returns a signed url to download a sprite
 *
 * @param {String|Object} tag     A string specifying a tag that indicates which images to include or an object
 *                                which includes options and image URLs.
 * @param {Object}       options  Configuration options. If options are passed as the first parameter, this parameter
 *                                should be empty
 *
 * @returns {string}
 */
exports.download_generated_sprite = function download_generated_sprite(tag) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return utils.api_download_url("sprite", utils.build_multi_and_sprite_params(tag, options), options);
};

/**
 * Returns a signed url to download a single animated image (GIF, PNG or WebP), video (MP4 or WebM) or a single PDF from
 * multiple image assets.
 *
 * @param {String|Object} tag     A string specifying a tag that indicates which images to include or an object
 *                                which includes options and image URLs.
 * @param {Object}       options  Configuration options. If options are passed as the first parameter, this parameter
 *                                should be empty
 *
 * @returns {string}
 */
exports.download_multi = function download_multi(tag) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return utils.api_download_url("multi", utils.build_multi_and_sprite_params(tag, options), options);
};

/**
 * Creates either a single animated image (GIF, PNG or WebP), video (MP4 or WebM) or a single PDF from multiple image
 * assets.
 *
 * Each asset is included as a single frame of the resulting animated image/video, or a page of the PDF (sorted
 * alphabetically by their Public ID).
 *
 * @param {String|Object} tag     A string specifying a tag that indicates which images to include or an object
 *                                which includes options and image URLs.
 * @param {Function}     callback   Callback function
 * @param {Object}       options  Configuration options. If options are passed as the first parameter, this parameter
 *                                should be empty
 *
 * @return {Object}
 */
exports.multi = function multi(tag, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("multi", callback, options, function () {
    return [utils.build_multi_and_sprite_params(tag, options)];
  });
};

exports.explode = function explode(public_id, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("explode", callback, options, function () {
    var transformation = utils.generate_transformation_string(extend({}, options));
    return [{
      timestamp: utils.timestamp(),
      public_id: public_id,
      transformation: transformation,
      format: options.format,
      type: options.type,
      notification_url: options.notification_url
    }];
  });
};

/**
 *
 * @param {String}          tag                  The tag or tags to assign. Can specify multiple
 *                                               tags in a single string, separated by commas - "t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11".
 *
 * @param {Array}          public_ids           A list of public IDs (up to 1000) of assets uploaded to Cloudinary.
 *
 * @param {Function}        callback             Callback function
 *
 * @param {Object}          options              Configuration options may include 'exclusive' (boolean) which causes
 *                                               clearing this tag from all other resources
 * @return {Object}
 */
exports.add_tag = function add_tag(tag) {
  var public_ids = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
  var callback = arguments[2];
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var exclusive = utils.option_consume("exclusive", options);
  var command = exclusive ? "set_exclusive" : "add";
  return call_tags_api(tag, command, public_ids, callback, options);
};

/**
 * @param {String}          tag                  The tag or tags to remove. Can specify multiple
 *                                               tags in a single string, separated by commas - "t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11".
 *
 * @param {Array}          public_ids            A list of public IDs (up to 1000) of assets uploaded to Cloudinary.
 *
 * @param {Function}        callback             Callback function
 *
 * @param {Object}          options              Configuration options may include 'exclusive' (boolean) which causes
 *                                               clearing this tag from all other resources
 * @return {Object}
 */
exports.remove_tag = function remove_tag(tag) {
  var public_ids = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
  var callback = arguments[2];
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  return call_tags_api(tag, "remove", public_ids, callback, options);
};

exports.remove_all_tags = function remove_all_tags() {
  var public_ids = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
  var callback = arguments[1];
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_tags_api(null, "remove_all", public_ids, callback, options);
};

exports.replace_tag = function replace_tag(tag) {
  var public_ids = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
  var callback = arguments[2];
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  return call_tags_api(tag, "replace", public_ids, callback, options);
};

function call_tags_api(tag, command) {
  var public_ids = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : [];
  var callback = arguments[3];
  var options = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : {};

  return call_api("tags", callback, options, function () {
    var params = {
      timestamp: utils.timestamp(),
      public_ids: utils.build_array(public_ids),
      command: command,
      type: options.type
    };
    if (tag != null) {
      params.tag = tag;
    }
    return [params];
  });
}

exports.add_context = function add_context(context) {
  var public_ids = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
  var callback = arguments[2];
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  return call_context_api(context, 'add', public_ids, callback, options);
};

exports.remove_all_context = function remove_all_context() {
  var public_ids = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
  var callback = arguments[1];
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_context_api(null, 'remove_all', public_ids, callback, options);
};

function call_context_api(context, command) {
  var public_ids = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : [];
  var callback = arguments[3];
  var options = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : {};

  return call_api('context', callback, options, function () {
    var params = {
      timestamp: utils.timestamp(),
      public_ids: utils.build_array(public_ids),
      command: command,
      type: options.type
    };
    if (context != null) {
      params.context = utils.encode_context(context);
    }
    return [params];
  });
}

/**
 * Cache (part of) the upload results.
 * @param result
 * @param {object} options
 * @param {string} options.type
 * @param {string} options.resource_type
 */
function cacheResults(result, _ref) {
  var type = _ref.type,
      resource_type = _ref.resource_type;

  if (result.responsive_breakpoints) {
    result.responsive_breakpoints.forEach(function (_ref2) {
      var transformation = _ref2.transformation,
          url = _ref2.url,
          breakpoints = _ref2.breakpoints;
      return Cache.set(result.public_id, { type, resource_type, raw_transformation: transformation, format: extname(breakpoints[0].url).slice(1) }, breakpoints.map(function (i) {
        return i.width;
      }));
    });
  }
}

function parseResult(buffer, res) {
  var result = '';
  try {
    result = JSON.parse(buffer);
    if (result.error && !result.error.name) {
      result.error.name = "Error";
    }
  } catch (jsonError) {
    result = {
      error: {
        message: `Server return invalid JSON response. Status Code ${res.statusCode}. ${jsonError}`,
        name: "Error"
      }
    };
  }
  return result;
}

function call_api(action, callback, options, get_params) {
  if (typeof callback !== "function") {
    callback = function callback() {};
  }

  var USE_PROMISES = !options.disable_promises;

  var deferred = Q.defer();
  if (options == null) {
    options = {};
  }

  var _get_params$call = get_params.call(),
      _get_params$call2 = _slicedToArray(_get_params$call, 3),
      params = _get_params$call2[0],
      unsigned_params = _get_params$call2[1],
      file = _get_params$call2[2];

  params = utils.process_request_params(params, options);
  params = extend(params, unsigned_params);
  var api_url = utils.api_url(action, options);
  var boundary = utils.random_public_id();
  var errorRaised = false;
  var handle_response = function handle_response(res) {
    // let buffer;
    if (errorRaised) {

      // Already reported
    } else if (res.error) {
      errorRaised = true;

      if (USE_PROMISES) {
        deferred.reject(res);
      }
      callback(res);
    } else if (includes([200, 400, 401, 404, 420, 500], res.statusCode)) {
      var buffer = "";
      res.on("data", function (d) {
        buffer += d;
        return buffer;
      });
      res.on("end", function () {
        var result = void 0;
        if (errorRaised) {
          return;
        }
        result = parseResult(buffer, res);
        if (result.error) {
          result.error.http_code = res.statusCode;
          if (USE_PROMISES) {
            deferred.reject(result.error);
          }
        } else {
          cacheResults(result, options);
          if (USE_PROMISES) {
            deferred.resolve(result);
          }
        }
        callback(result);
      });
      res.on("error", function (error) {
        errorRaised = true;
        if (USE_PROMISES) {
          deferred.reject(error);
        }
        callback({ error });
      });
    } else {
      var error = {
        message: `Server returned unexpected status code - ${res.statusCode}`,
        http_code: res.statusCode,
        name: "UnexpectedResponse"
      };
      if (USE_PROMISES) {
        deferred.reject(error);
      }
      callback({ error });
    }
  };
  var post_data = utils.hashToParameters(params).filter(function (_ref3) {
    var _ref4 = _slicedToArray(_ref3, 2),
        key = _ref4[0],
        value = _ref4[1];

    return value != null;
  }).map(function (_ref5) {
    var _ref6 = _slicedToArray(_ref5, 2),
        key = _ref6[0],
        value = _ref6[1];

    return Buffer.from(encodeFieldPart(boundary, key, value), 'utf8');
  });
  var result = post(api_url, post_data, boundary, file, handle_response, options);
  if (isObject(result)) {
    return result;
  }

  if (USE_PROMISES) {
    return deferred.promise;
  }
}

function post(url, post_data, boundary, file, callback, options) {
  var file_header = void 0;
  var finish_buffer = Buffer.from("--" + boundary + "--", 'ascii');
  var oauth_token = options.oauth_token || config().oauth_token;
  if (file != null || options.stream) {
    // eslint-disable-next-line no-nested-ternary
    var filename = options.stream ? options.filename ? options.filename : "file" : basename(file);
    file_header = Buffer.from(encodeFilePart(boundary, 'application/octet-stream', 'file', filename), 'binary');
  }
  var post_options = urlLib.parse(url);
  var headers = {
    'Content-Type': `multipart/form-data; boundary=${boundary}`,
    'User-Agent': utils.getUserAgent()
  };
  if (options.content_range != null) {
    headers['Content-Range'] = options.content_range;
  }
  if (options.x_unique_upload_id != null) {
    headers['X-Unique-Upload-Id'] = options.x_unique_upload_id;
  }
  if (options.extra_headers !== null) {
    headers = merge(headers, options.extra_headers);
  }
  if (oauth_token != null) {
    headers.Authorization = `Bearer ${oauth_token}`;
  }

  post_options = extend(post_options, {
    method: 'POST',
    headers: headers
  });
  if (options.agent != null) {
    post_options.agent = options.agent;
  }
  var proxy = options.api_proxy || config().api_proxy;
  if (!isEmpty(proxy)) {
    if (!post_options.agent && agent) {
      post_options.agent = agent;
    } else if (!post_options.agent) {
      post_options.agent = new https.Agent(proxy);
    } else {
      console.warn("Proxy is set, but request uses a custom agent, proxy is ignored.");
    }
  }

  var post_request = https.request(post_options, callback);
  var upload_stream = new UploadStream({ boundary });
  upload_stream.pipe(post_request);
  var timeout = false;
  post_request.on("error", function (error) {
    if (timeout) {
      error = {
        message: "Request Timeout",
        http_code: 499,
        name: "TimeoutError"
      };
    }
    return callback({ error });
  });
  post_request.setTimeout(options.timeout != null ? options.timeout : 60000, function () {
    timeout = true;
    return post_request.abort();
  });
  post_data.forEach(function (postDatum) {
    return post_request.write(postDatum);
  });
  if (options.stream) {
    post_request.write(file_header);
    return upload_stream;
  }
  if (file != null) {
    post_request.write(file_header);
    fs.createReadStream(file).on('error', function (error) {
      callback({
        error: error
      });
      return post_request.abort();
    }).pipe(upload_stream);
  } else {
    post_request.write(finish_buffer);
    post_request.end();
  }
  return true;
}

function encodeFieldPart(boundary, name, value) {
  return [`--${boundary}`, `Content-Disposition: form-data; name="${name}"`, '', value, ''].join("\r\n");
}

function encodeFilePart(boundary, type, name, filename) {
  return [`--${boundary}`, `Content-Disposition: form-data; name="${name}"; filename="${filename}"`, `Content-Type: ${type}`, '', ''].join("\r\n");
}

exports.direct_upload = function direct_upload(callback_url) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var params = build_upload_params(extend({
    callback: callback_url
  }, options));
  params = utils.process_request_params(params, options);
  var api_url = utils.api_url("upload", options);
  return {
    hidden_fields: params,
    form_attrs: {
      action: api_url,
      method: "POST",
      enctype: "multipart/form-data"
    }
  };
};

exports.upload_tag_params = function upload_tag_params() {
  var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

  var params = build_upload_params(options);
  params = utils.process_request_params(params, options);
  return JSON.stringify(params);
};

exports.upload_url = function upload_url() {
  var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

  if (options.resource_type == null) {
    options.resource_type = "auto";
  }
  return utils.api_url("upload", options);
};

exports.image_upload_tag = function image_upload_tag(field) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var html_options = options.html || {};
  var tag_options = extend({
    type: "file",
    name: "file",
    "data-url": exports.upload_url(options),
    "data-form-data": exports.upload_tag_params(options),
    "data-cloudinary-field": field,
    "data-max-chunk-size": options.chunk_size,
    "class": [html_options.class, "cloudinary-fileupload"].join(" ")
  }, html_options);
  return `<input ${utils.html_attrs(tag_options)}/>`;
};

exports.unsigned_image_upload_tag = function unsigned_image_upload_tag(field, upload_preset) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return exports.image_upload_tag(field, merge(options, {
    unsigned: true,
    upload_preset: upload_preset
  }));
};

/**
 * Populates metadata fields with the given values. Existing values will be overwritten.
 *
 * @param {Object}   metadata   A list of custom metadata fields (by external_id) and the values to assign to each
 * @param {Array}    public_ids The public IDs of the resources to update
 * @param {Function} callback   Callback function
 * @param {Object}   options    Configuration options
 *
 * @return {Object}
 */
exports.update_metadata = function update_metadata(metadata, public_ids, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  return call_api("metadata", callback, options, function () {
    var params = {
      metadata: utils.encode_context(metadata),
      public_ids: utils.build_array(public_ids),
      timestamp: utils.timestamp(),
      type: options.type,
      clear_invalid: options.clear_invalid
    };
    return [params];
  });
};