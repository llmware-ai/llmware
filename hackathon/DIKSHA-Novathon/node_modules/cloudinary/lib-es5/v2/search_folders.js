'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Search = require('./search');
var api = require('./api');

var SearchFolders = function (_Search) {
  _inherits(SearchFolders, _Search);

  function SearchFolders() {
    _classCallCheck(this, SearchFolders);

    return _possibleConstructorReturn(this, (SearchFolders.__proto__ || Object.getPrototypeOf(SearchFolders)).call(this));
  }

  _createClass(SearchFolders, [{
    key: 'execute',
    value: function execute(options, callback) {
      if (callback === null) {
        callback = options;
      }
      options = options || {};
      return api.search_folders(this.to_query(), options, callback);
    }
  }], [{
    key: 'instance',
    value: function instance() {
      return new SearchFolders();
    }
  }]);

  return SearchFolders;
}(Search);

module.exports = SearchFolders;