
var assert = require('assert')
var slice = require('sliced')
var mongo = require('mongodb')
var utils = require('../../').utils;

var uri = process.env.MQUERY_URI || 'mongodb://localhost/mquery';
var db;

exports.getCollection = function (cb) {
  mongo.MongoClient.connect(uri, function (err, db_) {
    assert.ifError(err);
    db = db_;

    var collection = db.collection('stuff');

    // clean test db before starting
    db.dropDatabase(function () {
      cb(null, collection);
    });
  })
}

exports.dropCollection = function (cb) {
  db.dropDatabase(function () {
    db.close(cb);
  })
}
