"use strict";

var EventEmitter = require('events').EventEmitter
  , inherits = require('util').inherits
  , f = require('util').format
  , Server = require('./server')
  , Cursor = require('./cursor')
  , AggregationCursor = require('./aggregation_cursor')
  , CommandCursor = require('./command_cursor')
  , ReadPreference = require('./read_preference')
  , MongoError = require('mongodb-core').MongoError
  , ServerCapabilities = require('./topology_base').ServerCapabilities
  , Store = require('./topology_base').Store
  , Define = require('./metadata')
  , CReplSet = require('mongodb-core').ReplSet
  , CoreReadPreference = require('mongodb-core').ReadPreference
  , MAX_JS_INT = require('./utils').MAX_JS_INT
  , translateOptions = require('./utils').translateOptions
  , filterOptions = require('./utils').filterOptions
  , getReadPreference = require('./utils').getReadPreference
  , mergeOptions = require('./utils').mergeOptions
  , os = require('os');
/**
 * @fileOverview The **ReplSet** class is a class that represents a Replicaset topology and is
 * used to construct connections.
 *
 * **ReplSet Should not be used, use MongoClient.connect**
 * @example
 * var Db = require('mongodb').Db,
 *   ReplSet = require('mongodb').ReplSet,
 *   Server = require('mongodb').Server,
 *   test = require('assert');
 * // Connect using ReplSet
 * var server = new Server('localhost', 27017);
 * var db = new Db('test', new ReplSet([server]));
 * db.open(function(err, db) {
 *   // Get an additional db
 *   db.close();
 * });
 */

// Allowed parameters
var legalOptionNames = ['ha', 'haInterval', 'replicaSet', 'rs_name', 'secondaryAcceptableLatencyMS'
  , 'connectWithNoPrimary', 'poolSize', 'ssl', 'checkServerIdentity', 'sslValidate'
  , 'sslCA', 'sslCert', 'sslCRL', 'sslKey', 'sslPass', 'socketOptions', 'bufferMaxEntries'
  , 'store', 'auto_reconnect', 'autoReconnect', 'emitError'
  , 'keepAlive', 'noDelay', 'connectTimeoutMS', 'socketTimeoutMS', 'strategy', 'debug', 'family'
  , 'loggerLevel', 'logger', 'reconnectTries', 'appname', 'domainsEnabled'
  , 'servername', 'promoteLongs', 'promoteValues', 'promoteBuffers', 'maxStalenessSeconds'];

// Get package.json variable
var driverVersion = require('../package.json').version;
var nodejsversion = f('Node.js %s, %s', process.version, os.endianness());
var type = os.type();
var name = process.platform;
var architecture = process.arch;
var release = os.release();

/**
 * Creates a new ReplSet instance
 * @class
 * @deprecated
 * @param {Server[]} servers A seedlist of servers participating in the replicaset.
 * @param {object} [options=null] Optional settings.
 * @param {boolean} [options.ha=true] Turn on high availability monitoring.
 * @param {number} [options.haInterval=10000] Time between each replicaset status check.
 * @param {string} [options.replicaSet] The name of the replicaset to connect to.
 * @param {number} [options.secondaryAcceptableLatencyMS=15] Sets the range of servers to pick when using NEAREST (lowest ping ms + the latency fence, ex: range of 1 to (1 + 15) ms)
 * @param {boolean} [options.connectWithNoPrimary=false] Sets if the driver should connect even if no primary is available
 * @param {number} [options.poolSize=5] Number of connections in the connection pool for each server instance, set to 5 as default for legacy reasons.
 * @param {boolean} [options.ssl=false] Use ssl connection (needs to have a mongod server with ssl support)
 * @param {boolean|function} [options.checkServerIdentity=true] Ensure we check server identify during SSL, set to false to disable checking. Only works for Node 0.12.x or higher. You can pass in a boolean or your own checkServerIdentity override function.
 * @param {object} [options.sslValidate=true] Validate mongod server certificate against ca (needs to have a mongod server with ssl support, 2.4 or higher)
 * @param {array} [options.sslCA=null] Array of valid certificates either as Buffers or Strings (needs to have a mongod server with ssl support, 2.4 or higher)
 * @param {array} [options.sslCRL=null] Array of revocation certificates either as Buffers or Strings (needs to have a mongod server with ssl support, 2.4 or higher)
 * @param {(Buffer|string)} [options.sslCert=null] String or buffer containing the certificate we wish to present (needs to have a mongod server with ssl support, 2.4 or higher)
 * @param {(Buffer|string)} [options.sslKey=null] String or buffer containing the certificate private key we wish to present (needs to have a mongod server with ssl support, 2.4 or higher)
 * @param {(Buffer|string)} [options.sslPass=null] String or buffer containing the certificate password (needs to have a mongod server with ssl support, 2.4 or higher)
 * @param {string} [options.servername=null] String containing the server name requested via TLS SNI.
 * @param {object} [options.socketOptions=null] Socket options
 * @param {boolean} [options.socketOptions.noDelay=true] TCP Socket NoDelay option.
 * @param {number} [options.socketOptions.keepAlive=0] TCP KeepAlive on the socket with a X ms delay before start.
 * @param {number} [options.socketOptions.connectTimeoutMS=10000] TCP Connection timeout setting
 * @param {number} [options.socketOptions.socketTimeoutMS=0] TCP Socket timeout setting
 * @param {boolean} [options.domainsEnabled=false] Enable the wrapping of the callback in the current domain, disabled by default to avoid perf hit.
 * @param {number} [options.maxStalenessSeconds=undefined] The max staleness to secondary reads (values under 10 seconds cannot be guaranteed);
 * @fires ReplSet#connect
 * @fires ReplSet#ha
 * @fires ReplSet#joined
 * @fires ReplSet#left
 * @fires ReplSet#fullsetup
 * @fires ReplSet#open
 * @fires ReplSet#close
 * @fires ReplSet#error
 * @fires ReplSet#timeout
 * @fires ReplSet#parseError
 * @property {string} parserType the parser type used (c++ or js).
 * @return {ReplSet} a ReplSet instance.
 */
var ReplSet = function(servers, options) {
  if(!(this instanceof ReplSet)) return new ReplSet(servers, options);
  options = options || {};
  var self = this;
  // Set up event emitter
  EventEmitter.call(this);

  // Filter the options
  options = filterOptions(options, legalOptionNames);

  // Ensure all the instances are Server
  for(var i = 0; i < servers.length; i++) {
    if(!(servers[i] instanceof Server)) {
      throw MongoError.create({message: "all seed list instances must be of the Server type", driver:true});
    }
  }

  // Stored options
  var storeOptions = {
      force: false
    , bufferMaxEntries: typeof options.bufferMaxEntries == 'number' ? options.bufferMaxEntries : MAX_JS_INT
  }

  // Shared global store
  var store = options.store || new Store(self, storeOptions);

  // Build seed list
  var seedlist = servers.map(function(x) {
    return {host: x.host, port: x.port}
  });

  // Clone options
  var clonedOptions = mergeOptions({}, {
    disconnectHandler: store,
    cursorFactory: Cursor,
    reconnect: false,
    emitError: typeof options.emitError == 'boolean' ? options.emitError : true,
    size: typeof options.poolSize == 'number' ? options.poolSize : 5
  });

  // Translate any SSL options and other connectivity options
  clonedOptions = translateOptions(clonedOptions, options);

  // Socket options
  var socketOptions = options.socketOptions && Object.keys(options.socketOptions).length > 0
    ? options.socketOptions : options;

  // Translate all the options to the mongodb-core ones
  clonedOptions = translateOptions(clonedOptions, socketOptions);
  if(typeof clonedOptions.keepAlive == 'number') {
    clonedOptions.keepAliveInitialDelay = clonedOptions.keepAlive;
    clonedOptions.keepAlive = clonedOptions.keepAlive > 0;
  }

  // Client info
  this.clientInfo = {
    driver: {
      name: "nodejs",
      version: driverVersion
    },
    os: {
      type: type,
      name: name,
      architecture: architecture,
      version: release
    },
    platform: nodejsversion
  }

  // Build default client information
  clonedOptions.clientInfo = this.clientInfo;
  // Do we have an application specific string
  if(options.appname) {
    clonedOptions.clientInfo.application = { name: options.appname };
  }

  // Create the ReplSet
  var replset = new CReplSet(seedlist, clonedOptions);

  // Listen to reconnect event
  replset.on('reconnect', function() {
    self.emit('reconnect');
    store.execute();
  });

  // Internal state
  this.s = {
    // Replicaset
    replset: replset
    // Server capabilities
    , sCapabilities: null
    // Debug tag
    , tag: options.tag
    // Store options
    , storeOptions: storeOptions
    // Cloned options
    , clonedOptions: clonedOptions
    // Store
    , store: store
    // Options
    , options: options
  }

  // Debug
  if(clonedOptions.debug) {
    // Last ismaster
    Object.defineProperty(this, 'replset', {
      enumerable:true, get: function() { return replset; }
    });
  }
}

/**
 * @ignore
 */
inherits(ReplSet, EventEmitter);

// Last ismaster
Object.defineProperty(ReplSet.prototype, 'isMasterDoc', {
  enumerable:true, get: function() { return this.s.replset.lastIsMaster(); }
});

Object.defineProperty(ReplSet.prototype, 'parserType', {
  enumerable:true, get: function() {
    return this.s.replset.parserType;
  }
});

// BSON property
Object.defineProperty(ReplSet.prototype, 'bson', {
  enumerable: true, get: function() {
    return this.s.replset.s.bson;
  }
});

Object.defineProperty(ReplSet.prototype, 'haInterval', {
  enumerable:true, get: function() { return this.s.replset.s.haInterval; }
});

var define = ReplSet.define = new Define('ReplSet', ReplSet, false);

// Ensure the right read Preference object
var translateReadPreference = function(options) {
  if(typeof options.readPreference == 'string') {
    options.readPreference = new CoreReadPreference(options.readPreference);
  } else if(options.readPreference instanceof ReadPreference) {
    options.readPreference = new CoreReadPreference(options.readPreference.mode
      , options.readPreference.tags, {maxStalenessSeconds: options.readPreference.maxStalenessSeconds});
  }

  return options;
}

// Connect method
ReplSet.prototype.connect = function(db, _options, callback) {
  var self = this;
  if('function' === typeof _options) callback = _options, _options = {};
  if(_options == null) _options = {};
  if(!('function' === typeof callback)) callback = null;
  self.s.options = _options;

  // Update bufferMaxEntries
  self.s.storeOptions.bufferMaxEntries = db.bufferMaxEntries;

  // Actual handler
  var errorHandler = function(event) {
    return function(err) {
      if(event != 'error') {
        self.emit(event, err);
      }
    }
  }

  // Clear out all the current handlers left over
  var events = ["timeout", "error", "close", 'serverOpening', 'serverDescriptionChanged', 'serverHeartbeatStarted',
    'serverHeartbeatSucceeded', 'serverHeartbeatFailed', 'serverClosed', 'topologyOpening',
    'topologyClosed', 'topologyDescriptionChanged', 'joined', 'left', 'ping', 'ha'];
  events.forEach(function(e) {
    self.s.replset.removeAllListeners(e);
  });

  // relay the event
  var relay = function(event) {
    return function(t, server) {
      self.emit(event, t, server);
    }
  }

  // Replset events relay
  var replsetRelay = function(event) {
    return function(t, server) {
      self.emit(event, t, server.lastIsMaster(), server);
    }
  }

  // Relay ha
  var relayHa = function(t, state) {
    self.emit('ha', t, state);

    if(t == 'start') {
      self.emit('ha_connect', t, state);
    } else if(t == 'end') {
      self.emit('ha_ismaster', t, state);
    }
  }

  // Set up serverConfig listeners
  self.s.replset.on('joined', replsetRelay('joined'));
  self.s.replset.on('left', relay('left'));
  self.s.replset.on('ping', relay('ping'));
  self.s.replset.on('ha', relayHa);

  // Set up SDAM listeners
  self.s.replset.on('serverDescriptionChanged', relay('serverDescriptionChanged'));
  self.s.replset.on('serverHeartbeatStarted', relay('serverHeartbeatStarted'));
  self.s.replset.on('serverHeartbeatSucceeded', relay('serverHeartbeatSucceeded'));
  self.s.replset.on('serverHeartbeatFailed', relay('serverHeartbeatFailed'));
  self.s.replset.on('serverOpening', relay('serverOpening'));
  self.s.replset.on('serverClosed', relay('serverClosed'));
  self.s.replset.on('topologyOpening', relay('topologyOpening'));
  self.s.replset.on('topologyClosed', relay('topologyClosed'));
  self.s.replset.on('topologyDescriptionChanged', relay('topologyDescriptionChanged'));

  self.s.replset.on('fullsetup', function() {
    self.emit('fullsetup', self, self);
  });

  self.s.replset.on('all', function() {
    self.emit('all', null, self);
  });

  // Connect handler
  var connectHandler = function() {
    // Set up listeners
    self.s.replset.once('timeout', errorHandler('timeout'));
    self.s.replset.once('error', errorHandler('error'));
    self.s.replset.once('close', errorHandler('close'));

    // Emit open event
    self.emit('open', null, self);

    // Return correctly
    try {
      callback(null, self);
    } catch(err) {
      process.nextTick(function() { throw err; })
    }
  }

  // Error handler
  var connectErrorHandler = function() {
    return function(err) {
      ['timeout', 'error', 'close'].forEach(function(e) {
        self.s.replset.removeListener(e, connectErrorHandler);
      });

      self.s.replset.removeListener('connect', connectErrorHandler);
      // Destroy the replset
      self.s.replset.destroy();

      // Try to callback
      try {
        callback(err);
      } catch(err) {
        if(!self.s.replset.isConnected())
          process.nextTick(function() { throw err; })
      }
    }
  }

  // Set up listeners
  self.s.replset.once('timeout', connectErrorHandler('timeout'));
  self.s.replset.once('error', connectErrorHandler('error'));
  self.s.replset.once('close', connectErrorHandler('close'));
  self.s.replset.once('connect', connectHandler);

  // Start connection
  self.s.replset.connect(_options);
}

// Server capabilities
ReplSet.prototype.capabilities = function() {
  if(this.s.sCapabilities) return this.s.sCapabilities;
  if(this.s.replset.lastIsMaster() == null) return null;
  this.s.sCapabilities = new ServerCapabilities(this.s.replset.lastIsMaster());
  return this.s.sCapabilities;
}

define.classMethod('capabilities', {callback: false, promise:false, returns: [ServerCapabilities]});

// Command
ReplSet.prototype.command = function(ns, cmd, options, callback) {
  this.s.replset.command(ns, cmd, getReadPreference(options), callback);
}

define.classMethod('command', {callback: true, promise:false});

// Insert
ReplSet.prototype.insert = function(ns, ops, options, callback) {
  this.s.replset.insert(ns, ops, options, callback);
}

define.classMethod('insert', {callback: true, promise:false});

// Update
ReplSet.prototype.update = function(ns, ops, options, callback) {
  this.s.replset.update(ns, ops, options, callback);
}

define.classMethod('update', {callback: true, promise:false});

// Remove
ReplSet.prototype.remove = function(ns, ops, options, callback) {
  this.s.replset.remove(ns, ops, options, callback);
}

define.classMethod('remove', {callback: true, promise:false});

// Destroyed
ReplSet.prototype.isDestroyed = function() {
  return this.s.replset.isDestroyed();
}

// IsConnected
ReplSet.prototype.isConnected = function(options) {
  options = options || {};

  // If we passed in a readPreference, translate to
  // a CoreReadPreference instance
  if(options.readPreference) {
    options.readPreference = translateReadPreference(options.readPreference);
  }

  return this.s.replset.isConnected(options);
}

define.classMethod('isConnected', {callback: false, promise:false, returns: [Boolean]});

// Insert
ReplSet.prototype.cursor = function(ns, cmd, options) {
  options = translateReadPreference(options);
  options.disconnectHandler = this.s.store;
  return this.s.replset.cursor(ns, cmd, options);
}

define.classMethod('cursor', {callback: false, promise:false, returns: [Cursor, AggregationCursor, CommandCursor]});

ReplSet.prototype.lastIsMaster = function() {
  return this.s.replset.lastIsMaster();
}

/**
 * Unref all sockets
 * @method
 */
ReplSet.prototype.unref = function() {
  return this.s.replset.unref();
}

ReplSet.prototype.close = function(forceClosed) {
  var self = this;
  // Call destroy on the topology
  this.s.replset.destroy({
    force: typeof forceClosed == 'boolean' ? forceClosed : false,
  });
  // We need to wash out all stored processes
  if(forceClosed == true) {
    this.s.storeOptions.force = forceClosed;
    this.s.store.flush();
  }

  var events = ['timeout', 'error', 'close', 'joined', 'left'];
  events.forEach(function(e) {
    self.removeAllListeners(e);
  });
}

define.classMethod('close', {callback: false, promise:false});

ReplSet.prototype.auth = function() {
  var args = Array.prototype.slice.call(arguments, 0);
  this.s.replset.auth.apply(this.s.replset, args);
}

define.classMethod('auth', {callback: true, promise:false});

ReplSet.prototype.logout = function() {
  var args = Array.prototype.slice.call(arguments, 0);
  this.s.replset.logout.apply(this.s.replset, args);
}

define.classMethod('logout', {callback: true, promise:false});

/**
 * All raw connections
 * @method
 * @return {array}
 */
ReplSet.prototype.connections = function() {
  return this.s.replset.connections();
}

define.classMethod('connections', {callback: false, promise:false, returns:[Array]});

/**
 * A replset connect event, used to verify that the connection is up and running
 *
 * @event ReplSet#connect
 * @type {ReplSet}
 */

/**
 * The replset high availability event
 *
 * @event ReplSet#ha
 * @type {function}
 * @param {string} type The stage in the high availability event (start|end)
 * @param {boolean} data.norepeat This is a repeating high availability process or a single execution only
 * @param {number} data.id The id for this high availability request
 * @param {object} data.state An object containing the information about the current replicaset
 */

/**
 * A server member left the replicaset
 *
 * @event ReplSet#left
 * @type {function}
 * @param {string} type The type of member that left (primary|secondary|arbiter)
 * @param {Server} server The server object that left
 */

/**
 * A server member joined the replicaset
 *
 * @event ReplSet#joined
 * @type {function}
 * @param {string} type The type of member that joined (primary|secondary|arbiter)
 * @param {Server} server The server object that joined
 */

/**
 * ReplSet open event, emitted when replicaset can start processing commands.
 *
 * @event ReplSet#open
 * @type {Replset}
 */

/**
 * ReplSet fullsetup event, emitted when all servers in the topology have been connected to.
 *
 * @event ReplSet#fullsetup
 * @type {Replset}
 */

/**
 * ReplSet close event
 *
 * @event ReplSet#close
 * @type {object}
 */

/**
 * ReplSet error event, emitted if there is an error listener.
 *
 * @event ReplSet#error
 * @type {MongoError}
 */

/**
 * ReplSet timeout event
 *
 * @event ReplSet#timeout
 * @type {object}
 */

/**
 * ReplSet parseError event
 *
 * @event ReplSet#parseError
 * @type {object}
 */

module.exports = ReplSet;
