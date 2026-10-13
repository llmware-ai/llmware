'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var crypto = require('crypto');
var CacheAdapter = require('../cache').CacheAdapter;

/**
 *
 */

var KeyValueCacheAdapter = function (_CacheAdapter) {
  _inherits(KeyValueCacheAdapter, _CacheAdapter);

  function KeyValueCacheAdapter(storage) {
    _classCallCheck(this, KeyValueCacheAdapter);

    var _this = _possibleConstructorReturn(this, (KeyValueCacheAdapter.__proto__ || Object.getPrototypeOf(KeyValueCacheAdapter)).call(this));

    _this.storage = storage;
    return _this;
  }

  /** @inheritDoc */


  _createClass(KeyValueCacheAdapter, [{
    key: 'get',
    value: function get(publicId, type, resourceType, transformation, format) {
      var key = KeyValueCacheAdapter.generateCacheKey(publicId, type, resourceType, transformation, format);
      return KeyValueCacheAdapter.extractData(this.storage.get(key));
    }

    /** @inheritDoc */

  }, {
    key: 'set',
    value: function set(publicId, type, resourceType, transformation, format, value) {
      var key = KeyValueCacheAdapter.generateCacheKey(publicId, type, resourceType, transformation, format);
      this.storage.set(key, KeyValueCacheAdapter.prepareData(publicId, type, resourceType, transformation, format, value));
    }

    /** @inheritDoc */

  }, {
    key: 'flushAll',
    value: function flushAll() {
      this.storage.clear();
    }

    /** @inheritDoc */

  }, {
    key: 'delete',
    value: function _delete(publicId, type, resourceType, transformation, format) {
      var key = KeyValueCacheAdapter.generateCacheKey(publicId, type, resourceType, transformation, format);
      return this.storage.delete(key);
    }
  }], [{
    key: 'generateCacheKey',
    value: function generateCacheKey(publicId, type, resourceType, transformation, format) {
      type = type || "upload";
      resourceType = resourceType || "image";
      var sha1 = crypto.createHash('sha1');
      return sha1.update([publicId, type, resourceType, transformation, format].filter(function (i) {
        return i;
      }).join('/')).digest('hex');
    }
  }, {
    key: 'prepareData',
    value: function prepareData(publicId, type, resourceType, transformation, format, data) {
      return { publicId, type, resourceType, transformation, format, breakpoints: data };
    }
  }, {
    key: 'extractData',
    value: function extractData(data) {
      return data ? data.breakpoints : null;
    }
  }]);

  return KeyValueCacheAdapter;
}(CacheAdapter);

module.exports = KeyValueCacheAdapter;