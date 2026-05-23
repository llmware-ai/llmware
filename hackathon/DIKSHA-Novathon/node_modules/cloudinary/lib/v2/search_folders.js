const Search = require('./search');
const api = require('./api');

const SearchFolders = class SearchFolders extends Search {
  constructor() {
    super();
  }

  static instance() {
    return new SearchFolders();
  }

  execute(options, callback) {
    if (callback === null) {
      callback = options;
    }
    options = options || {};
    return api.search_folders(this.to_query(), options, callback);
  }
};

module.exports = SearchFolders;
