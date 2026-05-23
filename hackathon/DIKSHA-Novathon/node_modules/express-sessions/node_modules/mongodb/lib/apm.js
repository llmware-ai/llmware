var EventEmitter = require('events').EventEmitter,
  inherits = require('util').inherits;

// Get prototypes
var AggregationCursor = require('./aggregation_cursor'),
  CommandCursor = require('./command_cursor'),
  OrderedBulkOperation = require('./bulk/ordered').OrderedBulkOperation,
  UnorderedBulkOperation = require('./bulk/unordered').UnorderedBulkOperation,
  GridStore = require('./gridfs/grid_store'),
  Cursor = require('./cursor'),
  Collection = require('./collection'),
  Db = require('./db');

var basicOperationIdGenerator = {
  operationId: 1,

  next: function() {
    return this.operationId++;
  }
}

var basicTimestampGenerator = {
  current: function() {
    return new Date().getTime();
  },

  duration: function(start, end) {
    return end - start;
  }
}

var senstiveCommands = ['authenticate', 'saslStart', 'saslContinue', 'getnonce',
  'createUser', 'updateUser', 'copydbgetnonce', 'copydbsaslstart', 'copydb'];

var Instrumentation = function(core, options, callback) {
  options = options || {};

  // Optional id generators
  var operationIdGenerator = options.operationIdGenerator || basicOperationIdGenerator;
  // Optional timestamp generator
  var timestampGenerator = options.timestampGenerator || basicTimestampGenerator;
  // Extend with event emitter functionality
  EventEmitter.call(this);

  // Contains all the instrumentation overloads
  this.overloads = [];

  // ---------------------------------------------------------
  //
  // Instrument prototype
  //
  // ---------------------------------------------------------

  var instrumentPrototype = function(callback) {
    var instrumentations = []

    // Classes to support
    var classes = [GridStore, OrderedBulkOperation, UnorderedBulkOperation,
      CommandCursor, AggregationCursor, Cursor, Collection, Db];

    // Add instrumentations to the available list
    for(var i = 0; i < classes.length; i++) {
      if(classes[i].define) {
        instrumentations.push(classes[i].define.generate());
      }
    }

    // Return the list of instrumentation points
    callback(null, instrumentations);
  }

  // Did the user want to instrument the prototype
  if(typeof callback == 'function') {
    instrumentPrototype(callback);
  }

  // ---------------------------------------------------------
  //
  // Server
  //
  // ---------------------------------------------------------

  // Reference
  var self = this;
  // Names of methods we need to wrap
  var methods = ['command', 'insert', 'update', 'remove'];
  // Prototype
  var proto = core.Server.prototype;
  // Core server method we are going to wrap
  methods.forEach(function(x) {
    var func = proto[x];

    // Add to overloaded methods
    self.overloads.push({proto: proto, name:x, func:func});

    // The actual prototype
    proto[x] = function() {
      var requestId = core.Query.nextRequestId();
      // Get the arguments
      var args = Array.prototype.slice.call(arguments, 0);
      var ns = args[0];
      var commandObj = args[1];
      var options = args[2] || {};
      var keys = Object.keys(commandObj);
      var commandName = keys[0];
      var db = ns.split('.')[0];

      // Get the collection
      var col = ns.split('.');
      col.shift();
      col = col.join('.');

      // Do we have a legacy insert/update/remove command
      if(x == 'insert') { //} && !this.lastIsMaster().maxWireVersion) {
        commandName = 'insert';

        // Re-write the command
        commandObj = {
          insert: col, documents: commandObj
        }

        if(options.writeConcern && Object.keys(options.writeConcern).length > 0)  {
          commandObj.writeConcern = options.writeConcern;
        }

        commandObj.ordered = options.ordered != undefined ? options.ordered : true;
      } else if(x == 'update') { // && !this.lastIsMaster().maxWireVersion) {
        commandName = 'update';

        // Re-write the command
        commandObj = {
          update: col, updates: commandObj
        }

        if(options.writeConcern && Object.keys(options.writeConcern).length > 0) {
          commandObj.writeConcern = options.writeConcern;
        }

        commandObj.ordered = options.ordered != undefined ? options.ordered : true;
      } else if(x == 'remove') { //&& !this.lastIsMaster().maxWireVersion) {
        commandName = 'delete';

        // Re-write the command
        commandObj = {
          delete: col, deletes: commandObj
        }

        if(options.writeConcern && Object.keys(options.writeConcern).length > 0) {
          commandObj.writeConcern = options.writeConcern;
        }

        commandObj.ordered = options.ordered != undefined ? options.ordered : true;
      }

      // Get the callback
      var callback = args.pop();
      // Set current callback operation id from the current context or create
      // a new one
      var ourOpId = callback.operationId || operationIdGenerator.next();

      // Get a connection reference for this server instance
      var connection = this.s.pool.get()

      // Emit the start event for the command
      var command = {
        // Returns the command.
        command: commandObj,
        // Returns the database name.
        databaseName: db,
        // Returns the command name.
        commandName: commandName,
        // Returns the driver generated request id.
        requestId: requestId,
        // Returns the driver generated operation id.
        // This is used to link events together such as bulk write operations. OPTIONAL.
        operationId: ourOpId,
        // Returns the connection id for the command. For languages that do not have this,
        // this MUST return the driver equivalent which MUST include the server address and port.
        // The name of this field is flexible to match the object that is returned from the driver.
        connectionId: connection
      };

      // Filter out any sensitive commands
      if(senstiveCommands.indexOf(commandName.toLowerCase()) != -1) {
        command.commandObj = {};
        command.commandObj[commandName] = true;
      }

      // Emit the started event
      self.emit('started', command)

      // Start time
      var startTime = timestampGenerator.current();

      // Push our handler callback
      args.push(function(err, r) {
        var endTime = timestampGenerator.current();
        var command = {
          duration: timestampGenerator.duration(startTime, endTime),
          commandName: commandName,
          requestId: requestId,
          operationId: ourOpId,
          connectionId: connection
        };

        // If we have an error
        if(err || (r && r.result && r.result.ok == 0)) {
          command.failure = err || r.result.writeErrors || r.result;

          // Filter out any sensitive commands
          if(senstiveCommands.indexOf(commandName.toLowerCase()) != -1) {
            command.failure = {};
          }

          self.emit('failed', command);
        } else if(commandObj && commandObj.writeConcern
          && commandObj.writeConcern.w == 0) {
          // If we have write concern 0
          command.reply = {ok:1};
          self.emit('succeeded', command);
        } else {
          command.reply = r && r.result ? r.result : r;

          // Filter out any sensitive commands
          if(senstiveCommands.indexOf(commandName.toLowerCase()) != -1) {
            command.reply = {};
          }

          self.emit('succeeded', command);
        }

        // Return to caller
        callback(err, r);
      });

      // Apply the call
      func.apply(this, args);
    }
  });

  // ---------------------------------------------------------
  //
  // Bulk Operations
  //
  // ---------------------------------------------------------

  // Inject ourselves into the Bulk methods
  methods = ['execute'];
  var prototypes = [
    require('./bulk/ordered').Bulk.prototype,
    require('./bulk/unordered').Bulk.prototype
  ]

  prototypes.forEach(function(proto) {
    // Core server method we are going to wrap
    methods.forEach(function(x) {
      var func = proto[x];

      // Add to overloaded methods
      self.overloads.push({proto: proto, name:x, func:func});

      // The actual prototype
      proto[x] = function() {
        // Get the arguments
        var args = Array.prototype.slice.call(arguments, 0);
        // Set an operation Id on the bulk object
        this.operationId = operationIdGenerator.next();

        // Get the callback
        var callback = args.pop();
        // If we have a callback use this
        if(typeof callback == 'function') {
          args.push(function(err, r) {
            // Return to caller
            callback(err, r);
          });

          // Apply the call
          func.apply(this, args);
        } else {
          return func.apply(this, args);
        }
      }
    });
  });

  // ---------------------------------------------------------
  //
  // Cursor
  //
  // ---------------------------------------------------------

  // Inject ourselves into the Cursor methods
  methods = ['_find', '_getmore', '_killcursor'];
  prototypes = [
    require('./cursor').prototype,
    require('./command_cursor').prototype,
    require('./aggregation_cursor').prototype
  ]

  // Command name translation
  var commandTranslation = {
    '_find': 'find', '_getmore': 'getMore', '_killcursor': 'killCursors', '_explain': 'explain'
  }

  prototypes.forEach(function(proto) {

    // Core server method we are going to wrap
    methods.forEach(function(x) {
      var func = proto[x];

      // Add to overloaded methods
      self.overloads.push({proto: proto, name:x, func:func});

      // The actual prototype
      proto[x] = function() {
        var cursor = this;
        var requestId = core.Query.nextRequestId();
        var ourOpId = operationIdGenerator.next();
        var parts = this.ns.split('.');
        var db = parts[0];

        // Get the collection
        parts.shift();
        var collection = parts.join('.');

        // Set the command
        var command = this.query;
        var cmd = this.s.cmd;

        // If we have a find method, set the operationId on the cursor
        if(x == '_find') {
          cursor.operationId = ourOpId;
        }

        // Do we have a find command rewrite it
        if(x == '_getmore') {
          command = {
            getMore: this.cursorState.cursorId,
            collection: collection,
            batchSize: cmd.batchSize
          }

          if(cmd.maxTimeMS) command.maxTimeMS = cmd.maxTimeMS;
        } else if(x == '_killcursor') {
          command = {
            killCursors: collection,
            cursors: [this.cursorState.cursorId]
          }
        } else if(cmd.find) {
          command = {
            find: collection, filter: cmd.query
          }

          if(cmd.sort) command.sort = cmd.sort;
          if(cmd.fields) command.projection = cmd.fields;
          if(cmd.limit && cmd.limit < 0) {
            command.limit = Math.abs(cmd.limit);
            command.singleBatch = true;
          } else if(cmd.limit) {
            command.limit = Math.abs(cmd.limit);
          }

          // Options
          if(cmd.skip) command.skip = cmd.skip;
          if(cmd.hint) command.hint = cmd.hint;
          if(cmd.batchSize) command.batchSize = cmd.batchSize;
          if(typeof cmd.returnKey == 'boolean') command.returnKey = cmd.returnKey;
          if(cmd.comment) command.comment = cmd.comment;
          if(cmd.min) command.min = cmd.min;
          if(cmd.max) command.max = cmd.max;
          if(cmd.maxScan) command.maxScan = cmd.maxScan;
          if(cmd.maxTimeMS) command.maxTimeMS = cmd.maxTimeMS;

          // Flags
          if(typeof cmd.awaitData == 'boolean') command.awaitData = cmd.awaitData;
          if(typeof cmd.snapshot == 'boolean') command.snapshot = cmd.snapshot;
          if(typeof cmd.tailable == 'boolean') command.tailable = cmd.tailable;
          if(typeof cmd.oplogReplay == 'boolean') command.oplogReplay = cmd.oplogReplay;
          if(typeof cmd.noCursorTimeout == 'boolean') command.noCursorTimeout = cmd.noCursorTimeout;
          if(typeof cmd.partial == 'boolean') command.partial = cmd.partial;
          if(typeof cmd.showDiskLoc == 'boolean') command.showRecordId = cmd.showDiskLoc;

          // Read Concern
          if(cmd.readConcern) command.readConcern = cmd.readConcern;

          // Override method
          if(cmd.explain) command.explain = cmd.explain;
          if(cmd.exhaust) command.exhaust = cmd.exhaust;

          // If we have a explain flag
          if(cmd.explain) {
            // Create fake explain command
            command = {
              explain: command,
              verbosity: 'allPlansExecution'
            }

            // Set readConcern on the command if available
            if(cmd.readConcern) command.readConcern = cmd.readConcern

            // Set up the _explain name for the command
            x = '_explain';
          }
        } else {
          command = cmd;
        }

        // Set up the connection
        var connectionId = null;

        // Set local connection
        if(this.connection) connectionId = this.connection;
        if(!connectionId && this.server && this.server.getConnection) connectionId = this.server.getConnection();

        // Get the command Name
        var commandName = x == '_find' ? Object.keys(command)[0] : commandTranslation[x];

        // Emit the start event for the command
        command = {
          // Returns the command.
          command: command,
          // Returns the database name.
          databaseName: db,
          // Returns the command name.
          commandName: commandName,
          // Returns the driver generated request id.
          requestId: requestId,
          // Returns the driver generated operation id.
          // This is used to link events together such as bulk write operations. OPTIONAL.
          operationId: this.operationId,
          // Returns the connection id for the command. For languages that do not have this,
          // this MUST return the driver equivalent which MUST include the server address and port.
          // The name of this field is flexible to match the object that is returned from the driver.
          connectionId: connectionId
        };

        // Get the arguments
        var args = Array.prototype.slice.call(arguments, 0);

        // Get the callback
        var callback = args.pop();

        // We do not have a callback but a Promise
        if(typeof callback == 'function' || command.commandName == 'killCursors') {
          var startTime = timestampGenerator.current();
          // Emit the started event
          self.emit('started', command)

          // Emit succeeded event with killcursor if we have a legacy protocol
          if(command.commandName == 'killCursors'
            && this.server.lastIsMaster()
            && this.server.lastIsMaster().maxWireVersion < 4) {
            // Emit the succeeded command
            command = {
              duration: timestampGenerator.duration(startTime, timestampGenerator.current()),
              commandName: commandName,
              requestId: requestId,
              operationId: cursor.operationId,
              connectionId: cursor.server.getConnection(),
              reply: [{ok:1}]
            };

            // Apply callback to the list of args
            args.push(callback);
            // Apply the call
            func.apply(this, args);
            // Emit the command
            return self.emit('succeeded', command)
          }

          // Add our callback handler
          args.push(function(err, r) {
            if(err) {
              // Command
              var command = {
                duration: timestampGenerator.duration(startTime, timestampGenerator.current()),
                commandName: commandName,
                requestId: requestId,
                operationId: ourOpId,
                connectionId: cursor.server.getConnection(),
                failure: err };

              // Emit the command
              self.emit('failed', command)
            } else {
              // Do we have a getMore
              if(commandName.toLowerCase() == 'getmore' && r == null) {
                r = {
                  cursor: {
                    id: cursor.cursorState.cursorId,
                    ns: cursor.ns,
                    nextBatch: cursor.cursorState.documents
                  }, ok:1
                }
              } else if((commandName.toLowerCase() == 'find'
                || commandName.toLowerCase() == 'aggregate'
                || commandName.toLowerCase() == 'listcollections') && r == null) {
                r = {
                  cursor: {
                    id: cursor.cursorState.cursorId,
                    ns: cursor.ns,
                    firstBatch: cursor.cursorState.documents
                  }, ok:1
                }
              } else if(commandName.toLowerCase() == 'killcursors' && r == null) {
                r = {
                  cursorsUnknown:[cursor.cursorState.lastCursorId],
                  ok:1
                }
              }

              // cursor id is zero, we can issue success command
              command = {
                duration: timestampGenerator.duration(startTime, timestampGenerator.current()),
                commandName: commandName,
                requestId: requestId,
                operationId: cursor.operationId,
                connectionId: cursor.server.getConnection(),
                reply: r && r.result ? r.result : r
              };

              // Emit the command
              self.emit('succeeded', command)
            }

            // Return
            if(!callback) return;

            // Return to caller
            callback(err, r);
          });

          // Apply the call
          func.apply(this, args);
        } else {
          // Assume promise, push back the missing value
          args.push(callback);
          // Get the promise
          var promise = func.apply(this, args);
          // Return a new promise
          return new cursor.s.promiseLibrary(function(resolve, reject) {
            var startTime = timestampGenerator.current();
            // Emit the started event
            self.emit('started', command)
            // Execute the function
            promise.then(function() {
              // cursor id is zero, we can issue success command
              var command = {
                duration: timestampGenerator.duration(startTime, timestampGenerator.current()),
                commandName: commandName,
                requestId: requestId,
                operationId: cursor.operationId,
                connectionId: cursor.server.getConnection(),
                reply: cursor.cursorState.documents
              };

              // Emit the command
              self.emit('succeeded', command)
            }).catch(function(err) {
              // Command
              var command = {
                duration: timestampGenerator.duration(startTime, timestampGenerator.current()),
                commandName: commandName,
                requestId: requestId,
                operationId: ourOpId,
                connectionId: cursor.server.getConnection(),
                failure: err };

              // Emit the command
              self.emit('failed', command)
              // reject the promise
              reject(err);
            });
          });
        }
      }
    });
  });
}

inherits(Instrumentation, EventEmitter);

Instrumentation.prototype.uninstrument = function() {
  for(var i = 0; i < this.overloads.length; i++) {
    var obj = this.overloads[i];
    obj.proto[obj.name] = obj.func;
  }

  // Remove all listeners
  this.removeAllListeners('started');
  this.removeAllListeners('succeeded');
  this.removeAllListeners('failed');
}

module.exports = Instrumentation;
