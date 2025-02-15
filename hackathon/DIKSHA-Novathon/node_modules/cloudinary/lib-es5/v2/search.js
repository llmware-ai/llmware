'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var api = require('./api');
var config = require('../config');

var _require = require('../utils'),
    isEmpty = _require.isEmpty,
    isNumber = _require.isNumber,
    compute_hash = _require.compute_hash,
    build_distribution_domain = _require.build_distribution_domain,
    clear_blank = _require.clear_blank,
    sort_object_by_key = _require.sort_object_by_key;

var _require2 = require('../utils/encoding/base64Encode'),
    base64Encode = _require2.base64Encode;

var Search = function () {
  function Search() {
    _classCallCheck(this, Search);

    this.query_hash = {
      sort_by: [],
      aggregate: [],
      with_field: []
    };
    this._ttl = 300;
  }

  _createClass(Search, [{
    key: 'expression',
    value: function expression(value) {
      this.query_hash.expression = value;
      return this;
    }
  }, {
    key: 'max_results',
    value: function max_results(value) {
      this.query_hash.max_results = value;
      return this;
    }
  }, {
    key: 'next_cursor',
    value: function next_cursor(value) {
      this.query_hash.next_cursor = value;
      return this;
    }
  }, {
    key: 'aggregate',
    value: function aggregate(value) {
      var found = this.query_hash.aggregate.find(function (v) {
        return v === value;
      });

      if (!found) {
        this.query_hash.aggregate.push(value);
      }

      return this;
    }
  }, {
    key: 'with_field',
    value: function with_field(value) {
      var found = this.query_hash.with_field.find(function (v) {
        return v === value;
      });

      if (!found) {
        this.query_hash.with_field.push(value);
      }

      return this;
    }
  }, {
    key: 'sort_by',
    value: function sort_by(field_name) {
      var dir = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "desc";

      var sort_bucket = void 0;
      sort_bucket = {};
      sort_bucket[field_name] = dir;

      // Check if this field name is already stored in the hash
      var previously_sorted_obj = this.query_hash.sort_by.find(function (sort_by) {
        return sort_by[field_name];
      });

      // Since objects are references in Javascript, we can update the reference we found
      // For example,
      if (previously_sorted_obj) {
        previously_sorted_obj[field_name] = dir;
      } else {
        this.query_hash.sort_by.push(sort_bucket);
      }

      return this;
    }
  }, {
    key: 'ttl',
    value: function ttl(newTtl) {
      if (isNumber(newTtl)) {
        this._ttl = newTtl;
        return this;
      }

      throw new Error('New TTL value has to be a Number.');
    }
  }, {
    key: 'to_query',
    value: function to_query() {
      var _this = this;

      Object.keys(this.query_hash).forEach(function (k) {
        var v = _this.query_hash[k];
        if (!isNumber(v) && isEmpty(v)) {
          delete _this.query_hash[k];
        }
      });
      return this.query_hash;
    }
  }, {
    key: 'execute',
    value: function execute(options, callback) {
      if (callback === null) {
        callback = options;
      }
      options = options || {};
      return api.search(this.to_query(), options, callback);
    }
  }, {
    key: 'to_url',
    value: function to_url(ttl, next_cursor) {
      var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

      var apiSecret = 'api_secret' in options ? options.api_secret : config().api_secret;
      if (!apiSecret) {
        throw new Error('Must supply api_secret');
      }

      var urlTtl = ttl || this._ttl;

      var query = this.to_query();

      var urlCursor = next_cursor;
      if (query.next_cursor && !next_cursor) {
        urlCursor = query.next_cursor;
      }
      delete query.next_cursor;

      var dataOrderedByKey = sort_object_by_key(clear_blank(query));
      var encodedQuery = base64Encode(JSON.stringify(dataOrderedByKey));

      var urlPrefix = build_distribution_domain(options.source, options);

      var signature = compute_hash(`${urlTtl}${encodedQuery}${apiSecret}`, 'sha256', 'hex');

      var urlWithoutCursor = `${urlPrefix}/search/${signature}/${urlTtl}/${encodedQuery}`;
      return urlCursor ? `${urlWithoutCursor}/${urlCursor}` : urlWithoutCursor;
    }
  }], [{
    key: 'instance',
    value: function instance() {
      return new Search();
    }
  }, {
    key: 'expression',
    value: function expression(value) {
      return this.instance().expression(value);
    }
  }, {
    key: 'max_results',
    value: function max_results(value) {
      return this.instance().max_results(value);
    }
  }, {
    key: 'next_cursor',
    value: function next_cursor(value) {
      return this.instance().next_cursor(value);
    }
  }, {
    key: 'aggregate',
    value: function aggregate(value) {
      return this.instance().aggregate(value);
    }
  }, {
    key: 'with_field',
    value: function with_field(value) {
      return this.instance().with_field(value);
    }
  }, {
    key: 'sort_by',
    value: function sort_by(field_name) {
      var dir = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 'asc';

      return this.instance().sort_by(field_name, dir);
    }
  }, {
    key: 'ttl',
    value: function ttl(newTtl) {
      return this.instance().ttl(newTtl);
    }
  }]);

  return Search;
}();

module.exports = Search;