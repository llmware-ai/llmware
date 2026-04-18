"use strict";

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var PRELOADED_CLOUDINARY_PATH = void 0,
    config = void 0,
    utils = void 0;

utils = require("./utils");

config = require("./config");

PRELOADED_CLOUDINARY_PATH = /^([^\/]+)\/([^\/]+)\/v(\d+)\/([^#]+)#([^\/]+)$/;

var PreloadedFile = function () {
  function PreloadedFile(file_info) {
    _classCallCheck(this, PreloadedFile);

    var matches = void 0,
        public_id_and_format = void 0;
    matches = file_info.match(PRELOADED_CLOUDINARY_PATH);
    if (!matches) {
      throw "Invalid preloaded file info";
    }
    this.resource_type = matches[1];
    this.type = matches[2];
    this.version = matches[3];
    this.filename = matches[4];
    this.signature = matches[5];
    public_id_and_format = PreloadedFile.split_format(this.filename);
    this.public_id = public_id_and_format[0];
    this.format = public_id_and_format[1];
  }

  _createClass(PreloadedFile, [{
    key: "is_valid",
    value: function is_valid() {
      var expected_signature = void 0;
      expected_signature = utils.api_sign_request({
        public_id: this.public_id,
        version: this.version
      }, config().api_secret);
      return this.signature === expected_signature;
    }
  }, {
    key: "identifier",
    value: function identifier() {
      return `v${this.version}/${this.filename}`;
    }
  }, {
    key: "toString",
    value: function toString() {
      return `${this.resource_type}/${this.type}/v${this.version}/${this.filename}#${this.signature}`;
    }
  }, {
    key: "toJSON",
    value: function toJSON() {
      var _this = this;

      var result = {};
      Object.getOwnPropertyNames(this).forEach(function (key) {
        var val = _this[key];
        if (typeof val !== 'function') {
          result[key] = val;
        }
      });
      return result;
    }
  }], [{
    key: "split_format",
    value: function split_format(identifier) {
      var format = void 0,
          last_dot = void 0,
          public_id = void 0;
      last_dot = identifier.lastIndexOf(".");
      if (last_dot === -1) {
        return [identifier, null];
      }
      public_id = identifier.substr(0, last_dot);
      format = identifier.substr(last_dot + 1);
      return [public_id, format];
    }
  }]);

  return PreloadedFile;
}();

module.exports = PreloadedFile;