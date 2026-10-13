"use strict";

var common = require('./common')
	, utils = require('../utils')
  , toError = require('../utils').toError
	, handleCallback = require('../utils').handleCallback
	, shallowClone = utils.shallowClone
  , BulkWriteResult = common.BulkWriteResult
  , ObjectID = require('mongodb-core').BSON.ObjectID
  , Define = require('../metadata')
	, BSON = require('mongodb-core').BSON
  , Batch = common.Batch
  , mergeBatchResults = common.mergeBatchResults;

var bson = new BSON([BSON.Binary, BSON.Code, BSON.DBRef, BSON.Decimal128,
	BSON.Double, BSON.Int32, BSON.Long, BSON.Map, BSON.MaxKey, BSON.MinKey,
	BSON.ObjectId, BSON.BSONRegExp, BSON.Symbol, BSON.Timestamp]);

/**
 * Create a FindOperatorsOrdered instance (INTERNAL TYPE, do not instantiate directly)
 * @class
 * @return {FindOperatorsOrdered} a FindOperatorsOrdered instance.
 */
var FindOperatorsOrdered = function(self) {
  this.s = self.s;
}

/**
 * Add a single update document to the bulk operation
 *
 * @method
 * @param {object} doc update operations
 * @throws {MongoError}
 * @return {OrderedBulkOperation}
 */
FindOperatorsOrdered.prototype.update = function(updateDocument) {
  // Perform upsert
  var upsert = typeof this.s.currentOp.upsert == 'boolean' ? this.s.currentOp.upsert : false;

  // Establish the update command
  var document = {
      q: this.s.currentOp.selector
    , u: updateDocument
    , multi: true
    , upsert: upsert
  }

  // Clear out current Op
  this.s.currentOp = null;
  // Add the update document to the list
  return addToOperationsList(this, common.UPDATE, document);
}

/**
 * Add a single update one document to the bulk operation
 *
 * @method
 * @param {object} doc update operations
 * @throws {MongoError}
 * @return {OrderedBulkOperation}
 */
FindOperatorsOrdered.prototype.updateOne = function(updateDocument) {
  // Perform upsert
  var upsert = typeof this.s.currentOp.upsert == 'boolean' ? this.s.currentOp.upsert : false;

  // Establish the update command
  var document = {
      q: this.s.currentOp.selector
    , u: updateDocument
    , multi: false
    , upsert: upsert
  }

  // Clear out current Op
  this.s.currentOp = null;
  // Add the update document to the list
  return addToOperationsList(this, common.UPDATE, document);
}

/**
 * Add a replace one operation to the bulk operation
 *
 * @method
 * @param {object} doc the new document to replace the existing one with
 * @throws {MongoError}
 * @return {OrderedBulkOperation}
 */
FindOperatorsOrdered.prototype.replaceOne = function(updateDocument) {
  this.updateOne(updateDocument);
}

/**
 * Upsert modifier for update bulk operation
 *
 * @method
 * @throws {MongoError}
 * @return {FindOperatorsOrdered}
 */
FindOperatorsOrdered.prototype.upsert = function() {
  this.s.currentOp.upsert = true;
  return this;
}

/**
 * Add a remove one operation to the bulk operation
 *
 * @method
 * @throws {MongoError}
 * @return {OrderedBulkOperation}
 */
FindOperatorsOrdered.prototype.deleteOne = function() {
  // Establish the update command
  var document = {
      q: this.s.currentOp.selector
    , limit: 1
  }

  // Clear out current Op
  this.s.currentOp = null;
  // Add the remove document to the list
  return addToOperationsList(this, common.REMOVE, document);
}

// Backward compatibility
FindOperatorsOrdered.prototype.removeOne = FindOperatorsOrdered.prototype.deleteOne;

/**
 * Add a remove operation to the bulk operation
 *
 * @method
 * @throws {MongoError}
 * @return {OrderedBulkOperation}
 */
FindOperatorsOrdered.prototype.delete = function() {
  // Establish the update command
  var document = {
      q: this.s.currentOp.selector
    , limit: 0
  }

  // Clear out current Op
  this.s.currentOp = null;
  // Add the remove document to the list
  return addToOperationsList(this, common.REMOVE, document);
}

// Backward compatibility
FindOperatorsOrdered.prototype.remove = FindOperatorsOrdered.prototype.delete;

// Add to internal list of documents
var addToOperationsList = function(_self, docType, document) {
  // Get the bsonSize
  var bsonSize = bson.calculateObjectSize(document, {
		checkKeys: false,
	});

  // Throw error if the doc is bigger than the max BSON size
  if(bsonSize >= _self.s.maxBatchSizeBytes) {
		throw toError("document is larger than the maximum size " + _self.s.maxBatchSizeBytes);
	}

  // Create a new batch object if we don't have a current one
  if(_self.s.currentBatch == null) _self.s.currentBatch = new Batch(docType, _self.s.currentIndex);

  // Check if we need to create a new batch
  if(((_self.s.currentBatchSize + 1) >= _self.s.maxWriteBatchSize)
    || ((_self.s.currentBatchSizeBytes +  _self.s.currentBatchSizeBytes) >= _self.s.maxBatchSizeBytes)
    || (_self.s.currentBatch.batchType != docType)) {
    // Save the batch to the execution stack
    _self.s.batches.push(_self.s.currentBatch);

    // Create a new batch
    _self.s.currentBatch = new Batch(docType, _self.s.currentIndex);

    // Reset the current size trackers
    _self.s.currentBatchSize = 0;
    _self.s.currentBatchSizeBytes = 0;
  } else {
    // Update current batch size
    _self.s.currentBatchSize = _self.s.currentBatchSize + 1;
    _self.s.currentBatchSizeBytes = _self.s.currentBatchSizeBytes + bsonSize;
  }

  if(docType == common.INSERT) {
    _self.s.bulkResult.insertedIds.push({index: _self.s.currentIndex, _id: document._id});
  }

  // We have an array of documents
  if(Array.isArray(document)) {
    throw toError("operation passed in cannot be an Array");
  } else {
    _self.s.currentBatch.originalIndexes.push(_self.s.currentIndex);
    _self.s.currentBatch.operations.push(document)
		_self.s.currentBatchSizeBytes = _self.s.currentBatchSizeBytes + bsonSize;
    _self.s.currentIndex = _self.s.currentIndex + 1;
  }

  // Return self
  return _self;
}

/**
 * Create a new OrderedBulkOperation instance (INTERNAL TYPE, do not instantiate directly)
 * @class
 * @property {number} length Get the number of operations in the bulk.
 * @return {OrderedBulkOperation} a OrderedBulkOperation instance.
 */
function OrderedBulkOperation(topology, collection, options) {
	options = options == null ? {} : options;
	// TODO Bring from driver information in isMaster
	var executed = false;

	// Current item
	var currentOp = null;

	// Handle to the bson serializer, used to calculate running sizes
	var bson = topology.bson;

	// Namespace for the operation
  var namespace = collection.collectionName;

  // Set max byte size
	var maxBatchSizeBytes = topology.isMasterDoc && topology.isMasterDoc.maxBsonObjectSize
    ? topology.isMasterDoc.maxBsonObjectSize : (1024*1025*16);
	var maxWriteBatchSize = topology.isMasterDoc && topology.isMasterDoc.maxWriteBatchSize
    ? topology.isMasterDoc.maxWriteBatchSize : 1000;

  // Get the write concern
  var writeConcern = common.writeConcern(shallowClone(options), collection, options);

  // Get the promiseLibrary
  var promiseLibrary = options.promiseLibrary;

  // No promise library selected fall back
  if(!promiseLibrary) {
    promiseLibrary = typeof global.Promise == 'function' ?
      global.Promise : require('es6-promise').Promise;
  }

  // Final results
  var bulkResult = {
      ok: 1
    , writeErrors: []
    , writeConcernErrors: []
    , insertedIds: []
    , nInserted: 0
    , nUpserted: 0
    , nMatched: 0
    , nModified: 0
    , nRemoved: 0
    , upserted: []
  };

  // Internal state
  this.s = {
    // Final result
      bulkResult: bulkResult
    // Current batch state
    , currentBatch: null
    , currentIndex: 0
    , currentBatchSize: 0
    , currentBatchSizeBytes: 0
    , batches: []
    // Write concern
    , writeConcern: writeConcern
    // Max batch size options
    , maxBatchSizeBytes: maxBatchSizeBytes
    , maxWriteBatchSize: maxWriteBatchSize
    // Namespace
    , namespace: namespace
    // BSON
    , bson: bson
    // Topology
    , topology: topology
    // Options
    , options: options
    // Current operation
    , currentOp: currentOp
    // Executed
    , executed: executed
    // Collection
    , collection: collection
    // Promise Library
    , promiseLibrary: promiseLibrary
		// Fundamental error
		, err: null
    // Bypass validation
    , bypassDocumentValidation: typeof options.bypassDocumentValidation == 'boolean' ? options.bypassDocumentValidation : false
  }
}

var define = OrderedBulkOperation.define = new Define('OrderedBulkOperation', OrderedBulkOperation, false);

OrderedBulkOperation.prototype.raw = function(op) {
  var key = Object.keys(op)[0];

  // Set up the force server object id
  var forceServerObjectId = typeof this.s.options.forceServerObjectId == 'boolean'
    ? this.s.options.forceServerObjectId : this.s.collection.s.db.options.forceServerObjectId;

  // Update operations
  if((op.updateOne && op.updateOne.q)
    || (op.updateMany && op.updateMany.q)
    || (op.replaceOne && op.replaceOne.q)) {
    op[key].multi = op.updateOne || op.replaceOne ? false : true;
    return addToOperationsList(this, common.UPDATE, op[key]);
  }

  // Crud spec update format
  if(op.updateOne || op.updateMany || op.replaceOne) {
    var multi = op.updateOne || op.replaceOne ? false : true;
    var operation = {q: op[key].filter, u: op[key].update || op[key].replacement, multi: multi}
    operation.upsert = op[key].upsert ? true: false;
		if(op.collation) operation.collation = op.collation;
    return addToOperationsList(this, common.UPDATE, operation);
  }

  // Remove operations
  if(op.removeOne || op.removeMany || (op.deleteOne && op.deleteOne.q) || op.deleteMany && op.deleteMany.q) {
    op[key].limit = op.removeOne ? 1 : 0;
    return addToOperationsList(this, common.REMOVE, op[key]);
  }

  // Crud spec delete operations, less efficient
  if(op.deleteOne || op.deleteMany) {
    var limit = op.deleteOne ? 1 : 0;
    operation = {q: op[key].filter, limit: limit}
		if(op.collation) operation.collation = op.collation;
    return addToOperationsList(this, common.REMOVE, operation);
  }

  // Insert operations
  if(op.insertOne && op.insertOne.document == null) {
    if(forceServerObjectId !== true && op.insertOne._id == null) op.insertOne._id = new ObjectID();
    return addToOperationsList(this, common.INSERT, op.insertOne);
  } else if(op.insertOne && op.insertOne.document) {
    if(forceServerObjectId !== true && op.insertOne.document._id == null) op.insertOne.document._id = new ObjectID();
    return addToOperationsList(this, common.INSERT, op.insertOne.document);
  }

  if(op.insertMany) {
    for(var i = 0; i < op.insertMany.length; i++) {
      if(forceServerObjectId !== true && op.insertMany[i]._id == null) op.insertMany[i]._id = new ObjectID();
      addToOperationsList(this, common.INSERT, op.insertMany[i]);
    }

    return;
  }

  // No valid type of operation
  throw toError("bulkWrite only supports insertOne, insertMany, updateOne, updateMany, removeOne, removeMany, deleteOne, deleteMany");
}

/**
 * Add a single insert document to the bulk operation
 *
 * @param {object} doc the document to insert
 * @throws {MongoError}
 * @return {OrderedBulkOperation}
 */
OrderedBulkOperation.prototype.insert = function(document) {
  if(this.s.collection.s.db.options.forceServerObjectId !== true && document._id == null) document._id = new ObjectID();
  return addToOperationsList(this, common.INSERT, document);
}

/**
 * Initiate a find operation for an update/updateOne/remove/removeOne/replaceOne
 *
 * @method
 * @param {object} selector The selector for the bulk operation.
 * @throws {MongoError}
 * @return {FindOperatorsOrdered}
 */
OrderedBulkOperation.prototype.find = function(selector) {
  if (!selector) {
    throw toError("Bulk find operation must specify a selector");
  }

  // Save a current selector
  this.s.currentOp = {
    selector: selector
  }

  return new FindOperatorsOrdered(this);
}

Object.defineProperty(OrderedBulkOperation.prototype, 'length', {
  enumerable: true,
  get: function() {
    return this.s.currentIndex;
  }
});

//
// Execute next write command in a chain
var executeCommands = function(self, callback) {
  if(self.s.batches.length == 0) {
    return handleCallback(callback, null, new BulkWriteResult(self.s.bulkResult));
  }

  // Ordered execution of the command
  var batch = self.s.batches.shift();

  var resultHandler = function(err, result) {
		// Error is a driver related error not a bulk op error, terminate
		if(err && err.driver || err && err.message) {
			return handleCallback(callback, err);
		}

    // If we have and error
    if(err) err.ok = 0;
    // Merge the results together
    var mergeResult = mergeBatchResults(true, batch, self.s.bulkResult, err, result);
    if(mergeResult != null) {
      return handleCallback(callback, null, new BulkWriteResult(self.s.bulkResult));
    }

    // If we are ordered and have errors and they are
    // not all replication errors terminate the operation
    if(self.s.bulkResult.writeErrors.length > 0) {
      return handleCallback(callback, toError(self.s.bulkResult.writeErrors[0]), new BulkWriteResult(self.s.bulkResult));
    }

    // Execute the next command in line
    executeCommands(self, callback);
  }

  var finalOptions = {ordered: true}
  if(self.s.writeConcern != null) {
    finalOptions.writeConcern = self.s.writeConcern;
  }

	// Set an operationIf if provided
	if(self.operationId) {
		resultHandler.operationId = self.operationId;
	}

	// Serialize functions
	if(self.s.options.serializeFunctions) {
		finalOptions.serializeFunctions = true
	}

  // Serialize functions
  if(self.s.options.ignoreUndefined) {
    finalOptions.ignoreUndefined = true
  }

  // Is the bypassDocumentValidation options specific
  if(self.s.bypassDocumentValidation == true) {
    finalOptions.bypassDocumentValidation = true;
  }

  try {
    if(batch.batchType == common.INSERT) {
      self.s.topology.insert(self.s.collection.namespace, batch.operations, finalOptions, resultHandler);
    } else if(batch.batchType == common.UPDATE) {
      self.s.topology.update(self.s.collection.namespace, batch.operations, finalOptions, resultHandler);
    } else if(batch.batchType == common.REMOVE) {
      self.s.topology.remove(self.s.collection.namespace, batch.operations, finalOptions, resultHandler);
    }
  } catch(err) {
    // Force top level error
    err.ok = 0;
    // Merge top level error and return
    handleCallback(callback, null, mergeBatchResults(false, batch, self.s.bulkResult, err, null));
  }
}

/**
 * The callback format for results
 * @callback OrderedBulkOperation~resultCallback
 * @param {MongoError} error An error instance representing the error during the execution.
 * @param {BulkWriteResult} result The bulk write result.
 */

/**
 * Execute the ordered bulk operation
 *
 * @method
 * @param {object} [options=null] Optional settings.
 * @param {(number|string)} [options.w=null] The write concern.
 * @param {number} [options.wtimeout=null] The write concern timeout.
 * @param {boolean} [options.j=false] Specify a journal write concern.
 * @param {boolean} [options.fsync=false] Specify a file sync write concern.
 * @param {OrderedBulkOperation~resultCallback} [callback] The result callback
 * @throws {MongoError}
 * @return {Promise} returns Promise if no callback passed
 */
OrderedBulkOperation.prototype.execute = function(_writeConcern, callback) {
  var self = this;
  if (this.s.executed) {
    var executedError = toError('batch cannot be re-executed');
    return (typeof callback === 'function') ?
      callback(executedError, null) : this.s.promiseLibrary.reject(executedError);
  }

  if (typeof _writeConcern === 'function') {
    callback = _writeConcern;
  } else if (_writeConcern && typeof _writeConcern === 'object') {
    this.s.writeConcern = _writeConcern;
  }

  // If we have current batch
  if (this.s.currentBatch) this.s.batches.push(this.s.currentBatch)

  // If we have no operations in the bulk raise an error
  if (this.s.batches.length == 0) {
    var emptyBatchError = toError('Invalid Operation, no operations specified');
    return (typeof callback === 'function') ?
      callback(emptyBatchError, null) : this.s.promiseLibrary.reject(emptyBatchError);
  }

  // Execute using callback
  if (typeof callback === 'function') {
    return executeCommands(this, callback);
  }

  // Return a Promise
  return new this.s.promiseLibrary(function(resolve, reject) {
    executeCommands(self, function(err, r) {
      if (err) return reject(err);
      resolve(r);
    });
  });
}

define.classMethod('execute', {callback: true, promise:false});

/**
 * Returns an unordered batch object
 * @ignore
 */
var initializeOrderedBulkOp = function(topology, collection, options) {
	return new OrderedBulkOperation(topology, collection, options);
}

initializeOrderedBulkOp.OrderedBulkOperation = OrderedBulkOperation;
module.exports = initializeOrderedBulkOp;
module.exports.Bulk = OrderedBulkOperation;
