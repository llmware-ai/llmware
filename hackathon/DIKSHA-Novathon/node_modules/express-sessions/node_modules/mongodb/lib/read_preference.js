"use strict";

/**
 * @fileOverview The **ReadPreference** class is a class that represents a MongoDB ReadPreference and is
 * used to construct connections.
 *
 * @example
 * var Db = require('mongodb').Db,
 *   ReplSet = require('mongodb').ReplSet,
 *   Server = require('mongodb').Server,
 *   ReadPreference = require('mongodb').ReadPreference,
 *   test = require('assert');
 * // Connect using ReplSet
 * var server = new Server('localhost', 27017);
 * var db = new Db('test', new ReplSet([server]));
 * db.open(function(err, db) {
 *   test.equal(null, err);
 *   // Perform a read
 *   var cursor = db.collection('t').find({});
 *   cursor.setReadPreference(ReadPreference.PRIMARY);
 *   cursor.toArray(function(err, docs) {
 *     test.equal(null, err);
 *     db.close();
 *   });
 * });
 */

/**
 * Creates a new ReadPreference instance
 *
 * Read Preferences
 *  - **ReadPreference.PRIMARY**, Read from primary only. All operations produce an error (throw an exception where applicable) if primary is unavailable. Cannot be combined with tags (This is the default.).
 *  - **ReadPreference.PRIMARY_PREFERRED**, Read from primary if available, otherwise a secondary.
 *  - **ReadPreference.SECONDARY**, Read from secondary if available, otherwise error.
 *  - **ReadPreference.SECONDARY_PREFERRED**, Read from a secondary if available, otherwise read from the primary.
 *  - **ReadPreference.NEAREST**, All modes read from among the nearest candidates, but unlike other modes, NEAREST will include both the primary and all secondaries in the random selection.
 *
 * @class
 * @param {string} mode The ReadPreference mode as listed above.
 * @param {array|object} tags An object representing read preference tags.
 * @param {object} [options] Additional read preference options
 * @param {number} [options.maxStalenessSeconds] Max Secondary Read Staleness in Seconds
 * @return {ReadPreference} a ReadPreference instance.
 */
var ReadPreference = function(mode, tags, options) {
  if(!(this instanceof ReadPreference)) {
    return new ReadPreference(mode, tags, options);
  }

  this._type = 'ReadPreference';
  this.mode = mode;
  this.tags = tags;
  this.options =  options;

  // If no tags were passed in
  if(tags && typeof tags == 'object' && !Array.isArray(tags)) {
    if(tags.maxStalenessSeconds) {
      this.options = tags;
      this.tags = null;
    }
  }

  // Add the maxStalenessSeconds value to the read Preference
  if(this.options && this.options.maxStalenessSeconds) {
    this.maxStalenessSeconds = this.options.maxStalenessSeconds;
  }
}

/**
 * Validate if a mode is legal
 *
 * @method
 * @param {string} mode The string representing the read preference mode.
 * @return {boolean}
 */
ReadPreference.isValid = function(_mode) {
  return (_mode == ReadPreference.PRIMARY || _mode == ReadPreference.PRIMARY_PREFERRED
    || _mode == ReadPreference.SECONDARY || _mode == ReadPreference.SECONDARY_PREFERRED
    || _mode == ReadPreference.NEAREST
    || _mode == true || _mode == false || _mode == null);
}

/**
 * Validate if a mode is legal
 *
 * @method
 * @param {string} mode The string representing the read preference mode.
 * @return {boolean}
 */
ReadPreference.prototype.isValid = function(mode) {
  var _mode = typeof mode == 'string' ? mode : this.mode;
  return ReadPreference.isValid(_mode);
}

/**
 * @ignore
 */
ReadPreference.prototype.toObject = function() {
  var object = {mode:this.mode};

  if(this.tags != null) {
    object['tags'] = this.tags;
  }

  if(this.maxStalenessSeconds) {
    object['maxStalenessSeconds'] = this.maxStalenessSeconds;
  }

  return object;
}

/**
 * @ignore
 */
ReadPreference.prototype.toJSON = function() {
  return this.toObject();
}

/**
 * @ignore
 */
ReadPreference.PRIMARY = 'primary';
ReadPreference.PRIMARY_PREFERRED = 'primaryPreferred';
ReadPreference.SECONDARY = 'secondary';
ReadPreference.SECONDARY_PREFERRED = 'secondaryPreferred';
ReadPreference.NEAREST = 'nearest'

/**
 * @ignore
 */
module.exports = ReadPreference;
