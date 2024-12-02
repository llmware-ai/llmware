"use strict";

var f = require('util').format
  , require_optional = require('require_optional')
  , Query = require('../connection/commands').Query
  , MongoError = require('../error');

var AuthSession = function(db, username, password, options) {
  this.db = db;
  this.username = username;
  this.password = password;
  this.options = options;
}

AuthSession.prototype.equal = function(session) {
  return session.db == this.db
    && session.username == this.username
    && session.password == this.password;
}

// Kerberos class
var Kerberos = null;
var MongoAuthProcess = null;

// Try to grab the Kerberos class
try {
  Kerberos = require_optional('kerberos').Kerberos;
  // Authentication process for Mongo
  MongoAuthProcess = require_optional('kerberos').processes.MongoAuthProcess;
} catch(err) {  
}

/**
 * Creates a new GSSAPI authentication mechanism
 * @class
 * @return {GSSAPI} A cursor instance
 */
var GSSAPI = function(bson) {
  this.bson = bson;
  this.authStore = [];
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
GSSAPI.prototype.auth = function(server, connections, db, username, password, options, callback) {
  var self = this;
  // We don't have the Kerberos library
  if(Kerberos == null) return callback(new Error("Kerberos library is not installed"));
  var gssapiServiceName = options['gssapiServiceName'] || 'mongodb';
  // Total connections
  var count = connections.length;
  if(count == 0) return callback(null, null);

  // Valid connections
  var numberOfValidConnections = 0;
  var errorObject = null;

  // For each connection we need to authenticate
  while(connections.length > 0) {
    // Execute MongoCR
    var execute = function(connection) {
      // Start Auth process for a connection
      GSSAPIInitialize(self, db, username, password, db, gssapiServiceName, server, connection, options, function(err, r) {
        // Adjust count
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
          addAuthSession(self.authStore, new AuthSession(db, username, password, options));
          // Return correct authentication
          callback(null, true);
        } else if(count == 0) {
          if(errorObject == null) errorObject = new MongoError(f("failed to authenticate using mongocr"));
          callback(errorObject, false);
        }
      });
    }

    var _execute = function(_connection) {
      process.nextTick(function() {
        execute(_connection);
      });
    }

    _execute(connections.shift());
  }
}

//
// Initialize step
var GSSAPIInitialize = function(self, db, username, password, authdb, gssapiServiceName, server, connection, options, callback) {
  // Create authenticator
  var mongo_auth_process = new MongoAuthProcess(connection.host, connection.port, gssapiServiceName, options);

  // Perform initialization
  mongo_auth_process.init(username, password, function(err) {
    if(err) return callback(err, false);

    // Perform the first step
    mongo_auth_process.transition('', function(err, payload) {
      if(err) return callback(err, false);

      // Call the next db step
      MongoDBGSSAPIFirstStep(self, mongo_auth_process, payload, db, username, password, authdb, server, connection, callback);
    });
  });
}

//
// Perform first step against mongodb
var MongoDBGSSAPIFirstStep = function(self, mongo_auth_process, payload, db, username, password, authdb, server, connection, callback) {
  // Build the sasl start command
  var command = {
      saslStart: 1
    , mechanism: 'GSSAPI'
    , payload: payload
    , autoAuthorize: 1
  };

  // Write the commmand on the connection
  server(connection, new Query(self.bson, "$external.$cmd", command, {
    numberToSkip: 0, numberToReturn: 1
  }), function(err, r) {
    if(err) return callback(err, false);
    var doc = r.result;
    // Execute mongodb transition
    mongo_auth_process.transition(r.result.payload, function(err, payload) {
      if(err) return callback(err, false);

      // MongoDB API Second Step
      MongoDBGSSAPISecondStep(self, mongo_auth_process, payload, doc, db, username, password, authdb, server, connection, callback);
    });
  });
}

//
// Perform first step against mongodb
var MongoDBGSSAPISecondStep = function(self, mongo_auth_process, payload, doc, db, username, password, authdb, server, connection, callback) {
  // Build Authentication command to send to MongoDB
  var command = {
      saslContinue: 1
    , conversationId: doc.conversationId
    , payload: payload
  };

  // Execute the command
  // Write the commmand on the connection
  server(connection, new Query(self.bson, "$external.$cmd", command, {
    numberToSkip: 0, numberToReturn: 1
  }), function(err, r) {
    if(err) return callback(err, false);
    var doc = r.result;
    // Call next transition for kerberos
    mongo_auth_process.transition(doc.payload, function(err, payload) {
      if(err) return callback(err, false);

      // Call the last and third step
      MongoDBGSSAPIThirdStep(self, mongo_auth_process, payload, doc, db, username, password, authdb, server, connection, callback);
    });
  });
}

var MongoDBGSSAPIThirdStep = function(self, mongo_auth_process, payload, doc, db, username, password, authdb, server, connection, callback) {
  // Build final command
  var command = {
      saslContinue: 1
    , conversationId: doc.conversationId
    , payload: payload
  };

  // Execute the command
  server(connection, new Query(self.bson, "$external.$cmd", command, {
    numberToSkip: 0, numberToReturn: 1
  }), function(err, r) {
    if(err) return callback(err, false);
    mongo_auth_process.transition(null, function(err) {
      if(err) return callback(err, null);
      callback(null, r);
    });
  });
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
 * Remove authStore credentials
 * @method
 * @param {string} db Name of database we are removing authStore details about
 * @return {object}
 */
GSSAPI.prototype.logout = function(dbName) {
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
GSSAPI.prototype.reauthenticate = function(server, connections, callback) {
  var authStore = this.authStore.slice(0);
  var count = authStore.length;
  if(count == 0) return callback(null, null);
  // Iterate over all the auth details stored
  for(var i = 0; i < authStore.length; i++) {
    this.auth(server, connections, authStore[i].db, authStore[i].username, authStore[i].password, authStore[i].options, function(err) {
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

module.exports = GSSAPI;
