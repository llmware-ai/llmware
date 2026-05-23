"use strict";

var inherits = require('util').inherits,
  EventEmitter = require('events').EventEmitter,
  Connection = require('./connection'),
  MongoError = require('../error'),
  Logger = require('./logger'),
  f = require('util').format,
  Query = require('./commands').Query,
  CommandResult = require('./command_result'),
  assign = require('../utils').assign;

var MongoCR = require('../auth/mongocr')
  , X509 = require('../auth/x509')
  , Plain = require('../auth/plain')
  , GSSAPI = require('../auth/gssapi')
  , SSPI = require('../auth/sspi')
  , ScramSHA1 = require('../auth/scram');

var DISCONNECTED = 'disconnected';
var CONNECTING = 'connecting';
var CONNECTED = 'connected';
var DESTROYING = 'destroying';
var DESTROYED = 'destroyed';

var _id = 0;

/**
 * Creates a new Pool instance
 * @class
 * @param {string} options.host The server host
 * @param {number} options.port The server port
 * @param {number} [options.size=1] Max server connection pool size
 * @param {boolean} [options.reconnect=true] Server will attempt to reconnect on loss of connection
 * @param {number} [options.reconnectTries=30] Server attempt to reconnect #times
 * @param {number} [options.reconnectInterval=1000] Server will wait # milliseconds between retries
 * @param {boolean} [options.keepAlive=true] TCP Connection keep alive enabled
 * @param {number} [options.keepAliveInitialDelay=300000] Initial delay before TCP keep alive enabled
 * @param {boolean} [options.noDelay=true] TCP Connection no delay
 * @param {number} [options.connectionTimeout=30000] TCP Connection timeout setting
 * @param {number} [options.socketTimeout=360000] TCP Socket timeout setting
 * @param {number} [options.monitoringSocketTimeout=30000] TCP Socket timeout setting for replicaset monitoring socket
 * @param {boolean} [options.ssl=false] Use SSL for connection
 * @param {boolean|function} [options.checkServerIdentity=true] Ensure we check server identify during SSL, set to false to disable checking. Only works for Node 0.12.x or higher. You can pass in a boolean or your own checkServerIdentity override function.
 * @param {Buffer} [options.ca] SSL Certificate store binary buffer
 * @param {Buffer} [options.crl] SSL Certificate revocation store binary buffer
 * @param {Buffer} [options.cert] SSL Certificate binary buffer
 * @param {Buffer} [options.key] SSL Key file binary buffer
 * @param {string} [options.passPhrase] SSL Certificate pass phrase
 * @param {boolean} [options.rejectUnauthorized=false] Reject unauthorized server certificates
 * @param {boolean} [options.promoteLongs=true] Convert Long values from the db into Numbers if they fit into 53 bits
 * @param {boolean} [options.promoteValues=true] Promotes BSON values to native types where possible, set to false to only receive wrapper types.
 * @param {boolean} [options.promoteBuffers=false] Promotes Binary BSON values to native Node Buffers.
 * @param {boolean} [options.domainsEnabled=false] Enable the wrapping of the callback in the current domain, disabled by default to avoid perf hit.
 * @fires Pool#connect
 * @fires Pool#close
 * @fires Pool#error
 * @fires Pool#timeout
 * @fires Pool#parseError
 * @return {Pool} A cursor instance
 */
var Pool = function(options) {
  // Add event listener
  EventEmitter.call(this);
  // Add the options
  this.options = assign({
    // Host and port settings
    host: 'localhost',
    port: 27017,
    // Pool default max size
    size: 5,
    // socket settings
    connectionTimeout: 30000,
    socketTimeout: 360000,
    keepAlive: true,
    keepAliveInitialDelay: 300000,
    noDelay: true,
    // SSL Settings
    ssl: false, checkServerIdentity: true,
    ca: null, crl: null, cert: null, key: null, passPhrase: null,
    rejectUnauthorized: false,
    promoteLongs: true,
    promoteValues: true,
    promoteBuffers: false,
    // Reconnection options
    reconnect: true,
    reconnectInterval: 1000,
    reconnectTries: 30,
    // Enable domains
    domainsEnabled: false
  }, options);

  // console.log("=================================== pool options")
  // console.dir(this.options)

  // Identification information
  this.id = _id++;
  // Current reconnect retries
  this.retriesLeft = this.options.reconnectTries;
  this.reconnectId = null;
  // No bson parser passed in
  if(!options.bson || (options.bson
    && (typeof options.bson.serialize != 'function'
    || typeof options.bson.deserialize != 'function'))) {
      throw new Error("must pass in valid bson parser");
  }

  // Logger instance
  this.logger = Logger('Pool', options);
  // Pool state
  this.state = DISCONNECTED;
  // Connections
  this.availableConnections = [];
  this.inUseConnections = [];
  this.connectingConnections = [];
  // Currently executing
  this.executing = false;
  // Operation work queue
  this.queue = [];

  // All the authProviders
  this.authProviders = options.authProviders || {
      'mongocr': new MongoCR(options.bson), 'x509': new X509(options.bson)
    , 'plain': new Plain(options.bson), 'gssapi': new GSSAPI(options.bson)
    , 'sspi': new SSPI(options.bson), 'scram-sha-1': new ScramSHA1(options.bson)
  }

  // Contains the reconnect connection
  this.reconnectConnection = null;

  // Are we currently authenticating
  this.authenticating = false;
  this.loggingout = false;
  this.nonAuthenticatedConnections = [];
  this.authenticatingTimestamp = null;
  // Number of consecutive timeouts caught
  this.numberOfConsecutiveTimeouts = 0;
  // Current pool Index
  this.connectionIndex = 0;
}

inherits(Pool, EventEmitter);

Object.defineProperty(Pool.prototype, 'size', {
  enumerable:true,
  get: function() { return this.options.size; }
});

Object.defineProperty(Pool.prototype, 'connectionTimeout', {
  enumerable:true,
  get: function() { return this.options.connectionTimeout; }
});

Object.defineProperty(Pool.prototype, 'socketTimeout', {
  enumerable:true,
  get: function() { return this.options.socketTimeout; }
});

function stateTransition(self, newState) {
  var legalTransitions = {
    'disconnected': [CONNECTING, DESTROYING, DISCONNECTED],
    'connecting': [CONNECTING, DESTROYING, CONNECTED, DISCONNECTED],
    'connected': [CONNECTED, DISCONNECTED, DESTROYING],
    'destroying': [DESTROYING, DESTROYED],
    'destroyed': [DESTROYED]
  }

  // Get current state
  var legalStates = legalTransitions[self.state];
  if(legalStates && legalStates.indexOf(newState) != -1) {
    self.state = newState;
  } else {
    self.logger.error(f('Pool with id [%s] failed attempted illegal state transition from [%s] to [%s] only following state allowed [%s]'
      , self.id, self.state, newState, legalStates));
  }
}

function authenticate(pool, auth, connection, cb) {
  if(auth[0] === undefined) return cb(null);
  // We need to authenticate the server
  var mechanism = auth[0];
  var db = auth[1];
  // Validate if the mechanism exists
  if(!pool.authProviders[mechanism]) {
    throw new MongoError(f('authMechanism %s not supported', mechanism));
  }

  // Get the provider
  var provider = pool.authProviders[mechanism];

  // Authenticate using the provided mechanism
  provider.auth.apply(provider, [write(pool), [connection], db].concat(auth.slice(2)).concat([cb]));
}

// The write function used by the authentication mechanism (bypasses external)
function write(self) {
  return function(connection, command, callback) {
    // Get the raw buffer
    // Ensure we stop auth if pool was destroyed
    if(self.state == DESTROYED || self.state == DESTROYING) {
      return callback(new MongoError('pool destroyed'));
    }

    // Set the connection workItem callback
    connection.workItems.push({
      cb: callback, command: true, requestId: command.requestId
    });

    // Write the buffer out to the connection
    connection.write(command.toBin());
  };
}


function reauthenticate(pool, connection, cb) {
  // Authenticate
  function authenticateAgainstProvider(pool, connection, providers, cb) {
    // Finished re-authenticating against providers
    if(providers.length == 0) return cb();
    // Get the provider name
    var provider = pool.authProviders[providers.pop()];

    // Auth provider
    provider.reauthenticate(write(pool), [connection], function(err) {
      // We got an error return immediately
      if(err) return cb(err);
      // Continue authenticating the connection
      authenticateAgainstProvider(pool, connection, providers, cb);
    });
  }

  // Start re-authenticating process
  authenticateAgainstProvider(pool, connection, Object.keys(pool.authProviders), cb);
}

function connectionFailureHandler(self, event) {
  return function(err) {
    // console.log("========== connectionFailureHandler :: " + event)
    // console.dir(err)

    if (this._connectionFailHandled) return;
    this._connectionFailHandled = true;
    // Destroy the connection
    this.destroy();

    // Remove the connection
    removeConnection(self, this);

    // Flush all work Items on this connection
    while(this.workItems.length > 0) {
      var workItem = this.workItems.shift();
      // if(workItem.cb) workItem.cb(err);
      if(workItem.cb) workItem.cb(err);
    }

    // Did we catch a timeout, increment the numberOfConsecutiveTimeouts
    if(event == 'timeout') {
      self.numberOfConsecutiveTimeouts = self.numberOfConsecutiveTimeouts + 1;

      // Have we timed out more than reconnectTries in a row ?
      // Force close the pool as we are trying to connect to tcp sink hole
      if(self.numberOfConsecutiveTimeouts > self.options.reconnectTries) {
        self.numberOfConsecutiveTimeouts = 0;
        // Destroy all connections and pool
        self.destroy(true);
        // Emit close event
        return self.emit('close', self);
      }
    }

    // No more socket available propegate the event
    if(self.socketCount() == 0) {
      if(self.state != DESTROYED && self.state != DESTROYING) {
        stateTransition(self, DISCONNECTED);
      }

      // Do not emit error events, they are always close events
      // do not trigger the low level error handler in node
      event = event == 'error' ? 'close' : event;
      self.emit(event, err);
    }

    // Start reconnection attempts
    if(!self.reconnectId && self.options.reconnect) {
      self.reconnectId = setTimeout(attemptReconnect(self), self.options.reconnectInterval);
    }
  };
}

function attemptReconnect(self) {
  return function() {
    // console.log("========================= attemptReconnect")
    self.emit('attemptReconnect', self);
    if(self.state == DESTROYED || self.state == DESTROYING) return;

    // We are connected do not try again
    if(self.isConnected()) {
      self.reconnectId = null;
      return;
    }

    // If we have failure schedule a retry
    function _connectionFailureHandler(self, event) {
      return function() {
    // console.log("========== _connectionFailureHandler :: " + event)
        if (this._connectionFailHandled) return;
        this._connectionFailHandled = true;
        // Destroy the connection
        this.destroy();
        // Count down the number of reconnects
        self.retriesLeft = self.retriesLeft - 1;
        // How many retries are left
        if(self.retriesLeft == 0) {
          // Destroy the instance
          self.destroy();
          // Emit close event
          self.emit('reconnectFailed'
            , new MongoError(f('failed to reconnect after %s attempts with interval %s ms', self.options.reconnectTries, self.options.reconnectInterval)));
        } else {
          self.reconnectId = setTimeout(attemptReconnect(self), self.options.reconnectInterval);
        }
      }
    }

    // Got a connect handler
    function _connectHandler(self) {
      return function() {
        // Assign
        var connection = this;

        // Pool destroyed stop the connection
        if(self.state == DESTROYED || self.state == DESTROYING) {
          return connection.destroy();
        }

        // Clear out all handlers
        handlers.forEach(function(event) {
          connection.removeAllListeners(event);
        });

        // Reset reconnect id
        self.reconnectId = null;

        // Apply pool connection handlers
        connection.on('error', connectionFailureHandler(self, 'error'));
        connection.on('close', connectionFailureHandler(self, 'close'));
        connection.on('timeout', connectionFailureHandler(self, 'timeout'));
        connection.on('parseError', connectionFailureHandler(self, 'parseError'));

        // Apply any auth to the connection
        reauthenticate(self, this, function() {
          // Reset retries
          self.retriesLeft = self.options.reconnectTries;
          // Push to available connections
          self.availableConnections.push(connection);
          // Set the reconnectConnection to null
          self.reconnectConnection = null;
          // Emit reconnect event
          self.emit('reconnect', self);
          // Trigger execute to start everything up again
          _execute(self)();
        });
      }
    }

    // Create a connection
    self.reconnectConnection = new Connection(messageHandler(self), self.options);
    // Add handlers
    self.reconnectConnection.on('close', _connectionFailureHandler(self, 'close'));
    self.reconnectConnection.on('error', _connectionFailureHandler(self, 'error'));
    self.reconnectConnection.on('timeout', _connectionFailureHandler(self, 'timeout'));
    self.reconnectConnection.on('parseError', _connectionFailureHandler(self, 'parseError'));
    // On connection
    self.reconnectConnection.on('connect', _connectHandler(self));
    // Attempt connection
    self.reconnectConnection.connect();
  }
}

function moveConnectionBetween(connection, from, to) {
  var index = from.indexOf(connection);
  // Move the connection from connecting to available
  if(index != -1) {
    from.splice(index, 1);
    to.push(connection);
  }
}

function messageHandler(self) {
  return function(message, connection) {
    // workItem to execute
    var workItem = null;

    // Locate the workItem
    for(var i = 0; i < connection.workItems.length; i++) {
      if(connection.workItems[i].requestId == message.responseTo) {
        // Get the callback
        workItem = connection.workItems[i];
        // Remove from list of workItems
        connection.workItems.splice(i, 1);
      }
    }


    // Reset timeout counter
    self.numberOfConsecutiveTimeouts = 0;

    // Reset the connection timeout if we modified it for
    // this operation
    if(workItem.socketTimeout) {
      connection.resetSocketTimeout();
    }

    // Log if debug enabled
    if(self.logger.isDebug()) {
      self.logger.debug(f('message [%s] received from %s:%s'
        , message.raw.toString('hex'), self.options.host, self.options.port));
    }

    // Authenticate any straggler connections
    function authenticateStragglers(self, connection, callback) {
      // Get any non authenticated connections
      var connections = self.nonAuthenticatedConnections.slice(0);
      var nonAuthenticatedConnections = self.nonAuthenticatedConnections;
      self.nonAuthenticatedConnections = [];

      // Establish if the connection need to be authenticated
      // Add to authentication list if
      // 1. we were in an authentication process when the operation was executed
      // 2. our current authentication timestamp is from the workItem one, meaning an auth has happened
      if(connection.workItems.length == 1 && (connection.workItems[0].authenticating == true
        || (typeof connection.workItems[0].authenticatingTimestamp == 'number'
            && connection.workItems[0].authenticatingTimestamp != self.authenticatingTimestamp))) {
        // Add connection to the list
        connections.push(connection);
      }

      // No connections need to be re-authenticated
      if(connections.length == 0) {
        // Release the connection back to the pool
        moveConnectionBetween(connection, self.inUseConnections, self.availableConnections);
        // Finish
        return callback();
      }

      // Apply re-authentication to all connections before releasing back to pool
      var connectionCount = connections.length;
      // Authenticate all connections
      for(var i = 0; i < connectionCount; i++) {
        reauthenticate(self, connections[i], function() {
          connectionCount = connectionCount - 1;

          if(connectionCount == 0) {
            // Put non authenticated connections in available connections
            self.availableConnections = self.availableConnections.concat(nonAuthenticatedConnections);
            // Release the connection back to the pool
            moveConnectionBetween(connection, self.inUseConnections, self.availableConnections);
            // Return
            callback();
          }
        });
      }
    }

    function handleOperationCallback(self, cb, err, result) {
      // No domain enabled
      if(!self.options.domainsEnabled) {
        return process.nextTick(function() {
          return cb(err, result);
        });
      }

      // Domain enabled just call the callback
      cb(err, result);
    }

    authenticateStragglers(self, connection, function() {
      // Keep executing, ensure current message handler does not stop execution
      if(!self.executing) {
        process.nextTick(function() {
          _execute(self)();
        });
      }

      // Time to dispatch the message if we have a callback
      if(!workItem.immediateRelease) {
        try {
          // Parse the message according to the provided options
          message.parse(workItem);
        } catch(err) {
          return handleOperationCallback(self, workItem.cb, MongoError.create(err));
        }

        // Establish if we have an error
        if(workItem.command && message.documents[0] && (message.documents[0].ok == 0 || message.documents[0]['$err']
        || message.documents[0]['errmsg'] || message.documents[0]['code'])) {
          return handleOperationCallback(self, workItem.cb, MongoError.create(message.documents[0]));
        }

        // Add the connection details
        message.hashedName = connection.hashedName;

        // Return the documents
        handleOperationCallback(self, workItem.cb, null, new CommandResult(workItem.fullResult ? message : message.documents[0], connection, message));
      }
    });
  }
}

/**
 * Return the total socket count in the pool.
 * @method
 * @return {Number} The number of socket available.
 */
Pool.prototype.socketCount = function() {
  return this.availableConnections.length
    + this.inUseConnections.length;
    // + this.connectingConnections.length;
}

/**
 * Return all pool connections
 * @method
 * @return {Connection[]} The pool connections
 */
Pool.prototype.allConnections = function() {
  return this.availableConnections
    .concat(this.inUseConnections)
    .concat(this.connectingConnections);
}

/**
 * Get a pool connection (round-robin)
 * @method
 * @return {Connection}
 */
Pool.prototype.get = function() {
  return this.allConnections()[0];
}

/**
 * Is the pool connected
 * @method
 * @return {boolean}
 */
Pool.prototype.isConnected = function() {
  // We are in a destroyed state
  if(this.state == DESTROYED || this.state == DESTROYING) {
    return false;
  }

  // Get connections
  var connections = this.availableConnections
    .concat(this.inUseConnections);

  // Check if we have any connected connections
  for(var i = 0; i < connections.length; i++) {
    if(connections[i].isConnected()) return true;
  }

  // Might be authenticating, but we are still connected
  if(connections.length == 0 && this.authenticating) {
    return true
  }

  // Not connected
  return false;
}

/**
 * Was the pool destroyed
 * @method
 * @return {boolean}
 */
Pool.prototype.isDestroyed = function() {
  return this.state == DESTROYED || this.state == DESTROYING;
}

/**
 * Is the pool in a disconnected state
 * @method
 * @return {boolean}
 */
Pool.prototype.isDisconnected = function() {
  return this.state == DISCONNECTED;
}

/**
 * Connect pool
 * @method
 */
Pool.prototype.connect = function() {
  if(this.state != DISCONNECTED) {
    throw new MongoError('connection in unlawful state ' + this.state);
  }

  var self = this;
  // Transition to connecting state
  stateTransition(this, CONNECTING);
  // Create an array of the arguments
  var args = Array.prototype.slice.call(arguments, 0);
  // Create a connection
  var connection = new Connection(messageHandler(self), this.options);
  // Add to list of connections
  this.connectingConnections.push(connection);
  // Add listeners to the connection
  connection.once('connect', function(connection) {
    if(self.state == DESTROYED || self.state == DESTROYING) return self.destroy();

    // If we are in a topology, delegate the auth to it
    // This is to avoid issues where we would auth against an
    // arbiter
    if(self.options.inTopology) {
      // Set connected mode
      stateTransition(self, CONNECTED);

      // Move the active connection
      moveConnectionBetween(connection, self.connectingConnections, self.availableConnections);

      // Emit the connect event
      return self.emit('connect', self);
    }

    // Apply any store credentials
    reauthenticate(self, connection, function(err) {
      if(self.state == DESTROYED || self.state == DESTROYING) return self.destroy();

      // We have an error emit it
      if(err) {
        // Destroy the pool
        self.destroy();
        // Emit the error
        return self.emit('error', err);
      }

      // Authenticate
      authenticate(self, args, connection, function(err) {
        if(self.state == DESTROYED || self.state == DESTROYING) return self.destroy();

        // We have an error emit it
        if(err) {
          // Destroy the pool
          self.destroy();
          // Emit the error
          return self.emit('error', err);
        }
        // Set connected mode
        stateTransition(self, CONNECTED);

        // Move the active connection
        moveConnectionBetween(connection, self.connectingConnections, self.availableConnections);

        // Emit the connect event
        self.emit('connect', self);
      });
    });
  });

  // Add error handlers
  connection.once('error', connectionFailureHandler(this, 'error'));
  connection.once('close', connectionFailureHandler(this, 'close'));
  connection.once('timeout', connectionFailureHandler(this, 'timeout'));
  connection.once('parseError', connectionFailureHandler(this, 'parseError'));

  try {
    connection.connect();
  } catch(err) {
    // SSL or something threw on connect
    process.nextTick(function() {
      self.emit('error', err);
    });
  }
}

/**
 * Authenticate using a specified mechanism
 * @method
 * @param {string} mechanism The Auth mechanism we are invoking
 * @param {string} db The db we are invoking the mechanism against
 * @param {...object} param Parameters for the specific mechanism
 * @param {authResultCallback} callback A callback function
 */
Pool.prototype.auth = function(mechanism) {
  var self = this;
  var args = Array.prototype.slice.call(arguments, 0);
  var callback = args.pop();

  // If we don't have the mechanism fail
  if(self.authProviders[mechanism] == null && mechanism != 'default') {
    throw new MongoError(f("auth provider %s does not exist", mechanism));
  }

  // Signal that we are authenticating a new set of credentials
  this.authenticating = true;
  this.authenticatingTimestamp = new Date().getTime();

  // Authenticate all live connections
  function authenticateLiveConnections(self, args, cb) {
    // Get the current viable connections
    var connections = self.allConnections();
    // Allow nothing else to use the connections while we authenticate them
    self.availableConnections = [];
    self.inUseConnections = [];
    self.connectingConnections = [];

    var connectionsCount = connections.length;
    var error = null;
    // No connections available, return
    if(connectionsCount == 0) {
      self.authenticating = false;
      return callback(null);
    }

    // Authenticate the connections
    for(var i = 0; i < connections.length; i++) {
      authenticate(self, args, connections[i], function(err) {
        connectionsCount = connectionsCount - 1;

        // Store the error
        if(err) error = err;

        // Processed all connections
        if(connectionsCount == 0) {
          // Auth finished
          self.authenticating = false;
          // Add the connections back to available connections
          self.availableConnections = self.availableConnections.concat(connections);
          // We had an error, return it
          if(error) {
            // Log the error
            if(self.logger.isError()) {
              self.logger.error(f('[%s] failed to authenticate against server %s:%s'
                , self.id, self.options.host, self.options.port));
            }

            return cb(error);
          }
          cb(null);
        }
      });
    }
  }

  // Wait for a logout in process to happen
  function waitForLogout(self, cb) {
    if(!self.loggingout) return cb();
    setTimeout(function() {
      waitForLogout(self, cb);
    }, 1)
  }

  // Wait for loggout to finish
  waitForLogout(self, function() {
    // Authenticate all live connections
    authenticateLiveConnections(self, args, function(err) {
      // Credentials correctly stored in auth provider if successful
      // Any new connections will now reauthenticate correctly
      self.authenticating = false;
      // Return after authentication connections
      callback(err);
    });
  });
}

/**
 * Logout all users against a database
 * @method
 * @param {string} dbName The database name
 * @param {authResultCallback} callback A callback function
 */
Pool.prototype.logout = function(dbName, callback) {
  var self = this;
  if(typeof dbName != 'string') {
    throw new MongoError('logout method requires a db name as first argument');
  }

  if(typeof callback != 'function') {
    throw new MongoError('logout method requires a callback');
  }

  // Indicate logout in process
  this.loggingout = true;

  // Get all relevant connections
  var connections = self.availableConnections.concat(self.inUseConnections);
  var count = connections.length;
  // Store any error
  var error = null;

  // Send logout command over all the connections
  for(var i = 0; i < connections.length; i++) {
    write(self)(connections[i], new Query(this.options.bson
      , f('%s.$cmd', dbName)
      , {logout:1}, {numberToSkip: 0, numberToReturn: 1}), function(err) {
      count = count - 1;
      if(err) error = err;

      if(count == 0) {
        self.loggingout = false;
        callback(error);
      }
    });
  }
}

/**
 * Unref the pool
 * @method
 */
Pool.prototype.unref = function() {
  // Get all the known connections
  var connections = this.availableConnections
    .concat(this.inUseConnections)
    .concat(this.connectingConnections);
  connections.forEach(function(c) {
    c.unref();
  });
}

// Events
var events = ['error', 'close', 'timeout', 'parseError', 'connect'];

// Destroy the connections
function destroy(self, connections) {
  // Destroy all connections
  connections.forEach(function(c) {
    // Remove all listeners
    for(var i = 0; i < events.length; i++) {
      c.removeAllListeners(events[i]);
    }
    // Destroy connection
    c.destroy();
  });

  // Zero out all connections
  self.inUseConnections = [];
  self.availableConnections = [];
  self.nonAuthenticatedConnections = [];
  self.connectingConnections = [];

  // Set state to destroyed
  stateTransition(self, DESTROYED);
}

/**
 * Destroy pool
 * @method
 */
Pool.prototype.destroy = function(force) {
  var self = this;
  // Do not try again if the pool is already dead
  if(this.state == DESTROYED || self.state == DESTROYING) return;
  // Set state to destroyed
  stateTransition(this, DESTROYING);

  // Are we force closing
  if(force) {
    // Get all the known connections
    var connections = self.availableConnections
      .concat(self.inUseConnections)
      .concat(self.nonAuthenticatedConnections)
      .concat(self.connectingConnections);

    // Flush any remaining work items with
    // an error
    while(self.queue.length > 0) {
      var workItem = self.queue.shift();
      if(typeof workItem.cb == 'function') {
        workItem.cb(new MongoError('Pool was force destroyed'));
      }
    }

    // Destroy the topology
    return destroy(self, connections);
  }

  // Clear out the reconnect if set
  if (this.reconnectId) {
    clearTimeout(this.reconnectId);
  }

  // If we have a reconnect connection running, close
  // immediately
  if (this.reconnectConnection) {
    this.reconnectConnection.destroy();
  }

  // Wait for the operations to drain before we close the pool
  function checkStatus() {
    flushMonitoringOperations(self.queue);

    if(self.queue.length == 0) {
      // Get all the known connections
      var connections = self.availableConnections
        .concat(self.inUseConnections)
        .concat(self.nonAuthenticatedConnections)
        .concat(self.connectingConnections);

      // Check if we have any in flight operations
      for(var i = 0; i < connections.length; i++) {
        // There is an operation still in flight, reschedule a
        // check waiting for it to drain
        if(connections[i].workItems.length > 0) {
          return setTimeout(checkStatus, 1);
        }
      }

      destroy(self, connections);
    // } else if (self.queue.length > 0 && !this.reconnectId) {

    } else {
      // Ensure we empty the queue
      _execute(self)();
      // Set timeout
      setTimeout(checkStatus, 1);
    }
  }

  // Initiate drain of operations
  checkStatus();
}

/**
 * Write a message to MongoDB
 * @method
 * @return {Connection}
 */
Pool.prototype.write = function(commands, options, cb) {
  var self = this;
  // Ensure we have a callback
  if(typeof options == 'function') {
    cb = options;
  }

  // Always have options
  options = options || {};

  // Pool was destroyed error out
  if(this.state == DESTROYED || this.state == DESTROYING) {
    // Callback with an error
    if(cb) {
      try {
        cb(new MongoError('pool destroyed'));
      } catch(err) {
        process.nextTick(function() {
          throw err;
        });
      }
    }

    return;
  }

  if(this.options.domainsEnabled
    && process.domain && typeof cb === "function") {
    // if we have a domain bind to it
    var oldCb = cb;
    cb = process.domain.bind(function() {
      // v8 - argumentsToArray one-liner
      var args = new Array(arguments.length); for(var i = 0; i < arguments.length; i++) { args[i] = arguments[i]; }
      // bounce off event loop so domain switch takes place
      process.nextTick(function() {
        oldCb.apply(null, args);
      });
    });
  }

  // Do we have an operation
  var operation = {
    cb: cb, raw: false, promoteLongs: true, promoteValues: true, promoteBuffers: false, fullResult: false
  };

  var buffer = null

  if(Array.isArray(commands)) {
    buffer = [];

    for(var i = 0; i < commands.length; i++) {
      buffer.push(commands[i].toBin());
    }

    // Get the requestId
    operation.requestId = commands[commands.length - 1].requestId;
  } else {
    operation.requestId = commands.requestId;
    buffer = commands.toBin();
  }

  // Set the buffers
  operation.buffer = buffer;

  // Set the options for the parsing
  operation.promoteLongs = typeof options.promoteLongs == 'boolean' ? options.promoteLongs : true;
  operation.promoteValues = typeof options.promoteValues == 'boolean' ? options.promoteValues : true;
  operation.promoteBuffers = typeof options.promoteBuffers == 'boolean' ? options.promoteBuffers : false;
  operation.raw = typeof options.raw == 'boolean' ? options.raw : false;
  operation.immediateRelease = typeof options.immediateRelease == 'boolean' ? options.immediateRelease : false;
  operation.documentsReturnedIn = options.documentsReturnedIn;
  operation.command = typeof options.command == 'boolean' ? options.command : false;
  operation.fullResult = typeof options.fullResult == 'boolean' ? options.fullResult : false;
  operation.noResponse = typeof options.noResponse == 'boolean' ? options.noResponse : false;
  // operation.requestId = options.requestId;

  // Optional per operation socketTimeout
  operation.socketTimeout = options.socketTimeout;
  operation.monitoring = options.monitoring;
  // Custom socket Timeout
  if(options.socketTimeout) {
    operation.socketTimeout = options.socketTimeout;
  }

  // We need to have a callback function unless the message returns no response
  if(!(typeof cb == 'function') && !options.noResponse) {
    throw new MongoError('write method must provide a callback');
  }

  // If we have a monitoring operation schedule as the very first operation
  // Otherwise add to back of queue
  if(options.monitoring) {
    this.queue.unshift(operation);
  } else {
    this.queue.push(operation);
  }

  // Attempt to execute the operation
  if(!self.executing) {
    process.nextTick(function() {
      _execute(self)();
    });
  }
}

// Remove connection method
function remove(connection, connections) {
  for(var i = 0; i < connections.length; i++) {
    if(connections[i] === connection) {
      connections.splice(i, 1);
      return true;
    }
  }
}

function removeConnection(self, connection) {
  if(remove(connection, self.availableConnections)) return;
  if(remove(connection, self.inUseConnections)) return;
  if(remove(connection, self.connectingConnections)) return;
  if(remove(connection, self.nonAuthenticatedConnections)) return;
}

// All event handlers
var handlers = ["close", "message", "error", "timeout", "parseError", "connect"];

function _createConnection(self) {
  if(self.state == DESTROYED || self.state == DESTROYING) {
    return;
  }
  var connection = new Connection(messageHandler(self), self.options);

  // Push the connection
  self.connectingConnections.push(connection);

  // Handle any errors
  var tempErrorHandler = function(_connection) {
    return function() {
      // Destroy the connection
      _connection.destroy();
      // Remove the connection from the connectingConnections list
      removeConnection(self, _connection);
      // Start reconnection attempts
      if(!self.reconnectId && self.options.reconnect) {
        self.reconnectId = setTimeout(attemptReconnect(self), self.options.reconnectInterval);
      }
    }
  }

  // Handle successful connection
  var tempConnectHandler = function(_connection) {
    return function() {
      // Destroyed state return
      if(self.state == DESTROYED || self.state == DESTROYING) {
        // Remove the connection from the list
        removeConnection(self, _connection);
        return _connection.destroy();
      }

      // Destroy all event emitters
      handlers.forEach(function(e) {
        _connection.removeAllListeners(e);
      });

      // Add the final handlers
      _connection.once('close', connectionFailureHandler(self, 'close'));
      _connection.once('error', connectionFailureHandler(self, 'error'));
      _connection.once('timeout', connectionFailureHandler(self, 'timeout'));
      _connection.once('parseError', connectionFailureHandler(self, 'parseError'));

      // Signal
      reauthenticate(self, _connection, function(err) {
        if(self.state == DESTROYED || self.state == DESTROYING) {
          return _connection.destroy();
        }
        // Remove the connection from the connectingConnections list
        removeConnection(self, _connection);

        // Handle error
        if(err) {
          return _connection.destroy();
        }

        // If we are c at the moment
        // Do not automatially put in available connections
        // As we need to apply the credentials first
        if(self.authenticating) {
          self.nonAuthenticatedConnections.push(_connection);
        } else {
          // Push to available
          self.availableConnections.push(_connection);
          // Execute any work waiting
          _execute(self)();
        }
      });
    }
  }

  // Add all handlers
  connection.once('close', tempErrorHandler(connection));
  connection.once('error', tempErrorHandler(connection));
  connection.once('timeout', tempErrorHandler(connection));
  connection.once('parseError', tempErrorHandler(connection));
  connection.once('connect', tempConnectHandler(connection));

  // Start connection
  connection.connect();
}

function flushMonitoringOperations(queue) {
  for(var i = 0; i < queue.length; i++) {
    if(queue[i].monitoring) {
      var workItem = queue[i];
      queue.splice(i, 1);
      workItem.cb(new MongoError({ message: 'no connection available for monitoring', driver:true }));
    }
  }
}

function _execute(self) {
  return function() {
    if(self.state == DESTROYED) return;
    // Already executing, skip
    if(self.executing) return;
    // Set pool as executing
    self.executing = true;

    // Wait for auth to clear before continuing
    function waitForAuth(cb) {
      if(!self.authenticating) return cb();
      // Wait for a milisecond and try again
      setTimeout(function() {
        waitForAuth(cb);
      }, 1);
    }

    // Block on any auth in process
    waitForAuth(function() {
      // New pool connections are in progress, wait them to finish
      // before executing any more operation to ensure distribution of
      // operations
      if(self.connectingConnections.length > 0) {
        return;
      }

      // As long as we have available connections
      while(true) {
        // Total availble connections
        var totalConnections = self.availableConnections.length
          + self.connectingConnections.length
          + self.inUseConnections.length;

        // No available connections available, flush any monitoring ops
        if(self.availableConnections.length == 0) {
          // Flush any monitoring operations
          flushMonitoringOperations(self.queue);
          break;
        }

        // No queue break
        if(self.queue.length == 0) {
          break;
        }

        // Get a connection
        var connection = null;

        // Locate all connections that have no work
        var connections = [];
        // Get a list of all connections
        for(var i = 0; i < self.availableConnections.length; i++) {
          if(self.availableConnections[i].workItems.length == 0) {
            connections.push(self.availableConnections[i]);
          }
        }

        // No connection found that has no work on it, just pick one for pipelining
        if(connections.length == 0) {
          connection = self.availableConnections[self.connectionIndex++ % self.availableConnections.length];
        } else {
          connection = connections[self.connectionIndex++ % connections.length];
        }

        // Is the connection connected
        if(connection.isConnected()) {
          // Get the next work item
          var workItem = self.queue.shift();

          // If we are monitoring we need to use a connection that is not
          // running another operation to avoid socket timeout changes
          // affecting an existing operation
          if (workItem.monitoring) {
            var foundValidConnection = false;

            for (var i = 0; i < self.availableConnections.length; i++) {
              // If the connection is connected
              // And there are no pending workItems on it
              // Then we can safely use it for monitoring.
              if(self.availableConnections[i].isConnected()
                && self.availableConnections[i].workItems.length == 0) {
                  foundValidConnection = true;
                  connection = self.availableConnections[i];
                  break;
                }
            }

            // No safe connection found, attempt to grow the connections
            // if possible and break from the loop
            if(!foundValidConnection) {
              // Put workItem back on the queue
              self.queue.unshift(workItem);

              // Attempt to grow the pool if it's not yet maxsize
              if(totalConnections < self.options.size
                && self.queue.length > 0) {
                // Create a new connection
                _createConnection(self);
              }

              // Re-execute the operation
              setTimeout(function() {
                _execute(self)();
              }, 10);

              break;
            }
          }

          // Don't execute operation until we have a full pool
          if(totalConnections < self.options.size) {
            // Connection has work items, then put it back on the queue
            // and create a new connection
            if(connection.workItems.length > 0) {
              // Lets put the workItem back on the list
              self.queue.unshift(workItem);
              // Create a new connection
              _createConnection(self);
              // Break from the loop
              break;
            }
          }

          // Get actual binary commands
          var buffer = workItem.buffer;

          // Set current status of authentication process
          workItem.authenticating = self.authenticating;
          workItem.authenticatingTimestamp = self.authenticatingTimestamp;

          // If we are monitoring take the connection of the availableConnections
          if (workItem.monitoring) {
            moveConnectionBetween(connection, self.availableConnections, self.inUseConnections);
          }

          // Track the executing commands on the mongo server
          // as long as there is an expected response
          if (! workItem.noResponse) {
            connection.workItems.push(workItem);
          }

          // We have a custom socketTimeout
          if(!workItem.immediateRelease && typeof workItem.socketTimeout == 'number') {
            connection.setSocketTimeout(workItem.socketTimeout);
          }

          // Capture if write was successful
          var writeSuccessful = true;

          // Put operation on the wire
          if(Array.isArray(buffer)) {
            for(var i = 0; i < buffer.length; i++) {
              writeSuccessful = connection.write(buffer[i])
            }
          } else {
            writeSuccessful = connection.write(buffer);
          }

          if(writeSuccessful && workItem.immediateRelease && self.authenticating) {
            removeConnection(self, connection);
            self.nonAuthenticatedConnections.push(connection);
          } else if(writeSuccessful === false) {
            // If write not successful put back on queue
            self.queue.unshift(workItem);
            // Remove the disconnected connection
            removeConnection(self, connection);
            // Flush any monitoring operations in the queue, failing fast
            flushMonitoringOperations(self.queue);
          }
        } else {
          // Remove the disconnected connection
          removeConnection(self, connection);
          // Flush any monitoring operations in the queue, failing fast
          flushMonitoringOperations(self.queue);
        }
      }
    });

    self.executing = false;
  }
}

// Make execution loop available for testing
Pool._execute = _execute;

/**
 * A server connect event, used to verify that the connection is up and running
 *
 * @event Pool#connect
 * @type {Pool}
 */

/**
 * A server reconnect event, used to verify that pool reconnected.
 *
 * @event Pool#reconnect
 * @type {Pool}
 */

/**
 * The server connection closed, all pool connections closed
 *
 * @event Pool#close
 * @type {Pool}
 */

/**
 * The server connection caused an error, all pool connections closed
 *
 * @event Pool#error
 * @type {Pool}
 */

/**
 * The server connection timed out, all pool connections closed
 *
 * @event Pool#timeout
 * @type {Pool}
 */

/**
 * The driver experienced an invalid message, all pool connections closed
 *
 * @event Pool#parseError
 * @type {Pool}
 */

/**
 * The driver attempted to reconnect
 *
 * @event Pool#attemptReconnect
 * @type {Pool}
 */

/**
 * The driver exhausted all reconnect attempts
 *
 * @event Pool#reconnectFailed
 * @type {Pool}
 */

module.exports = Pool;
