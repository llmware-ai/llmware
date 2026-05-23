"use strict";

var Query = require('../connection/commands').Query
  , retrieveBSON = require('../connection/utils').retrieveBSON
  , f = require('util').format
  , MongoError = require('../error')
  , getReadPreference = require('./shared').getReadPreference;

var BSON = retrieveBSON(),
  Long = BSON.Long;

var WireProtocol = function(legacyWireProtocol) {
  this.legacyWireProtocol = legacyWireProtocol;
}

//
// Execute a write operation
var executeWrite = function(pool, bson, type, opsField, ns, ops, options, callback) {
  if(ops.length == 0) throw new MongoError("insert must contain at least one document");
  if(typeof options == 'function') {
    callback = options;
    options = {};
    options = options || {};
  }

  // Split the ns up to get db and collection
  var p = ns.split(".");
  var d = p.shift();
  // Options
  var ordered = typeof options.ordered == 'boolean' ? options.ordered : true;
  var writeConcern = options.writeConcern;

  // return skeleton
  var writeCommand = {};
  writeCommand[type] = p.join('.');
  writeCommand[opsField] = ops;
  writeCommand.ordered = ordered;

  // Did we specify a write concern
  if(writeConcern && Object.keys(writeConcern).length > 0) {
    writeCommand.writeConcern = writeConcern;
  }

  // If we have collation passed in
  if(options.collation) {
    for(var i = 0; i < writeCommand[opsField].length; i++) {
      if(!writeCommand[opsField][i].collation) {
        writeCommand[opsField][i].collation = options.collation;
      }
    }
  }

  // Do we have bypassDocumentValidation set, then enable it on the write command
  if(typeof options.bypassDocumentValidation == 'boolean') {
    writeCommand.bypassDocumentValidation = options.bypassDocumentValidation;
  }

  // Options object
  var opts = { command: true };
  var queryOptions = { checkKeys : false, numberToSkip: 0, numberToReturn: 1 };
  if(type == 'insert') queryOptions.checkKeys = true;
  if(typeof options.checkKeys == 'boolean') queryOptions.checkKeys = options.checkKeys;

  // Ensure we support serialization of functions
  if(options.serializeFunctions) queryOptions.serializeFunctions = options.serializeFunctions;
  // Do not serialize the undefined fields
  if(options.ignoreUndefined) queryOptions.ignoreUndefined = options.ignoreUndefined;

  try {
    // Create write command
    var cmd = new Query(bson, f("%s.$cmd", d), writeCommand, queryOptions);
    // Execute command
    pool.write(cmd, opts, callback);
  } catch(err) {
    callback(err);
  }
}

//
// Needs to support legacy mass insert as well as ordered/unordered legacy
// emulation
//
WireProtocol.prototype.insert = function(pool, ismaster, ns, bson, ops, options, callback) {
  executeWrite(pool, bson, 'insert', 'documents', ns, ops, options, callback);
}

WireProtocol.prototype.update = function(pool, ismaster, ns, bson, ops, options, callback) {
  executeWrite(pool, bson, 'update', 'updates', ns, ops, options, callback);
}

WireProtocol.prototype.remove = function(pool, ismaster, ns, bson, ops, options, callback) {
  executeWrite(pool, bson, 'delete', 'deletes', ns, ops, options, callback);
}

WireProtocol.prototype.killCursor = function(bson, ns, cursorId, pool, callback) {
  // Build command namespace
  var parts = ns.split(/\./);
  // Command namespace
  var commandns = f('%s.$cmd', parts.shift());
  // Create getMore command
  var killcursorCmd = {
    killCursors: parts.join('.'),
    cursors: [cursorId]
  }

  // Build Query object
  var query = new Query(bson, commandns, killcursorCmd, {
      numberToSkip: 0, numberToReturn: -1
    , checkKeys: false, returnFieldSelector: null
  });

  // Set query flags
  query.slaveOk = true;

  // Kill cursor callback
  var killCursorCallback = function(err, result) {
    if(err) {
      if(typeof callback != 'function') return;
      return callback(err);
    }

    // Result
    var r = result.message;
    // If we have a timed out query or a cursor that was killed
    if((r.responseFlags & (1 << 0)) != 0) {
      if(typeof callback != 'function') return;
      return callback(new MongoError("cursor killed or timed out"), null);
    }

    if(!Array.isArray(r.documents) || r.documents.length == 0) {
      if(typeof callback != 'function') return;
      return callback(new MongoError(f('invalid killCursors result returned for cursor id %s', cursorId)));
    }

    // Return the result
    if(typeof callback == 'function') {
      callback(null, r.documents[0]);
    }
  }

  // Execute the kill cursor command
  if(pool && pool.isConnected()) {
    pool.write(query, {
      command: true
    }, killCursorCallback);
  }
}

WireProtocol.prototype.getMore = function(bson, ns, cursorState, batchSize, raw, connection, options, callback) {
  options = options || {};
  // Build command namespace
  var parts = ns.split(/\./);
  // Command namespace
  var commandns = f('%s.$cmd', parts.shift());

  // Create getMore command
  var getMoreCmd = {
    getMore: cursorState.cursorId,
    collection: parts.join('.'),
    batchSize: Math.abs(batchSize)
  }

  if(cursorState.cmd.tailable
    && typeof cursorState.cmd.maxAwaitTimeMS == 'number') {
    getMoreCmd.maxTimeMS = cursorState.cmd.maxAwaitTimeMS;
  }

  // Build Query object
  var query = new Query(bson, commandns, getMoreCmd, {
      numberToSkip: 0, numberToReturn: -1
    , checkKeys: false, returnFieldSelector: null
  });

  // Set query flags
  query.slaveOk = true;

  // Query callback
  var queryCallback = function(err, result) {
    if(err) return callback(err);
    // Get the raw message
    var r = result.message;

    // If we have a timed out query or a cursor that was killed
    if((r.responseFlags & (1 << 0)) != 0) {
      return callback(new MongoError("cursor killed or timed out"), null);
    }

    // Raw, return all the extracted documents
    if(raw) {
      cursorState.documents = r.documents;
      cursorState.cursorId = r.cursorId;
      return callback(null, r.documents);
    }

    // We have an error detected
    if(r.documents[0].ok == 0) {
      return callback(MongoError.create(r.documents[0]));
    }

    // Ensure we have a Long valid cursor id
    var cursorId = typeof r.documents[0].cursor.id == 'number'
      ? Long.fromNumber(r.documents[0].cursor.id)
      : r.documents[0].cursor.id;

    // Set all the values
    cursorState.documents = r.documents[0].cursor.nextBatch;
    cursorState.cursorId = cursorId;

    // Return the result
    callback(null, r.documents[0], r.connection);
  }

  // Query options
  var queryOptions = { command: true };

  // If we have a raw query decorate the function
  if(raw) {
    queryOptions.raw = raw;
  }

  // Add the result field needed
  queryOptions.documentsReturnedIn = 'nextBatch';

  // Check if we need to promote longs
  if(typeof cursorState.promoteLongs == 'boolean') {
    queryOptions.promoteLongs = cursorState.promoteLongs;
  }

  if(typeof cursorState.promoteValues == 'boolean') {
    queryOptions.promoteValues = cursorState.promoteValues;
  }

  if(typeof cursorState.promoteBuffers == 'boolean') {
    queryOptions.promoteBuffers = cursorState.promoteBuffers;
  }

  // Write out the getMore command
  connection.write(query, queryOptions, queryCallback);
}

WireProtocol.prototype.command = function(bson, ns, cmd, cursorState, topology, options) {
  options = options || {}
  // Check if this is a wire protocol command or not
  var wireProtocolCommand = typeof options.wireProtocolCommand == 'boolean' ? options.wireProtocolCommand : true;

  // Establish type of command
  if(cmd.find && wireProtocolCommand) {
    // Create the find command
    var query = executeFindCommand(bson, ns, cmd, cursorState, topology, options)
    // Mark the cmd as virtual
    cmd.virtual = false;
    // Signal the documents are in the firstBatch value
    query.documentsReturnedIn = 'firstBatch';
    // Return the query
    return query;
  } else if(cursorState.cursorId != null) {
    return;
  } else if(cmd) {
    return setupCommand(bson, ns, cmd, cursorState, topology, options);
  } else {
    throw new MongoError(f("command %s does not return a cursor", JSON.stringify(cmd)));
  }
}

// // Command
// {
//     find: ns
//   , query: <object>
//   , limit: <n>
//   , fields: <object>
//   , skip: <n>
//   , hint: <string>
//   , explain: <boolean>
//   , snapshot: <boolean>
//   , batchSize: <n>
//   , returnKey: <boolean>
//   , maxScan: <n>
//   , min: <n>
//   , max: <n>
//   , showDiskLoc: <boolean>
//   , comment: <string>
//   , maxTimeMS: <n>
//   , raw: <boolean>
//   , readPreference: <ReadPreference>
//   , tailable: <boolean>
//   , oplogReplay: <boolean>
//   , noCursorTimeout: <boolean>
//   , awaitdata: <boolean>
//   , exhaust: <boolean>
//   , partial: <boolean>
// }

// FIND/GETMORE SPEC
// {
//     “find”: <string>,
//     “filter”: { ... },
//     “sort”: { ... },
//     “projection”: { ... },
//     “hint”: { ... },
//     “skip”: <int>,
//     “limit”: <int>,
//     “batchSize”: <int>,
//     “singleBatch”: <bool>,
//     “comment”: <string>,
//     “maxScan”: <int>,
//     “maxTimeMS”: <int>,
//     “max”: { ... },
//     “min”: { ... },
//     “returnKey”: <bool>,
//     “showRecordId”: <bool>,
//     “snapshot”: <bool>,
//     “tailable”: <bool>,
//     “oplogReplay”: <bool>,
//     “noCursorTimeout”: <bool>,
//     “awaitData”: <bool>,
//     “partial”: <bool>,
//     “$readPreference”: { ... }
// }

//
// Execute a find command
var executeFindCommand = function(bson, ns, cmd, cursorState, topology, options) {
  // Ensure we have at least some options
  options = options || {};
  // Get the readPreference
  var readPreference = getReadPreference(cmd, options);
  // Set the optional batchSize
  cursorState.batchSize = cmd.batchSize || cursorState.batchSize;

  // Build command namespace
  var parts = ns.split(/\./);
  // Command namespace
  var commandns = f('%s.$cmd', parts.shift());

  // Build actual find command
  var findCmd = {
    find: parts.join('.')
  };

  // I we provided a filter
  if(cmd.query) {
    // Check if the user is passing in the $query parameter
    if(cmd.query['$query']) {
      findCmd.filter = cmd.query['$query'];
    } else {
      findCmd.filter = cmd.query;
    }
  }

  // Sort value
  var sortValue = cmd.sort;

  // Handle issue of sort being an Array
  if(Array.isArray(sortValue)) {
    var sortObject = {};

    if(sortValue.length > 0 && !Array.isArray(sortValue[0])) {
      var sortDirection = sortValue[1];
      // Translate the sort order text
      if(sortDirection == 'asc') {
        sortDirection = 1;
      } else if(sortDirection == 'desc') {
        sortDirection = -1;
      }

      // Set the sort order
      sortObject[sortValue[0]] = sortDirection;
    } else {
      for(var i = 0; i < sortValue.length; i++) {
        sortDirection = sortValue[i][1];
        // Translate the sort order text
        if(sortDirection == 'asc') {
          sortDirection = 1;
        } else if(sortDirection == 'desc') {
          sortDirection = -1;
        }

        // Set the sort order
        sortObject[sortValue[i][0]] = sortDirection;
      }
    }

    sortValue = sortObject;
  }

  // Add sort to command
  if(cmd.sort) findCmd.sort = sortValue;
  // Add a projection to the command
  if(cmd.fields) findCmd.projection = cmd.fields;
  // Add a hint to the command
  if(cmd.hint) findCmd.hint = cmd.hint;
  // Add a skip
  if(cmd.skip) findCmd.skip = cmd.skip;
  // Add a limit
  if(cmd.limit) findCmd.limit = cmd.limit;

  // Check if we wish to have a singleBatch
  if(cmd.limit < 0) {
    findCmd.limit = Math.abs(cmd.limit);
    findCmd.singleBatch = true;
  }

  // Add a batchSize
  if(typeof cmd.batchSize == 'number') {
    if (cmd.batchSize < 0) {
      if (cmd.limit != 0 && Math.abs(cmd.batchSize) < Math.abs(cmd.limit)) {
        findCmd.limit = Math.abs(cmd.batchSize);
      }

      findCmd.singleBatch = true;
    }

    findCmd.batchSize = Math.abs(cmd.batchSize);
  }

  // If we have comment set
  if(cmd.comment) findCmd.comment = cmd.comment;

  // If we have maxScan
  if(cmd.maxScan) findCmd.maxScan = cmd.maxScan;

  // If we have maxTimeMS set
  if(cmd.maxTimeMS) findCmd.maxTimeMS = cmd.maxTimeMS;

  // If we have min
  if(cmd.min) findCmd.min = cmd.min;

  // If we have max
  if(cmd.max) findCmd.max = cmd.max;

  // If we have returnKey set
  if(cmd.returnKey) findCmd.returnKey = cmd.returnKey;

  // If we have showDiskLoc set
  if(cmd.showDiskLoc) findCmd.showRecordId = cmd.showDiskLoc;

  // If we have snapshot set
  if(cmd.snapshot) findCmd.snapshot = cmd.snapshot;

  // If we have tailable set
  if(cmd.tailable) findCmd.tailable = cmd.tailable;

  // If we have oplogReplay set
  if(cmd.oplogReplay) findCmd.oplogReplay = cmd.oplogReplay;

  // If we have noCursorTimeout set
  if(cmd.noCursorTimeout) findCmd.noCursorTimeout = cmd.noCursorTimeout;

  // If we have awaitData set
  if(cmd.awaitData) findCmd.awaitData = cmd.awaitData;
  if(cmd.awaitdata) findCmd.awaitData = cmd.awaitdata;

  // If we have partial set
  if(cmd.partial) findCmd.partial = cmd.partial;

  // If we have collation passed in
  if(cmd.collation) findCmd.collation = cmd.collation;

  // If we have explain, we need to rewrite the find command
  // to wrap it in the explain command
  if(cmd.explain) {
    findCmd = {
      explain: findCmd
    }
  }

  // Did we provide a readConcern
  if(cmd.readConcern) findCmd.readConcern = cmd.readConcern;

  // Set up the serialize and ignoreUndefined fields
  var serializeFunctions = typeof options.serializeFunctions == 'boolean'
    ? options.serializeFunctions : false;
  var ignoreUndefined = typeof options.ignoreUndefined == 'boolean'
    ? options.ignoreUndefined : false;

  // We have a Mongos topology, check if we need to add a readPreference
  if(topology.type == 'mongos'
    && readPreference
    && readPreference.preference != 'primary') {
    findCmd = {
      '$query': findCmd,
      '$readPreference': readPreference.toJSON()
    };
  }

  // Build Query object
  var query = new Query(bson, commandns, findCmd, {
      numberToSkip: 0, numberToReturn: 1
    , checkKeys: false, returnFieldSelector: null
    , serializeFunctions: serializeFunctions, ignoreUndefined: ignoreUndefined
  });

  // Set query flags
  query.slaveOk = readPreference.slaveOk();

  // Return the query
  return query;
}

//
// Set up a command cursor
var setupCommand = function(bson, ns, cmd, cursorState, topology, options) {
  // Set empty options object
  options = options || {}
  // Get the readPreference
  var readPreference = getReadPreference(cmd, options);

  // Final query
  var finalCmd = {};
  for(var name in cmd) {
    finalCmd[name] = cmd[name];
  }

  // Build command namespace
  var parts = ns.split(/\./);

  // Serialize functions
  var serializeFunctions = typeof options.serializeFunctions == 'boolean'
    ? options.serializeFunctions : false;

  // Set up the serialize and ignoreUndefined fields
  var ignoreUndefined = typeof options.ignoreUndefined == 'boolean'
    ? options.ignoreUndefined : false;

  // We have a Mongos topology, check if we need to add a readPreference
  if(topology.type == 'mongos'
    && readPreference
    && readPreference.preference != 'primary') {
    finalCmd = {
      '$query': finalCmd,
      '$readPreference': readPreference.toJSON()
    };
  }

  // Build Query object
  var query = new Query(bson, f('%s.$cmd', parts.shift()), finalCmd, {
      numberToSkip: 0, numberToReturn: -1
    , checkKeys: false, serializeFunctions: serializeFunctions
    , ignoreUndefined: ignoreUndefined
  });

  // Set query flags
  query.slaveOk = readPreference.slaveOk();

  // Return the query
  return query;
}

module.exports = WireProtocol;
