"use strict"

var inherits = require('util').inherits,
  f = require('util').format,
  EventEmitter = require('events').EventEmitter,
  ReadPreference = require('./read_preference'),
  Logger = require('../connection/logger'),
  debugOptions = require('../connection/utils').debugOptions,
  retrieveBSON = require('../connection/utils').retrieveBSON,
  Pool = require('../connection/pool'),
  Query = require('../connection/commands').Query,
  MongoError = require('../error'),
  PreTwoSixWireProtocolSupport = require('../wireprotocol/2_4_support'),
  TwoSixWireProtocolSupport = require('../wireprotocol/2_6_support'),
  ThreeTwoWireProtocolSupport = require('../wireprotocol/3_2_support'),
  BasicCursor = require('../cursor'),
  sdam = require('./shared'),
  assign = require('../utils').assign,
  createClientInfo = require('./shared').createClientInfo;

// Used for filtering out fields for loggin
var debugFields = ['reconnect', 'reconnectTries', 'reconnectInterval', 'emitError', 'cursorFactory', 'host'
  , 'port', 'size', 'keepAlive', 'keepAliveInitialDelay', 'noDelay', 'connectionTimeout', 'checkServerIdentity'
  , 'socketTimeout', 'singleBufferSerializtion', 'ssl', 'ca', 'crl', 'cert', 'key', 'rejectUnauthorized', 'promoteLongs', 'promoteValues'
  , 'promoteBuffers', 'servername'];

// Server instance id
var id = 0;
var serverAccounting = false;
var servers = {};
var BSON = retrieveBSON();

/**
 * Creates a new Server instance
 * @class
 * @param {boolean} [options.reconnect=true] Server will attempt to reconnect on loss of connection
 * @param {number} [options.reconnectTries=30] Server attempt to reconnect #times
 * @param {number} [options.reconnectInterval=1000] Server will wait # milliseconds between retries
 * @param {number} [options.monitoring=true] Enable the server state monitoring (calling ismaster at monitoringInterval)
 * @param {number} [options.monitoringInterval=5000] The interval of calling ismaster when monitoring is enabled.
 * @param {Cursor} [options.cursorFactory=Cursor] The cursor factory class used for all query cursors
 * @param {string} options.host The server host
 * @param {number} options.port The server port
 * @param {number} [options.size=5] Server connection pool size
 * @param {boolean} [options.keepAlive=true] TCP Connection keep alive enabled
 * @param {number} [options.keepAliveInitialDelay=300000] Initial delay before TCP keep alive enabled
 * @param {boolean} [options.noDelay=true] TCP Connection no delay
 * @param {number} [options.connectionTimeout=30000] TCP Connection timeout setting
 * @param {number} [options.socketTimeout=360000] TCP Socket timeout setting
 * @param {boolean} [options.ssl=false] Use SSL for connection
 * @param {boolean|function} [options.checkServerIdentity=true] Ensure we check server identify during SSL, set to false to disable checking. Only works for Node 0.12.x or higher. You can pass in a boolean or your own checkServerIdentity override function.
 * @param {Buffer} [options.ca] SSL Certificate store binary buffer
 * @param {Buffer} [options.crl] SSL Certificate revocation store binary buffer
 * @param {Buffer} [options.cert] SSL Certificate binary buffer
 * @param {Buffer} [options.key] SSL Key file binary buffer
 * @param {string} [options.passphrase] SSL Certificate pass phrase
 * @param {boolean} [options.rejectUnauthorized=true] Reject unauthorized server certificates
 * @param {string} [options.servername=null] String containing the server name requested via TLS SNI.
 * @param {boolean} [options.promoteLongs=true] Convert Long values from the db into Numbers if they fit into 53 bits
 * @param {boolean} [options.promoteValues=true] Promotes BSON values to native types where possible, set to false to only receive wrapper types.
 * @param {boolean} [options.promoteBuffers=false] Promotes Binary BSON values to native Node Buffers.
 * @param {string} [options.appname=null] Application name, passed in on ismaster call and logged in mongod server logs. Maximum size 128 bytes.
 * @param {boolean} [options.domainsEnabled=false] Enable the wrapping of the callback in the current domain, disabled by default to avoid perf hit.
 * @return {Server} A cursor instance
 * @fires Server#connect
 * @fires Server#close
 * @fires Server#error
 * @fires Server#timeout
 * @fires Server#parseError
 * @fires Server#reconnect
 * @fires Server#reconnectFailed
 * @fires Server#serverHeartbeatStarted
 * @fires Server#serverHeartbeatSucceeded
 * @fires Server#serverHeartbeatFailed
 * @fires Server#topologyOpening
 * @fires Server#topologyClosed
 * @fires Server#topologyDescriptionChanged
 * @property {string} type the topology type.
 * @property {string} parserType the parser type used (c++ or js).
 */
var Server = function(options) {
  options = options || {};

  // Add event listener
  EventEmitter.call(this);

  // Server instance id
  this.id = id++;

  // Internal state
  this.s = {
    // Options
    options: options,
    // Logger
    logger: Logger('Server', options),
    // Factory overrides
    Cursor: options.cursorFactory || BasicCursor,
    // BSON instance
    bson: options.bson || new BSON([BSON.Binary, BSON.Code, BSON.DBRef, BSON.Decimal128,
      BSON.Double, BSON.Int32, BSON.Long, BSON.Map, BSON.MaxKey, BSON.MinKey,
      BSON.ObjectId, BSON.BSONRegExp, BSON.Symbol, BSON.Timestamp]),
    // Pool
    pool: null,
    // Disconnect handler
    disconnectHandler: options.disconnectHandler,
    // Monitor thread (keeps the connection alive)
    monitoring: typeof options.monitoring == 'boolean' ? options.monitoring : true,
    // Is the server in a topology
    inTopology: typeof options.inTopology == 'boolean' ? options.inTopology : false,
    // Monitoring timeout
    monitoringInterval: typeof options.monitoringInterval == 'number'
      ? options.monitoringInterval
      : 5000,
    // Topology id
    topologyId: -1
  }

  // Curent ismaster
  this.ismaster = null;
  // Current ping time
  this.lastIsMasterMS = -1;
  // The monitoringProcessId
  this.monitoringProcessId = null;
  // Initial connection
  this.initalConnect = true;
  // Wire protocol handler, default to oldest known protocol handler
  // this gets changed when the first ismaster is called.
  this.wireProtocolHandler = new PreTwoSixWireProtocolSupport();
  // Default type
  this._type = 'server';
  // Set the client info
  this.clientInfo = createClientInfo(options);

  // Max Stalleness values
  // last time we updated the ismaster state
  this.lastUpdateTime = 0;
  // Last write time
  this.lastWriteDate = 0;
  // Stalleness
  this.staleness = 0;
}

inherits(Server, EventEmitter);

Object.defineProperty(Server.prototype, 'type', {
  enumerable:true, get: function() { return this._type; }
});

Object.defineProperty(Server.prototype, 'parserType', {
  enumerable:true, get: function() {
    return BSON.native ? "c++" : "js";
  }
});

Server.enableServerAccounting = function() {
  serverAccounting = true;
  servers = {};
}

Server.disableServerAccounting = function() {
  serverAccounting = false;
}

Server.servers = function() {
  return servers;
}

Object.defineProperty(Server.prototype, 'name', {
  enumerable:true,
  get: function() { return this.s.options.host + ":" + this.s.options.port; }
});

function configureWireProtocolHandler(self, ismaster) {
  // 3.2 wire protocol handler
  if(ismaster.maxWireVersion >= 4) {
    return new ThreeTwoWireProtocolSupport(new TwoSixWireProtocolSupport());
  }

  // 2.6 wire protocol handler
  if(ismaster.maxWireVersion >= 2) {
    return new TwoSixWireProtocolSupport();
  }

  // 2.4 or earlier wire protocol handler
  return new PreTwoSixWireProtocolSupport();
}

function disconnectHandler(self, type, ns, cmd, options, callback) {
  // Topology is not connected, save the call in the provided store to be
  // Executed at some point when the handler deems it's reconnected
  if(!self.s.pool.isConnected() && self.s.options.reconnect && self.s.disconnectHandler != null && !options.monitoring) {
    self.s.disconnectHandler.add(type, ns, cmd, options, callback);
    return true;
  }

  // If we have no connection error
  if(!self.s.pool.isConnected()) {
    callback(MongoError.create(f("no connection available to server %s", self.name)));
    return true;
  }
}

function monitoringProcess(self) {
  return function() {
    // Pool was destroyed do not continue process
    if(self.s.pool.isDestroyed()) return;
    // Emit monitoring Process event
    self.emit('monitoring', self);
    // Perform ismaster call
    // Query options
    var queryOptions = { numberToSkip: 0, numberToReturn: -1, checkKeys: false, slaveOk: true };
    // Create a query instance
    var query = new Query(self.s.bson, 'admin.$cmd', {ismaster:true}, queryOptions);
    // Get start time
    var start = new Date().getTime();

    // Execute the ismaster query
    self.s.pool.write(query, {
      socketTimeout: (typeof self.s.options.connectionTimeout !== 'number') ? 2000 : self.s.options.connectionTimeout,
      monitoring: true,
    }, function(err, result) {
      // Set initial lastIsMasterMS
      self.lastIsMasterMS = new Date().getTime() - start;
      if(self.s.pool.isDestroyed()) return;
      // Update the ismaster view if we have a result
      if(result) {
        self.ismaster = result.result;
      }
      // Re-schedule the monitoring process
      self.monitoringProcessId = setTimeout(monitoringProcess(self), self.s.monitoringInterval);
    });
  }
}

var eventHandler = function(self, event) {
  return function(err) {
    // Log information of received information if in info mode
    if(self.s.logger.isInfo()) {
      var object = err instanceof MongoError ? JSON.stringify(err) : {}
      self.s.logger.info(f('server %s fired event %s out with message %s'
        , self.name, event, object));
    }

    // Handle connect event
    if(event == 'connect') {
      // Issue an ismaster command at connect
      // Query options
      var queryOptions = { numberToSkip: 0, numberToReturn: -1, checkKeys: false, slaveOk: true };
      // Create a query instance
      var query = new Query(self.s.bson, 'admin.$cmd', {ismaster:true, client: self.clientInfo}, queryOptions);
      // Get start time
      var start = new Date().getTime();
      // Execute the ismaster query
      self.s.pool.write(query, {
        socketTimeout: self.s.options.connectionTimeout || 2000,
      }, function(err, result) {
        // Set initial lastIsMasterMS
        self.lastIsMasterMS = new Date().getTime() - start;
        if(err) {
          self.destroy();
          if(self.listeners('error').length > 0) self.emit('error', err);
          return;
        }

        // Ensure no error emitted after initial connect when reconnecting
        self.initalConnect = false;
        // Save the ismaster
        self.ismaster = result.result;

        // It's a proxy change the type so
        // the wireprotocol will send $readPreference
        if(self.ismaster.msg == 'isdbgrid') {
          self._type = 'mongos';
        }
        // Add the correct wire protocol handler
        self.wireProtocolHandler = configureWireProtocolHandler(self, self.ismaster);
        // Have we defined self monitoring
        if(self.s.monitoring) {
          self.monitoringProcessId = setTimeout(monitoringProcess(self), self.s.monitoringInterval);
        }

        // Emit server description changed if something listening
        sdam.emitServerDescriptionChanged(self, {
          address: self.name, arbiters: [], hosts: [], passives: [], type: sdam.getTopologyType(self)
        });

        if(!self.s.inTopology) {
          // Emit topology description changed if something listening
          sdam.emitTopologyDescriptionChanged(self, {
            topologyType: 'Single', servers: [{address: self.name, arbiters: [], hosts: [], passives: [], type: sdam.getTopologyType(self)}]
          });
        }

        // Log the ismaster if available
        if(self.s.logger.isInfo()) {
          self.s.logger.info(f('server %s connected with ismaster [%s]', self.name, JSON.stringify(self.ismaster)));
        }

        // Emit connect
        self.emit('connect', self);
      });
    } else if(event == 'error' || event == 'parseError'
      || event == 'close' || event == 'timeout' || event == 'reconnect'
      || event == 'attemptReconnect' || 'reconnectFailed') {
      // Remove server instance from accounting
      if(serverAccounting && ['close', 'timeout', 'error', 'parseError', 'reconnectFailed'].indexOf(event) != -1) {
        // Emit toplogy opening event if not in topology
        if(!self.s.inTopology) {
          self.emit('topologyOpening', { topologyId: self.id });
        }

        delete servers[self.id];
      }

      if (event === 'close') {
        // Closing emits a server description changed event going to unknown.
        sdam.emitServerDescriptionChanged(self, {
          address: self.name, arbiters: [], hosts: [], passives: [], type: 'Unknown'
        });
      }

      // Reconnect failed return error
      if(event == 'reconnectFailed') {
        self.emit('reconnectFailed', err);
        // Emit error if any listeners
        if(self.listeners('error').length > 0) {
          self.emit('error', err);
        }
        // Terminate
        return;
      }

      // On first connect fail
      if(self.s.pool.state == 'disconnected' && self.initalConnect && ['close', 'timeout', 'error', 'parseError'].indexOf(event) != -1) {
        self.initalConnect = false;
        return self.emit('error', new MongoError(f('failed to connect to server [%s] on first connect [%s]', self.name, err)));
      }

      // Reconnect event, emit the server
      if(event == 'reconnect') {
        // Reconnecting emits a server description changed event going from unknown to the
        // current server type.
        sdam.emitServerDescriptionChanged(self, {
          address: self.name, arbiters: [], hosts: [], passives: [], type: sdam.getTopologyType(self)
        });
        return self.emit(event, self);
      }

      // Emit the event
      self.emit(event, err);
    }
  }
}

/**
 * Initiate server connect
 * @method
 * @param {array} [options.auth=null] Array of auth options to apply on connect
 */
Server.prototype.connect = function(options) {
  var self = this;
  options = options || {};

  // Set the connections
  if(serverAccounting) servers[this.id] = this;

  // Do not allow connect to be called on anything that's not disconnected
  if(self.s.pool && !self.s.pool.isDisconnected() && !self.s.pool.isDestroyed()) {
    throw MongoError.create(f('server instance in invalid state %s', self.s.pool.state));
  }

  // Create a pool
  self.s.pool = new Pool(assign(self.s.options, options, {bson: this.s.bson}));

  // Set up listeners
  self.s.pool.on('close', eventHandler(self, 'close'));
  self.s.pool.on('error', eventHandler(self, 'error'));
  self.s.pool.on('timeout', eventHandler(self, 'timeout'));
  self.s.pool.on('parseError', eventHandler(self, 'parseError'));
  self.s.pool.on('connect', eventHandler(self, 'connect'));
  self.s.pool.on('reconnect', eventHandler(self, 'reconnect'));
  self.s.pool.on('reconnectFailed', eventHandler(self, 'reconnectFailed'));

  // Emit toplogy opening event if not in topology
  if(!self.s.inTopology) {
    this.emit('topologyOpening', { topologyId: self.id });
  }

  // Emit opening server event
  self.emit('serverOpening', {
    topologyId: self.s.topologyId != -1 ? self.s.topologyId : self.id,
    address: self.name
  });

  // Connect with optional auth settings
  if(options.auth) {
    self.s.pool.connect.apply(self.s.pool, options.auth);
  } else {
    self.s.pool.connect();
  }
}

/**
 * Get the server description
 * @method
 * @return {object}
*/
Server.prototype.getDescription = function() {
  var ismaster = this.ismaster || {};
  var description = {
    type: sdam.getTopologyType(this),
    address: this.name,
  };

  // Add fields if available
  if(ismaster.hosts) description.hosts = ismaster.hosts;
  if(ismaster.arbiters) description.arbiters = ismaster.arbiters;
  if(ismaster.passives) description.passives = ismaster.passives;
  if(ismaster.setName) description.setName = ismaster.setName;
  return description;
}

/**
 * Returns the last known ismaster document for this server
 * @method
 * @return {object}
 */
Server.prototype.lastIsMaster = function() {
  return this.ismaster;
}

/**
 * Unref all connections belong to this server
 * @method
 */
Server.prototype.unref = function() {
  this.s.pool.unref();
}

/**
 * Figure out if the server is connected
 * @method
 * @return {boolean}
 */
Server.prototype.isConnected = function() {
  if(!this.s.pool) return false;
  return this.s.pool.isConnected();
}

/**
 * Figure out if the server instance was destroyed by calling destroy
 * @method
 * @return {boolean}
 */
Server.prototype.isDestroyed = function() {
  if(!this.s.pool) return false;
  return this.s.pool.isDestroyed();
}

function basicWriteValidations(self) {
  if(!self.s.pool) return MongoError.create('server instance is not connected');
  if(self.s.pool.isDestroyed()) return MongoError.create('server instance pool was destroyed');
}

function basicReadValidations(self, options) {
  basicWriteValidations(self, options);

  if(options.readPreference && !(options.readPreference instanceof ReadPreference)) {
    throw new Error("readPreference must be an instance of ReadPreference");
  }
}

/**
 * Execute a command
 * @method
 * @param {string} ns The MongoDB fully qualified namespace (ex: db1.collection1)
 * @param {object} cmd The command hash
 * @param {ReadPreference} [options.readPreference] Specify read preference if command supports it
 * @param {Boolean} [options.serializeFunctions=false] Specify if functions on an object should be serialized.
 * @param {Boolean} [options.checkKeys=false] Specify if the bson parser should validate keys.
 * @param {Boolean} [options.ignoreUndefined=false] Specify if the BSON serializer should ignore undefined fields.
 * @param {Boolean} [options.fullResult=false] Return the full envelope instead of just the result document.
 * @param {opResultCallback} callback A callback function
 */
Server.prototype.command = function(ns, cmd, options, callback) {
  var self = this;
  if(typeof options == 'function') callback = options, options = {}, options = options || {};
  var result = basicReadValidations(self, options);
  if(result) return callback(result);

  // Clone the options
  options = assign({}, options, { wireProtocolCommand: false });

  // Debug log
  if(self.s.logger.isDebug()) self.s.logger.debug(f('executing command [%s] against %s', JSON.stringify({
    ns: ns, cmd: cmd, options: debugOptions(debugFields, options)
  }), self.name));

  // If we are not connected or have a disconnectHandler specified
  if(disconnectHandler(self, 'command', ns, cmd, options, callback)) return;

  // Check if we have collation support
  if(this.ismaster && this.ismaster.maxWireVersion < 5 && cmd.collation) {
    return callback(new MongoError(f('server %s does not support collation', this.name)));
  }

  // Query options
  var queryOptions = {
    numberToSkip: 0,
    numberToReturn: -1,
    checkKeys: typeof options.checkKeys == 'boolean' ? options.checkKeys: false,
    serializeFunctions: typeof options.serializeFunctions == 'boolean' ? options.serializeFunctions : false,
    ignoreUndefined: typeof options.ignoreUndefined == 'boolean' ? options.ignoreUndefined : false
  };

  // Are we executing against a specific topology
  var topology = options.topology || {};
  // Create the query object
  var query = self.wireProtocolHandler.command(self.s.bson, ns, cmd, {}, topology, options);
  // Set slave OK of the query
  query.slaveOk = options.readPreference ? options.readPreference.slaveOk() : false;

  // Write options
  var writeOptions = {
    raw: typeof options.raw == 'boolean' ? options.raw : false,
    promoteLongs: typeof options.promoteLongs == 'boolean' ? options.promoteLongs : true,
    promoteValues: typeof options.promoteValues == 'boolean' ? options.promoteValues : true,
    promoteBuffers: typeof options.promoteBuffers == 'boolean' ? options.promoteBuffers : false,
    command: true,
    monitoring: typeof options.monitoring == 'boolean' ? options.monitoring : false,
    fullResult: typeof options.fullResult == 'boolean' ? options.fullResult : false,
    requestId: query.requestId,
    socketTimeout: typeof options.socketTimeout == 'number' ? options.socketTimeout : null,
  };

  // Write the operation to the pool
  self.s.pool.write(query, writeOptions, callback);
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
Server.prototype.insert = function(ns, ops, options, callback) {
  var self = this;
  if(typeof options == 'function') callback = options, options = {}, options = options || {};
  var result = basicWriteValidations(self, options);
  if(result) return callback(result);

  // If we are not connected or have a disconnectHandler specified
  if(disconnectHandler(self, 'insert', ns, ops, options, callback)) return;

  // Setup the docs as an array
  ops = Array.isArray(ops) ? ops : [ops];

  // Execute write
  return self.wireProtocolHandler.insert(self.s.pool, self.ismaster, ns, self.s.bson, ops, options, callback);
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
Server.prototype.update = function(ns, ops, options, callback) {
  var self = this;
  if(typeof options == 'function') callback = options, options = {}, options = options || {};
  var result = basicWriteValidations(self, options);
  if(result) return callback(result);

  // If we are not connected or have a disconnectHandler specified
  if(disconnectHandler(self, 'update', ns, ops, options, callback)) return;

  // Check if we have collation support
  if(this.ismaster && this.ismaster.maxWireVersion < 5 && options.collation) {
    return callback(new MongoError(f('server %s does not support collation', this.name)));
  }

  // Setup the docs as an array
  ops = Array.isArray(ops) ? ops : [ops];
  // Execute write
  return self.wireProtocolHandler.update(self.s.pool, self.ismaster, ns, self.s.bson, ops, options, callback);
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
Server.prototype.remove = function(ns, ops, options, callback) {
  var self = this;
  if(typeof options == 'function') callback = options, options = {}, options = options || {};
  var result = basicWriteValidations(self, options);
  if(result) return callback(result);

  // If we are not connected or have a disconnectHandler specified
  if(disconnectHandler(self, 'remove', ns, ops, options, callback)) return;

  // Check if we have collation support
  if(this.ismaster && this.ismaster.maxWireVersion < 5 && options.collation) {
    return callback(new MongoError(f('server %s does not support collation', this.name)));
  }

  // Setup the docs as an array
  ops = Array.isArray(ops) ? ops : [ops];
  // Execute write
  return self.wireProtocolHandler.remove(self.s.pool, self.ismaster, ns, self.s.bson, ops, options, callback);
}

/**
 * Get a new cursor
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
Server.prototype.cursor = function(ns, cmd, cursorOptions) {
  var s = this.s;
  cursorOptions = cursorOptions || {};
  // Set up final cursor type
  var FinalCursor = cursorOptions.cursorFactory || s.Cursor;
  // Return the cursor
  return new FinalCursor(s.bson, ns, cmd, cursorOptions, this, s.options);
}

/**
 * Logout from a database
 * @method
 * @param {string} db The db we are logging out from
 * @param {authResultCallback} callback A callback function
 */
Server.prototype.logout = function(dbName, callback) {
  this.s.pool.logout(dbName, callback);
}

/**
 * Authenticate using a specified mechanism
 * @method
 * @param {string} mechanism The Auth mechanism we are invoking
 * @param {string} db The db we are invoking the mechanism against
 * @param {...object} param Parameters for the specific mechanism
 * @param {authResultCallback} callback A callback function
 */
Server.prototype.auth = function(mechanism, db) {
  var self = this;

  // If we have the default mechanism we pick mechanism based on the wire
  // protocol max version. If it's >= 3 then scram-sha1 otherwise mongodb-cr
  if(mechanism == 'default' && self.ismaster && self.ismaster.maxWireVersion >= 3) {
    mechanism = 'scram-sha-1';
  } else if(mechanism == 'default') {
    mechanism = 'mongocr';
  }

  // Slice all the arguments off
  var args = Array.prototype.slice.call(arguments, 0);
  // Set the mechanism
  args[0] = mechanism;
  // Get the callback
  var callback = args[args.length - 1];

  // If we are not connected or have a disconnectHandler specified
  if(disconnectHandler(self, 'auth', db, args, {}, callback)) {
    return;
  }

  // Do not authenticate if we are an arbiter
  if(this.lastIsMaster() && this.lastIsMaster().arbiterOnly) {
    return callback(null, true);
  }

  // Apply the arguments to the pool
  self.s.pool.auth.apply(self.s.pool, args);
}

/**
 * Compare two server instances
 * @method
 * @param {Server} server Server to compare equality against
 * @return {boolean}
 */
Server.prototype.equals = function(server) {
  if(typeof server == 'string') return this.name.toLowerCase() == server.toLowerCase();
  if(server.name) return this.name.toLowerCase() == server.name.toLowerCase();
  return false;
}

/**
 * All raw connections
 * @method
 * @return {Connection[]}
 */
Server.prototype.connections = function() {
  return this.s.pool.allConnections();
}

/**
 * Get server
 * @method
 * @return {Server}
 */
Server.prototype.getServer = function() {
  return this;
}

/**
 * Get connection
 * @method
 * @return {Connection}
 */
Server.prototype.getConnection = function() {
  return this.s.pool.get();
}

var listeners = ['close', 'error', 'timeout', 'parseError', 'connect'];

/**
 * Destroy the server connection
 * @method
 * @param {boolean} [options.emitClose=false] Emit close event on destroy
 * @param {boolean} [options.emitDestroy=false] Emit destroy event on destroy
 * @param {boolean} [options.force=false] Force destroy the pool
 */
Server.prototype.destroy = function(options) {
  options = options || {};
  var self = this;

  // Set the connections
  if(serverAccounting) delete servers[this.id];

  // Destroy the monitoring process if any
  if(this.monitoringProcessId) {
    clearTimeout(this.monitoringProcessId);
  }

  // No pool, return
  if(!self.s.pool) return;

  // Emit close event
  if(options.emitClose) {
    self.emit('close', self);
  }

  // Emit destroy event
  if(options.emitDestroy) {
    self.emit('destroy', self);
  }

  // Remove all listeners
  listeners.forEach(function(event) {
    self.s.pool.removeAllListeners(event);
  });

  // Emit opening server event
  if(self.listeners('serverClosed').length > 0) self.emit('serverClosed', {
    topologyId: self.s.topologyId != -1 ? self.s.topologyId : self.id, address: self.name
  });

  // Emit toplogy opening event if not in topology
  if(self.listeners('topologyClosed').length > 0 && !self.s.inTopology) {
    self.emit('topologyClosed', { topologyId: self.id });
  }

  if(self.s.logger.isDebug()) {
    self.s.logger.debug(f('destroy called on server %s', self.name));
  }

  // Destroy the pool
  this.s.pool.destroy(options.force);
}

/**
 * A server connect event, used to verify that the connection is up and running
 *
 * @event Server#connect
 * @type {Server}
 */

/**
 * A server reconnect event, used to verify that the server topology has reconnected
 *
 * @event Server#reconnect
 * @type {Server}
 */

/**
 * A server opening SDAM monitoring event
 *
 * @event Server#serverOpening
 * @type {object}
 */

/**
 * A server closed SDAM monitoring event
 *
 * @event Server#serverClosed
 * @type {object}
 */

/**
 * A server description SDAM change monitoring event
 *
 * @event Server#serverDescriptionChanged
 * @type {object}
 */

/**
 * A topology open SDAM event
 *
 * @event Server#topologyOpening
 * @type {object}
 */

/**
 * A topology closed SDAM event
 *
 * @event Server#topologyClosed
 * @type {object}
 */

/**
 * A topology structure SDAM change event
 *
 * @event Server#topologyDescriptionChanged
 * @type {object}
 */

/**
 * Server reconnect failed
 *
 * @event Server#reconnectFailed
 * @type {Error}
 */

/**
 * Server connection pool closed
 *
 * @event Server#close
 * @type {object}
 */

/**
 * Server connection pool caused an error
 *
 * @event Server#error
 * @type {Error}
 */

/**
 * Server destroyed was called
 *
 * @event Server#destroy
 * @type {Server}
 */

module.exports = Server;
