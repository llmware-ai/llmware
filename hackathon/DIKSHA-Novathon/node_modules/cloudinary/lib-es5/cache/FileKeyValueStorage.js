'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var fs = require('fs');
var path = require('path');
var rimraf = require('../utils/rimraf');

var FileKeyValueStorage = function () {
  function FileKeyValueStorage() {
    var _ref = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {},
        baseFolder = _ref.baseFolder;

    _classCallCheck(this, FileKeyValueStorage);

    this.init(baseFolder);
  }

  _createClass(FileKeyValueStorage, [{
    key: 'init',
    value: function init(baseFolder) {
      if (baseFolder) {
        try {
          fs.accessSync(baseFolder);
          this.baseFolder = baseFolder;
        } catch (err) {
          throw err;
        }
      } else {
        if (!fs.existsSync('test_cache')) {
          fs.mkdirSync('test_cache');
        }
        this.baseFolder = fs.mkdtempSync('test_cache/cloudinary_cache_');
        console.info("Created temporary cache folder at " + this.baseFolder);
      }
    }
  }, {
    key: 'get',
    value: function get(key) {
      var value = fs.readFileSync(this.getFilename(key));
      try {
        return JSON.parse(value);
      } catch (e) {
        throw "Cannot parse cache value";
      }
    }
  }, {
    key: 'set',
    value: function set(key, value) {
      fs.writeFileSync(this.getFilename(key), JSON.stringify(value));
    }
  }, {
    key: 'clear',
    value: function clear() {
      var _this = this;

      var files = fs.readdirSync(this.baseFolder);
      files.forEach(function (file) {
        return fs.unlinkSync(path.join(_this.baseFolder, file));
      });
    }
  }, {
    key: 'deleteBaseFolder',
    value: function deleteBaseFolder() {
      rimraf(this.baseFolder);
    }
  }, {
    key: 'getFilename',
    value: function getFilename(key) {
      return path.format({ name: key, base: key, ext: '.json', dir: this.baseFolder });
    }
  }]);

  return FileKeyValueStorage;
}();

module.exports = FileKeyValueStorage;