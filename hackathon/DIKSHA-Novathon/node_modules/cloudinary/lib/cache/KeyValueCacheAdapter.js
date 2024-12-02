const crypto = require('crypto');
const CacheAdapter = require('../cache').CacheAdapter;

/**
 *
 */
class KeyValueCacheAdapter extends CacheAdapter {
  constructor(storage) {
    super();
    this.storage = storage;
  }

  /** @inheritDoc */
  get(publicId, type, resourceType, transformation, format) {
    let key = KeyValueCacheAdapter.generateCacheKey(publicId, type, resourceType, transformation, format);
    return KeyValueCacheAdapter.extractData(this.storage.get(key));
  }

  /** @inheritDoc */
  set(publicId, type, resourceType, transformation, format, value) {
    let key = KeyValueCacheAdapter.generateCacheKey(publicId, type, resourceType, transformation, format);
    this.storage.set(
      key,
      KeyValueCacheAdapter.prepareData(
        publicId,
        type,
        resourceType,
        transformation,
        format,
        value
      )
    );
  }

  /** @inheritDoc */
  flushAll() {
    this.storage.clear();
  }

  /** @inheritDoc */
  delete(publicId, type, resourceType, transformation, format) {
    let key = KeyValueCacheAdapter.generateCacheKey(publicId, type, resourceType, transformation, format);
    return this.storage.delete(key);
  }

  static generateCacheKey(publicId, type, resourceType, transformation, format) {
    type = type || "upload";
    resourceType = resourceType || "image";
    let sha1 = crypto.createHash('sha1');
    return sha1.update([publicId, type, resourceType, transformation, format].filter(i => i).join('/')).digest('hex');
  }

  static prepareData(publicId, type, resourceType, transformation, format, data) {
    return { publicId, type, resourceType, transformation, format, breakpoints: data };
  }

  static extractData(data) {
    return data ? data.breakpoints : null;
  }
}

module.exports = KeyValueCacheAdapter;
