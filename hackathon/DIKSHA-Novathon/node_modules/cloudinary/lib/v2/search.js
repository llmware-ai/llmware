const api = require('./api');
const config = require('../config');
const {
  isEmpty,
  isNumber,
  compute_hash,
  build_distribution_domain,
  clear_blank,
  sort_object_by_key
} = require('../utils');
const {base64Encode} = require('../utils/encoding/base64Encode');

const Search = class Search {
  constructor() {
    this.query_hash = {
      sort_by: [],
      aggregate: [],
      with_field: []
    };
    this._ttl = 300;
  }

  static instance() {
    return new Search();
  }

  static expression(value) {
    return this.instance().expression(value);
  }

  static max_results(value) {
    return this.instance().max_results(value);
  }

  static next_cursor(value) {
    return this.instance().next_cursor(value);
  }

  static aggregate(value) {
    return this.instance().aggregate(value);
  }

  static with_field(value) {
    return this.instance().with_field(value);
  }

  static sort_by(field_name, dir = 'asc') {
    return this.instance().sort_by(field_name, dir);
  }

  static ttl(newTtl) {
    return this.instance().ttl(newTtl);
  }

  expression(value) {
    this.query_hash.expression = value;
    return this;
  }

  max_results(value) {
    this.query_hash.max_results = value;
    return this;
  }

  next_cursor(value) {
    this.query_hash.next_cursor = value;
    return this;
  }

  aggregate(value) {
    const found = this.query_hash.aggregate.find(v => v === value);

    if (!found) {
      this.query_hash.aggregate.push(value);
    }

    return this;
  }

  with_field(value) {
    const found = this.query_hash.with_field.find(v => v === value);

    if (!found) {
      this.query_hash.with_field.push(value);
    }

    return this;
  }

  sort_by(field_name, dir = "desc") {
    let sort_bucket;
    sort_bucket = {};
    sort_bucket[field_name] = dir;

    // Check if this field name is already stored in the hash
    const previously_sorted_obj = this.query_hash.sort_by.find((sort_by) => sort_by[field_name]);

    // Since objects are references in Javascript, we can update the reference we found
    // For example,
    if (previously_sorted_obj) {
      previously_sorted_obj[field_name] = dir;
    } else {
      this.query_hash.sort_by.push(sort_bucket);
    }

    return this;
  }

  ttl(newTtl) {
    if (isNumber(newTtl)) {
      this._ttl = newTtl;
      return this;
    }

    throw new Error('New TTL value has to be a Number.');
  }

  to_query() {
    Object.keys(this.query_hash).forEach((k) => {
      let v = this.query_hash[k];
      if (!isNumber(v) && isEmpty(v)) {
        delete this.query_hash[k];
      }
    });
    return this.query_hash;
  }

  execute(options, callback) {
    if (callback === null) {
      callback = options;
    }
    options = options || {};
    return api.search(this.to_query(), options, callback);
  }

  to_url(ttl, next_cursor, options = {}) {
    const apiSecret = 'api_secret' in options ? options.api_secret : config().api_secret;
    if (!apiSecret) {
      throw new Error('Must supply api_secret');
    }

    const urlTtl = ttl || this._ttl;

    const query = this.to_query();

    let urlCursor = next_cursor;
    if (query.next_cursor && !next_cursor) {
      urlCursor = query.next_cursor;
    }
    delete query.next_cursor;

    const dataOrderedByKey = sort_object_by_key(clear_blank(query));
    const encodedQuery = base64Encode(JSON.stringify(dataOrderedByKey));

    const urlPrefix = build_distribution_domain(options.source, options);

    const signature = compute_hash(`${urlTtl}${encodedQuery}${apiSecret}`, 'sha256', 'hex');

    const urlWithoutCursor = `${urlPrefix}/search/${signature}/${urlTtl}/${encodedQuery}`;
    return urlCursor ? `${urlWithoutCursor}/${urlCursor}` : urlWithoutCursor;
  }
};

module.exports = Search;
