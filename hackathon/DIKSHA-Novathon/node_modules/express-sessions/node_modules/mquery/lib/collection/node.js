'use strict';

/**
 * Module dependencies
 */

var Collection = require('./collection');
var utils = require('../utils');

function NodeCollection (col) {
  this.collection = col;
  this.collectionName = col.collectionName;
}

/**
 * inherit from collection base class
 */

utils.inherits(NodeCollection, Collection);

/**
 * find(match, options, function(err, docs))
 */

NodeCollection.prototype.find = function (match, options, cb) {
  this.collection.find(match, options, function (err, cursor) {
    if (err) return cb(err);

    try {
      cursor.toArray(cb);
    } catch (error) {
      cb(error);
    }
  });
}

/**
 * findOne(match, options, function(err, doc))
 */

NodeCollection.prototype.findOne = function (match, options, cb) {
  this.collection.findOne(match, options, cb);
}

/**
 * count(match, options, function(err, count))
 */

NodeCollection.prototype.count = function (match, options, cb) {
  this.collection.count(match, options, cb);
}

/**
 * distinct(prop, match, options, function(err, count))
 */

NodeCollection.prototype.distinct  = function (prop, match, options, cb) {
  this.collection.distinct(prop, match, options, cb);
}

/**
 * update(match, update, options, function(err[, result]))
 */

NodeCollection.prototype.update = function (match, update, options, cb) {
  this.collection.update(match, update, options, cb);
}

/**
 * update(match, update, options, function(err[, result]))
 */

NodeCollection.prototype.updateMany = function (match, update, options, cb) {
  this.collection.updateMany(match, update, options, cb);
}

/**
 * update(match, update, options, function(err[, result]))
 */

NodeCollection.prototype.updateOne = function (match, update, options, cb) {
  this.collection.updateOne(match, update, options, cb);
}

/**
 * replaceOne(match, update, options, function(err[, result]))
 */

NodeCollection.prototype.replaceOne = function (match, update, options, cb) {
  this.collection.replaceOne(match, update, options, cb);
}

/**
 * deleteOne(match, options, function(err[, result])
 */

NodeCollection.prototype.deleteOne = function (match, options, cb) {
  this.collection.deleteOne(match, options, cb);
}

/**
 * deleteMany(match, options, function(err[, result])
 */

NodeCollection.prototype.deleteMany = function (match, options, cb) {
  this.collection.deleteMany(match, options, cb);
}

/**
 * remove(match, options, function(err[, result])
 */

NodeCollection.prototype.remove = function (match, options, cb) {
  this.collection.remove(match, options, cb);
}

/**
 * findAndModify(match, update, options, function(err, doc))
 */

NodeCollection.prototype.findAndModify = function (match, update, options, cb) {
  var sort = Array.isArray(options.sort) ? options.sort : [];
  this.collection.findAndModify(match, sort, update, options, cb);
}

/**
 * var stream = findStream(match, findOptions, streamOptions)
 */

NodeCollection.prototype.findStream = function(match, findOptions, streamOptions) {
  return this.collection.find(match, findOptions);
}

/**
 * var cursor = findCursor(match, findOptions)
 */

NodeCollection.prototype.findCursor = function(match, findOptions) {
  return this.collection.find(match, findOptions);
}

/**
 * aggregation(operators..., function(err, doc))
 * TODO
 */

/**
 * Expose
 */

module.exports = exports = NodeCollection;
