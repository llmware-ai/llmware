"use strict";

var inherits = require('util').inherits
  , MongoError = require('mongodb-core').MongoError
  , Readable = require('stream').Readable || require('readable-stream').Readable
  , Define = require('./metadata')
  , CoreCursor = require('./cursor');

/**
 * @fileOverview The **AggregationCursor** class is an internal class that embodies an aggregation cursor on MongoDB
 * allowing for iteration over the results returned from the underlying query. It supports
 * one by one document iteration, conversion to an array or can be iterated as a Node 0.10.X
 * or higher stream
 *
 * **AGGREGATIONCURSOR Cannot directly be instantiated**
 * @example
 * var MongoClient = require('mongodb').MongoClient,
 *   test = require('assert');
 * // Connection url
 * var url = 'mongodb://localhost:27017/test';
 * // Connect using MongoClient
 * MongoClient.connect(url, function(err, db) {
 *   // Create a collection we want to drop later
 *   var col = db.collection('createIndexExample1');
 *   // Insert a bunch of documents
 *   col.insert([{a:1, b:1}
 *     , {a:2, b:2}, {a:3, b:3}
 *     , {a:4, b:4}], {w:1}, function(err, result) {
 *     test.equal(null, err);
 *     // Show that duplicate records got dropped
 *     col.aggregation({}, {cursor: {}}).toArray(function(err, items) {
 *       test.equal(null, err);
 *       test.equal(4, items.length);
 *       db.close();
 *     });
 *   });
 * });
 */

/**
 * Namespace provided by the browser.
 * @external Readable
 */

/**
 * Creates a new Aggregation Cursor instance (INTERNAL TYPE, do not instantiate directly)
 * @class AggregationCursor
 * @extends external:Readable
 * @fires AggregationCursor#data
 * @fires AggregationCursor#end
 * @fires AggregationCursor#close
 * @fires AggregationCursor#readable
 * @return {AggregationCursor} an AggregationCursor instance.
 */
var AggregationCursor = function(bson, ns, cmd, options, topology, topologyOptions) {
  CoreCursor.apply(this, Array.prototype.slice.call(arguments, 0));
  var state = AggregationCursor.INIT;
  var streamOptions = {};

  // MaxTimeMS
  var maxTimeMS = null;

  // Get the promiseLibrary
  var promiseLibrary = options.promiseLibrary;

  // No promise library selected fall back
  if(!promiseLibrary) {
    promiseLibrary = typeof global.Promise == 'function' ?
      global.Promise : require('es6-promise').Promise;
  }

  // Set up
  Readable.call(this, {objectMode: true});

  // Internal state
  this.s = {
    // MaxTimeMS
      maxTimeMS: maxTimeMS
    // State
    , state: state
    // Stream options
    , streamOptions: streamOptions
    // BSON
    , bson: bson
    // Namespace
    , ns: ns
    // Command
    , cmd: cmd
    // Options
    , options: options
    // Topology
    , topology: topology
    // Topology Options
    , topologyOptions: topologyOptions
    // Promise library
    , promiseLibrary: promiseLibrary
  }
}

/**
 * AggregationCursor stream data event, fired for each document in the cursor.
 *
 * @event AggregationCursor#data
 * @type {object}
 */

/**
 * AggregationCursor stream end event
 *
 * @event AggregationCursor#end
 * @type {null}
 */

/**
 * AggregationCursor stream close event
 *
 * @event AggregationCursor#close
 * @type {null}
 */

/**
 * AggregationCursor stream readable event
 *
 * @event AggregationCursor#readable
 * @type {null}
 */

// Inherit from Readable
inherits(AggregationCursor, Readable);

// Extend the Cursor
for(var name in CoreCursor.prototype) {
  AggregationCursor.prototype[name] = CoreCursor.prototype[name];
}

var define = AggregationCursor.define = new Define('AggregationCursor', AggregationCursor, true);

/**
 * Set the batch size for the cursor.
 * @method
 * @param {number} value The batchSize for the cursor.
 * @throws {MongoError}
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.batchSize = function(value) {
  if(this.s.state == AggregationCursor.CLOSED || this.isDead()) throw MongoError.create({message: "Cursor is closed", driver:true });
  if(typeof value != 'number') throw MongoError.create({message: "batchSize requires an integer", driver:true });
  if(this.s.cmd.cursor) this.s.cmd.cursor.batchSize = value;
  this.setCursorBatchSize(value);
  return this;
}

define.classMethod('batchSize', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a geoNear stage to the aggregation pipeline
 * @method
 * @param {object} document The geoNear stage document.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.geoNear = function(document) {
  this.s.cmd.pipeline.push({$geoNear: document});
  return this;
}

define.classMethod('geoNear', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a group stage to the aggregation pipeline
 * @method
 * @param {object} document The group stage document.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.group = function(document) {
  this.s.cmd.pipeline.push({$group: document});
  return this;
}

define.classMethod('group', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a limit stage to the aggregation pipeline
 * @method
 * @param {number} value The state limit value.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.limit = function(value) {
  this.s.cmd.pipeline.push({$limit: value});
  return this;
}

define.classMethod('limit', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a match stage to the aggregation pipeline
 * @method
 * @param {object} document The match stage document.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.match = function(document) {
  this.s.cmd.pipeline.push({$match: document});
  return this;
}

define.classMethod('match', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a maxTimeMS stage to the aggregation pipeline
 * @method
 * @param {number} value The state maxTimeMS value.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.maxTimeMS = function(value) {
  if(this.s.topology.lastIsMaster().minWireVersion > 2) {
    this.s.cmd.maxTimeMS = value;
  }
  return this;
}

define.classMethod('maxTimeMS', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a out stage to the aggregation pipeline
 * @method
 * @param {number} destination The destination name.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.out = function(destination) {
  this.s.cmd.pipeline.push({$out: destination});
  return this;
}

define.classMethod('out', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a project stage to the aggregation pipeline
 * @method
 * @param {object} document The project stage document.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.project = function(document) {
  this.s.cmd.pipeline.push({$project: document});
  return this;
}

define.classMethod('project', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a lookup stage to the aggregation pipeline
 * @method
 * @param {object} document The lookup stage document.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.lookup = function(document) {
  this.s.cmd.pipeline.push({$lookup: document});
  return this;
}

define.classMethod('lookup', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a redact stage to the aggregation pipeline
 * @method
 * @param {object} document The redact stage document.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.redact = function(document) {
  this.s.cmd.pipeline.push({$redact: document});
  return this;
}

define.classMethod('redact', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a skip stage to the aggregation pipeline
 * @method
 * @param {number} value The state skip value.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.skip = function(value) {
  this.s.cmd.pipeline.push({$skip: value});
  return this;
}

define.classMethod('skip', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a sort stage to the aggregation pipeline
 * @method
 * @param {object} document The sort stage document.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.sort = function(document) {
  this.s.cmd.pipeline.push({$sort: document});
  return this;
}

define.classMethod('sort', {callback: false, promise:false, returns: [AggregationCursor]});

/**
 * Add a unwind stage to the aggregation pipeline
 * @method
 * @param {number} field The unwind field name.
 * @return {AggregationCursor}
 */
AggregationCursor.prototype.unwind = function(field) {
  this.s.cmd.pipeline.push({$unwind: field});
  return this;
}

define.classMethod('unwind', {callback: false, promise:false, returns: [AggregationCursor]});

AggregationCursor.prototype.get = AggregationCursor.prototype.toArray;

// Inherited methods
define.classMethod('toArray', {callback: true, promise:true});
define.classMethod('each', {callback: true, promise:false});
define.classMethod('forEach', {callback: true, promise:false});
define.classMethod('hasNext', {callback: true, promise:true});
define.classMethod('next', {callback: true, promise:true});
define.classMethod('close', {callback: true, promise:true});
define.classMethod('isClosed', {callback: false, promise:false, returns: [Boolean]});
define.classMethod('rewind', {callback: false, promise:false});
define.classMethod('bufferedCount', {callback: false, promise:false, returns: [Number]});
define.classMethod('readBufferedDocuments', {callback: false, promise:false, returns: [Array]});

/**
 * Get the next available document from the cursor, returns null if no more documents are available.
 * @function AggregationCursor.prototype.next
 * @param {AggregationCursor~resultCallback} [callback] The result callback.
 * @throws {MongoError}
 * @return {Promise} returns Promise if no callback passed
 */

/**
 * Check if there is any document still available in the cursor
 * @function AggregationCursor.prototype.hasNext
 * @param {AggregationCursor~resultCallback} [callback] The result callback.
 * @throws {MongoError}
 * @return {Promise} returns Promise if no callback passed
 */

/**
 * The callback format for results
 * @callback AggregationCursor~toArrayResultCallback
 * @param {MongoError} error An error instance representing the error during the execution.
 * @param {object[]} documents All the documents the satisfy the cursor.
 */

/**
 * Returns an array of documents. The caller is responsible for making sure that there
 * is enough memory to store the results. Note that the array only contain partial
 * results when this cursor had been previously accessed. In that case,
 * cursor.rewind() can be used to reset the cursor.
 * @method AggregationCursor.prototype.toArray
 * @param {AggregationCursor~toArrayResultCallback} [callback] The result callback.
 * @throws {MongoError}
 * @return {Promise} returns Promise if no callback passed
 */

/**
 * The callback format for results
 * @callback AggregationCursor~resultCallback
 * @param {MongoError} error An error instance representing the error during the execution.
 * @param {(object|null)} result The result object if the command was executed successfully.
 */

/**
 * Iterates over all the documents for this cursor. As with **{cursor.toArray}**,
 * not all of the elements will be iterated if this cursor had been previously accessed.
 * In that case, **{cursor.rewind}** can be used to reset the cursor. However, unlike
 * **{cursor.toArray}**, the cursor will only hold a maximum of batch size elements
 * at any given time if batch size is specified. Otherwise, the caller is responsible
 * for making sure that the entire result can fit the memory.
 * @method AggregationCursor.prototype.each
 * @param {AggregationCursor~resultCallback} callback The result callback.
 * @throws {MongoError}
 * @return {null}
 */

/**
 * Close the cursor, sending a AggregationCursor command and emitting close.
 * @method AggregationCursor.prototype.close
 * @param {AggregationCursor~resultCallback} [callback] The result callback.
 * @return {Promise} returns Promise if no callback passed
 */

/**
 * Is the cursor closed
 * @method AggregationCursor.prototype.isClosed
 * @return {boolean}
 */

/**
 * Execute the explain for the cursor
 * @method AggregationCursor.prototype.explain
 * @param {AggregationCursor~resultCallback} [callback] The result callback.
 * @return {Promise} returns Promise if no callback passed
 */

/**
 * Clone the cursor
 * @function AggregationCursor.prototype.clone
 * @return {AggregationCursor}
 */

/**
 * Resets the cursor
 * @function AggregationCursor.prototype.rewind
 * @return {AggregationCursor}
 */

/**
 * The callback format for the forEach iterator method
 * @callback AggregationCursor~iteratorCallback
 * @param {Object} doc An emitted document for the iterator
 */

/**
 * The callback error format for the forEach iterator method
 * @callback AggregationCursor~endCallback
 * @param {MongoError} error An error instance representing the error during the execution.
 */

/*
 * Iterates over all the documents for this cursor using the iterator, callback pattern.
 * @method AggregationCursor.prototype.forEach
 * @param {AggregationCursor~iteratorCallback} iterator The iteration callback.
 * @param {AggregationCursor~endCallback} callback The end callback.
 * @throws {MongoError}
 * @return {null}
 */

AggregationCursor.INIT = 0;
AggregationCursor.OPEN = 1;
AggregationCursor.CLOSED = 2;

module.exports = AggregationCursor;
