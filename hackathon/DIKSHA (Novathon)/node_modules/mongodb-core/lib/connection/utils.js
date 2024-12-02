"use strict";

var f = require('util').format,
  require_optional = require('require_optional');

// Set property function
var setProperty = function(obj, prop, flag, values) {
  Object.defineProperty(obj, prop.name, {
      enumerable:true,
      set: function(value) {
        if(typeof value != 'boolean') throw new Error(f("%s required a boolean", prop.name));
        // Flip the bit to 1
        if(value == true) values.flags |= flag;
        // Flip the bit to 0 if it's set, otherwise ignore
        if(value == false && (values.flags & flag) == flag) values.flags ^= flag;
        prop.value = value;
      }
    , get: function() { return prop.value; }
  });
}

// Set property function
var getProperty = function(obj, propName, fieldName, values, func) {
  Object.defineProperty(obj, propName, {
    enumerable:true,
    get: function() {
      // Not parsed yet, parse it
      if(values[fieldName] == null && obj.isParsed && !obj.isParsed()) {
        obj.parse();
      }

      // Do we have a post processing function
      if(typeof func == 'function') return func(values[fieldName]);
      // Return raw value
      return values[fieldName];
    }
  });
}

// Set simple property
var getSingleProperty = function(obj, name, value) {
  Object.defineProperty(obj, name, {
    enumerable:true,
    get: function() {
      return value
    }
  });
}

// Shallow copy
var copy = function(fObj, tObj) {
  tObj = tObj || {};
  for(var name in fObj) tObj[name] = fObj[name];
  return tObj;
}

var debugOptions = function(debugFields, options) {
  var finaloptions = {};
  debugFields.forEach(function(n) {
    finaloptions[n] = options[n];
  });

  return finaloptions;
}

var retrieveBSON = function() {
  var BSON = require('bson');
  BSON.native = false;

  try {
    var optionalBSON = require_optional('bson-ext');
    if(optionalBSON) {
      optionalBSON.native = true;
      return optionalBSON;
    }
  } catch(err) {}

  return BSON;
}

exports.setProperty = setProperty;
exports.getProperty = getProperty;
exports.getSingleProperty = getSingleProperty;
exports.copy = copy;
exports.debugOptions = debugOptions;
exports.retrieveBSON = retrieveBSON;
