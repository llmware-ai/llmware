"use strict";

var EventEmitter = require('events').EventEmitter
  , inherits = require('util').inherits
  , f = require('util').format
  , ServerCapabilities = require('./topology_base').ServerCapabilities
  , MongoError = require('mongodb-core').MongoError
  , CMongos = require('mongodb-core').Mongos
  , Cursor = require('./cursor')
  , AggregationCursor = require('./aggregation_cursor')
  , CommandCursor = require('./command_cursor')
  , Define = require('./metadata')
  , Server = require('./server')
  , Store = require('./topology_base').Store
  , MAX_JS_INT = require('./utils').MAX_JS_INT
  , translateOptions = require('./utils').translateOptions
  , filterOptions = require('./utils').filterOptions
  , mergeOptions = require('./utils').mergeOptions
  , getReadPreference = require('./utils').getReadPreference
  , os = require('os');

// Get package.json variable
var driverVersion = require('../package.json').version;
var nodejsversion = f('Node.js %s, %s', process.version, os.endianness());
var type = os.type();
var name = process.platform;
var architecture = process.arch;
var release = os.release();

/**
 * @fileOverview The **Mongos** class is a class that represents a Mongos Proxy topology and is
 * used to construct connections.
 *
 * **Mongos Should not be used, use MongoClient.connect**
 * @example
 * var Db = require('mongodb').Db,
 *   Mongos = require('mongodb').Mongos,
 *   Server = require('mongodb').Server,
 *   test = require('assert');
 * // Connect using Mongos
 * var server = new Server('localhost', 27017);
 * var db = new Db('test', new Mongos([server]));
 * db.open(function(err, db) {
 *   // Get an additional db
 *   db.close();
 * });
 */

 // Allowed parameters
 var legalOptionNames = ['ha', 'haInterval', 'acceptableLatencyMS'
   , 'poolSize', 'ssl', 'checkServerIdentity', 'sslValidate', 'ciphers', 'ecdhCurve'
   , 'sslCA', 'sslCRL', 'sslCert', 'sslKey', 'sslPass', 'socketOptions', 'bufferMaxEntries'
   , 'store', 'auto_reconnect', 'autoReconnect', 'emitError'
   , 'keepAlive', 'noDelay', 'connectTimeoutMS', 'socketTimeoutMS'
   , 'loggerLevel', 'logger', 'reconnectTries', 'appname', 'domainsEnabled'
   , 'servername', 'promoteLongs', 'promoteValues', 'promoteBuffers'];

/**
 * Creates a new Mongos instance
 * @class
 * @deprecated
 * @param {Server[]} servers A seedlist of servers participating in the replicaset.
 * @param {object} [options=null] Optional settings.
 * @param {booelan} [options.ha=true] Turn on high availability monitoring.
 * @param {number} [options.haInterval=5000] Time between each replicaset status check.
 * @param {number} [options.poolSize=5] Number of connections in the connection pool for each server instance, set to 5 as default for legacy reasons.
 * @param {number} [options.acceptableLatencyMS=15] Cutoff latency point in MS for MongoS proxy selection
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
 * @param {number} [options.socketOptions.connectTimeoutMS=0] TCP Connection timeout setting
 * @param {number} [options.socketOptions.socketTimeoutMS=0] TCP Socket timeout setting
 * @param {boolean} [options.domainsEnabled=false] Enable the wrapping of the callback in the current domain, disabled by default to avoid perf hit.
 * @fires Mongos#connect
 * @fires Mongos#ha
 * @fires Mongos#joined
 * @fires Mongos#left
 * @fires Mongos#fullsetup
 * @fires Mongos#open
 * @fires Mongos#close
 * @fires Mongos#error
 * @fires Mongos#timeout
 * @fires Mongos#parseError
 * @property {string} parserType the parser type used (c++ or js).
 * @return {Mongos} a Mongos instance.
 */
var Mongos = function(servers, options) {
  if(!(this instanceof Mongos)) return new Mongos(servers, options);
  options = options || {};
  var self = this;

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

  // Set up event emitter
  EventEmitter.call(this);

  // Build seed list
  var seedlist = servers.map(function(x) {
    return {host: x.host, port: x.port}
  });

  // Get the reconnect option
  var reconnect = typeof options.auto_reconnect == 'boolean' ? options.auto_reconnect : true;
  reconnect = typeof options.autoReconnect == 'boolean' ? options.autoReconnect : reconnect;

  // Clone options
  var clonedOptions = mergeOptions({}, {
    disconnectHandler: store,
    cursorFactory: Cursor,
    reconnect: reconnect,
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

  // Build default client information
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

  // Create the Mongos
  var mongos = new CMongos(seedlist, clonedOptions)
  // Server capabilities
  var sCapabilities = null;

  // Internal state
  this.s = {
    // Create the Mongos
      mongos: mongos
    // Server capabilities
    , sCapabilities: sCapabilities
    // Debug turned on
    , debug: clonedOptions.debug
    // Store option defaults
    , storeOptions: storeOptions
    // Cloned options
    , clonedOptions: clonedOptions
    // Actual store of callbacks
    , store: store
    // Options
    , options: options
  }
}

var define = Mongos.define = new Define('Mongos', Mongos, false);

/**
 * @ignore
 */
inherits(Mongos, EventEmitter);

// Last ismaster
Object.defineProperty(Mongos.prototype, 'isMasterDoc', {
  enumerable:true, get: function() { return this.s.mongos.lastIsMaster(); }
});

Object.defineProperty(Mongos.prototype, 'parserType', {
  enumerable:true, get: function() {
    return this.s.mongos.parserType;
  }
});

// BSON property
Object.defineProperty(Mongos.prototype, 'bson', {
  enumerable: true, get: function() {
    return this.s.mongos.s.bson;
  }
});

Object.defineProperty(Mongos.prototype, 'haInterval', {
  enumerable:true, get: function() { return this.s.mongos.s.haInterval; }
});

// Connect
Mongos.prototype.connect = function(db, _options, callback) {
  var self = this;
  if('function' === typeof _options) callback = _options, _options = {};
  if(_options == null) _options = {};
  if(!('function' === typeof callback)) callback = null;
  self.s.options = _options;

  // Update bufferMaxEntries
  self.s.storeOptions.bufferMaxEntries = db.bufferMaxEntries;

  // Error handler
  var connectErrorHandler = function() {
    return function(err) {
      // Remove all event handlers
      var events = ['timeout', 'error', 'close'];
      events.forEach(function(e) {
        self.removeListener(e, connectErrorHandler);
      });

      self.s.mongos.removeListener('connect', connectErrorHandler);

      // Try to callback
      try {
        callback(err);
      } catch(err) {
        process.nextTick(function() { throw err; })
      }
    }
  }

  // Actual handler
  var errorHandler = function(event) {
    return function(err) {
      if(event != 'error') {
        self.emit(event, err);
      }
    }
  }

  // Error handler
  var reconnectHandler = function() {
    self.emit('reconnect');
    self.s.store.execute();
  }

  // relay the event
  var relay = function(event) {
    return function(t, server) {
      self.emit(event, t, server);
    }
  }

  // Connect handler
  var connectHandler = function() {
    // Clear out all the current handlers left over
    var events = ["timeout", "error", "close", 'fullsetup'];
    events.forEach(function(e) {
      self.s.mongos.removeAllListeners(e);
    });

    // Set up listeners
    self.s.mongos.once('timeout', errorHandler('timeout'));
    self.s.mongos.once('error', errorHandler('error'));
    self.s.mongos.once('close', errorHandler('close'));

    // Set up serverConfig listeners
    self.s.mongos.on('fullsetup', function() { self.emit('fullsetup', self); });

    // Emit open event
    self.emit('open', null, self);

    // Return correctly
    try {
      callback(null, self);
    } catch(err) {
      process.nextTick(function() { throw err; })
    }
  }

  // Clear out all the current handlers left over
  var events = ["timeout", "error", "close", 'serverOpening', 'serverDescriptionChanged', 'serverHeartbeatStarted',
    'serverHeartbeatSucceeded', 'serverHeartbeatFailed', 'serverClosed', 'topologyOpening',
    'topologyClosed', 'topologyDescriptionChanged'];
  events.forEach(function(e) {
    self.s.mongos.removeAllListeners(e);
  });

  // Set up SDAM listeners
  self.s.mongos.on('serverDescriptionChanged', relay('serverDescriptionChanged'));
  self.s.mongos.on('serverHeartbeatStarted', relay('serverHeartbeatStarted'));
  self.s.mongos.on('serverHeartbeatSucceeded', relay('serverHeartbeatSucceeded'));
  self.s.mongos.on('serverHeartbeatFailed', relay('serverHeartbeatFailed'));
  self.s.mongos.on('serverOpening', relay('serverOpening'));
  self.s.mongos.on('serverClosed', relay('serverClosed'));
  self.s.mongos.on('topologyOpening', relay('topologyOpening'));
  self.s.mongos.on('topologyClosed', relay('topologyClosed'));
  self.s.mongos.on('topologyDescriptionChanged', relay('topologyDescriptionChanged'));

  // Set up listeners
  self.s.mongos.once('timeout', connectErrorHandler('timeout'));
  self.s.mongos.once('error', connectErrorHandler('error'));
  self.s.mongos.once('close', connectErrorHandler('close'));
  self.s.mongos.once('connect', connectHandler);
  // Join and leave events
  self.s.mongos.on('joined', relay('joined'));
  self.s.mongos.on('left', relay('left'));

  // Reconnect server
  self.s.mongos.on('reconnect', reconnectHandler);

  // Start connection
  self.s.mongos.connect(_options);
}

// Server capabilities
Mongos.prototype.capabilities = function() {
  if(this.s.sCapabilities) return this.s.sCapabilities;
  if(this.s.mongos.lastIsMaster() == null) return null;
  this.s.sCapabilities = new ServerCapabilities(this.s.mongos.lastIsMaster());
  return this.s.sCapabilities;
}

define.classMethod('capabilities', {callback: false, promise:false, returns: [ServerCapabilities]});

// Command
Mongos.prototype.command = function(ns, cmd, options, callback) {
  this.s.mongos.command(ns, cmd, getReadPreference(options), callback);
}

define.classMethod('command', {callback: true, promise:false});

// Insert
Mongos.prototype.insert = function(ns, ops, options, callback) {
  this.s.mongos.insert(ns, ops, options, function(e, m) {
    callback(e, m)
  });
}

define.classMethod('insert', {callback: true, promise:false});

// Update
Mongos.prototype.update = function(ns, ops, options, callback) {
  this.s.mongos.update(ns, ops, options, callback);
}

define.classMethod('update', {callback: true, promise:false});

// Remove
Mongos.prototype.remove = function(ns, ops, options, callback) {
  this.s.mongos.remove(ns, ops, options, callback);
}

define.classMethod('remove', {callback: true, promise:false});

// Destroyed
Mongos.prototype.isDestroyed = function() {
  return this.s.mongos.isDestroyed();
}

// IsConnected
Mongos.prototype.isConnected = function() {
  return this.s.mongos.isConnected();
}

define.classMethod('isConnected', {callback: false, promise:false, returns: [Boolean]});

// Insert
Mongos.prototype.cursor = function(ns, cmd, options) {
  options.disconnectHandler = this.s.store;
  return this.s.mongos.cursor(ns, cmd, options);
}

define.classMethod('cursor', {callback: false, promise:false, returns: [Cursor, AggregationCursor, CommandCursor]});

Mongos.prototype.lastIsMaster = function() {
  return this.s.mongos.lastIsMaster();
}

/**
 * Unref all sockets
 * @method
 */
Mongos.prototype.unref = function () {
  return this.s.mongos.unref();
}

Mongos.prototype.close = function(forceClosed) {
  this.s.mongos.destroy({
    force: typeof forceClosed == 'boolean' ? forceClosed : false,
  });
  // We need to wash out all stored processes
  if(forceClosed == true) {
    this.s.storeOptions.force = forceClosed;
    this.s.store.flush();
  }
}

define.classMethod('close', {callback: false, promise:false});

Mongos.prototype.auth = function() {
  var args = Array.prototype.slice.call(arguments, 0);
  this.s.mongos.auth.apply(this.s.mongos, args);
}

define.classMethod('auth', {callback: true, promise:false});

Mongos.prototype.logout = function() {
  var args = Array.prototype.slice.call(arguments, 0);
  this.s.mongos.logout.apply(this.s.mongos, args);
}

define.classMethod('logout', {callback: true, promise:false});

/**
 * All raw connections
 * @method
 * @return {array}
 */
Mongos.prototype.connections = function() {
  return this.s.mongos.connections();
}

define.classMethod('connections', {callback: false, promise:false, returns:[Array]});

/**
 * A mongos connect event, used to verify that the connection is up and running
 *
 * @event Mongos#connect
 * @type {Mongos}
 */

/**
 * The mongos high availability event
 *
 * @event Mongos#ha
 * @type {function}
 * @param {string} type The stage in the high availability event (start|end)
 * @param {boolean} data.norepeat This is a repeating high availability process or a single execution only
 * @param {number} data.id The id for this high availability request
 * @param {object} data.state An object containing the information about the current replicaset
 */

/**
 * A server member left the mongos set
 *
 * @event Mongos#left
 * @type {function}
 * @param {string} type The type of member that left (primary|secondary|arbiter)
 * @param {Server} server The server object that left
 */

/**
 * A server member joined the mongos set
 *
 * @event Mongos#joined
 * @type {function}
 * @param {string} type The type of member that joined (primary|secondary|arbiter)
 * @param {Server} server The server object that joined
 */

/**
 * Mongos fullsetup event, emitted when all proxies in the topology have been connected to.
 *
 * @event Mongos#fullsetup
 * @type {Mongos}
 */

/**
 * Mongos open event, emitted when mongos can start processing commands.
 *
 * @event Mongos#open
 * @type {Mongos}
 */

/**
 * Mongos close event
 *
 * @event Mongos#close
 * @type {object}
 */

/**
 * Mongos error event, emitted if there is an error listener.
 *
 * @event Mongos#error
 * @type {MongoError}
 */

/**
 * Mongos timeout event
 *
 * @event Mongos#timeout
 * @type {object}
 */

/**
 * Mongos parseError event
 *
 * @event Mongos#parseError
 * @type {object}
 */

module.exports = Mongos;
