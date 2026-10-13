"use strict"

var inherits = require('util').inherits,
  f = require('util').format,
  EventEmitter = require('events').EventEmitter,
  BasicCursor = require('../cursor'),
  Logger = require('../connection/logger'),
  retrieveBSON = require('../connection/utils').retrieveBSON,
  MongoError = require('../error'),
  Server = require('./server'),
  assign = require('../utils').assign,
  clone = require('./shared').clone,
  sdam = require('./shared'),
  diff = require('./shared').diff,
  cloneOptions = require('./shared').cloneOptions,
  createClientInfo = require('./shared').createClientInfo;

var BSON = retrieveBSON();

/**
 * @fileOverview The **Mongos** class is a class that represents a Mongos Proxy topology and is
 * used to construct connections.
 *
 * @example
 * var Mongos = require('mongodb-core').Mongos
 *   , ReadPreference = require('mongodb-core').ReadPreference
 *   , assert = require('assert');
 *
 * var server = new Mongos([{host: 'localhost', port: 30000}]);
 * // Wait for the connection event
 * server.on('connect', function(server) {
 *   server.destroy();
 * });
 *
 * // Start connecting
 * server.connect();
 */

var MongoCR = require('../auth/mongocr')
  , X509 = require('../auth/x509')
  , Plain = require('../auth/plain')
  , GSSAPI = require('../auth/gssapi')
  , SSPI = require('../auth/sspi')
  , ScramSHA1 = require('../auth/scram');

//
// States
var DISCONNECTED = 'disconnected';
var CONNECTING = 'connecting';
var CONNECTED = 'connected';
var UNREFERENCED = 'unreferenced';
var DESTROYED = 'destroyed';

function stateTransition(self, newState) {
  var legalTransitions = {
    'disconnected': [CONNECTING, DESTROYED, DISCONNECTED],
    'connecting': [CONNECTING, DESTROYED, CONNECTED, DISCONNECTED],
    'connected': [CONNECTED, DISCONNECTED, DESTROYED, UNREFERENCED],
    'unreferenced': [UNREFERENCED, DESTROYED],
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

//
// ReplSet instance id
var id = 1;
var handlers = ['connect', 'close', 'error', 'timeout', 'parseError'];

/**
 * Creates a new Mongos instance
 * @class
 * @param {array} seedlist A list of seeds for the replicaset
 * @param {number} [options.haInterval=5000] The High availability period for replicaset inquiry
 * @param {Cursor} [options.cursorFactory=Cursor] The cursor factory class used for all query cursors
 * @param {number} [options.size=5] Server connection pool size
 * @param {boolean} [options.keepAlive=true] TCP Connection keep alive enabled
 * @param {number} [options.keepAliveInitialDelay=0] Initial delay before TCP keep alive enabled
 * @param {number} [options.localThresholdMS=15] Cutoff latency point in MS for MongoS proxy selection
 * @param {boolean} [options.noDelay=true] TCP Connection no delay
 * @param {number} [options.connectionTimeout=1000] TCP Connection timeout setting
 * @param {number} [options.socketTimeout=0] TCP Socket timeout setting
 * @param {boolean} [options.singleBufferSerializtion=true] Serialize into single buffer, trade of peak memory for serialization speed
 * @param {boolean} [options.ssl=false] Use SSL for connection
 * @param {boolean|function} [options.checkServerIdentity=true] Ensure we check server identify during SSL, set to false to disable checking. Only works for Node 0.12.x or higher. You can pass in a boolean or your own checkServerIdentity override function.
 * @param {Buffer} [options.ca] SSL Certificate store binary buffer
 * @param {Buffer} [options.crl] SSL Certificate revocation store binary buffer
 * @param {Buffer} [options.cert] SSL Certificate binary buffer
 * @param {Buffer} [options.key] SSL Key file binary buffer
 * @param {string} [options.passphrase] SSL Certificate pass phrase
 * @param {string} [options.servername=null] String containing the server name requested via TLS SNI.
 * @param {boolean} [options.rejectUnauthorized=true] Reject unauthorized server certificates
 * @param {boolean} [options.promoteLongs=true] Convert Long values from the db into Numbers if they fit into 53 bits
 * @param {boolean} [options.promoteValues=true] Promotes BSON values to native types where possible, set to false to only receive wrapper types.
 * @param {boolean} [options.promoteBuffers=false] Promotes Binary BSON values to native Node Buffers.
 * @param {boolean} [options.domainsEnabled=false] Enable the wrapping of the callback in the current domain, disabled by default to avoid perf hit.
 * @return {Mongos} A cursor instance
 * @fires Mongos#connect
 * @fires Mongos#reconnect
 * @fires Mongos#joined
 * @fires Mongos#left
 * @fires Mongos#failed
 * @fires Mongos#fullsetup
 * @fires Mongos#all
 * @fires Mongos#serverHeartbeatStarted
 * @fires Mongos#serverHeartbeatSucceeded
 * @fires Mongos#serverHeartbeatFailed
 * @fires Mongos#topologyOpening
 * @fires Mongos#topologyClosed
 * @fires Mongos#topologyDescriptionChanged
 * @property {string} type the topology type.
 * @property {string} parserType the parser type used (c++ or js).
 */
var Mongos = function(seedlist, options) {
  options = options || {};

  // Get replSet Id
  this.id = id++;

  // Internal state
  this.s = {
    options: assign({}, options),
    // BSON instance
    bson: options.bson || new BSON([BSON.Binary, BSON.Code, BSON.DBRef, BSON.Decimal128,
      BSON.Double, BSON.Int32, BSON.Long, BSON.Map, BSON.MaxKey, BSON.MinKey,
      BSON.ObjectId, BSON.BSONRegExp, BSON.Symbol, BSON.Timestamp]),
    // Factory overrides
    Cursor: options.cursorFactory || BasicCursor,
    // Logger instance
    logger: Logger('Mongos', options),
    // Seedlist
    seedlist: seedlist,
    // Ha interval
    haInterval: options.haInterval ? options.haInterval : 10000,
    // Disconnect handler
    disconnectHandler: options.disconnectHandler,
    // Server selection index
    index: 0,
    // Connect function options passed in
    connectOptions: {},
    // Are we running in debug mode
    debug: typeof options.debug == 'boolean' ? options.debug : false,
    // localThresholdMS
    localThresholdMS: options.localThresholdMS || 15,
    // Client info
    clientInfo: createClientInfo(options),
    // Authentication context
    authenticationContexts: [],
  }

  // Set the client info
  this.s.options.clientInfo = createClientInfo(options);

  // Log info warning if the socketTimeout < haInterval as it will cause
  // a lot of recycled connections to happen.
  if(this.s.logger.isWarn()
    && this.s.options.socketTimeout != 0
    && this.s.options.socketTimeout < this.s.haInterval) {
      this.s.logger.warn(f('warning socketTimeout %s is less than haInterval %s. This might cause unnecessary server reconnections due to socket timeouts'
        , this.s.options.socketTimeout, this.s.haInterval));
  }

  // All the authProviders
  this.authProviders = options.authProviders || {
      'mongocr': new MongoCR(this.s.bson), 'x509': new X509(this.s.bson)
    , 'plain': new Plain(this.s.bson), 'gssapi': new GSSAPI(this.s.bson)
    , 'sspi': new SSPI(this.s.bson), 'scram-sha-1': new ScramSHA1(this.s.bson)
  }

  // Disconnected state
  this.state = DISCONNECTED;

  // Current proxies we are connecting to
  this.connectingProxies = [];
  // Currently connected proxies
  this.connectedProxies = [];
  // Disconnected proxies
  this.disconnectedProxies = [];
  // Are we authenticating
  this.authenticating = false;
  // Index of proxy to run operations against
  this.index = 0;
  // High availability timeout id
  this.haTimeoutId = null;
  // Last ismaster
  this.ismaster = null;

  // Description of the Replicaset
  this.topologyDescription = {
    "topologyType": "Unknown", "servers": []
  };

  // Add event listener
  EventEmitter.call(this);
}

inherits(Mongos, EventEmitter);

Object.defineProperty(Mongos.prototype, 'type', {
  enumerable:true, get: function() { return 'mongos'; }
});

Object.defineProperty(Mongos.prototype, 'parserType', {
  enumerable:true, get: function() {
    return BSON.native ? "c++" : "js";
  }
});

/**
 * Emit event if it exists
 * @method
 */
function emitSDAMEvent(self, event, description) {
  if(self.listeners(event).length > 0) {
    self.emit(event, description);
  }
}

/**
 * Initiate server connect
 * @method
 * @param {array} [options.auth=null] Array of auth options to apply on connect
 */
Mongos.prototype.connect = function(options) {
  var self = this;
  // Add any connect level options to the internal state
  this.s.connectOptions = options || {};
  // Set connecting state
  stateTransition(this, CONNECTING);
  // Create server instances
  var servers = this.s.seedlist.map(function(x) {
    return new Server(assign({}, self.s.options, x, {
      authProviders: self.authProviders, reconnect:false, monitoring:false, inTopology: true
    }, {
      clientInfo: clone(self.s.clientInfo)
    }));
  });

  servers.forEach(function(server) {
    server.on('serverDescriptionChanged', function(event) { self.emit('serverDescriptionChanged', event); });
  });

  // Emit the topology opening event
  emitSDAMEvent(this, 'topologyOpening', { topologyId: this.id });

  // Start all server connections
  connectProxies(self, servers);
}

function handleEvent(self) {
  return function() {
    if(self.state == DESTROYED) return;
    // Move to list of disconnectedProxies
    moveServerFrom(self.connectedProxies, self.disconnectedProxies, this);
    // Emit the initial topology
    emitTopologyDescriptionChanged(self);
    // Emit the left signal
    self.emit('left', 'mongos', this);
    // Emit the sdam event
    self.emit('serverClosed', {
      topologyId: self.id,
      address: this.name
    });
  }
}

function handleInitialConnectEvent(self, event) {
  return function() {
    var _this = this;

    // Destroy the instance
    if(self.state == DESTROYED) {
      // Emit the initial topology
      emitTopologyDescriptionChanged(self);
      // Move from connectingProxies
      moveServerFrom(self.connectingProxies, self.disconnectedProxies, this);
      return this.destroy();
    }

    // Check the type of server
    if(event == 'connect') {
      // Do we have authentication contexts that need to be applied
      applyAuthenticationContexts(self, _this, function() {
        // Get last known ismaster
        self.ismaster = _this.lastIsMaster();

        // Is this not a proxy, remove t
        if(self.ismaster.msg == 'isdbgrid') {
          // Add to the connectd list
          for(var i = 0; i < self.connectedProxies.length; i++) {
            if(self.connectedProxies[i].name == _this.name) {
              // Move from connectingProxies
              moveServerFrom(self.connectingProxies, self.disconnectedProxies, _this);
              // Emit the initial topology
              emitTopologyDescriptionChanged(self);
              _this.destroy();
              return self.emit('failed', _this);
            }
          }

          // Remove the handlers
          for(i = 0; i < handlers.length; i++) {
            _this.removeAllListeners(handlers[i]);
          }

          // Add stable state handlers
          _this.on('error', handleEvent(self, 'error'));
          _this.on('close', handleEvent(self, 'close'));
          _this.on('timeout', handleEvent(self, 'timeout'));
          _this.on('parseError', handleEvent(self, 'parseError'));

          // Move from connecting proxies connected
          moveServerFrom(self.connectingProxies, self.connectedProxies, _this);
          // Emit the joined event
          self.emit('joined', 'mongos', _this);
        } else {

          // Print warning if we did not find a mongos proxy
          if(self.s.logger.isWarn()) {
            var message = 'expected mongos proxy, but found replicaset member mongod for server %s';
            // We have a standalone server
            if(!self.ismaster.hosts) {
              message = 'expected mongos proxy, but found standalone mongod for server %s';
            }

            self.s.logger.warn(f(message, _this.name));
          }

          // This is not a mongos proxy, remove it completely
          removeProxyFrom(self.connectingProxies, _this);
          // Emit the left event
          self.emit('left', 'server', _this);
          // Emit failed event
          self.emit('failed', _this);
        }
      });
    } else {
      moveServerFrom(self.connectingProxies, self.disconnectedProxies, this);
      // Emit the left event
      self.emit('left', 'mongos', this);
      // Emit failed event
      self.emit('failed', this);
    }

    // Emit the initial topology
    emitTopologyDescriptionChanged(self);

    // Trigger topologyMonitor
    if(self.connectingProxies.length == 0) {
      // Emit connected if we are connected
      if(self.connectedProxies.length > 0) {
        // Set the state to connected
        stateTransition(self, CONNECTED);
        // Emit the connect event
        self.emit('connect', self);
        self.emit('fullsetup', self);
        self.emit('all', self);
      } else if(self.disconnectedProxies.length == 0) {
        // Print warning if we did not find a mongos proxy
        if(self.s.logger.isWarn()) {
          self.s.logger.warn(f('no mongos proxies found in seed list, did you mean to connect to a replicaset'));
        }

        // Emit the error that no proxies were found
        return self.emit('error', new MongoError('no mongos proxies found in seed list'));
      }

      // Topology monitor
      topologyMonitor(self, {firstConnect:true});
    }
  };
}

function connectProxies(self, servers) {
  // Update connectingProxies
  self.connectingProxies = self.connectingProxies.concat(servers);

  // Index used to interleaf the server connects, avoiding
  // runtime issues on io constrained vm's
  var timeoutInterval = 0;

  function connect(server, timeoutInterval) {
    setTimeout(function() {
      // Emit opening server event
      self.emit('serverOpening', {
        topologyId: self.id,
        address: server.name
      });

      // Emit the initial topology
      emitTopologyDescriptionChanged(self);

      // Add event handlers
      server.once('close', handleInitialConnectEvent(self, 'close'));
      server.once('timeout', handleInitialConnectEvent(self, 'timeout'));
      server.once('parseError', handleInitialConnectEvent(self, 'parseError'));
      server.once('error', handleInitialConnectEvent(self, 'error'));
      server.once('connect', handleInitialConnectEvent(self, 'connect'));
      // Start connection
      server.connect(self.s.connectOptions);
    }, timeoutInterval);
  }
  // Start all the servers
  while(servers.length > 0) {
    connect(servers.shift(), timeoutInterval++);
  }
}

function pickProxy(self) {
  // Get the currently connected Proxies
  var connectedProxies = self.connectedProxies.slice(0);

  // Set lower bound
  var lowerBoundLatency = Number.MAX_VALUE;

  // Determine the lower bound for the Proxies
  for(var i = 0; i < connectedProxies.length; i++) {
    if(connectedProxies[i].lastIsMasterMS < lowerBoundLatency) {
      lowerBoundLatency = connectedProxies[i].lastIsMasterMS;
    }
  }

  // Filter out the possible servers
  connectedProxies = connectedProxies.filter(function(server) {
    if((server.lastIsMasterMS <= (lowerBoundLatency + self.s.localThresholdMS))
      && server.isConnected()) {
      return true;
    }
  });

  // We have no connectedProxies pick first of the connected ones
  if(connectedProxies.length == 0) {
    return self.connectedProxies[0];
  }

  // Get proxy
  var proxy = connectedProxies[self.index % connectedProxies.length];
  // Update the index
  self.index = (self.index + 1) % connectedProxies.length;
  // Return the proxy
  return proxy;
}

function moveServerFrom(from, to, proxy) {
  for(var i = 0; i < from.length; i++) {
    if(from[i].name == proxy.name) {
      from.splice(i, 1);
    }
  }

  for(i = 0; i < to.length; i++) {
    if(to[i].name == proxy.name) {
      to.splice(i, 1);
    }
  }

  to.push(proxy);
}

function removeProxyFrom(from, proxy) {
  for(var i = 0; i < from.length; i++) {
    if(from[i].name == proxy.name) {
      from.splice(i, 1);
    }
  }
}

function reconnectProxies(self, proxies, callback) {
  // Count lefts
  var count = proxies.length;

  // Handle events
  var _handleEvent = function(self, event) {
    return function() {
      var _self = this;
      count = count - 1;

      // Destroyed
      if(self.state == DESTROYED || self.state == UNREFERENCED) {
        moveServerFrom(self.connectingProxies, self.disconnectedProxies, _self);
        // Return destroy
        return this.destroy();
      }

      if(event == 'connect' && !self.authenticating) {
        // Do we have authentication contexts that need to be applied
        applyAuthenticationContexts(self, _self, function() {
          // Destroyed
          if(self.state == DESTROYED || self.state == UNREFERENCED) {
            moveServerFrom(self.connectingProxies, self.disconnectedProxies, _self);
            return _self.destroy();
          }

          // Remove the handlers
          for(var i = 0; i < handlers.length; i++) {
            _self.removeAllListeners(handlers[i]);
          }

          // Add stable state handlers
          _self.on('error', handleEvent(self, 'error'));
          _self.on('close', handleEvent(self, 'close'));
          _self.on('timeout', handleEvent(self, 'timeout'));
          _self.on('parseError', handleEvent(self, 'parseError'));

          // Move to the connected servers
          moveServerFrom(self.disconnectedProxies, self.connectedProxies, _self);
          // Emit topology Change
          emitTopologyDescriptionChanged(self);
          // Emit joined event
          self.emit('joined', 'mongos', _self);
        });
      } else if(event == 'connect' && self.authenticating) {
        // Move from connectingProxies
        moveServerFrom(self.connectingProxies, self.disconnectedProxies, _self);
        this.destroy();
      }

      // Are we done finish up callback
      if(count == 0) {
        callback();
      }
    }
  }

  // No new servers
  if(count == 0) {
    return callback();
  }

  // Execute method
  function execute(_server, i) {
    setTimeout(function() {
      // Destroyed
      if(self.state == DESTROYED || self.state == UNREFERENCED) {
        return;
      }

      // Create a new server instance
      var server = new Server(assign({}, self.s.options, {
        host: _server.name.split(':')[0],
        port: parseInt(_server.name.split(':')[1], 10)
      }, {
        authProviders: self.authProviders, reconnect:false, monitoring: false, inTopology: true
      }, {
        clientInfo: clone(self.s.clientInfo)
      }));

      // Relay the server description change
      server.on('serverDescriptionChanged', function(event) { self.emit('serverDescriptionChanged', event); });

      // Emit opening server event
      self.emit('serverOpening', {
        topologyId: server.s.topologyId != -1 ? server.s.topologyId : self.id,
        address: server.name
      });

      // Add temp handlers
      server.once('connect', _handleEvent(self, 'connect'));
      server.once('close', _handleEvent(self, 'close'));
      server.once('timeout', _handleEvent(self, 'timeout'));
      server.once('error', _handleEvent(self, 'error'));
      server.once('parseError', _handleEvent(self, 'parseError'));

      // Connect to proxy
      server.connect(self.s.connectOptions);
    }, i);
  }

  // Create new instances
  for(var i = 0; i < proxies.length; i++) {
    execute(proxies[i], i);
  }
}

function applyAuthenticationContexts(self, server, callback) {
  if(self.s.authenticationContexts.length == 0) {
    return callback();
  }

  // Copy contexts to ensure no modificiation in the middle of
  // auth process.
  var authContexts = self.s.authenticationContexts.slice(0);

  // Apply one of the contexts
  function applyAuth(authContexts, server, callback) {
    if(authContexts.length == 0) return callback();
    // Get the first auth context
    var authContext = authContexts.shift();
    // Copy the params
    var customAuthContext = authContext.slice(0);
    // Push our callback handler
    customAuthContext.push(function(err) {
      applyAuth(authContexts, server, callback);
    });

    // Attempt authentication
    server.auth.apply(server, customAuthContext)
  }

  // Apply all auth contexts
  applyAuth(authContexts, server, callback);
}

function topologyMonitor(self, options) {
  options = options || {};

  // Set momitoring timeout
  self.haTimeoutId = setTimeout(function() {
    if(self.state == DESTROYED || self.state == UNREFERENCED) return;
    // If we have a primary and a disconnect handler, execute
    // buffered operations
    if(self.isConnected() && self.s.disconnectHandler) {
      self.s.disconnectHandler.execute();
    }

    // Get the connectingServers
    var proxies = self.connectedProxies.slice(0);
    // Get the count
    var count = proxies.length;

    // If the count is zero schedule a new fast
    function pingServer(_self, _server, cb) {
      // Measure running time
      var start = new Date().getTime();

      // Emit the server heartbeat start
      emitSDAMEvent(self, 'serverHeartbeatStarted', { connectionId: _server.name });

      // Execute ismaster
      _server.command('admin.$cmd', {
        ismaster:true
      }, {
        monitoring: true,
        socketTimeout: self.s.options.connectionTimeout || 2000,
      }, function(err, r) {
        if(self.state == DESTROYED || self.state == UNREFERENCED) {
          // Move from connectingProxies
          moveServerFrom(self.connectedProxies, self.disconnectedProxies, _server);
          _server.destroy();
          return cb(err, r);
        }

        // Calculate latency
        var latencyMS = new Date().getTime() - start;

        // We had an error, remove it from the state
        if(err) {
          // Emit the server heartbeat failure
          emitSDAMEvent(self, 'serverHeartbeatFailed', { durationMS: latencyMS, failure: err, connectionId: _server.name });
          // Move from connected proxies to disconnected proxies
          moveServerFrom(self.connectedProxies, self.disconnectedProxies, _server);
        } else {
          // Update the server ismaster
          _server.ismaster = r.result;
          _server.lastIsMasterMS = latencyMS;

          // Server heart beat event
          emitSDAMEvent(self, 'serverHeartbeatSucceeded', { durationMS: latencyMS, reply: r.result, connectionId: _server.name });
        }

        cb(err, r);
      });
    }

    // No proxies initiate monitor again
    if(proxies.length == 0) {
      // Emit close event if any listeners registered
      if(self.listeners("close").length > 0 && self.state == CONNECTING) {
        self.emit('error', new MongoError('no mongos proxy available'));
      } else {
        self.emit('close', self);
      }

      // Attempt to connect to any unknown servers
      return reconnectProxies(self, self.disconnectedProxies, function() {
        if(self.state == DESTROYED || self.state == UNREFERENCED) return;

        // Are we connected ? emit connect event
        if(self.state == CONNECTING && options.firstConnect) {
          self.emit('connect', self);
          self.emit('fullsetup', self);
          self.emit('all', self);
        } else if(self.isConnected()) {
          self.emit('reconnect', self);
        } else if(!self.isConnected() && self.listeners("close").length > 0) {
          self.emit('close', self);
        }

        // Perform topology monitor
        topologyMonitor(self);
      });
    }

    // Ping all servers
    for(var i = 0; i < proxies.length; i++) {
      pingServer(self, proxies[i], function() {
        count = count - 1;

        if(count == 0) {
          if(self.state == DESTROYED || self.state == UNREFERENCED) return;

          // Attempt to connect to any unknown servers
          reconnectProxies(self, self.disconnectedProxies, function() {
            if(self.state == DESTROYED || self.state == UNREFERENCED) return;
            // Perform topology monitor
            topologyMonitor(self);
          });
        }
      });
    }
  }, self.s.haInterval);
}

/**
 * Returns the last known ismaster document for this server
 * @method
 * @return {object}
 */
Mongos.prototype.lastIsMaster = function() {
  return this.ismaster;
}

/**
 * Unref all connections belong to this server
 * @method
 */
Mongos.prototype.unref = function() {
  // Transition state
  stateTransition(this, UNREFERENCED);
  // Get all proxies
  var proxies = this.connectedProxies.concat(this.connectingProxies);
  proxies.forEach(function(x) {
    x.unref();
  });

  clearTimeout(this.haTimeoutId);
}

/**
 * Destroy the server connection
 * @param {boolean} [options.force=false] Force destroy the pool
 * @method
 */
Mongos.prototype.destroy = function(options) {
  var self = this;
  // Transition state
  stateTransition(this, DESTROYED);
  // Get all proxies
  var proxies = this.connectedProxies.concat(this.connectingProxies);
  // Clear out any monitoring process
  if(this.haTimeoutId) clearTimeout(this.haTimeoutId);
  // Clear out authentication contexts
  this.s.authenticationContexts = [];

  // Destroy all connecting servers
  proxies.forEach(function(x) {
    // Emit the sdam event
    self.emit('serverClosed', {
      topologyId: self.id,
      address: x.name
    });

    // Destroy the server
    x.destroy(options);
    // Move to list of disconnectedProxies
    moveServerFrom(self.connectedProxies, self.disconnectedProxies, x);
  });

  // Emit the final topology change
  emitTopologyDescriptionChanged(self);
  // Emit toplogy closing event
  emitSDAMEvent(this, 'topologyClosed', { topologyId: this.id });
}

/**
 * Figure out if the server is connected
 * @method
 * @return {boolean}
 */
Mongos.prototype.isConnected = function() {
  return this.connectedProxies.length > 0;
}

/**
 * Figure out if the server instance was destroyed by calling destroy
 * @method
 * @return {boolean}
 */
Mongos.prototype.isDestroyed = function() {
  return this.state == DESTROYED;
}

//
// Operations
//

// Execute write operation
var executeWriteOperation = function(self, op, ns, ops, options, callback) {
  if(typeof options == 'function') callback = options, options = {}, options = options || {};
  // Ensure we have no options
  options = options || {};
  // Pick a server
  var server = pickProxy(self);
  // No server found error out
  if(!server) return callback(new MongoError('no mongos proxy available'));
  // Execute the command
  server[op](ns, ops, options, callback);
}

/**
 * Insert one or more documents
 * @method
 * @param {string} ns The MongoDB fully qualified namespace (ex: db1.collection1)
 * @param {array} ops An array of documents to insert
 * @param {boolean} [options.ordered=true] Execute in order or out of order
 * @param {object} [options.writeConcern={}] Write concern for the operation
 * @param {Boolean} [options.serializeFunctions=false] Specify if functions on an object should be serialized.
 * @param {Boolean} [options.ignoreUndefined=false] Specify if the BSON serializer should ignore undefined fields.
 * @param {opResultCallback} callback A callback function
 */
Mongos.prototype.insert = function(ns, ops, options, callback) {
  if(typeof options == 'function') callback = options, options = {}, options = options || {};
  if(this.state == DESTROYED) return callback(new MongoError(f('topology was destroyed')));

  // Not connected but we have a disconnecthandler
  if(!this.isConnected() && this.s.disconnectHandler != null) {
    return this.s.disconnectHandler.add('insert', ns, ops, options, callback);
  }

  // No mongos proxy available
  if(!this.isConnected()) {
    return callback(new MongoError('no mongos proxy available'));
  }

  // Execute write operation
  executeWriteOperation(this, 'insert', ns, ops, options, callback);
}

/**
 * Perform one or more update operations
 * @method
 * @param {string} ns The MongoDB fully qualified namespace (ex: db1.collection1)
 * @param {array} ops An array of updates
 * @param {boolean} [options.ordered=true] Execute in order or out of order
 * @param {object} [options.writeConcern={}] Write concern for the operation
 * @param {Boolean} [options.serializeFunctions=false] Specify if functions on an object should be serialized.
 * @param {Boolean} [options.ignoreUndefined=false] Specify if the BSON serializer should ignore undefined fields.
 * @param {opResultCallback} callback A callback function
 */
Mongos.prototype.update = function(ns, ops, options, callback) {
  if(typeof options == 'function') callback = options, options = {}, options = options || {};
  if(this.state == DESTROYED) return callback(new MongoError(f('topology was destroyed')));

  // Not connected but we have a disconnecthandler
  if(!this.isConnected() && this.s.disconnectHandler != null) {
    return this.s.disconnectHandler.add('update', ns, ops, options, callback);
  }

  // No mongos proxy available
  if(!this.isConnected()) {
    return callback(new MongoError('no mongos proxy available'));
  }

  // Execute write operation
  executeWriteOperation(this, 'update', ns, ops, options, callback);
}

/**
 * Perform one or more remove operations
 * @method
 * @param {string} ns The MongoDB fully qualified namespace (ex: db1.collection1)
 * @param {array} ops An array of removes
 * @param {boolean} [options.ordered=true] Execute in order or out of order
 * @param {object} [options.writeConcern={}] Write concern for the operation
 * @param {Boolean} [options.serializeFunctions=false] Specify if functions on an object should be serialized.
 * @param {Boolean} [options.ignoreUndefined=false] Specify if the BSON serializer should ignore undefined fields.
 * @param {opResultCallback} callback A callback function
 */
Mongos.prototype.remove = function(ns, ops, options, callback) {
  if(typeof options == 'function') callback = options, options = {}, options = options || {};
  if(this.state == DESTROYED) return callback(new MongoError(f('topology was destroyed')));

  // Not connected but we have a disconnecthandler
  if(!this.isConnected() && this.s.disconnectHandler != null) {
    return this.s.disconnectHandler.add('remove', ns, ops, options, callback);
  }

  // No mongos proxy available
  if(!this.isConnected()) {
    return callback(new MongoError('no mongos proxy available'));
  }

  // Execute write operation
  executeWriteOperation(this, 'remove', ns, ops, options, callback);
}

/**
 * Execute a command
 * @method
 * @param {string} ns The MongoDB fully qualified namespace (ex: db1.collection1)
 * @param {object} cmd The command hash
 * @param {ReadPreference} [options.readPreference] Specify read preference if command supports it
 * @param {Connection} [options.connection] Specify connection object to execute command against
 * @param {Boolean} [options.serializeFunctions=false] Specify if functions on an object should be serialized.
 * @param {Boolean} [options.ignoreUndefined=false] Specify if the BSON serializer should ignore undefined fields.
 * @param {opResultCallback} callback A callback function
 */
Mongos.prototype.command = function(ns, cmd, options, callback) {
  if(typeof options == 'function') callback = options, options = {}, options = options || {};
  if(this.state == DESTROYED) return callback(new MongoError(f('topology was destroyed')));
  var self = this;

  // Pick a proxy
  var server = pickProxy(self);

  // Topology is not connected, save the call in the provided store to be
  // Executed at some point when the handler deems it's reconnected
  if((server == null || !server.isConnected()) && this.s.disconnectHandler != null) {
    return this.s.disconnectHandler.add('command', ns, cmd, options, callback);
  }

  // No server returned we had an error
  if(server == null) {
    return callback(new MongoError('no mongos proxy available'));
  }

  // Cloned options
  var clonedOptions = cloneOptions(options);
  clonedOptions.topology = self;

  // Execute the command
  server.command(ns, cmd, clonedOptions, callback);
}

/**
 * Perform one or more remove operations
 * @method
 * @param {string} ns The MongoDB fully qualified namespace (ex: db1.collection1)
 * @param {{object}|{Long}} cmd Can be either a command returning a cursor or a cursorId
 * @param {object} [options.batchSize=0] Batchsize for the operation
 * @param {array} [options.documents=[]] Initial documents list for cursor
 * @param {ReadPreference} [options.readPreference] Specify read preference if command supports it
 * @param {Boolean} [options.serializeFunctions=false] Specify if functions on an object should be serialized.
 * @param {Boolean} [options.ignoreUndefined=false] Specify if the BSON serializer should ignore undefined fields.
 * @param {opResultCallback} callback A callback function
 */
Mongos.prototype.cursor = function(ns, cmd, cursorOptions) {
  cursorOptions = cursorOptions || {};
  var FinalCursor = cursorOptions.cursorFactory || this.s.Cursor;
  return new FinalCursor(this.s.bson, ns, cmd, cursorOptions, this, this.s.options);
}

/**
 * Authenticate using a specified mechanism
 * @method
 * @param {string} mechanism The Auth mechanism we are invoking
 * @param {string} db The db we are invoking the mechanism against
 * @param {...object} param Parameters for the specific mechanism
 * @param {authResultCallback} callback A callback function
 */
Mongos.prototype.auth = function(mechanism, db) {
  var allArgs = Array.prototype.slice.call(arguments, 0).slice(0);
  var self = this;
  var args = Array.prototype.slice.call(arguments, 2);
  var callback = args.pop();
  var currentContextIndex = 0;

  // If we don't have the mechanism fail
  if(this.authProviders[mechanism] == null && mechanism != 'default') {
    return callback(new MongoError(f("auth provider %s does not exist", mechanism)));
  }

  // Are we already authenticating, throw
  if(this.authenticating) {
    return callback(new MongoError('authentication or logout allready in process'));
  }

  // Topology is not connected, save the call in the provided store to be
  // Executed at some point when the handler deems it's reconnected
  if(!self.isConnected() && self.s.disconnectHandler != null) {
    return self.s.disconnectHandler.add('auth', db, allArgs, {}, callback);
  }

  // Set to authenticating
  this.authenticating = true;
  // All errors
  var errors = [];

  // Get all the servers
  var servers = this.connectedProxies.slice(0);
  // No servers return
  if(servers.length == 0) {
    this.authenticating = false;
    callback(null, true);
  }

  // Authenticate
  function auth(server) {
    // Arguments without a callback
    var argsWithoutCallback = [mechanism, db].concat(args.slice(0));
    // Create arguments
    var finalArguments = argsWithoutCallback.concat([function(err) {
      count = count - 1;
      // Save all the errors
      if(err) errors.push({name: server.name, err: err});
      // We are done
      if(count == 0) {
        // Auth is done
        self.authenticating = false;

        // Return the auth error
        if(errors.length) {
          // Remove the entry from the stored authentication contexts
          self.s.authenticationContexts.splice(currentContextIndex, 0);
          // Return error
          return callback(MongoError.create({
            message: 'authentication fail', errors: errors
          }), false);
        }

        // Successfully authenticated session
        callback(null, self);
      }
    }]);

    // Execute the auth only against non arbiter servers
    if(!server.lastIsMaster().arbiterOnly) {
      server.auth.apply(server, finalArguments);
    }
  }

  // Save current context index
  currentContextIndex = this.s.authenticationContexts.length;
  // Store the auth context and return the last index
  this.s.authenticationContexts.push([mechanism, db].concat(args.slice(0)));

  // Get total count
  var count = servers.length;
  // Authenticate against all servers
  while(servers.length > 0) {
    auth(servers.shift());
  }
}

/**
 * Logout from a database
 * @method
 * @param {string} db The db we are logging out from
 * @param {authResultCallback} callback A callback function
 */
Mongos.prototype.logout = function(dbName, callback) {
  var self = this;
  // Are we authenticating or logging out, throw
  if(this.authenticating) {
    throw new MongoError('authentication or logout allready in process');
  }

  // Ensure no new members are processed while logging out
  this.authenticating = true;

  // Remove from all auth providers (avoid any reaplication of the auth details)
  var providers = Object.keys(this.authProviders);
  for(var i = 0; i < providers.length; i++) {
    this.authProviders[providers[i]].logout(dbName);
  }

  // Now logout all the servers
  var servers = this.connectedProxies.slice(0);
  var count = servers.length;
  if(count == 0) return callback();
  var errors = [];

  function logoutServer(_server, cb) {
    _server.logout(dbName, function(err) {
      if(err) errors.push({name: _server.name, err: err});
      cb();
    });
  }

  // Execute logout on all server instances
  for(i = 0; i < servers.length; i++) {
    logoutServer(servers[i], function() {
      count = count - 1;

      if(count == 0) {
        // Do not block new operations
        self.authenticating = false;
        // If we have one or more errors
        if(errors.length) return callback(MongoError.create({
          message: f('logout failed against db %s', dbName), errors: errors
        }), false);

        // No errors
        callback();
      }
    })
  }
}

/**
 * Get server
 * @method
 * @return {Server}
 */
Mongos.prototype.getServer = function() {
  var server = pickProxy(this);
  if(this.s.debug) this.emit('pickedServer', null, server);
  return server;
}

/**
 * Get a direct connection
 * @method
 * @return {Connection}
 */
Mongos.prototype.getConnection = function() {
  var server = this.getServer();
  if(server) return server.getConnection();
}

/**
 * All raw connections
 * @method
 * @return {Connection[]}
 */
Mongos.prototype.connections = function() {
  var connections = [];

  for(var i = 0; i < this.connectedProxies.length; i++) {
    connections = connections.concat(this.connectedProxies[i].connections());
  }

  return connections;
}

function emitTopologyDescriptionChanged(self) {
  if(self.listeners('topologyDescriptionChanged').length > 0) {
    var topology = 'Unknown';
    var setName = self.setName;

    if(self.connectedProxies.length > 0) {
      topology = 'Sharded';
    }

    // Generate description
    var description = {
      topologyType: topology,
      servers: []
    }

    // All proxies
    var proxies = self.disconnectedProxies
      .concat(self.connectingProxies);

    // Add all the disconnected proxies
    description.servers = description.servers.concat(proxies.map(function(x) {
      var description = x.getDescription();
      description.type = 'Unknown';
      return description;
    }));

    // Add all the connected proxies
    description.servers = description.servers.concat(self.connectedProxies.map(function(x) {
      var description = x.getDescription();
      description.type = 'Mongos';
      return description;
    }));

    // Get the diff
    var diffResult = diff(self.topologyDescription, description);

    // Create the result
    var result = {
      topologyId: self.id,
      previousDescription: self.topologyDescription,
      newDescription: description,
      diff: diffResult
    };

    // Emit the topologyDescription change
    if(diffResult.servers.length > 0) {
      self.emit('topologyDescriptionChanged', result);
    }

    // Set the new description
    self.topologyDescription = description;
  }
}

/**
 * A mongos connect event, used to verify that the connection is up and running
 *
 * @event Mongos#connect
 * @type {Mongos}
 */

/**
 * A mongos reconnect event, used to verify that the mongos topology has reconnected
 *
 * @event Mongos#reconnect
 * @type {Mongos}
 */

/**
 * A mongos fullsetup event, used to signal that all topology members have been contacted.
 *
 * @event Mongos#fullsetup
 * @type {Mongos}
 */

/**
 * A mongos all event, used to signal that all topology members have been contacted.
 *
 * @event Mongos#all
 * @type {Mongos}
 */

/**
 * A server member left the mongos list
 *
 * @event Mongos#left
 * @type {Mongos}
 * @param {string} type The type of member that left (mongos)
 * @param {Server} server The server object that left
 */

/**
 * A server member joined the mongos list
 *
 * @event Mongos#joined
 * @type {Mongos}
 * @param {string} type The type of member that left (mongos)
 * @param {Server} server The server object that joined
 */

/**
 * A server opening SDAM monitoring event
 *
 * @event Mongos#serverOpening
 * @type {object}
 */

/**
 * A server closed SDAM monitoring event
 *
 * @event Mongos#serverClosed
 * @type {object}
 */

/**
 * A server description SDAM change monitoring event
 *
 * @event Mongos#serverDescriptionChanged
 * @type {object}
 */

/**
 * A topology open SDAM event
 *
 * @event Mongos#topologyOpening
 * @type {object}
 */

/**
 * A topology closed SDAM event
 *
 * @event Mongos#topologyClosed
 * @type {object}
 */

/**
 * A topology structure SDAM change event
 *
 * @event Mongos#topologyDescriptionChanged
 * @type {object}
 */

/**
 * A topology serverHeartbeatStarted SDAM event
 *
 * @event Mongos#serverHeartbeatStarted
 * @type {object}
 */

/**
 * A topology serverHeartbeatFailed SDAM event
 *
 * @event Mongos#serverHeartbeatFailed
 * @type {object}
 */

/**
 * A topology serverHeartbeatSucceeded SDAM change event
 *
 * @event Mongos#serverHeartbeatSucceeded
 * @type {object}
 */

module.exports = Mongos;
