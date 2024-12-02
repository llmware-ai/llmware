"use strict";

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/* eslint-disable class-methods-use-this */

var CACHE = Symbol.for("com.cloudinary.cache");
var CACHE_ADAPTER = Symbol.for("com.cloudinary.cacheAdapter");

var _require = require('./utils'),
    ensurePresenceOf = _require.ensurePresenceOf,
    generate_transformation_string = _require.generate_transformation_string;

/**
 * The adapter used to communicate with the underlying cache storage
 */


var CacheAdapter = function () {
  function CacheAdapter() {
    _classCallCheck(this, CacheAdapter);
  }

  _createClass(CacheAdapter, [{
    key: "get",

    /**
     * Get a value from the cache
     * @param {string} publicId
     * @param {string} type
     * @param {string} resourceType
     * @param {string} transformation
     * @param {string} format
     * @return {*} the value associated with the provided arguments
     */
    value: function get(publicId, type, resourceType, transformation, format) {}

    /**
     * Set a new value in the cache
     * @param {string} publicId
     * @param {string} type
     * @param {string} resourceType
     * @param {string} transformation
     * @param {string} format
     * @param {*} value
     */

  }, {
    key: "set",
    value: function set(publicId, type, resourceType, transformation, format, value) {}

    /**
     * Delete all values in the cache
     */

  }, {
    key: "flushAll",
    value: function flushAll() {}
  }]);

  return CacheAdapter;
}();
/**
 * @class Cache
 * Stores and retrieves values identified by publicId / options pairs
 */


var Cache = {
  /**
   * The adapter interface. Extend this class to implement a specific adapter.
   * @type CacheAdapter
   */
  CacheAdapter,
  /**
   * Set the cache adapter
   * @param {CacheAdapter} adapter The cache adapter
   */
  setAdapter(adapter) {
    if (this.adapter) {
      console.warn("Overriding existing cache adapter");
    }
    this.adapter = adapter;
  },
  /**
   * Get the adapter the Cache is using
   * @return {CacheAdapter} the current cache adapter
   */
  getAdapter() {
    return this.adapter;
  },
  /**
   * Get an item from the cache
   * @param {string} publicId
   * @param {object} options
   * @return {*}
   */
  get(publicId, options) {
    if (!this.adapter) {
      return undefined;
    }
    ensurePresenceOf({ publicId });
    var transformation = generate_transformation_string(_extends({}, options));
    return this.adapter.get(publicId, options.type || 'upload', options.resource_type || 'image', transformation, options.format);
  },
  /**
   * Set a new value in the cache
   * @param {string} publicId
   * @param {object} options
   * @param {*} value
   * @return {*}
   */
  set(publicId, options, value) {
    if (!this.adapter) {
      return undefined;
    }
    ensurePresenceOf({ publicId, value });
    var transformation = generate_transformation_string(_extends({}, options));
    return this.adapter.set(publicId, options.type || 'upload', options.resource_type || 'image', transformation, options.format, value);
  },
  /**
   * Clear all items in the cache
   * @return {*} Returns the value from the adapter's flushAll() method
   */
  flushAll() {
    if (!this.adapter) {
      return undefined;
    }
    return this.adapter.flushAll();
  }

};

// Define singleton property
Object.defineProperty(Cache, "instance", {
  get() {
    return global[CACHE];
  }
});
Object.defineProperty(Cache, "adapter", {
  /**
   *
   * @return {CacheAdapter} The current cache adapter
   */
  get() {
    return global[CACHE_ADAPTER];
  },
  /**
   * Set the cache adapter to be used by Cache
   * @param {CacheAdapter} adapter Cache adapter
   */
  set(adapter) {
    global[CACHE_ADAPTER] = adapter;
  }
});
Object.freeze(Cache);

// Instantiate the singleton
var symbols = Object.getOwnPropertySymbols(global);
if (symbols.indexOf(CACHE) < 0) {
  global[CACHE] = Cache;
}

/**
 * Store key value pairs

 */
module.exports = Cache;