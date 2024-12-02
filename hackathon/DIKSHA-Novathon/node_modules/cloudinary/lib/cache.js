/* eslint-disable class-methods-use-this */

const CACHE = Symbol.for("com.cloudinary.cache");
const CACHE_ADAPTER = Symbol.for("com.cloudinary.cacheAdapter");
const { ensurePresenceOf, generate_transformation_string } = require('./utils');

/**
 * The adapter used to communicate with the underlying cache storage
 */
class CacheAdapter {
  /**
   * Get a value from the cache
   * @param {string} publicId
   * @param {string} type
   * @param {string} resourceType
   * @param {string} transformation
   * @param {string} format
   * @return {*} the value associated with the provided arguments
   */
  get(publicId, type, resourceType, transformation, format) {}

  /**
   * Set a new value in the cache
   * @param {string} publicId
   * @param {string} type
   * @param {string} resourceType
   * @param {string} transformation
   * @param {string} format
   * @param {*} value
   */
  set(publicId, type, resourceType, transformation, format, value) {}

  /**
   * Delete all values in the cache
   */
  flushAll() {}
}
/**
 * @class Cache
 * Stores and retrieves values identified by publicId / options pairs
 */
const Cache = {
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
    if (!this.adapter) { return undefined; }
    ensurePresenceOf({ publicId });
    let transformation = generate_transformation_string({ ...options });
    return this.adapter.get(
      publicId, options.type || 'upload',
      options.resource_type || 'image',
      transformation,
      options.format
    );
  },
  /**
   * Set a new value in the cache
   * @param {string} publicId
   * @param {object} options
   * @param {*} value
   * @return {*}
   */
  set(publicId, options, value) {
    if (!this.adapter) { return undefined; }
    ensurePresenceOf({ publicId, value });
    let transformation = generate_transformation_string({ ...options });
    return this.adapter.set(
      publicId,
      options.type || 'upload',
      options.resource_type || 'image',
      transformation,
      options.format,
      value
    );
  },
  /**
   * Clear all items in the cache
   * @return {*} Returns the value from the adapter's flushAll() method
   */
  flushAll() {
    if (!this.adapter) { return undefined; }
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
let symbols = Object.getOwnPropertySymbols(global);
if (symbols.indexOf(CACHE) < 0) {
  global[CACHE] = Cache;
}

/**
 * Store key value pairs

 */
module.exports = Cache;
