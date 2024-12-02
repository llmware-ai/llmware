"use strict";

var retrieveBSON = require('../connection/utils').retrieveBSON;
var BSON = retrieveBSON();
var Long = BSON.Long;

// Incrementing request id
var _requestId = 0;

// Wire command operation ids
var OP_QUERY = 2004;
var OP_GETMORE = 2005;
var OP_KILL_CURSORS = 2007;

// Query flags
var OPTS_TAILABLE_CURSOR = 2;
var OPTS_SLAVE = 4;
var OPTS_OPLOG_REPLAY = 8;
var OPTS_NO_CURSOR_TIMEOUT = 16;
var OPTS_AWAIT_DATA = 32;
var OPTS_EXHAUST = 64;
var OPTS_PARTIAL = 128;

// Response flags
var CURSOR_NOT_FOUND = 0;
var QUERY_FAILURE = 2;
var SHARD_CONFIG_STALE = 4;
var AWAIT_CAPABLE = 8;

/**************************************************************
 * QUERY
 **************************************************************/
var Query = function(bson, ns, query, options) {
  var self = this;
  // Basic options needed to be passed in
  if(ns == null) throw new Error("ns must be specified for query");
  if(query == null) throw new Error("query must be specified for query");

  // Validate that we are not passing 0x00 in the collection name
  if(!!~ns.indexOf("\x00")) {
    throw new Error("namespace cannot contain a null character");
  }

  // Basic options
  this.bson = bson;
  this.ns = ns;
  this.query = query;

  // Ensure empty options
  this.options = options || {};

  // Additional options
  this.numberToSkip = options.numberToSkip || 0;
  this.numberToReturn = options.numberToReturn || 0;
  this.returnFieldSelector = options.returnFieldSelector || null;
  this.requestId = Query.getRequestId();

  // Serialization option
  this.serializeFunctions = typeof options.serializeFunctions == 'boolean' ? options.serializeFunctions : false;
  this.ignoreUndefined = typeof options.ignoreUndefined == 'boolean' ? options.ignoreUndefined : false;
  this.maxBsonSize = options.maxBsonSize || 1024 * 1024 * 16;
  this.checkKeys = typeof options.checkKeys == 'boolean' ? options.checkKeys : true;
  this.batchSize = self.numberToReturn;

  // Flags
  this.tailable = false;
  this.slaveOk = typeof options.slaveOk == 'boolean'? options.slaveOk : false;
  this.oplogReplay = false;
  this.noCursorTimeout = false;
  this.awaitData = false;
  this.exhaust = false;
  this.partial = false;
}

//
// Assign a new request Id
Query.prototype.incRequestId = function() {
  this.requestId = _requestId++;
}

//
// Assign a new request Id
Query.nextRequestId = function() {
  return _requestId + 1;
}

//
// Uses a single allocated buffer for the process, avoiding multiple memory allocations
Query.prototype.toBin = function() {
  var self = this;
  var buffers = [];
  var projection = null;

  // Set up the flags
  var flags = 0;
  if(this.tailable) {
    flags |= OPTS_TAILABLE_CURSOR;
  }

  if(this.slaveOk) {
    flags |= OPTS_SLAVE;
  }

  if(this.oplogReplay) {
    flags |= OPTS_OPLOG_REPLAY;
  }

  if(this.noCursorTimeout) {
    flags |= OPTS_NO_CURSOR_TIMEOUT;
  }

  if(this.awaitData) {
    flags |= OPTS_AWAIT_DATA;
  }

  if(this.exhaust) {
    flags |= OPTS_EXHAUST;
  }

  if(this.partial) {
    flags |= OPTS_PARTIAL;
  }

  // If batchSize is different to self.numberToReturn
  if(self.batchSize != self.numberToReturn) self.numberToReturn = self.batchSize;

  // Allocate write protocol header buffer
  var header = new Buffer(
    4 * 4 // Header
    + 4   // Flags
    + Buffer.byteLength(self.ns) + 1 // namespace
    + 4 // numberToSkip
    + 4 // numberToReturn
  );

  // Add header to buffers
  buffers.push(header);

  // Serialize the query
  var query = self.bson.serialize(this.query, {
    checkKeys: this.checkKeys,
    serializeFunctions: this.serializeFunctions,
    ignoreUndefined: this.ignoreUndefined,
  });

  // Add query document
  buffers.push(query);

  if(self.returnFieldSelector && Object.keys(self.returnFieldSelector).length > 0) {
    // Serialize the projection document
    projection = self.bson.serialize(this.returnFieldSelector, {
      checkKeys: this.checkKeys,
      serializeFunctions: this.serializeFunctions,
      ignoreUndefined: this.ignoreUndefined,
    });
    // Add projection document
    buffers.push(projection);
  }

  // Total message size
  var totalLength = header.length + query.length + (projection ? projection.length : 0);

  // Set up the index
  var index = 4;

  // Write total document length
  header[3] = (totalLength >> 24) & 0xff;
  header[2] = (totalLength >> 16) & 0xff;
  header[1] = (totalLength >> 8) & 0xff;
  header[0] = (totalLength) & 0xff;

  // Write header information requestId
  header[index + 3] = (this.requestId >> 24) & 0xff;
  header[index + 2] = (this.requestId >> 16) & 0xff;
  header[index + 1] = (this.requestId >> 8) & 0xff;
  header[index] = (this.requestId) & 0xff;
  index = index + 4;

  // Write header information responseTo
  header[index + 3] = (0 >> 24) & 0xff;
  header[index + 2] = (0 >> 16) & 0xff;
  header[index + 1] = (0 >> 8) & 0xff;
  header[index] = (0) & 0xff;
  index = index + 4;

  // Write header information OP_QUERY
  header[index + 3] = (OP_QUERY >> 24) & 0xff;
  header[index + 2] = (OP_QUERY >> 16) & 0xff;
  header[index + 1] = (OP_QUERY >> 8) & 0xff;
  header[index] = (OP_QUERY) & 0xff;
  index = index + 4;

  // Write header information flags
  header[index + 3] = (flags >> 24) & 0xff;
  header[index + 2] = (flags >> 16) & 0xff;
  header[index + 1] = (flags >> 8) & 0xff;
  header[index] = (flags) & 0xff;
  index = index + 4;

  // Write collection name
  index = index + header.write(this.ns, index, 'utf8') + 1;
  header[index - 1] = 0;

  // Write header information flags numberToSkip
  header[index + 3] = (this.numberToSkip >> 24) & 0xff;
  header[index + 2] = (this.numberToSkip >> 16) & 0xff;
  header[index + 1] = (this.numberToSkip >> 8) & 0xff;
  header[index] = (this.numberToSkip) & 0xff;
  index = index + 4;

  // Write header information flags numberToReturn
  header[index + 3] = (this.numberToReturn >> 24) & 0xff;
  header[index + 2] = (this.numberToReturn >> 16) & 0xff;
  header[index + 1] = (this.numberToReturn >> 8) & 0xff;
  header[index] = (this.numberToReturn) & 0xff;
  index = index + 4;

  // Return the buffers
  return buffers;
}

Query.getRequestId = function() {
  return ++_requestId;
}

/**************************************************************
 * GETMORE
 **************************************************************/
var GetMore = function(bson, ns, cursorId, opts) {
  opts = opts || {};
  this.numberToReturn = opts.numberToReturn || 0;
  this.requestId = _requestId++;
  this.bson = bson;
  this.ns = ns;
  this.cursorId = cursorId;
}

//
// Uses a single allocated buffer for the process, avoiding multiple memory allocations
GetMore.prototype.toBin = function() {
  var length = 4 + Buffer.byteLength(this.ns) + 1 + 4 + 8 + (4 * 4);
  // Create command buffer
  var index = 0;
  // Allocate buffer
  var _buffer = new Buffer(length);

  // Write header information
  // index = write32bit(index, _buffer, length);
  _buffer[index + 3] = (length >> 24) & 0xff;
  _buffer[index + 2] = (length >> 16) & 0xff;
  _buffer[index + 1] = (length >> 8) & 0xff;
  _buffer[index] = (length) & 0xff;
  index = index + 4;

  // index = write32bit(index, _buffer, requestId);
  _buffer[index + 3] = (this.requestId >> 24) & 0xff;
  _buffer[index + 2] = (this.requestId >> 16) & 0xff;
  _buffer[index + 1] = (this.requestId >> 8) & 0xff;
  _buffer[index] = (this.requestId) & 0xff;
  index = index + 4;

  // index = write32bit(index, _buffer, 0);
  _buffer[index + 3] = (0 >> 24) & 0xff;
  _buffer[index + 2] = (0 >> 16) & 0xff;
  _buffer[index + 1] = (0 >> 8) & 0xff;
  _buffer[index] = (0) & 0xff;
  index = index + 4;

  // index = write32bit(index, _buffer, OP_GETMORE);
  _buffer[index + 3] = (OP_GETMORE >> 24) & 0xff;
  _buffer[index + 2] = (OP_GETMORE >> 16) & 0xff;
  _buffer[index + 1] = (OP_GETMORE >> 8) & 0xff;
  _buffer[index] = (OP_GETMORE) & 0xff;
  index = index + 4;

  // index = write32bit(index, _buffer, 0);
  _buffer[index + 3] = (0 >> 24) & 0xff;
  _buffer[index + 2] = (0 >> 16) & 0xff;
  _buffer[index + 1] = (0 >> 8) & 0xff;
  _buffer[index] = (0) & 0xff;
  index = index + 4;

  // Write collection name
  index = index + _buffer.write(this.ns, index, 'utf8') + 1;
  _buffer[index - 1] = 0;

  // Write batch size
  // index = write32bit(index, _buffer, numberToReturn);
  _buffer[index + 3] = (this.numberToReturn >> 24) & 0xff;
  _buffer[index + 2] = (this.numberToReturn >> 16) & 0xff;
  _buffer[index + 1] = (this.numberToReturn >> 8) & 0xff;
  _buffer[index] = (this.numberToReturn) & 0xff;
  index = index + 4;

  // Write cursor id
  // index = write32bit(index, _buffer, cursorId.getLowBits());
  _buffer[index + 3] = (this.cursorId.getLowBits() >> 24) & 0xff;
  _buffer[index + 2] = (this.cursorId.getLowBits() >> 16) & 0xff;
  _buffer[index + 1] = (this.cursorId.getLowBits() >> 8) & 0xff;
  _buffer[index] = (this.cursorId.getLowBits()) & 0xff;
  index = index + 4;

  // index = write32bit(index, _buffer, cursorId.getHighBits());
  _buffer[index + 3] = (this.cursorId.getHighBits() >> 24) & 0xff;
  _buffer[index + 2] = (this.cursorId.getHighBits() >> 16) & 0xff;
  _buffer[index + 1] = (this.cursorId.getHighBits() >> 8) & 0xff;
  _buffer[index] = (this.cursorId.getHighBits()) & 0xff;
  index = index + 4;

  // Return buffer
  return _buffer;
}

/**************************************************************
 * KILLCURSOR
 **************************************************************/
var KillCursor = function(bson, cursorIds) {
  this.requestId = _requestId++;
  this.cursorIds = cursorIds;
}

//
// Uses a single allocated buffer for the process, avoiding multiple memory allocations
KillCursor.prototype.toBin = function() {
  var length = 4 + 4 + (4 * 4) + (this.cursorIds.length * 8);

  // Create command buffer
  var index = 0;
  var _buffer = new Buffer(length);

  // Write header information
  // index = write32bit(index, _buffer, length);
  _buffer[index + 3] = (length >> 24) & 0xff;
  _buffer[index + 2] = (length >> 16) & 0xff;
  _buffer[index + 1] = (length >> 8) & 0xff;
  _buffer[index] = (length) & 0xff;
  index = index + 4;

  // index = write32bit(index, _buffer, requestId);
  _buffer[index + 3] = (this.requestId >> 24) & 0xff;
  _buffer[index + 2] = (this.requestId >> 16) & 0xff;
  _buffer[index + 1] = (this.requestId >> 8) & 0xff;
  _buffer[index] = (this.requestId) & 0xff;
  index = index + 4;

  // index = write32bit(index, _buffer, 0);
  _buffer[index + 3] = (0 >> 24) & 0xff;
  _buffer[index + 2] = (0 >> 16) & 0xff;
  _buffer[index + 1] = (0 >> 8) & 0xff;
  _buffer[index] = (0) & 0xff;
  index = index + 4;

  // index = write32bit(index, _buffer, OP_KILL_CURSORS);
  _buffer[index + 3] = (OP_KILL_CURSORS >> 24) & 0xff;
  _buffer[index + 2] = (OP_KILL_CURSORS >> 16) & 0xff;
  _buffer[index + 1] = (OP_KILL_CURSORS >> 8) & 0xff;
  _buffer[index] = (OP_KILL_CURSORS) & 0xff;
  index = index + 4;

  // index = write32bit(index, _buffer, 0);
  _buffer[index + 3] = (0 >> 24) & 0xff;
  _buffer[index + 2] = (0 >> 16) & 0xff;
  _buffer[index + 1] = (0 >> 8) & 0xff;
  _buffer[index] = (0) & 0xff;
  index = index + 4;

  // Write batch size
  // index = write32bit(index, _buffer, this.cursorIds.length);
  _buffer[index + 3] = (this.cursorIds.length >> 24) & 0xff;
  _buffer[index + 2] = (this.cursorIds.length >> 16) & 0xff;
  _buffer[index + 1] = (this.cursorIds.length >> 8) & 0xff;
  _buffer[index] = (this.cursorIds.length) & 0xff;
  index = index + 4;

  // Write all the cursor ids into the array
  for(var i = 0; i < this.cursorIds.length; i++) {
    // Write cursor id
    // index = write32bit(index, _buffer, cursorIds[i].getLowBits());
    _buffer[index + 3] = (this.cursorIds[i].getLowBits() >> 24) & 0xff;
    _buffer[index + 2] = (this.cursorIds[i].getLowBits() >> 16) & 0xff;
    _buffer[index + 1] = (this.cursorIds[i].getLowBits() >> 8) & 0xff;
    _buffer[index] = (this.cursorIds[i].getLowBits()) & 0xff;
    index = index + 4;

    // index = write32bit(index, _buffer, cursorIds[i].getHighBits());
    _buffer[index + 3] = (this.cursorIds[i].getHighBits() >> 24) & 0xff;
    _buffer[index + 2] = (this.cursorIds[i].getHighBits() >> 16) & 0xff;
    _buffer[index + 1] = (this.cursorIds[i].getHighBits() >> 8) & 0xff;
    _buffer[index] = (this.cursorIds[i].getHighBits()) & 0xff;
    index = index + 4;
  }

  // Return buffer
  return _buffer;
}

var Response = function(bson, data, opts) {
  opts = opts || {promoteLongs: true, promoteValues: true, promoteBuffers: false};
  this.parsed = false;

  //
  // Parse Header
  //
  this.index = 0;
  this.raw = data;
  this.data = data;
  this.bson = bson;
  this.opts = opts;

  // Read the message length
  this.length = data[this.index] | data[this.index + 1] << 8 | data[this.index + 2] << 16 | data[this.index + 3] << 24;
  this.index = this.index + 4;

  // Fetch the request id for this reply
  this.requestId = data[this.index] | data[this.index + 1] << 8 | data[this.index + 2] << 16 | data[this.index + 3] << 24;
  this.index = this.index + 4;

  // Fetch the id of the request that triggered the response
  this.responseTo = data[this.index] | data[this.index + 1] << 8 | data[this.index + 2] << 16 | data[this.index + 3] << 24;
  this.index = this.index + 4;

  // Skip op-code field
  this.index = this.index + 4;

  // Unpack flags
  this.responseFlags = data[this.index] | data[this.index + 1] << 8 | data[this.index + 2] << 16 | data[this.index + 3] << 24;
  this.index = this.index + 4;

  // Unpack the cursor
  var lowBits = data[this.index] | data[this.index + 1] << 8 | data[this.index + 2] << 16 | data[this.index + 3] << 24;
  this.index = this.index + 4;
  var highBits = data[this.index] | data[this.index + 1] << 8 | data[this.index + 2] << 16 | data[this.index + 3] << 24;
  this.index = this.index + 4;
  // Create long object
  this.cursorId = new Long(lowBits, highBits);

  // Unpack the starting from
  this.startingFrom = data[this.index] | data[this.index + 1] << 8 | data[this.index + 2] << 16 | data[this.index + 3] << 24;
  this.index = this.index + 4;

  // Unpack the number of objects returned
  this.numberReturned = data[this.index] | data[this.index + 1] << 8 | data[this.index + 2] << 16 | data[this.index + 3] << 24;
  this.index = this.index + 4;

  // Preallocate document array
  this.documents = new Array(this.numberReturned);

  // Flag values
  this.cursorNotFound = (this.responseFlags & CURSOR_NOT_FOUND) != 0;
  this.queryFailure = (this.responseFlags & QUERY_FAILURE) != 0;
  this.shardConfigStale = (this.responseFlags & SHARD_CONFIG_STALE) != 0;
  this.awaitCapable = (this.responseFlags & AWAIT_CAPABLE) != 0;
  this.promoteLongs = typeof opts.promoteLongs == 'boolean' ? opts.promoteLongs : true;
  this.promoteValues = typeof opts.promoteValues == 'boolean' ? opts.promoteValues : true;
  this.promoteBuffers = typeof opts.promoteBuffers == 'boolean' ? opts.promoteBuffers : false;
}

Response.prototype.isParsed = function() {
  return this.parsed;
}

Response.prototype.parse = function(options) {
  // Don't parse again if not needed
  if(this.parsed) return;
  options = options || {};

  // Allow the return of raw documents instead of parsing
  var raw = options.raw || false;
  var documentsReturnedIn = options.documentsReturnedIn || null;
  var promoteLongs = typeof options.promoteLongs == 'boolean'
    ? options.promoteLongs
    : this.opts.promoteLongs;
  var promoteValues = typeof options.promoteValues == 'boolean'
    ? options.promoteValues
    : this.opts.promoteValues;
  var promoteBuffers = typeof options.promoteBuffers == 'boolean'
    ? options.promoteBuffers
    : this.opts.promoteBuffers
  var bsonSize, _options;

  // Set up the options
  _options = {
    promoteLongs: promoteLongs,
    promoteValues: promoteValues,
    promoteBuffers: promoteBuffers
  };

  //
  // Single document and documentsReturnedIn set
  //
  if(this.numberReturned == 1 && documentsReturnedIn != null && raw) {
    // Calculate the bson size
    bsonSize = this.data[this.index] | this.data[this.index + 1] << 8 | this.data[this.index + 2] << 16 | this.data[this.index + 3] << 24;
    // Slice out the buffer containing the command result document
    var document = this.data.slice(this.index, this.index + bsonSize);
    // Set up field we wish to keep as raw
    var fieldsAsRaw = {}
    fieldsAsRaw[documentsReturnedIn] = true;
    _options.fieldsAsRaw = fieldsAsRaw;

    // Deserialize but keep the array of documents in non-parsed form
    var doc = this.bson.deserialize(document, _options);

    // Get the documents
    this.documents = doc.cursor[documentsReturnedIn];
    this.numberReturned = this.documents.length;
    // Ensure we have a Long valie cursor id
    this.cursorId = typeof doc.cursor.id == 'number'
      ? Long.fromNumber(doc.cursor.id)
      : doc.cursor.id;

    // Adjust the index
    this.index = this.index + bsonSize;

    // Set as parsed
    this.parsed = true
    return;
  }

  //
  // Parse Body
  //
  for(var i = 0; i < this.numberReturned; i++) {
    bsonSize = this.data[this.index] | this.data[this.index + 1] << 8 | this.data[this.index + 2] << 16 | this.data[this.index + 3] << 24;

    // If we have raw results specified slice the return document
    if(raw) {
      this.documents[i] = this.data.slice(this.index, this.index + bsonSize);
    } else {
      this.documents[i] = this.bson.deserialize(this.data.slice(this.index, this.index + bsonSize), _options);
    }

    // Adjust the index
    this.index = this.index + bsonSize;
  }

  // Set parsed
  this.parsed = true;
}

module.exports = {
    Query: Query
  , GetMore: GetMore
  , Response: Response
  , KillCursor: KillCursor
}
