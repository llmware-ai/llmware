"use strict";

var MongoError = require('../error');

// Wire command operation ids
var OP_UPDATE = 2001;
var OP_INSERT = 2002;
var OP_DELETE = 2006;

var Insert = function(requestId, ismaster, bson, ns, documents, options) {
  // Basic options needed to be passed in
  if(ns == null) throw new MongoError("ns must be specified for query");
  if(!Array.isArray(documents) || documents.length == 0) throw new MongoError("documents array must contain at least one document to insert");

  // Validate that we are not passing 0x00 in the collection name
  if(!!~ns.indexOf("\x00")) {
    throw new MongoError("namespace cannot contain a null character");
  }

  // Set internal
  this.requestId = requestId;
  this.bson = bson;
  this.ns = ns;
  this.documents = documents;
  this.ismaster = ismaster;

  // Ensure empty options
  options = options || {};

  // Unpack options
  this.serializeFunctions = typeof options.serializeFunctions == 'boolean' ? options.serializeFunctions : false;
  this.ignoreUndefined = typeof options.ignoreUndefined == 'boolean' ? options.ignoreUndefined : false;
  this.checkKeys = typeof options.checkKeys == 'boolean' ? options.checkKeys : true;
  this.continueOnError = typeof options.continueOnError == 'boolean' ? options.continueOnError : false;
  // Set flags
  this.flags = this.continueOnError ? 1 : 0;
}

// To Binary
Insert.prototype.toBin = function() {
  // Contains all the buffers to be written
  var buffers = [];

  // Header buffer
  var header = new Buffer(
    4 * 4 // Header
    + 4   // Flags
    + Buffer.byteLength(this.ns) + 1 // namespace
  );

  // Add header to buffers
  buffers.push(header);

  // Total length of the message
  var totalLength = header.length;

  // Serialize all the documents
  for(var i = 0; i < this.documents.length; i++) {
    var buffer = this.bson.serialize(this.documents[i], {
      checkKeys: this.checkKeys,
      serializeFunctions: this.serializeFunctions,
      ignoreUndefined: this.ignoreUndefined,
    });

    // Document is larger than maxBsonObjectSize, terminate serialization
    if(buffer.length > this.ismaster.maxBsonObjectSize) {
      throw new MongoError("Document exceeds maximum allowed bson size of " + this.ismaster.maxBsonObjectSize + " bytes");
    }

    // Add to total length of wire protocol message
    totalLength = totalLength + buffer.length;
    // Add to buffer
    buffers.push(buffer);
  }

  // Command is larger than maxMessageSizeBytes terminate serialization
  if(totalLength > this.ismaster.maxMessageSizeBytes) {
    throw new MongoError("Command exceeds maximum message size of " + this.ismaster.maxMessageSizeBytes + " bytes");
  }

  // Add all the metadata
  var index = 0;

  // Write header length
  header[index + 3] = (totalLength >> 24) & 0xff;
  header[index + 2] = (totalLength >> 16) & 0xff;
  header[index + 1] = (totalLength >> 8) & 0xff;
  header[index] = (totalLength) & 0xff;
  index = index + 4;

  // Write header requestId
  header[index + 3] = (this.requestId >> 24) & 0xff;
  header[index + 2] = (this.requestId >> 16) & 0xff;
  header[index + 1] = (this.requestId >> 8) & 0xff;
  header[index] = (this.requestId) & 0xff;
  index = index + 4;

  // No flags
  header[index + 3] = (0 >> 24) & 0xff;
  header[index + 2] = (0 >> 16) & 0xff;
  header[index + 1] = (0 >> 8) & 0xff;
  header[index] = (0) & 0xff;
  index = index + 4;

  // Operation
  header[index + 3] = (OP_INSERT >> 24) & 0xff;
  header[index + 2] = (OP_INSERT >> 16) & 0xff;
  header[index + 1] = (OP_INSERT >> 8) & 0xff;
  header[index] = (OP_INSERT) & 0xff;
  index = index + 4;

  // Flags
  header[index + 3] = (this.flags >> 24) & 0xff;
  header[index + 2] = (this.flags >> 16) & 0xff;
  header[index + 1] = (this.flags >> 8) & 0xff;
  header[index] = (this.flags) & 0xff;
  index = index + 4;

  // Write collection name
  index = index + header.write(this.ns, index, 'utf8') + 1;
  header[index - 1] = 0;

  // Return the buffers
  return buffers;
}

var Update = function(requestId, ismaster, bson, ns, update, options) {
  // Basic options needed to be passed in
  if(ns == null) throw new MongoError("ns must be specified for query");

  // Ensure empty options
  options = options || {};

  // Set internal
  this.requestId = requestId;
  this.bson = bson;
  this.ns = ns;
  this.ismaster = ismaster;

  // Unpack options
  this.serializeFunctions = typeof options.serializeFunctions == 'boolean' ? options.serializeFunctions : false;
  this.ignoreUndefined = typeof options.ignoreUndefined == 'boolean' ? options.ignoreUndefined : false;
  this.checkKeys = typeof options.checkKeys == 'boolean' ? options.checkKeys : false;

  // Unpack the update document
  this.upsert = typeof update[0].upsert == 'boolean' ? update[0].upsert : false;
  this.multi = typeof update[0].multi == 'boolean' ? update[0].multi : false;
  this.q = update[0].q;
  this.u = update[0].u;

  // Create flag value
  this.flags = this.upsert ? 1 : 0;
  this.flags = this.multi ? this.flags | 2 : this.flags;
}

// To Binary
Update.prototype.toBin = function() {
  // Contains all the buffers to be written
  var buffers = [];

  // Header buffer
  var header = new Buffer(
    4 * 4 // Header
    + 4   // ZERO
    + Buffer.byteLength(this.ns) + 1 // namespace
    + 4   // Flags
  );

  // Add header to buffers
  buffers.push(header);

  // Total length of the message
  var totalLength = header.length;

  // Serialize the selector
  var selector = this.bson.serialize(this.q, {
    checkKeys: this.checkKeys,
    serializeFunctions: this.serializeFunctions,
    ignoreUndefined: this.ignoreUndefined,
  });
  buffers.push(selector);
  totalLength = totalLength + selector.length;

  // Serialize the update
  var update = this.bson.serialize(this.u, {
    checkKeys: this.checkKeys,
    serializeFunctions: this.serializeFunctions,
    ignoreUndefined: this.ignoreUndefined,
  });
  buffers.push(update);
  totalLength = totalLength + update.length;

  // Index in header buffer
  var index = 0;

  // Write header length
  header[index + 3] = (totalLength >> 24) & 0xff;
  header[index + 2] = (totalLength >> 16) & 0xff;
  header[index + 1] = (totalLength >> 8) & 0xff;
  header[index] = (totalLength) & 0xff;
  index = index + 4;

  // Write header requestId
  header[index + 3] = (this.requestId >> 24) & 0xff;
  header[index + 2] = (this.requestId >> 16) & 0xff;
  header[index + 1] = (this.requestId >> 8) & 0xff;
  header[index] = (this.requestId) & 0xff;
  index = index + 4;

  // No flags
  header[index + 3] = (0 >> 24) & 0xff;
  header[index + 2] = (0 >> 16) & 0xff;
  header[index + 1] = (0 >> 8) & 0xff;
  header[index] = (0) & 0xff;
  index = index + 4;

  // Operation
  header[index + 3] = (OP_UPDATE >> 24) & 0xff;
  header[index + 2] = (OP_UPDATE >> 16) & 0xff;
  header[index + 1] = (OP_UPDATE >> 8) & 0xff;
  header[index] = (OP_UPDATE) & 0xff;
  index = index + 4;

  // Write ZERO
  header[index + 3] = (0 >> 24) & 0xff;
  header[index + 2] = (0 >> 16) & 0xff;
  header[index + 1] = (0 >> 8) & 0xff;
  header[index] = (0) & 0xff;
  index = index + 4;

  // Write collection name
  index = index + header.write(this.ns, index, 'utf8') + 1;
  header[index - 1] = 0;

  // Flags
  header[index + 3] = (this.flags >> 24) & 0xff;
  header[index + 2] = (this.flags >> 16) & 0xff;
  header[index + 1] = (this.flags >> 8) & 0xff;
  header[index] = (this.flags) & 0xff;
  index = index + 4;

  // Return the buffers
  return buffers;
}

var Remove = function(requestId, ismaster, bson, ns, remove, options) {
  // Basic options needed to be passed in
  if(ns == null) throw new MongoError("ns must be specified for query");

  // Ensure empty options
  options = options || {};

  // Set internal
  this.requestId = requestId;
  this.bson = bson;
  this.ns = ns;
  this.ismaster = ismaster;

  // Unpack options
  this.serializeFunctions = typeof options.serializeFunctions == 'boolean' ? options.serializeFunctions : false;
  this.ignoreUndefined = typeof options.ignoreUndefined == 'boolean' ? options.ignoreUndefined : false;
  this.checkKeys = typeof options.checkKeys == 'boolean' ? options.checkKeys : false;

  // Unpack the update document
  this.limit = typeof remove[0].limit == 'number' ? remove[0].limit : 1;
  this.q = remove[0].q;

  // Create flag value
  this.flags = this.limit == 1 ? 1 : 0;
}

// To Binary
Remove.prototype.toBin = function() {
  // Contains all the buffers to be written
  var buffers = [];

  // Header buffer
  var header = new Buffer(
    4 * 4 // Header
    + 4   // ZERO
    + Buffer.byteLength(this.ns) + 1 // namespace
    + 4   // Flags
  );

  // Add header to buffers
  buffers.push(header);

  // Total length of the message
  var totalLength = header.length;

  // Serialize the selector
  var selector = this.bson.serialize(this.q, {
    checkKeys: this.checkKeys,
    serializeFunctions: this.serializeFunctions,
    ignoreUndefined: this.ignoreUndefined,
  });
  buffers.push(selector);
  totalLength = totalLength + selector.length;

  // Index in header buffer
  var index = 0;

  // Write header length
  header[index + 3] = (totalLength >> 24) & 0xff;
  header[index + 2] = (totalLength >> 16) & 0xff;
  header[index + 1] = (totalLength >> 8) & 0xff;
  header[index] = (totalLength) & 0xff;
  index = index + 4;

  // Write header requestId
  header[index + 3] = (this.requestId >> 24) & 0xff;
  header[index + 2] = (this.requestId >> 16) & 0xff;
  header[index + 1] = (this.requestId >> 8) & 0xff;
  header[index] = (this.requestId) & 0xff;
  index = index + 4;

  // No flags
  header[index + 3] = (0 >> 24) & 0xff;
  header[index + 2] = (0 >> 16) & 0xff;
  header[index + 1] = (0 >> 8) & 0xff;
  header[index] = (0) & 0xff;
  index = index + 4;

  // Operation
  header[index + 3] = (OP_DELETE >> 24) & 0xff;
  header[index + 2] = (OP_DELETE >> 16) & 0xff;
  header[index + 1] = (OP_DELETE >> 8) & 0xff;
  header[index] = (OP_DELETE) & 0xff;
  index = index + 4;

  // Write ZERO
  header[index + 3] = (0 >> 24) & 0xff;
  header[index + 2] = (0 >> 16) & 0xff;
  header[index + 1] = (0 >> 8) & 0xff;
  header[index] = (0) & 0xff;
  index = index + 4;

  // Write collection name
  index = index + header.write(this.ns, index, 'utf8') + 1;
  header[index - 1] = 0;

  // Write ZERO
  header[index + 3] = (this.flags >> 24) & 0xff;
  header[index + 2] = (this.flags >> 16) & 0xff;
  header[index + 1] = (this.flags >> 8) & 0xff;
  header[index] = (this.flags) & 0xff;
  index = index + 4;

  // Return the buffers
  return buffers;
}

module.exports = {
    Insert: Insert
  , Update: Update
  , Remove: Remove
}
