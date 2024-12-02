"use strict";

var f = require('util').format
  , crypto = require('crypto')
  , Query = require('../connection/commands').Query
  , MongoError = require('../error');

var AuthSession = function(db, username, password) {
  this.db = db;
  this.username = username;
  this.password = password;
}

AuthSession.prototype.equal = function(session) {
  return session.db == this.db
    && session.username == this.username
    && session.password == this.password;
}

/**
 * Creates a new MongoCR authentication mechanism
 * @class
 * @return {MongoCR} A cursor instance
 */
var MongoCR = function(bson) {
  this.bson = bson;
  this.authStore = [];
}

// Add to store only if it does not exist
var addAuthSession = function(authStore, session) {
  var found = false;

  for(var i = 0; i < authStore.length; i++) {
    if(authStore[i].equal(session)) {
      found = true;
      break;
    }
  }

  if(!found) authStore.push(session);
}

/**
 * Authenticate
 * @method
 * @param {{Server}|{ReplSet}|{Mongos}} server Topology the authentication method is being called on
 * @param {[]Connections} connections Connections to authenticate using this authenticator
 * @param {string} db Name of the database
 * @param {string} username Username
 * @param {string} password Password
 * @param {authResultCallback} callback The callback to return the result from the authentication
 * @return {object}
 */
MongoCR.prototype.auth = function(server, connections, db, username, password, callback) {
  var self = this;
  // Total connections
  var count = connections.length;
  if(count == 0) return callback(null, null);

  // Valid connections
  var numberOfValidConnections = 0;
  var errorObject = null;

  // For each connection we need to authenticate
  while(connections.length > 0) {
    // Execute MongoCR
    var executeMongoCR = function(connection) {
      // Write the commmand on the connection
      server(connection, new Query(self.bson, f("%s.$cmd", db), {
        getnonce:1
      }, {
        numberToSkip: 0, numberToReturn: 1
      }), function(err, r) {
        var nonce = null;
        var key = null;

        // Adjust the number of connections left
        // Get nonce
        if(err == null) {
          nonce = r.result.nonce;
          // Use node md5 generator
          var md5 = crypto.createHash('md5');
          // Generate keys used for authentication
          md5.update(username + ":mongo:" + password, 'utf8');
          var hash_password = md5.digest('hex');
          // Final key
          md5 = crypto.createHash('md5');
          md5.update(nonce + username + hash_password, 'utf8');
          key = md5.digest('hex');
        }

        // Execute command
        // Write the commmand on the connection
        server(connection, new Query(self.bson, f("%s.$cmd", db), {
          authenticate: 1, user: username, nonce: nonce, key:key
        }, {
          numberToSkip: 0, numberToReturn: 1
        }), function(err, r) {
          count = count - 1;

          // If we have an error
          if(err) {
            errorObject = err;
          } else if(r.result['$err']) {
            errorObject = r.result;
          } else if(r.result['errmsg']) {
            errorObject = r.result;
          } else {
            numberOfValidConnections = numberOfValidConnections + 1;
          }

          // We have authenticated all connections
          if(count == 0 && numberOfValidConnections > 0) {
            // Store the auth details
            addAuthSession(self.authStore, new AuthSession(db, username, password));
            // Return correct authentication
            callback(null, true);
          } else if(count == 0) {
            if(errorObject == null) errorObject = new MongoError(f("failed to authenticate using mongocr"));
            callback(errorObject, false);
          }
        });
      });
    }

    var _execute = function(_connection) {
      process.nextTick(function() {
        executeMongoCR(_connection);
      });
    }

    _execute(connections.shift());
  }
}

/**
 * Remove authStore credentials
 * @method
 * @param {string} db Name of database we are removing authStore details about
 * @return {object}
 */
MongoCR.prototype.logout = function(dbName) {
  this.authStore = this.authStore.filter(function(x) {
    return x.db != dbName;
  });
}

/**
 * Re authenticate pool
 * @method
 * @param {{Server}|{ReplSet}|{Mongos}} server Topology the authentication method is being called on
 * @param {[]Connections} connections Connections to authenticate using this authenticator
 * @param {authResultCallback} callback The callback to return the result from the authentication
 * @return {object}
 */
MongoCR.prototype.reauthenticate = function(server, connections, callback) {
  var authStore = this.authStore.slice(0);
  var count = authStore.length;
  if(count == 0) return callback(null, null);
  // Iterate over all the auth details stored
  for(var i = 0; i < authStore.length; i++) {
    this.auth(server, connections, authStore[i].db, authStore[i].username, authStore[i].password, function(err) {
      count = count - 1;
      // Done re-authenticating
      if(count == 0) {
        callback(err, null);
      }
    });
  }
}

/**
 * This is a result from a authentication strategy
 *
 * @callback authResultCallback
 * @param {error} error An error object. Set to null if no error present
 * @param {boolean} result The result of the authentication process
 */

module.exports = MongoCR;
