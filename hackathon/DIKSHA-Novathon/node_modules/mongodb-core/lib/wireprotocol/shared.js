"use strict"

var ReadPreference = require('../topologies/read_preference'),
  MongoError = require('../error');

var getReadPreference = function(cmd, options) {
  // Default to command version of the readPreference
  var readPreference = cmd.readPreference || new ReadPreference('primary');
  // If we have an option readPreference override the command one
  if(options.readPreference) {
    readPreference = options.readPreference;
  }

  if(typeof readPreference == 'string') {
    readPreference = new ReadPreference(readPreference);
  }

  if(!(readPreference instanceof ReadPreference)) {
    throw new MongoError('readPreference must be a ReadPreference instance');
  }

  return readPreference;
}

module.exports = {
  getReadPreference: getReadPreference
}
