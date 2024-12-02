/**
   * cloudinary-core-shrinkwrap.js
   * Cloudinary's JavaScript library - Version 2.13.1
   * Copyright Cloudinary
   * see https://github.com/cloudinary/cloudinary_js
   *
   */
(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory();
	else if(typeof define === 'function' && define.amd)
		define([], factory);
	else if(typeof exports === 'object')
		exports["cloudinary"] = factory();
	else
		root["cloudinary"] = factory();
})(this, function() {
return /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./src/namespace/cloudinary-core-shrinkwrap.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./node_modules/lodash/_DataView.js":
/***/ (function(module, exports, __webpack_require__) {

var getNative = __webpack_require__("./node_modules/lodash/_getNative.js"),
    root = __webpack_require__("./node_modules/lodash/_root.js");

/* Built-in method references that are verified to be native. */
var DataView = getNative(root, 'DataView');

module.exports = DataView;


/***/ }),

/***/ "./node_modules/lodash/_Hash.js":
/***/ (function(module, exports, __webpack_require__) {

var hashClear = __webpack_require__("./node_modules/lodash/_hashClear.js"),
    hashDelete = __webpack_require__("./node_modules/lodash/_hashDelete.js"),
    hashGet = __webpack_require__("./node_modules/lodash/_hashGet.js"),
    hashHas = __webpack_require__("./node_modules/lodash/_hashHas.js"),
    hashSet = __webpack_require__("./node_modules/lodash/_hashSet.js");

/**
 * Creates a hash object.
 *
 * @private
 * @constructor
 * @param {Array} [entries] The key-value pairs to cache.
 */
function Hash(entries) {
  var index = -1,
      length = entries == null ? 0 : entries.length;

  this.clear();
  while (++index < length) {
    var entry = entries[index];
    this.set(entry[0], entry[1]);
  }
}

// Add methods to `Hash`.
Hash.prototype.clear = hashClear;
Hash.prototype['delete'] = hashDelete;
Hash.prototype.get = hashGet;
Hash.prototype.has = hashHas;
Hash.prototype.set = hashSet;

module.exports = Hash;


/***/ }),

/***/ "./node_modules/lodash/_ListCache.js":
/***/ (function(module, exports, __webpack_require__) {

var listCacheClear = __webpack_require__("./node_modules/lodash/_listCacheClear.js"),
    listCacheDelete = __webpack_require__("./node_modules/lodash/_listCacheDelete.js"),
    listCacheGet = __webpack_require__("./node_modules/lodash/_listCacheGet.js"),
    listCacheHas = __webpack_require__("./node_modules/lodash/_listCacheHas.js"),
    listCacheSet = __webpack_require__("./node_modules/lodash/_listCacheSet.js");

/**
 * Creates an list cache object.
 *
 * @private
 * @constructor
 * @param {Array} [entries] The key-value pairs to cache.
 */
function ListCache(entries) {
  var index = -1,
      length = entries == null ? 0 : entries.length;

  this.clear();
  while (++index < length) {
    var entry = entries[index];
    this.set(entry[0], entry[1]);
  }
}

// Add methods to `ListCache`.
ListCache.prototype.clear = listCacheClear;
ListCache.prototype['delete'] = listCacheDelete;
ListCache.prototype.get = listCacheGet;
ListCache.prototype.has = listCacheHas;
ListCache.prototype.set = listCacheSet;

module.exports = ListCache;


/***/ }),

/***/ "./node_modules/lodash/_Map.js":
/***/ (function(module, exports, __webpack_require__) {

var getNative = __webpack_require__("./node_modules/lodash/_getNative.js"),
    root = __webpack_require__("./node_modules/lodash/_root.js");

/* Built-in method references that are verified to be native. */
var Map = getNative(root, 'Map');

module.exports = Map;


/***/ }),

/***/ "./node_modules/lodash/_MapCache.js":
/***/ (function(module, exports, __webpack_require__) {

var mapCacheClear = __webpack_require__("./node_modules/lodash/_mapCacheClear.js"),
    mapCacheDelete = __webpack_require__("./node_modules/lodash/_mapCacheDelete.js"),
    mapCacheGet = __webpack_require__("./node_modules/lodash/_mapCacheGet.js"),
    mapCacheHas = __webpack_require__("./node_modules/lodash/_mapCacheHas.js"),
    mapCacheSet = __webpack_require__("./node_modules/lodash/_mapCacheSet.js");

/**
 * Creates a map cache object to store key-value pairs.
 *
 * @private
 * @constructor
 * @param {Array} [entries] The key-value pairs to cache.
 */
function MapCache(entries) {
  var index = -1,
      length = entries == null ? 0 : entries.length;

  this.clear();
  while (++index < length) {
    var entry = entries[index];
    this.set(entry[0], entry[1]);
  }
}

// Add methods to `MapCache`.
MapCache.prototype.clear = mapCacheClear;
MapCache.prototype['delete'] = mapCacheDelete;
MapCache.prototype.get = mapCacheGet;
MapCache.prototype.has = mapCacheHas;
MapCache.prototype.set = mapCacheSet;

module.exports = MapCache;


/***/ }),

/***/ "./node_modules/lodash/_Promise.js":
/***/ (function(module, exports, __webpack_require__) {

var getNative = __webpack_require__("./node_modules/lodash/_getNative.js"),
    root = __webpack_require__("./node_modules/lodash/_root.js");

/* Built-in method references that are verified to be native. */
var Promise = getNative(root, 'Promise');

module.exports = Promise;


/***/ }),

/***/ "./node_modules/lodash/_Set.js":
/***/ (function(module, exports, __webpack_require__) {

var getNative = __webpack_require__("./node_modules/lodash/_getNative.js"),
    root = __webpack_require__("./node_modules/lodash/_root.js");

/* Built-in method references that are verified to be native. */
var Set = getNative(root, 'Set');

module.exports = Set;


/***/ }),

/***/ "./node_modules/lodash/_SetCache.js":
/***/ (function(module, exports, __webpack_require__) {

var MapCache = __webpack_require__("./node_modules/lodash/_MapCache.js"),
    setCacheAdd = __webpack_require__("./node_modules/lodash/_setCacheAdd.js"),
    setCacheHas = __webpack_require__("./node_modules/lodash/_setCacheHas.js");

/**
 *
 * Creates an array cache object to store unique values.
 *
 * @private
 * @constructor
 * @param {Array} [values] The values to cache.
 */
function SetCache(values) {
  var index = -1,
      length = values == null ? 0 : values.length;

  this.__data__ = new MapCache;
  while (++index < length) {
    this.add(values[index]);
  }
}

// Add methods to `SetCache`.
SetCache.prototype.add = SetCache.prototype.push = setCacheAdd;
SetCache.prototype.has = setCacheHas;

module.exports = SetCache;


/***/ }),

/***/ "./node_modules/lodash/_Stack.js":
/***/ (function(module, exports, __webpack_require__) {

var ListCache = __webpack_require__("./node_modules/lodash/_ListCache.js"),
    stackClear = __webpack_require__("./node_modules/lodash/_stackClear.js"),
    stackDelete = __webpack_require__("./node_modules/lodash/_stackDelete.js"),
    stackGet = __webpack_require__("./node_modules/lodash/_stackGet.js"),
    stackHas = __webpack_require__("./node_modules/lodash/_stackHas.js"),
    stackSet = __webpack_require__("./node_modules/lodash/_stackSet.js");

/**
 * Creates a stack cache object to store key-value pairs.
 *
 * @private
 * @constructor
 * @param {Array} [entries] The key-value pairs to cache.
 */
function Stack(entries) {
  var data = this.__data__ = new ListCache(entries);
  this.size = data.size;
}

// Add methods to `Stack`.
Stack.prototype.clear = stackClear;
Stack.prototype['delete'] = stackDelete;
Stack.prototype.get = stackGet;
Stack.prototype.has = stackHas;
Stack.prototype.set = stackSet;

module.exports = Stack;


/***/ }),

/***/ "./node_modules/lodash/_Symbol.js":
/***/ (function(module, exports, __webpack_require__) {

var root = __webpack_require__("./node_modules/lodash/_root.js");

/** Built-in value references. */
var Symbol = root.Symbol;

module.exports = Symbol;


/***/ }),

/***/ "./node_modules/lodash/_Uint8Array.js":
/***/ (function(module, exports, __webpack_require__) {

var root = __webpack_require__("./node_modules/lodash/_root.js");

/** Built-in value references. */
var Uint8Array = root.Uint8Array;

module.exports = Uint8Array;


/***/ }),

/***/ "./node_modules/lodash/_WeakMap.js":
/***/ (function(module, exports, __webpack_require__) {

var getNative = __webpack_require__("./node_modules/lodash/_getNative.js"),
    root = __webpack_require__("./node_modules/lodash/_root.js");

/* Built-in method references that are verified to be native. */
var WeakMap = getNative(root, 'WeakMap');

module.exports = WeakMap;


/***/ }),

/***/ "./node_modules/lodash/_apply.js":
/***/ (function(module, exports) {

/**
 * A faster alternative to `Function#apply`, this function invokes `func`
 * with the `this` binding of `thisArg` and the arguments of `args`.
 *
 * @private
 * @param {Function} func The function to invoke.
 * @param {*} thisArg The `this` binding of `func`.
 * @param {Array} args The arguments to invoke `func` with.
 * @returns {*} Returns the result of `func`.
 */
function apply(func, thisArg, args) {
  switch (args.length) {
    case 0: return func.call(thisArg);
    case 1: return func.call(thisArg, args[0]);
    case 2: return func.call(thisArg, args[0], args[1]);
    case 3: return func.call(thisArg, args[0], args[1], args[2]);
  }
  return func.apply(thisArg, args);
}

module.exports = apply;


/***/ }),

/***/ "./node_modules/lodash/_arrayEach.js":
/***/ (function(module, exports) {

/**
 * A specialized version of `_.forEach` for arrays without support for
 * iteratee shorthands.
 *
 * @private
 * @param {Array} [array] The array to iterate over.
 * @param {Function} iteratee The function invoked per iteration.
 * @returns {Array} Returns `array`.
 */
function arrayEach(array, iteratee) {
  var index = -1,
      length = array == null ? 0 : array.length;

  while (++index < length) {
    if (iteratee(array[index], index, array) === false) {
      break;
    }
  }
  return array;
}

module.exports = arrayEach;


/***/ }),

/***/ "./node_modules/lodash/_arrayFilter.js":
/***/ (function(module, exports) {

/**
 * A specialized version of `_.filter` for arrays without support for
 * iteratee shorthands.
 *
 * @private
 * @param {Array} [array] The array to iterate over.
 * @param {Function} predicate The function invoked per iteration.
 * @returns {Array} Returns the new filtered array.
 */
function arrayFilter(array, predicate) {
  var index = -1,
      length = array == null ? 0 : array.length,
      resIndex = 0,
      result = [];

  while (++index < length) {
    var value = array[index];
    if (predicate(value, index, array)) {
      result[resIndex++] = value;
    }
  }
  return result;
}

module.exports = arrayFilter;


/***/ }),

/***/ "./node_modules/lodash/_arrayIncludes.js":
/***/ (function(module, exports, __webpack_require__) {

var baseIndexOf = __webpack_require__("./node_modules/lodash/_baseIndexOf.js");

/**
 * A specialized version of `_.includes` for arrays without support for
 * specifying an index to search from.
 *
 * @private
 * @param {Array} [array] The array to inspect.
 * @param {*} target The value to search for.
 * @returns {boolean} Returns `true` if `target` is found, else `false`.
 */
function arrayIncludes(array, value) {
  var length = array == null ? 0 : array.length;
  return !!length && baseIndexOf(array, value, 0) > -1;
}

module.exports = arrayIncludes;


/***/ }),

/***/ "./node_modules/lodash/_arrayIncludesWith.js":
/***/ (function(module, exports) {

/**
 * This function is like `arrayIncludes` except that it accepts a comparator.
 *
 * @private
 * @param {Array} [array] The array to inspect.
 * @param {*} target The value to search for.
 * @param {Function} comparator The comparator invoked per element.
 * @returns {boolean} Returns `true` if `target` is found, else `false`.
 */
function arrayIncludesWith(array, value, comparator) {
  var index = -1,
      length = array == null ? 0 : array.length;

  while (++index < length) {
    if (comparator(value, array[index])) {
      return true;
    }
  }
  return false;
}

module.exports = arrayIncludesWith;


/***/ }),

/***/ "./node_modules/lodash/_arrayLikeKeys.js":
/***/ (function(module, exports, __webpack_require__) {

var baseTimes = __webpack_require__("./node_modules/lodash/_baseTimes.js"),
    isArguments = __webpack_require__("./node_modules/lodash/isArguments.js"),
    isArray = __webpack_require__("./node_modules/lodash/isArray.js"),
    isBuffer = __webpack_require__("./node_modules/lodash/isBuffer.js"),
    isIndex = __webpack_require__("./node_modules/lodash/_isIndex.js"),
    isTypedArray = __webpack_require__("./node_modules/lodash/isTypedArray.js");

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/**
 * Creates an array of the enumerable property names of the array-like `value`.
 *
 * @private
 * @param {*} value The value to query.
 * @param {boolean} inherited Specify returning inherited property names.
 * @returns {Array} Returns the array of property names.
 */
function arrayLikeKeys(value, inherited) {
  var isArr = isArray(value),
      isArg = !isArr && isArguments(value),
      isBuff = !isArr && !isArg && isBuffer(value),
      isType = !isArr && !isArg && !isBuff && isTypedArray(value),
      skipIndexes = isArr || isArg || isBuff || isType,
      result = skipIndexes ? baseTimes(value.length, String) : [],
      length = result.length;

  for (var key in value) {
    if ((inherited || hasOwnProperty.call(value, key)) &&
        !(skipIndexes && (
           // Safari 9 has enumerable `arguments.length` in strict mode.
           key == 'length' ||
           // Node.js 0.10 has enumerable non-index properties on buffers.
           (isBuff && (key == 'offset' || key == 'parent')) ||
           // PhantomJS 2 has enumerable non-index properties on typed arrays.
           (isType && (key == 'buffer' || key == 'byteLength' || key == 'byteOffset')) ||
           // Skip index properties.
           isIndex(key, length)
        ))) {
      result.push(key);
    }
  }
  return result;
}

module.exports = arrayLikeKeys;


/***/ }),

/***/ "./node_modules/lodash/_arrayMap.js":
/***/ (function(module, exports) {

/**
 * A specialized version of `_.map` for arrays without support for iteratee
 * shorthands.
 *
 * @private
 * @param {Array} [array] The array to iterate over.
 * @param {Function} iteratee The function invoked per iteration.
 * @returns {Array} Returns the new mapped array.
 */
function arrayMap(array, iteratee) {
  var index = -1,
      length = array == null ? 0 : array.length,
      result = Array(length);

  while (++index < length) {
    result[index] = iteratee(array[index], index, array);
  }
  return result;
}

module.exports = arrayMap;


/***/ }),

/***/ "./node_modules/lodash/_arrayPush.js":
/***/ (function(module, exports) {

/**
 * Appends the elements of `values` to `array`.
 *
 * @private
 * @param {Array} array The array to modify.
 * @param {Array} values The values to append.
 * @returns {Array} Returns `array`.
 */
function arrayPush(array, values) {
  var index = -1,
      length = values.length,
      offset = array.length;

  while (++index < length) {
    array[offset + index] = values[index];
  }
  return array;
}

module.exports = arrayPush;


/***/ }),

/***/ "./node_modules/lodash/_asciiToArray.js":
/***/ (function(module, exports) {

/**
 * Converts an ASCII `string` to an array.
 *
 * @private
 * @param {string} string The string to convert.
 * @returns {Array} Returns the converted array.
 */
function asciiToArray(string) {
  return string.split('');
}

module.exports = asciiToArray;


/***/ }),

/***/ "./node_modules/lodash/_assignMergeValue.js":
/***/ (function(module, exports, __webpack_require__) {

var baseAssignValue = __webpack_require__("./node_modules/lodash/_baseAssignValue.js"),
    eq = __webpack_require__("./node_modules/lodash/eq.js");

/**
 * This function is like `assignValue` except that it doesn't assign
 * `undefined` values.
 *
 * @private
 * @param {Object} object The object to modify.
 * @param {string} key The key of the property to assign.
 * @param {*} value The value to assign.
 */
function assignMergeValue(object, key, value) {
  if ((value !== undefined && !eq(object[key], value)) ||
      (value === undefined && !(key in object))) {
    baseAssignValue(object, key, value);
  }
}

module.exports = assignMergeValue;


/***/ }),

/***/ "./node_modules/lodash/_assignValue.js":
/***/ (function(module, exports, __webpack_require__) {

var baseAssignValue = __webpack_require__("./node_modules/lodash/_baseAssignValue.js"),
    eq = __webpack_require__("./node_modules/lodash/eq.js");

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/**
 * Assigns `value` to `key` of `object` if the existing value is not equivalent
 * using [`SameValueZero`](http://ecma-international.org/ecma-262/7.0/#sec-samevaluezero)
 * for equality comparisons.
 *
 * @private
 * @param {Object} object The object to modify.
 * @param {string} key The key of the property to assign.
 * @param {*} value The value to assign.
 */
function assignValue(object, key, value) {
  var objValue = object[key];
  if (!(hasOwnProperty.call(object, key) && eq(objValue, value)) ||
      (value === undefined && !(key in object))) {
    baseAssignValue(object, key, value);
  }
}

module.exports = assignValue;


/***/ }),

/***/ "./node_modules/lodash/_assocIndexOf.js":
/***/ (function(module, exports, __webpack_require__) {

var eq = __webpack_require__("./node_modules/lodash/eq.js");

/**
 * Gets the index at which the `key` is found in `array` of key-value pairs.
 *
 * @private
 * @param {Array} array The array to inspect.
 * @param {*} key The key to search for.
 * @returns {number} Returns the index of the matched value, else `-1`.
 */
function assocIndexOf(array, key) {
  var length = array.length;
  while (length--) {
    if (eq(array[length][0], key)) {
      return length;
    }
  }
  return -1;
}

module.exports = assocIndexOf;


/***/ }),

/***/ "./node_modules/lodash/_baseAssign.js":
/***/ (function(module, exports, __webpack_require__) {

var copyObject = __webpack_require__("./node_modules/lodash/_copyObject.js"),
    keys = __webpack_require__("./node_modules/lodash/keys.js");

/**
 * The base implementation of `_.assign` without support for multiple sources
 * or `customizer` functions.
 *
 * @private
 * @param {Object} object The destination object.
 * @param {Object} source The source object.
 * @returns {Object} Returns `object`.
 */
function baseAssign(object, source) {
  return object && copyObject(source, keys(source), object);
}

module.exports = baseAssign;


/***/ }),

/***/ "./node_modules/lodash/_baseAssignIn.js":
/***/ (function(module, exports, __webpack_require__) {

var copyObject = __webpack_require__("./node_modules/lodash/_copyObject.js"),
    keysIn = __webpack_require__("./node_modules/lodash/keysIn.js");

/**
 * The base implementation of `_.assignIn` without support for multiple sources
 * or `customizer` functions.
 *
 * @private
 * @param {Object} object The destination object.
 * @param {Object} source The source object.
 * @returns {Object} Returns `object`.
 */
function baseAssignIn(object, source) {
  return object && copyObject(source, keysIn(source), object);
}

module.exports = baseAssignIn;


/***/ }),

/***/ "./node_modules/lodash/_baseAssignValue.js":
/***/ (function(module, exports, __webpack_require__) {

var defineProperty = __webpack_require__("./node_modules/lodash/_defineProperty.js");

/**
 * The base implementation of `assignValue` and `assignMergeValue` without
 * value checks.
 *
 * @private
 * @param {Object} object The object to modify.
 * @param {string} key The key of the property to assign.
 * @param {*} value The value to assign.
 */
function baseAssignValue(object, key, value) {
  if (key == '__proto__' && defineProperty) {
    defineProperty(object, key, {
      'configurable': true,
      'enumerable': true,
      'value': value,
      'writable': true
    });
  } else {
    object[key] = value;
  }
}

module.exports = baseAssignValue;


/***/ }),

/***/ "./node_modules/lodash/_baseClone.js":
/***/ (function(module, exports, __webpack_require__) {

var Stack = __webpack_require__("./node_modules/lodash/_Stack.js"),
    arrayEach = __webpack_require__("./node_modules/lodash/_arrayEach.js"),
    assignValue = __webpack_require__("./node_modules/lodash/_assignValue.js"),
    baseAssign = __webpack_require__("./node_modules/lodash/_baseAssign.js"),
    baseAssignIn = __webpack_require__("./node_modules/lodash/_baseAssignIn.js"),
    cloneBuffer = __webpack_require__("./node_modules/lodash/_cloneBuffer.js"),
    copyArray = __webpack_require__("./node_modules/lodash/_copyArray.js"),
    copySymbols = __webpack_require__("./node_modules/lodash/_copySymbols.js"),
    copySymbolsIn = __webpack_require__("./node_modules/lodash/_copySymbolsIn.js"),
    getAllKeys = __webpack_require__("./node_modules/lodash/_getAllKeys.js"),
    getAllKeysIn = __webpack_require__("./node_modules/lodash/_getAllKeysIn.js"),
    getTag = __webpack_require__("./node_modules/lodash/_getTag.js"),
    initCloneArray = __webpack_require__("./node_modules/lodash/_initCloneArray.js"),
    initCloneByTag = __webpack_require__("./node_modules/lodash/_initCloneByTag.js"),
    initCloneObject = __webpack_require__("./node_modules/lodash/_initCloneObject.js"),
    isArray = __webpack_require__("./node_modules/lodash/isArray.js"),
    isBuffer = __webpack_require__("./node_modules/lodash/isBuffer.js"),
    isMap = __webpack_require__("./node_modules/lodash/isMap.js"),
    isObject = __webpack_require__("./node_modules/lodash/isObject.js"),
    isSet = __webpack_require__("./node_modules/lodash/isSet.js"),
    keys = __webpack_require__("./node_modules/lodash/keys.js"),
    keysIn = __webpack_require__("./node_modules/lodash/keysIn.js");

/** Used to compose bitmasks for cloning. */
var CLONE_DEEP_FLAG = 1,
    CLONE_FLAT_FLAG = 2,
    CLONE_SYMBOLS_FLAG = 4;

/** `Object#toString` result references. */
var argsTag = '[object Arguments]',
    arrayTag = '[object Array]',
    boolTag = '[object Boolean]',
    dateTag = '[object Date]',
    errorTag = '[object Error]',
    funcTag = '[object Function]',
    genTag = '[object GeneratorFunction]',
    mapTag = '[object Map]',
    numberTag = '[object Number]',
    objectTag = '[object Object]',
    regexpTag = '[object RegExp]',
    setTag = '[object Set]',
    stringTag = '[object String]',
    symbolTag = '[object Symbol]',
    weakMapTag = '[object WeakMap]';

var arrayBufferTag = '[object ArrayBuffer]',
    dataViewTag = '[object DataView]',
    float32Tag = '[object Float32Array]',
    float64Tag = '[object Float64Array]',
    int8Tag = '[object Int8Array]',
    int16Tag = '[object Int16Array]',
    int32Tag = '[object Int32Array]',
    uint8Tag = '[object Uint8Array]',
    uint8ClampedTag = '[object Uint8ClampedArray]',
    uint16Tag = '[object Uint16Array]',
    uint32Tag = '[object Uint32Array]';

/** Used to identify `toStringTag` values supported by `_.clone`. */
var cloneableTags = {};
cloneableTags[argsTag] = cloneableTags[arrayTag] =
cloneableTags[arrayBufferTag] = cloneableTags[dataViewTag] =
cloneableTags[boolTag] = cloneableTags[dateTag] =
cloneableTags[float32Tag] = cloneableTags[float64Tag] =
cloneableTags[int8Tag] = cloneableTags[int16Tag] =
cloneableTags[int32Tag] = cloneableTags[mapTag] =
cloneableTags[numberTag] = cloneableTags[objectTag] =
cloneableTags[regexpTag] = cloneableTags[setTag] =
cloneableTags[stringTag] = cloneableTags[symbolTag] =
cloneableTags[uint8Tag] = cloneableTags[uint8ClampedTag] =
cloneableTags[uint16Tag] = cloneableTags[uint32Tag] = true;
cloneableTags[errorTag] = cloneableTags[funcTag] =
cloneableTags[weakMapTag] = false;

/**
 * The base implementation of `_.clone` and `_.cloneDeep` which tracks
 * traversed objects.
 *
 * @private
 * @param {*} value The value to clone.
 * @param {boolean} bitmask The bitmask flags.
 *  1 - Deep clone
 *  2 - Flatten inherited properties
 *  4 - Clone symbols
 * @param {Function} [customizer] The function to customize cloning.
 * @param {string} [key] The key of `value`.
 * @param {Object} [object] The parent object of `value`.
 * @param {Object} [stack] Tracks traversed objects and their clone counterparts.
 * @returns {*} Returns the cloned value.
 */
function baseClone(value, bitmask, customizer, key, object, stack) {
  var result,
      isDeep = bitmask & CLONE_DEEP_FLAG,
      isFlat = bitmask & CLONE_FLAT_FLAG,
      isFull = bitmask & CLONE_SYMBOLS_FLAG;

  if (customizer) {
    result = object ? customizer(value, key, object, stack) : customizer(value);
  }
  if (result !== undefined) {
    return result;
  }
  if (!isObject(value)) {
    return value;
  }
  var isArr = isArray(value);
  if (isArr) {
    result = initCloneArray(value);
    if (!isDeep) {
      return copyArray(value, result);
    }
  } else {
    var tag = getTag(value),
        isFunc = tag == funcTag || tag == genTag;

    if (isBuffer(value)) {
      return cloneBuffer(value, isDeep);
    }
    if (tag == objectTag || tag == argsTag || (isFunc && !object)) {
      result = (isFlat || isFunc) ? {} : initCloneObject(value);
      if (!isDeep) {
        return isFlat
          ? copySymbolsIn(value, baseAssignIn(result, value))
          : copySymbols(value, baseAssign(result, value));
      }
    } else {
      if (!cloneableTags[tag]) {
        return object ? value : {};
      }
      result = initCloneByTag(value, tag, isDeep);
    }
  }
  // Check for circular references and return its corresponding clone.
  stack || (stack = new Stack);
  var stacked = stack.get(value);
  if (stacked) {
    return stacked;
  }
  stack.set(value, result);

  if (isSet(value)) {
    value.forEach(function(subValue) {
      result.add(baseClone(subValue, bitmask, customizer, subValue, value, stack));
    });
  } else if (isMap(value)) {
    value.forEach(function(subValue, key) {
      result.set(key, baseClone(subValue, bitmask, customizer, key, value, stack));
    });
  }

  var keysFunc = isFull
    ? (isFlat ? getAllKeysIn : getAllKeys)
    : (isFlat ? keysIn : keys);

  var props = isArr ? undefined : keysFunc(value);
  arrayEach(props || value, function(subValue, key) {
    if (props) {
      key = subValue;
      subValue = value[key];
    }
    // Recursively populate clone (susceptible to call stack limits).
    assignValue(result, key, baseClone(subValue, bitmask, customizer, key, value, stack));
  });
  return result;
}

module.exports = baseClone;


/***/ }),

/***/ "./node_modules/lodash/_baseCreate.js":
/***/ (function(module, exports, __webpack_require__) {

var isObject = __webpack_require__("./node_modules/lodash/isObject.js");

/** Built-in value references. */
var objectCreate = Object.create;

/**
 * The base implementation of `_.create` without support for assigning
 * properties to the created object.
 *
 * @private
 * @param {Object} proto The object to inherit from.
 * @returns {Object} Returns the new object.
 */
var baseCreate = (function() {
  function object() {}
  return function(proto) {
    if (!isObject(proto)) {
      return {};
    }
    if (objectCreate) {
      return objectCreate(proto);
    }
    object.prototype = proto;
    var result = new object;
    object.prototype = undefined;
    return result;
  };
}());

module.exports = baseCreate;


/***/ }),

/***/ "./node_modules/lodash/_baseDifference.js":
/***/ (function(module, exports, __webpack_require__) {

var SetCache = __webpack_require__("./node_modules/lodash/_SetCache.js"),
    arrayIncludes = __webpack_require__("./node_modules/lodash/_arrayIncludes.js"),
    arrayIncludesWith = __webpack_require__("./node_modules/lodash/_arrayIncludesWith.js"),
    arrayMap = __webpack_require__("./node_modules/lodash/_arrayMap.js"),
    baseUnary = __webpack_require__("./node_modules/lodash/_baseUnary.js"),
    cacheHas = __webpack_require__("./node_modules/lodash/_cacheHas.js");

/** Used as the size to enable large array optimizations. */
var LARGE_ARRAY_SIZE = 200;

/**
 * The base implementation of methods like `_.difference` without support
 * for excluding multiple arrays or iteratee shorthands.
 *
 * @private
 * @param {Array} array The array to inspect.
 * @param {Array} values The values to exclude.
 * @param {Function} [iteratee] The iteratee invoked per element.
 * @param {Function} [comparator] The comparator invoked per element.
 * @returns {Array} Returns the new array of filtered values.
 */
function baseDifference(array, values, iteratee, comparator) {
  var index = -1,
      includes = arrayIncludes,
      isCommon = true,
      length = array.length,
      result = [],
      valuesLength = values.length;

  if (!length) {
    return result;
  }
  if (iteratee) {
    values = arrayMap(values, baseUnary(iteratee));
  }
  if (comparator) {
    includes = arrayIncludesWith;
    isCommon = false;
  }
  else if (values.length >= LARGE_ARRAY_SIZE) {
    includes = cacheHas;
    isCommon = false;
    values = new SetCache(values);
  }
  outer:
  while (++index < length) {
    var value = array[index],
        computed = iteratee == null ? value : iteratee(value);

    value = (comparator || value !== 0) ? value : 0;
    if (isCommon && computed === computed) {
      var valuesIndex = valuesLength;
      while (valuesIndex--) {
        if (values[valuesIndex] === computed) {
          continue outer;
        }
      }
      result.push(value);
    }
    else if (!includes(values, computed, comparator)) {
      result.push(value);
    }
  }
  return result;
}

module.exports = baseDifference;


/***/ }),

/***/ "./node_modules/lodash/_baseFindIndex.js":
/***/ (function(module, exports) {

/**
 * The base implementation of `_.findIndex` and `_.findLastIndex` without
 * support for iteratee shorthands.
 *
 * @private
 * @param {Array} array The array to inspect.
 * @param {Function} predicate The function invoked per iteration.
 * @param {number} fromIndex The index to search from.
 * @param {boolean} [fromRight] Specify iterating from right to left.
 * @returns {number} Returns the index of the matched value, else `-1`.
 */
function baseFindIndex(array, predicate, fromIndex, fromRight) {
  var length = array.length,
      index = fromIndex + (fromRight ? 1 : -1);

  while ((fromRight ? index-- : ++index < length)) {
    if (predicate(array[index], index, array)) {
      return index;
    }
  }
  return -1;
}

module.exports = baseFindIndex;


/***/ }),

/***/ "./node_modules/lodash/_baseFlatten.js":
/***/ (function(module, exports, __webpack_require__) {

var arrayPush = __webpack_require__("./node_modules/lodash/_arrayPush.js"),
    isFlattenable = __webpack_require__("./node_modules/lodash/_isFlattenable.js");

/**
 * The base implementation of `_.flatten` with support for restricting flattening.
 *
 * @private
 * @param {Array} array The array to flatten.
 * @param {number} depth The maximum recursion depth.
 * @param {boolean} [predicate=isFlattenable] The function invoked per iteration.
 * @param {boolean} [isStrict] Restrict to values that pass `predicate` checks.
 * @param {Array} [result=[]] The initial result value.
 * @returns {Array} Returns the new flattened array.
 */
function baseFlatten(array, depth, predicate, isStrict, result) {
  var index = -1,
      length = array.length;

  predicate || (predicate = isFlattenable);
  result || (result = []);

  while (++index < length) {
    var value = array[index];
    if (depth > 0 && predicate(value)) {
      if (depth > 1) {
        // Recursively flatten arrays (susceptible to call stack limits).
        baseFlatten(value, depth - 1, predicate, isStrict, result);
      } else {
        arrayPush(result, value);
      }
    } else if (!isStrict) {
      result[result.length] = value;
    }
  }
  return result;
}

module.exports = baseFlatten;


/***/ }),

/***/ "./node_modules/lodash/_baseFor.js":
/***/ (function(module, exports, __webpack_require__) {

var createBaseFor = __webpack_require__("./node_modules/lodash/_createBaseFor.js");

/**
 * The base implementation of `baseForOwn` which iterates over `object`
 * properties returned by `keysFunc` and invokes `iteratee` for each property.
 * Iteratee functions may exit iteration early by explicitly returning `false`.
 *
 * @private
 * @param {Object} object The object to iterate over.
 * @param {Function} iteratee The function invoked per iteration.
 * @param {Function} keysFunc The function to get the keys of `object`.
 * @returns {Object} Returns `object`.
 */
var baseFor = createBaseFor();

module.exports = baseFor;


/***/ }),

/***/ "./node_modules/lodash/_baseFunctions.js":
/***/ (function(module, exports, __webpack_require__) {

var arrayFilter = __webpack_require__("./node_modules/lodash/_arrayFilter.js"),
    isFunction = __webpack_require__("./node_modules/lodash/isFunction.js");

/**
 * The base implementation of `_.functions` which creates an array of
 * `object` function property names filtered from `props`.
 *
 * @private
 * @param {Object} object The object to inspect.
 * @param {Array} props The property names to filter.
 * @returns {Array} Returns the function names.
 */
function baseFunctions(object, props) {
  return arrayFilter(props, function(key) {
    return isFunction(object[key]);
  });
}

module.exports = baseFunctions;


/***/ }),

/***/ "./node_modules/lodash/_baseGetAllKeys.js":
/***/ (function(module, exports, __webpack_require__) {

var arrayPush = __webpack_require__("./node_modules/lodash/_arrayPush.js"),
    isArray = __webpack_require__("./node_modules/lodash/isArray.js");

/**
 * The base implementation of `getAllKeys` and `getAllKeysIn` which uses
 * `keysFunc` and `symbolsFunc` to get the enumerable property names and
 * symbols of `object`.
 *
 * @private
 * @param {Object} object The object to query.
 * @param {Function} keysFunc The function to get the keys of `object`.
 * @param {Function} symbolsFunc The function to get the symbols of `object`.
 * @returns {Array} Returns the array of property names and symbols.
 */
function baseGetAllKeys(object, keysFunc, symbolsFunc) {
  var result = keysFunc(object);
  return isArray(object) ? result : arrayPush(result, symbolsFunc(object));
}

module.exports = baseGetAllKeys;


/***/ }),

/***/ "./node_modules/lodash/_baseGetTag.js":
/***/ (function(module, exports, __webpack_require__) {

var Symbol = __webpack_require__("./node_modules/lodash/_Symbol.js"),
    getRawTag = __webpack_require__("./node_modules/lodash/_getRawTag.js"),
    objectToString = __webpack_require__("./node_modules/lodash/_objectToString.js");

/** `Object#toString` result references. */
var nullTag = '[object Null]',
    undefinedTag = '[object Undefined]';

/** Built-in value references. */
var symToStringTag = Symbol ? Symbol.toStringTag : undefined;

/**
 * The base implementation of `getTag` without fallbacks for buggy environments.
 *
 * @private
 * @param {*} value The value to query.
 * @returns {string} Returns the `toStringTag`.
 */
function baseGetTag(value) {
  if (value == null) {
    return value === undefined ? undefinedTag : nullTag;
  }
  return (symToStringTag && symToStringTag in Object(value))
    ? getRawTag(value)
    : objectToString(value);
}

module.exports = baseGetTag;


/***/ }),

/***/ "./node_modules/lodash/_baseIndexOf.js":
/***/ (function(module, exports, __webpack_require__) {

var baseFindIndex = __webpack_require__("./node_modules/lodash/_baseFindIndex.js"),
    baseIsNaN = __webpack_require__("./node_modules/lodash/_baseIsNaN.js"),
    strictIndexOf = __webpack_require__("./node_modules/lodash/_strictIndexOf.js");

/**
 * The base implementation of `_.indexOf` without `fromIndex` bounds checks.
 *
 * @private
 * @param {Array} array The array to inspect.
 * @param {*} value The value to search for.
 * @param {number} fromIndex The index to search from.
 * @returns {number} Returns the index of the matched value, else `-1`.
 */
function baseIndexOf(array, value, fromIndex) {
  return value === value
    ? strictIndexOf(array, value, fromIndex)
    : baseFindIndex(array, baseIsNaN, fromIndex);
}

module.exports = baseIndexOf;


/***/ }),

/***/ "./node_modules/lodash/_baseIsArguments.js":
/***/ (function(module, exports, __webpack_require__) {

var baseGetTag = __webpack_require__("./node_modules/lodash/_baseGetTag.js"),
    isObjectLike = __webpack_require__("./node_modules/lodash/isObjectLike.js");

/** `Object#toString` result references. */
var argsTag = '[object Arguments]';

/**
 * The base implementation of `_.isArguments`.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is an `arguments` object,
 */
function baseIsArguments(value) {
  return isObjectLike(value) && baseGetTag(value) == argsTag;
}

module.exports = baseIsArguments;


/***/ }),

/***/ "./node_modules/lodash/_baseIsMap.js":
/***/ (function(module, exports, __webpack_require__) {

var getTag = __webpack_require__("./node_modules/lodash/_getTag.js"),
    isObjectLike = __webpack_require__("./node_modules/lodash/isObjectLike.js");

/** `Object#toString` result references. */
var mapTag = '[object Map]';

/**
 * The base implementation of `_.isMap` without Node.js optimizations.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a map, else `false`.
 */
function baseIsMap(value) {
  return isObjectLike(value) && getTag(value) == mapTag;
}

module.exports = baseIsMap;


/***/ }),

/***/ "./node_modules/lodash/_baseIsNaN.js":
/***/ (function(module, exports) {

/**
 * The base implementation of `_.isNaN` without support for number objects.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is `NaN`, else `false`.
 */
function baseIsNaN(value) {
  return value !== value;
}

module.exports = baseIsNaN;


/***/ }),

/***/ "./node_modules/lodash/_baseIsNative.js":
/***/ (function(module, exports, __webpack_require__) {

var isFunction = __webpack_require__("./node_modules/lodash/isFunction.js"),
    isMasked = __webpack_require__("./node_modules/lodash/_isMasked.js"),
    isObject = __webpack_require__("./node_modules/lodash/isObject.js"),
    toSource = __webpack_require__("./node_modules/lodash/_toSource.js");

/**
 * Used to match `RegExp`
 * [syntax characters](http://ecma-international.org/ecma-262/7.0/#sec-patterns).
 */
var reRegExpChar = /[\\^$.*+?()[\]{}|]/g;

/** Used to detect host constructors (Safari). */
var reIsHostCtor = /^\[object .+?Constructor\]$/;

/** Used for built-in method references. */
var funcProto = Function.prototype,
    objectProto = Object.prototype;

/** Used to resolve the decompiled source of functions. */
var funcToString = funcProto.toString;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/** Used to detect if a method is native. */
var reIsNative = RegExp('^' +
  funcToString.call(hasOwnProperty).replace(reRegExpChar, '\\$&')
  .replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, '$1.*?') + '$'
);

/**
 * The base implementation of `_.isNative` without bad shim checks.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a native function,
 *  else `false`.
 */
function baseIsNative(value) {
  if (!isObject(value) || isMasked(value)) {
    return false;
  }
  var pattern = isFunction(value) ? reIsNative : reIsHostCtor;
  return pattern.test(toSource(value));
}

module.exports = baseIsNative;


/***/ }),

/***/ "./node_modules/lodash/_baseIsSet.js":
/***/ (function(module, exports, __webpack_require__) {

var getTag = __webpack_require__("./node_modules/lodash/_getTag.js"),
    isObjectLike = __webpack_require__("./node_modules/lodash/isObjectLike.js");

/** `Object#toString` result references. */
var setTag = '[object Set]';

/**
 * The base implementation of `_.isSet` without Node.js optimizations.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a set, else `false`.
 */
function baseIsSet(value) {
  return isObjectLike(value) && getTag(value) == setTag;
}

module.exports = baseIsSet;


/***/ }),

/***/ "./node_modules/lodash/_baseIsTypedArray.js":
/***/ (function(module, exports, __webpack_require__) {

var baseGetTag = __webpack_require__("./node_modules/lodash/_baseGetTag.js"),
    isLength = __webpack_require__("./node_modules/lodash/isLength.js"),
    isObjectLike = __webpack_require__("./node_modules/lodash/isObjectLike.js");

/** `Object#toString` result references. */
var argsTag = '[object Arguments]',
    arrayTag = '[object Array]',
    boolTag = '[object Boolean]',
    dateTag = '[object Date]',
    errorTag = '[object Error]',
    funcTag = '[object Function]',
    mapTag = '[object Map]',
    numberTag = '[object Number]',
    objectTag = '[object Object]',
    regexpTag = '[object RegExp]',
    setTag = '[object Set]',
    stringTag = '[object String]',
    weakMapTag = '[object WeakMap]';

var arrayBufferTag = '[object ArrayBuffer]',
    dataViewTag = '[object DataView]',
    float32Tag = '[object Float32Array]',
    float64Tag = '[object Float64Array]',
    int8Tag = '[object Int8Array]',
    int16Tag = '[object Int16Array]',
    int32Tag = '[object Int32Array]',
    uint8Tag = '[object Uint8Array]',
    uint8ClampedTag = '[object Uint8ClampedArray]',
    uint16Tag = '[object Uint16Array]',
    uint32Tag = '[object Uint32Array]';

/** Used to identify `toStringTag` values of typed arrays. */
var typedArrayTags = {};
typedArrayTags[float32Tag] = typedArrayTags[float64Tag] =
typedArrayTags[int8Tag] = typedArrayTags[int16Tag] =
typedArrayTags[int32Tag] = typedArrayTags[uint8Tag] =
typedArrayTags[uint8ClampedTag] = typedArrayTags[uint16Tag] =
typedArrayTags[uint32Tag] = true;
typedArrayTags[argsTag] = typedArrayTags[arrayTag] =
typedArrayTags[arrayBufferTag] = typedArrayTags[boolTag] =
typedArrayTags[dataViewTag] = typedArrayTags[dateTag] =
typedArrayTags[errorTag] = typedArrayTags[funcTag] =
typedArrayTags[mapTag] = typedArrayTags[numberTag] =
typedArrayTags[objectTag] = typedArrayTags[regexpTag] =
typedArrayTags[setTag] = typedArrayTags[stringTag] =
typedArrayTags[weakMapTag] = false;

/**
 * The base implementation of `_.isTypedArray` without Node.js optimizations.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a typed array, else `false`.
 */
function baseIsTypedArray(value) {
  return isObjectLike(value) &&
    isLength(value.length) && !!typedArrayTags[baseGetTag(value)];
}

module.exports = baseIsTypedArray;


/***/ }),

/***/ "./node_modules/lodash/_baseKeys.js":
/***/ (function(module, exports, __webpack_require__) {

var isPrototype = __webpack_require__("./node_modules/lodash/_isPrototype.js"),
    nativeKeys = __webpack_require__("./node_modules/lodash/_nativeKeys.js");

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/**
 * The base implementation of `_.keys` which doesn't treat sparse arrays as dense.
 *
 * @private
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of property names.
 */
function baseKeys(object) {
  if (!isPrototype(object)) {
    return nativeKeys(object);
  }
  var result = [];
  for (var key in Object(object)) {
    if (hasOwnProperty.call(object, key) && key != 'constructor') {
      result.push(key);
    }
  }
  return result;
}

module.exports = baseKeys;


/***/ }),

/***/ "./node_modules/lodash/_baseKeysIn.js":
/***/ (function(module, exports, __webpack_require__) {

var isObject = __webpack_require__("./node_modules/lodash/isObject.js"),
    isPrototype = __webpack_require__("./node_modules/lodash/_isPrototype.js"),
    nativeKeysIn = __webpack_require__("./node_modules/lodash/_nativeKeysIn.js");

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/**
 * The base implementation of `_.keysIn` which doesn't treat sparse arrays as dense.
 *
 * @private
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of property names.
 */
function baseKeysIn(object) {
  if (!isObject(object)) {
    return nativeKeysIn(object);
  }
  var isProto = isPrototype(object),
      result = [];

  for (var key in object) {
    if (!(key == 'constructor' && (isProto || !hasOwnProperty.call(object, key)))) {
      result.push(key);
    }
  }
  return result;
}

module.exports = baseKeysIn;


/***/ }),

/***/ "./node_modules/lodash/_baseMerge.js":
/***/ (function(module, exports, __webpack_require__) {

var Stack = __webpack_require__("./node_modules/lodash/_Stack.js"),
    assignMergeValue = __webpack_require__("./node_modules/lodash/_assignMergeValue.js"),
    baseFor = __webpack_require__("./node_modules/lodash/_baseFor.js"),
    baseMergeDeep = __webpack_require__("./node_modules/lodash/_baseMergeDeep.js"),
    isObject = __webpack_require__("./node_modules/lodash/isObject.js"),
    keysIn = __webpack_require__("./node_modules/lodash/keysIn.js"),
    safeGet = __webpack_require__("./node_modules/lodash/_safeGet.js");

/**
 * The base implementation of `_.merge` without support for multiple sources.
 *
 * @private
 * @param {Object} object The destination object.
 * @param {Object} source The source object.
 * @param {number} srcIndex The index of `source`.
 * @param {Function} [customizer] The function to customize merged values.
 * @param {Object} [stack] Tracks traversed source values and their merged
 *  counterparts.
 */
function baseMerge(object, source, srcIndex, customizer, stack) {
  if (object === source) {
    return;
  }
  baseFor(source, function(srcValue, key) {
    stack || (stack = new Stack);
    if (isObject(srcValue)) {
      baseMergeDeep(object, source, key, srcIndex, baseMerge, customizer, stack);
    }
    else {
      var newValue = customizer
        ? customizer(safeGet(object, key), srcValue, (key + ''), object, source, stack)
        : undefined;

      if (newValue === undefined) {
        newValue = srcValue;
      }
      assignMergeValue(object, key, newValue);
    }
  }, keysIn);
}

module.exports = baseMerge;


/***/ }),

/***/ "./node_modules/lodash/_baseMergeDeep.js":
/***/ (function(module, exports, __webpack_require__) {

var assignMergeValue = __webpack_require__("./node_modules/lodash/_assignMergeValue.js"),
    cloneBuffer = __webpack_require__("./node_modules/lodash/_cloneBuffer.js"),
    cloneTypedArray = __webpack_require__("./node_modules/lodash/_cloneTypedArray.js"),
    copyArray = __webpack_require__("./node_modules/lodash/_copyArray.js"),
    initCloneObject = __webpack_require__("./node_modules/lodash/_initCloneObject.js"),
    isArguments = __webpack_require__("./node_modules/lodash/isArguments.js"),
    isArray = __webpack_require__("./node_modules/lodash/isArray.js"),
    isArrayLikeObject = __webpack_require__("./node_modules/lodash/isArrayLikeObject.js"),
    isBuffer = __webpack_require__("./node_modules/lodash/isBuffer.js"),
    isFunction = __webpack_require__("./node_modules/lodash/isFunction.js"),
    isObject = __webpack_require__("./node_modules/lodash/isObject.js"),
    isPlainObject = __webpack_require__("./node_modules/lodash/isPlainObject.js"),
    isTypedArray = __webpack_require__("./node_modules/lodash/isTypedArray.js"),
    safeGet = __webpack_require__("./node_modules/lodash/_safeGet.js"),
    toPlainObject = __webpack_require__("./node_modules/lodash/toPlainObject.js");

/**
 * A specialized version of `baseMerge` for arrays and objects which performs
 * deep merges and tracks traversed objects enabling objects with circular
 * references to be merged.
 *
 * @private
 * @param {Object} object The destination object.
 * @param {Object} source The source object.
 * @param {string} key The key of the value to merge.
 * @param {number} srcIndex The index of `source`.
 * @param {Function} mergeFunc The function to merge values.
 * @param {Function} [customizer] The function to customize assigned values.
 * @param {Object} [stack] Tracks traversed source values and their merged
 *  counterparts.
 */
function baseMergeDeep(object, source, key, srcIndex, mergeFunc, customizer, stack) {
  var objValue = safeGet(object, key),
      srcValue = safeGet(source, key),
      stacked = stack.get(srcValue);

  if (stacked) {
    assignMergeValue(object, key, stacked);
    return;
  }
  var newValue = customizer
    ? customizer(objValue, srcValue, (key + ''), object, source, stack)
    : undefined;

  var isCommon = newValue === undefined;

  if (isCommon) {
    var isArr = isArray(srcValue),
        isBuff = !isArr && isBuffer(srcValue),
        isTyped = !isArr && !isBuff && isTypedArray(srcValue);

    newValue = srcValue;
    if (isArr || isBuff || isTyped) {
      if (isArray(objValue)) {
        newValue = objValue;
      }
      else if (isArrayLikeObject(objValue)) {
        newValue = copyArray(objValue);
      }
      else if (isBuff) {
        isCommon = false;
        newValue = cloneBuffer(srcValue, true);
      }
      else if (isTyped) {
        isCommon = false;
        newValue = cloneTypedArray(srcValue, true);
      }
      else {
        newValue = [];
      }
    }
    else if (isPlainObject(srcValue) || isArguments(srcValue)) {
      newValue = objValue;
      if (isArguments(objValue)) {
        newValue = toPlainObject(objValue);
      }
      else if (!isObject(objValue) || isFunction(objValue)) {
        newValue = initCloneObject(srcValue);
      }
    }
    else {
      isCommon = false;
    }
  }
  if (isCommon) {
    // Recursively merge objects and arrays (susceptible to call stack limits).
    stack.set(srcValue, newValue);
    mergeFunc(newValue, srcValue, srcIndex, customizer, stack);
    stack['delete'](srcValue);
  }
  assignMergeValue(object, key, newValue);
}

module.exports = baseMergeDeep;


/***/ }),

/***/ "./node_modules/lodash/_baseRest.js":
/***/ (function(module, exports, __webpack_require__) {

var identity = __webpack_require__("./node_modules/lodash/identity.js"),
    overRest = __webpack_require__("./node_modules/lodash/_overRest.js"),
    setToString = __webpack_require__("./node_modules/lodash/_setToString.js");

/**
 * The base implementation of `_.rest` which doesn't validate or coerce arguments.
 *
 * @private
 * @param {Function} func The function to apply a rest parameter to.
 * @param {number} [start=func.length-1] The start position of the rest parameter.
 * @returns {Function} Returns the new function.
 */
function baseRest(func, start) {
  return setToString(overRest(func, start, identity), func + '');
}

module.exports = baseRest;


/***/ }),

/***/ "./node_modules/lodash/_baseSetToString.js":
/***/ (function(module, exports, __webpack_require__) {

var constant = __webpack_require__("./node_modules/lodash/constant.js"),
    defineProperty = __webpack_require__("./node_modules/lodash/_defineProperty.js"),
    identity = __webpack_require__("./node_modules/lodash/identity.js");

/**
 * The base implementation of `setToString` without support for hot loop shorting.
 *
 * @private
 * @param {Function} func The function to modify.
 * @param {Function} string The `toString` result.
 * @returns {Function} Returns `func`.
 */
var baseSetToString = !defineProperty ? identity : function(func, string) {
  return defineProperty(func, 'toString', {
    'configurable': true,
    'enumerable': false,
    'value': constant(string),
    'writable': true
  });
};

module.exports = baseSetToString;


/***/ }),

/***/ "./node_modules/lodash/_baseSlice.js":
/***/ (function(module, exports) {

/**
 * The base implementation of `_.slice` without an iteratee call guard.
 *
 * @private
 * @param {Array} array The array to slice.
 * @param {number} [start=0] The start position.
 * @param {number} [end=array.length] The end position.
 * @returns {Array} Returns the slice of `array`.
 */
function baseSlice(array, start, end) {
  var index = -1,
      length = array.length;

  if (start < 0) {
    start = -start > length ? 0 : (length + start);
  }
  end = end > length ? length : end;
  if (end < 0) {
    end += length;
  }
  length = start > end ? 0 : ((end - start) >>> 0);
  start >>>= 0;

  var result = Array(length);
  while (++index < length) {
    result[index] = array[index + start];
  }
  return result;
}

module.exports = baseSlice;


/***/ }),

/***/ "./node_modules/lodash/_baseTimes.js":
/***/ (function(module, exports) {

/**
 * The base implementation of `_.times` without support for iteratee shorthands
 * or max array length checks.
 *
 * @private
 * @param {number} n The number of times to invoke `iteratee`.
 * @param {Function} iteratee The function invoked per iteration.
 * @returns {Array} Returns the array of results.
 */
function baseTimes(n, iteratee) {
  var index = -1,
      result = Array(n);

  while (++index < n) {
    result[index] = iteratee(index);
  }
  return result;
}

module.exports = baseTimes;


/***/ }),

/***/ "./node_modules/lodash/_baseToString.js":
/***/ (function(module, exports, __webpack_require__) {

var Symbol = __webpack_require__("./node_modules/lodash/_Symbol.js"),
    arrayMap = __webpack_require__("./node_modules/lodash/_arrayMap.js"),
    isArray = __webpack_require__("./node_modules/lodash/isArray.js"),
    isSymbol = __webpack_require__("./node_modules/lodash/isSymbol.js");

/** Used as references for various `Number` constants. */
var INFINITY = 1 / 0;

/** Used to convert symbols to primitives and strings. */
var symbolProto = Symbol ? Symbol.prototype : undefined,
    symbolToString = symbolProto ? symbolProto.toString : undefined;

/**
 * The base implementation of `_.toString` which doesn't convert nullish
 * values to empty strings.
 *
 * @private
 * @param {*} value The value to process.
 * @returns {string} Returns the string.
 */
function baseToString(value) {
  // Exit early for strings to avoid a performance hit in some environments.
  if (typeof value == 'string') {
    return value;
  }
  if (isArray(value)) {
    // Recursively convert values (susceptible to call stack limits).
    return arrayMap(value, baseToString) + '';
  }
  if (isSymbol(value)) {
    return symbolToString ? symbolToString.call(value) : '';
  }
  var result = (value + '');
  return (result == '0' && (1 / value) == -INFINITY) ? '-0' : result;
}

module.exports = baseToString;


/***/ }),

/***/ "./node_modules/lodash/_baseTrim.js":
/***/ (function(module, exports, __webpack_require__) {

var trimmedEndIndex = __webpack_require__("./node_modules/lodash/_trimmedEndIndex.js");

/** Used to match leading whitespace. */
var reTrimStart = /^\s+/;

/**
 * The base implementation of `_.trim`.
 *
 * @private
 * @param {string} string The string to trim.
 * @returns {string} Returns the trimmed string.
 */
function baseTrim(string) {
  return string
    ? string.slice(0, trimmedEndIndex(string) + 1).replace(reTrimStart, '')
    : string;
}

module.exports = baseTrim;


/***/ }),

/***/ "./node_modules/lodash/_baseUnary.js":
/***/ (function(module, exports) {

/**
 * The base implementation of `_.unary` without support for storing metadata.
 *
 * @private
 * @param {Function} func The function to cap arguments for.
 * @returns {Function} Returns the new capped function.
 */
function baseUnary(func) {
  return function(value) {
    return func(value);
  };
}

module.exports = baseUnary;


/***/ }),

/***/ "./node_modules/lodash/_baseValues.js":
/***/ (function(module, exports, __webpack_require__) {

var arrayMap = __webpack_require__("./node_modules/lodash/_arrayMap.js");

/**
 * The base implementation of `_.values` and `_.valuesIn` which creates an
 * array of `object` property values corresponding to the property names
 * of `props`.
 *
 * @private
 * @param {Object} object The object to query.
 * @param {Array} props The property names to get values for.
 * @returns {Object} Returns the array of property values.
 */
function baseValues(object, props) {
  return arrayMap(props, function(key) {
    return object[key];
  });
}

module.exports = baseValues;


/***/ }),

/***/ "./node_modules/lodash/_cacheHas.js":
/***/ (function(module, exports) {

/**
 * Checks if a `cache` value for `key` exists.
 *
 * @private
 * @param {Object} cache The cache to query.
 * @param {string} key The key of the entry to check.
 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
 */
function cacheHas(cache, key) {
  return cache.has(key);
}

module.exports = cacheHas;


/***/ }),

/***/ "./node_modules/lodash/_castSlice.js":
/***/ (function(module, exports, __webpack_require__) {

var baseSlice = __webpack_require__("./node_modules/lodash/_baseSlice.js");

/**
 * Casts `array` to a slice if it's needed.
 *
 * @private
 * @param {Array} array The array to inspect.
 * @param {number} start The start position.
 * @param {number} [end=array.length] The end position.
 * @returns {Array} Returns the cast slice.
 */
function castSlice(array, start, end) {
  var length = array.length;
  end = end === undefined ? length : end;
  return (!start && end >= length) ? array : baseSlice(array, start, end);
}

module.exports = castSlice;


/***/ }),

/***/ "./node_modules/lodash/_charsEndIndex.js":
/***/ (function(module, exports, __webpack_require__) {

var baseIndexOf = __webpack_require__("./node_modules/lodash/_baseIndexOf.js");

/**
 * Used by `_.trim` and `_.trimEnd` to get the index of the last string symbol
 * that is not found in the character symbols.
 *
 * @private
 * @param {Array} strSymbols The string symbols to inspect.
 * @param {Array} chrSymbols The character symbols to find.
 * @returns {number} Returns the index of the last unmatched string symbol.
 */
function charsEndIndex(strSymbols, chrSymbols) {
  var index = strSymbols.length;

  while (index-- && baseIndexOf(chrSymbols, strSymbols[index], 0) > -1) {}
  return index;
}

module.exports = charsEndIndex;


/***/ }),

/***/ "./node_modules/lodash/_charsStartIndex.js":
/***/ (function(module, exports, __webpack_require__) {

var baseIndexOf = __webpack_require__("./node_modules/lodash/_baseIndexOf.js");

/**
 * Used by `_.trim` and `_.trimStart` to get the index of the first string symbol
 * that is not found in the character symbols.
 *
 * @private
 * @param {Array} strSymbols The string symbols to inspect.
 * @param {Array} chrSymbols The character symbols to find.
 * @returns {number} Returns the index of the first unmatched string symbol.
 */
function charsStartIndex(strSymbols, chrSymbols) {
  var index = -1,
      length = strSymbols.length;

  while (++index < length && baseIndexOf(chrSymbols, strSymbols[index], 0) > -1) {}
  return index;
}

module.exports = charsStartIndex;


/***/ }),

/***/ "./node_modules/lodash/_cloneArrayBuffer.js":
/***/ (function(module, exports, __webpack_require__) {

var Uint8Array = __webpack_require__("./node_modules/lodash/_Uint8Array.js");

/**
 * Creates a clone of `arrayBuffer`.
 *
 * @private
 * @param {ArrayBuffer} arrayBuffer The array buffer to clone.
 * @returns {ArrayBuffer} Returns the cloned array buffer.
 */
function cloneArrayBuffer(arrayBuffer) {
  var result = new arrayBuffer.constructor(arrayBuffer.byteLength);
  new Uint8Array(result).set(new Uint8Array(arrayBuffer));
  return result;
}

module.exports = cloneArrayBuffer;


/***/ }),

/***/ "./node_modules/lodash/_cloneBuffer.js":
/***/ (function(module, exports, __webpack_require__) {

/* WEBPACK VAR INJECTION */(function(module) {var root = __webpack_require__("./node_modules/lodash/_root.js");

/** Detect free variable `exports`. */
var freeExports =  true && exports && !exports.nodeType && exports;

/** Detect free variable `module`. */
var freeModule = freeExports && typeof module == 'object' && module && !module.nodeType && module;

/** Detect the popular CommonJS extension `module.exports`. */
var moduleExports = freeModule && freeModule.exports === freeExports;

/** Built-in value references. */
var Buffer = moduleExports ? root.Buffer : undefined,
    allocUnsafe = Buffer ? Buffer.allocUnsafe : undefined;

/**
 * Creates a clone of  `buffer`.
 *
 * @private
 * @param {Buffer} buffer The buffer to clone.
 * @param {boolean} [isDeep] Specify a deep clone.
 * @returns {Buffer} Returns the cloned buffer.
 */
function cloneBuffer(buffer, isDeep) {
  if (isDeep) {
    return buffer.slice();
  }
  var length = buffer.length,
      result = allocUnsafe ? allocUnsafe(length) : new buffer.constructor(length);

  buffer.copy(result);
  return result;
}

module.exports = cloneBuffer;

/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__("./node_modules/webpack/buildin/module.js")(module)))

/***/ }),

/***/ "./node_modules/lodash/_cloneDataView.js":
/***/ (function(module, exports, __webpack_require__) {

var cloneArrayBuffer = __webpack_require__("./node_modules/lodash/_cloneArrayBuffer.js");

/**
 * Creates a clone of `dataView`.
 *
 * @private
 * @param {Object} dataView The data view to clone.
 * @param {boolean} [isDeep] Specify a deep clone.
 * @returns {Object} Returns the cloned data view.
 */
function cloneDataView(dataView, isDeep) {
  var buffer = isDeep ? cloneArrayBuffer(dataView.buffer) : dataView.buffer;
  return new dataView.constructor(buffer, dataView.byteOffset, dataView.byteLength);
}

module.exports = cloneDataView;


/***/ }),

/***/ "./node_modules/lodash/_cloneRegExp.js":
/***/ (function(module, exports) {

/** Used to match `RegExp` flags from their coerced string values. */
var reFlags = /\w*$/;

/**
 * Creates a clone of `regexp`.
 *
 * @private
 * @param {Object} regexp The regexp to clone.
 * @returns {Object} Returns the cloned regexp.
 */
function cloneRegExp(regexp) {
  var result = new regexp.constructor(regexp.source, reFlags.exec(regexp));
  result.lastIndex = regexp.lastIndex;
  return result;
}

module.exports = cloneRegExp;


/***/ }),

/***/ "./node_modules/lodash/_cloneSymbol.js":
/***/ (function(module, exports, __webpack_require__) {

var Symbol = __webpack_require__("./node_modules/lodash/_Symbol.js");

/** Used to convert symbols to primitives and strings. */
var symbolProto = Symbol ? Symbol.prototype : undefined,
    symbolValueOf = symbolProto ? symbolProto.valueOf : undefined;

/**
 * Creates a clone of the `symbol` object.
 *
 * @private
 * @param {Object} symbol The symbol object to clone.
 * @returns {Object} Returns the cloned symbol object.
 */
function cloneSymbol(symbol) {
  return symbolValueOf ? Object(symbolValueOf.call(symbol)) : {};
}

module.exports = cloneSymbol;


/***/ }),

/***/ "./node_modules/lodash/_cloneTypedArray.js":
/***/ (function(module, exports, __webpack_require__) {

var cloneArrayBuffer = __webpack_require__("./node_modules/lodash/_cloneArrayBuffer.js");

/**
 * Creates a clone of `typedArray`.
 *
 * @private
 * @param {Object} typedArray The typed array to clone.
 * @param {boolean} [isDeep] Specify a deep clone.
 * @returns {Object} Returns the cloned typed array.
 */
function cloneTypedArray(typedArray, isDeep) {
  var buffer = isDeep ? cloneArrayBuffer(typedArray.buffer) : typedArray.buffer;
  return new typedArray.constructor(buffer, typedArray.byteOffset, typedArray.length);
}

module.exports = cloneTypedArray;


/***/ }),

/***/ "./node_modules/lodash/_copyArray.js":
/***/ (function(module, exports) {

/**
 * Copies the values of `source` to `array`.
 *
 * @private
 * @param {Array} source The array to copy values from.
 * @param {Array} [array=[]] The array to copy values to.
 * @returns {Array} Returns `array`.
 */
function copyArray(source, array) {
  var index = -1,
      length = source.length;

  array || (array = Array(length));
  while (++index < length) {
    array[index] = source[index];
  }
  return array;
}

module.exports = copyArray;


/***/ }),

/***/ "./node_modules/lodash/_copyObject.js":
/***/ (function(module, exports, __webpack_require__) {

var assignValue = __webpack_require__("./node_modules/lodash/_assignValue.js"),
    baseAssignValue = __webpack_require__("./node_modules/lodash/_baseAssignValue.js");

/**
 * Copies properties of `source` to `object`.
 *
 * @private
 * @param {Object} source The object to copy properties from.
 * @param {Array} props The property identifiers to copy.
 * @param {Object} [object={}] The object to copy properties to.
 * @param {Function} [customizer] The function to customize copied values.
 * @returns {Object} Returns `object`.
 */
function copyObject(source, props, object, customizer) {
  var isNew = !object;
  object || (object = {});

  var index = -1,
      length = props.length;

  while (++index < length) {
    var key = props[index];

    var newValue = customizer
      ? customizer(object[key], source[key], key, object, source)
      : undefined;

    if (newValue === undefined) {
      newValue = source[key];
    }
    if (isNew) {
      baseAssignValue(object, key, newValue);
    } else {
      assignValue(object, key, newValue);
    }
  }
  return object;
}

module.exports = copyObject;


/***/ }),

/***/ "./node_modules/lodash/_copySymbols.js":
/***/ (function(module, exports, __webpack_require__) {

var copyObject = __webpack_require__("./node_modules/lodash/_copyObject.js"),
    getSymbols = __webpack_require__("./node_modules/lodash/_getSymbols.js");

/**
 * Copies own symbols of `source` to `object`.
 *
 * @private
 * @param {Object} source The object to copy symbols from.
 * @param {Object} [object={}] The object to copy symbols to.
 * @returns {Object} Returns `object`.
 */
function copySymbols(source, object) {
  return copyObject(source, getSymbols(source), object);
}

module.exports = copySymbols;


/***/ }),

/***/ "./node_modules/lodash/_copySymbolsIn.js":
/***/ (function(module, exports, __webpack_require__) {

var copyObject = __webpack_require__("./node_modules/lodash/_copyObject.js"),
    getSymbolsIn = __webpack_require__("./node_modules/lodash/_getSymbolsIn.js");

/**
 * Copies own and inherited symbols of `source` to `object`.
 *
 * @private
 * @param {Object} source The object to copy symbols from.
 * @param {Object} [object={}] The object to copy symbols to.
 * @returns {Object} Returns `object`.
 */
function copySymbolsIn(source, object) {
  return copyObject(source, getSymbolsIn(source), object);
}

module.exports = copySymbolsIn;


/***/ }),

/***/ "./node_modules/lodash/_coreJsData.js":
/***/ (function(module, exports, __webpack_require__) {

var root = __webpack_require__("./node_modules/lodash/_root.js");

/** Used to detect overreaching core-js shims. */
var coreJsData = root['__core-js_shared__'];

module.exports = coreJsData;


/***/ }),

/***/ "./node_modules/lodash/_createAssigner.js":
/***/ (function(module, exports, __webpack_require__) {

var baseRest = __webpack_require__("./node_modules/lodash/_baseRest.js"),
    isIterateeCall = __webpack_require__("./node_modules/lodash/_isIterateeCall.js");

/**
 * Creates a function like `_.assign`.
 *
 * @private
 * @param {Function} assigner The function to assign values.
 * @returns {Function} Returns the new assigner function.
 */
function createAssigner(assigner) {
  return baseRest(function(object, sources) {
    var index = -1,
        length = sources.length,
        customizer = length > 1 ? sources[length - 1] : undefined,
        guard = length > 2 ? sources[2] : undefined;

    customizer = (assigner.length > 3 && typeof customizer == 'function')
      ? (length--, customizer)
      : undefined;

    if (guard && isIterateeCall(sources[0], sources[1], guard)) {
      customizer = length < 3 ? undefined : customizer;
      length = 1;
    }
    object = Object(object);
    while (++index < length) {
      var source = sources[index];
      if (source) {
        assigner(object, source, index, customizer);
      }
    }
    return object;
  });
}

module.exports = createAssigner;


/***/ }),

/***/ "./node_modules/lodash/_createBaseFor.js":
/***/ (function(module, exports) {

/**
 * Creates a base function for methods like `_.forIn` and `_.forOwn`.
 *
 * @private
 * @param {boolean} [fromRight] Specify iterating from right to left.
 * @returns {Function} Returns the new base function.
 */
function createBaseFor(fromRight) {
  return function(object, iteratee, keysFunc) {
    var index = -1,
        iterable = Object(object),
        props = keysFunc(object),
        length = props.length;

    while (length--) {
      var key = props[fromRight ? length : ++index];
      if (iteratee(iterable[key], key, iterable) === false) {
        break;
      }
    }
    return object;
  };
}

module.exports = createBaseFor;


/***/ }),

/***/ "./node_modules/lodash/_defineProperty.js":
/***/ (function(module, exports, __webpack_require__) {

var getNative = __webpack_require__("./node_modules/lodash/_getNative.js");

var defineProperty = (function() {
  try {
    var func = getNative(Object, 'defineProperty');
    func({}, '', {});
    return func;
  } catch (e) {}
}());

module.exports = defineProperty;


/***/ }),

/***/ "./node_modules/lodash/_freeGlobal.js":
/***/ (function(module, exports, __webpack_require__) {

/* WEBPACK VAR INJECTION */(function(global) {/** Detect free variable `global` from Node.js. */
var freeGlobal = typeof global == 'object' && global && global.Object === Object && global;

module.exports = freeGlobal;

/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__("./node_modules/webpack/buildin/global.js")))

/***/ }),

/***/ "./node_modules/lodash/_getAllKeys.js":
/***/ (function(module, exports, __webpack_require__) {

var baseGetAllKeys = __webpack_require__("./node_modules/lodash/_baseGetAllKeys.js"),
    getSymbols = __webpack_require__("./node_modules/lodash/_getSymbols.js"),
    keys = __webpack_require__("./node_modules/lodash/keys.js");

/**
 * Creates an array of own enumerable property names and symbols of `object`.
 *
 * @private
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of property names and symbols.
 */
function getAllKeys(object) {
  return baseGetAllKeys(object, keys, getSymbols);
}

module.exports = getAllKeys;


/***/ }),

/***/ "./node_modules/lodash/_getAllKeysIn.js":
/***/ (function(module, exports, __webpack_require__) {

var baseGetAllKeys = __webpack_require__("./node_modules/lodash/_baseGetAllKeys.js"),
    getSymbolsIn = __webpack_require__("./node_modules/lodash/_getSymbolsIn.js"),
    keysIn = __webpack_require__("./node_modules/lodash/keysIn.js");

/**
 * Creates an array of own and inherited enumerable property names and
 * symbols of `object`.
 *
 * @private
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of property names and symbols.
 */
function getAllKeysIn(object) {
  return baseGetAllKeys(object, keysIn, getSymbolsIn);
}

module.exports = getAllKeysIn;


/***/ }),

/***/ "./node_modules/lodash/_getMapData.js":
/***/ (function(module, exports, __webpack_require__) {

var isKeyable = __webpack_require__("./node_modules/lodash/_isKeyable.js");

/**
 * Gets the data for `map`.
 *
 * @private
 * @param {Object} map The map to query.
 * @param {string} key The reference key.
 * @returns {*} Returns the map data.
 */
function getMapData(map, key) {
  var data = map.__data__;
  return isKeyable(key)
    ? data[typeof key == 'string' ? 'string' : 'hash']
    : data.map;
}

module.exports = getMapData;


/***/ }),

/***/ "./node_modules/lodash/_getNative.js":
/***/ (function(module, exports, __webpack_require__) {

var baseIsNative = __webpack_require__("./node_modules/lodash/_baseIsNative.js"),
    getValue = __webpack_require__("./node_modules/lodash/_getValue.js");

/**
 * Gets the native function at `key` of `object`.
 *
 * @private
 * @param {Object} object The object to query.
 * @param {string} key The key of the method to get.
 * @returns {*} Returns the function if it's native, else `undefined`.
 */
function getNative(object, key) {
  var value = getValue(object, key);
  return baseIsNative(value) ? value : undefined;
}

module.exports = getNative;


/***/ }),

/***/ "./node_modules/lodash/_getPrototype.js":
/***/ (function(module, exports, __webpack_require__) {

var overArg = __webpack_require__("./node_modules/lodash/_overArg.js");

/** Built-in value references. */
var getPrototype = overArg(Object.getPrototypeOf, Object);

module.exports = getPrototype;


/***/ }),

/***/ "./node_modules/lodash/_getRawTag.js":
/***/ (function(module, exports, __webpack_require__) {

var Symbol = __webpack_require__("./node_modules/lodash/_Symbol.js");

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/**
 * Used to resolve the
 * [`toStringTag`](http://ecma-international.org/ecma-262/7.0/#sec-object.prototype.tostring)
 * of values.
 */
var nativeObjectToString = objectProto.toString;

/** Built-in value references. */
var symToStringTag = Symbol ? Symbol.toStringTag : undefined;

/**
 * A specialized version of `baseGetTag` which ignores `Symbol.toStringTag` values.
 *
 * @private
 * @param {*} value The value to query.
 * @returns {string} Returns the raw `toStringTag`.
 */
function getRawTag(value) {
  var isOwn = hasOwnProperty.call(value, symToStringTag),
      tag = value[symToStringTag];

  try {
    value[symToStringTag] = undefined;
    var unmasked = true;
  } catch (e) {}

  var result = nativeObjectToString.call(value);
  if (unmasked) {
    if (isOwn) {
      value[symToStringTag] = tag;
    } else {
      delete value[symToStringTag];
    }
  }
  return result;
}

module.exports = getRawTag;


/***/ }),

/***/ "./node_modules/lodash/_getSymbols.js":
/***/ (function(module, exports, __webpack_require__) {

var arrayFilter = __webpack_require__("./node_modules/lodash/_arrayFilter.js"),
    stubArray = __webpack_require__("./node_modules/lodash/stubArray.js");

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Built-in value references. */
var propertyIsEnumerable = objectProto.propertyIsEnumerable;

/* Built-in method references for those with the same name as other `lodash` methods. */
var nativeGetSymbols = Object.getOwnPropertySymbols;

/**
 * Creates an array of the own enumerable symbols of `object`.
 *
 * @private
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of symbols.
 */
var getSymbols = !nativeGetSymbols ? stubArray : function(object) {
  if (object == null) {
    return [];
  }
  object = Object(object);
  return arrayFilter(nativeGetSymbols(object), function(symbol) {
    return propertyIsEnumerable.call(object, symbol);
  });
};

module.exports = getSymbols;


/***/ }),

/***/ "./node_modules/lodash/_getSymbolsIn.js":
/***/ (function(module, exports, __webpack_require__) {

var arrayPush = __webpack_require__("./node_modules/lodash/_arrayPush.js"),
    getPrototype = __webpack_require__("./node_modules/lodash/_getPrototype.js"),
    getSymbols = __webpack_require__("./node_modules/lodash/_getSymbols.js"),
    stubArray = __webpack_require__("./node_modules/lodash/stubArray.js");

/* Built-in method references for those with the same name as other `lodash` methods. */
var nativeGetSymbols = Object.getOwnPropertySymbols;

/**
 * Creates an array of the own and inherited enumerable symbols of `object`.
 *
 * @private
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of symbols.
 */
var getSymbolsIn = !nativeGetSymbols ? stubArray : function(object) {
  var result = [];
  while (object) {
    arrayPush(result, getSymbols(object));
    object = getPrototype(object);
  }
  return result;
};

module.exports = getSymbolsIn;


/***/ }),

/***/ "./node_modules/lodash/_getTag.js":
/***/ (function(module, exports, __webpack_require__) {

var DataView = __webpack_require__("./node_modules/lodash/_DataView.js"),
    Map = __webpack_require__("./node_modules/lodash/_Map.js"),
    Promise = __webpack_require__("./node_modules/lodash/_Promise.js"),
    Set = __webpack_require__("./node_modules/lodash/_Set.js"),
    WeakMap = __webpack_require__("./node_modules/lodash/_WeakMap.js"),
    baseGetTag = __webpack_require__("./node_modules/lodash/_baseGetTag.js"),
    toSource = __webpack_require__("./node_modules/lodash/_toSource.js");

/** `Object#toString` result references. */
var mapTag = '[object Map]',
    objectTag = '[object Object]',
    promiseTag = '[object Promise]',
    setTag = '[object Set]',
    weakMapTag = '[object WeakMap]';

var dataViewTag = '[object DataView]';

/** Used to detect maps, sets, and weakmaps. */
var dataViewCtorString = toSource(DataView),
    mapCtorString = toSource(Map),
    promiseCtorString = toSource(Promise),
    setCtorString = toSource(Set),
    weakMapCtorString = toSource(WeakMap);

/**
 * Gets the `toStringTag` of `value`.
 *
 * @private
 * @param {*} value The value to query.
 * @returns {string} Returns the `toStringTag`.
 */
var getTag = baseGetTag;

// Fallback for data views, maps, sets, and weak maps in IE 11 and promises in Node.js < 6.
if ((DataView && getTag(new DataView(new ArrayBuffer(1))) != dataViewTag) ||
    (Map && getTag(new Map) != mapTag) ||
    (Promise && getTag(Promise.resolve()) != promiseTag) ||
    (Set && getTag(new Set) != setTag) ||
    (WeakMap && getTag(new WeakMap) != weakMapTag)) {
  getTag = function(value) {
    var result = baseGetTag(value),
        Ctor = result == objectTag ? value.constructor : undefined,
        ctorString = Ctor ? toSource(Ctor) : '';

    if (ctorString) {
      switch (ctorString) {
        case dataViewCtorString: return dataViewTag;
        case mapCtorString: return mapTag;
        case promiseCtorString: return promiseTag;
        case setCtorString: return setTag;
        case weakMapCtorString: return weakMapTag;
      }
    }
    return result;
  };
}

module.exports = getTag;


/***/ }),

/***/ "./node_modules/lodash/_getValue.js":
/***/ (function(module, exports) {

/**
 * Gets the value at `key` of `object`.
 *
 * @private
 * @param {Object} [object] The object to query.
 * @param {string} key The key of the property to get.
 * @returns {*} Returns the property value.
 */
function getValue(object, key) {
  return object == null ? undefined : object[key];
}

module.exports = getValue;


/***/ }),

/***/ "./node_modules/lodash/_hasUnicode.js":
/***/ (function(module, exports) {

/** Used to compose unicode character classes. */
var rsAstralRange = '\\ud800-\\udfff',
    rsComboMarksRange = '\\u0300-\\u036f',
    reComboHalfMarksRange = '\\ufe20-\\ufe2f',
    rsComboSymbolsRange = '\\u20d0-\\u20ff',
    rsComboRange = rsComboMarksRange + reComboHalfMarksRange + rsComboSymbolsRange,
    rsVarRange = '\\ufe0e\\ufe0f';

/** Used to compose unicode capture groups. */
var rsZWJ = '\\u200d';

/** Used to detect strings with [zero-width joiners or code points from the astral planes](http://eev.ee/blog/2015/09/12/dark-corners-of-unicode/). */
var reHasUnicode = RegExp('[' + rsZWJ + rsAstralRange  + rsComboRange + rsVarRange + ']');

/**
 * Checks if `string` contains Unicode symbols.
 *
 * @private
 * @param {string} string The string to inspect.
 * @returns {boolean} Returns `true` if a symbol is found, else `false`.
 */
function hasUnicode(string) {
  return reHasUnicode.test(string);
}

module.exports = hasUnicode;


/***/ }),

/***/ "./node_modules/lodash/_hashClear.js":
/***/ (function(module, exports, __webpack_require__) {

var nativeCreate = __webpack_require__("./node_modules/lodash/_nativeCreate.js");

/**
 * Removes all key-value entries from the hash.
 *
 * @private
 * @name clear
 * @memberOf Hash
 */
function hashClear() {
  this.__data__ = nativeCreate ? nativeCreate(null) : {};
  this.size = 0;
}

module.exports = hashClear;


/***/ }),

/***/ "./node_modules/lodash/_hashDelete.js":
/***/ (function(module, exports) {

/**
 * Removes `key` and its value from the hash.
 *
 * @private
 * @name delete
 * @memberOf Hash
 * @param {Object} hash The hash to modify.
 * @param {string} key The key of the value to remove.
 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
 */
function hashDelete(key) {
  var result = this.has(key) && delete this.__data__[key];
  this.size -= result ? 1 : 0;
  return result;
}

module.exports = hashDelete;


/***/ }),

/***/ "./node_modules/lodash/_hashGet.js":
/***/ (function(module, exports, __webpack_require__) {

var nativeCreate = __webpack_require__("./node_modules/lodash/_nativeCreate.js");

/** Used to stand-in for `undefined` hash values. */
var HASH_UNDEFINED = '__lodash_hash_undefined__';

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/**
 * Gets the hash value for `key`.
 *
 * @private
 * @name get
 * @memberOf Hash
 * @param {string} key The key of the value to get.
 * @returns {*} Returns the entry value.
 */
function hashGet(key) {
  var data = this.__data__;
  if (nativeCreate) {
    var result = data[key];
    return result === HASH_UNDEFINED ? undefined : result;
  }
  return hasOwnProperty.call(data, key) ? data[key] : undefined;
}

module.exports = hashGet;


/***/ }),

/***/ "./node_modules/lodash/_hashHas.js":
/***/ (function(module, exports, __webpack_require__) {

var nativeCreate = __webpack_require__("./node_modules/lodash/_nativeCreate.js");

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/**
 * Checks if a hash value for `key` exists.
 *
 * @private
 * @name has
 * @memberOf Hash
 * @param {string} key The key of the entry to check.
 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
 */
function hashHas(key) {
  var data = this.__data__;
  return nativeCreate ? (data[key] !== undefined) : hasOwnProperty.call(data, key);
}

module.exports = hashHas;


/***/ }),

/***/ "./node_modules/lodash/_hashSet.js":
/***/ (function(module, exports, __webpack_require__) {

var nativeCreate = __webpack_require__("./node_modules/lodash/_nativeCreate.js");

/** Used to stand-in for `undefined` hash values. */
var HASH_UNDEFINED = '__lodash_hash_undefined__';

/**
 * Sets the hash `key` to `value`.
 *
 * @private
 * @name set
 * @memberOf Hash
 * @param {string} key The key of the value to set.
 * @param {*} value The value to set.
 * @returns {Object} Returns the hash instance.
 */
function hashSet(key, value) {
  var data = this.__data__;
  this.size += this.has(key) ? 0 : 1;
  data[key] = (nativeCreate && value === undefined) ? HASH_UNDEFINED : value;
  return this;
}

module.exports = hashSet;


/***/ }),

/***/ "./node_modules/lodash/_initCloneArray.js":
/***/ (function(module, exports) {

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/**
 * Initializes an array clone.
 *
 * @private
 * @param {Array} array The array to clone.
 * @returns {Array} Returns the initialized clone.
 */
function initCloneArray(array) {
  var length = array.length,
      result = new array.constructor(length);

  // Add properties assigned by `RegExp#exec`.
  if (length && typeof array[0] == 'string' && hasOwnProperty.call(array, 'index')) {
    result.index = array.index;
    result.input = array.input;
  }
  return result;
}

module.exports = initCloneArray;


/***/ }),

/***/ "./node_modules/lodash/_initCloneByTag.js":
/***/ (function(module, exports, __webpack_require__) {

var cloneArrayBuffer = __webpack_require__("./node_modules/lodash/_cloneArrayBuffer.js"),
    cloneDataView = __webpack_require__("./node_modules/lodash/_cloneDataView.js"),
    cloneRegExp = __webpack_require__("./node_modules/lodash/_cloneRegExp.js"),
    cloneSymbol = __webpack_require__("./node_modules/lodash/_cloneSymbol.js"),
    cloneTypedArray = __webpack_require__("./node_modules/lodash/_cloneTypedArray.js");

/** `Object#toString` result references. */
var boolTag = '[object Boolean]',
    dateTag = '[object Date]',
    mapTag = '[object Map]',
    numberTag = '[object Number]',
    regexpTag = '[object RegExp]',
    setTag = '[object Set]',
    stringTag = '[object String]',
    symbolTag = '[object Symbol]';

var arrayBufferTag = '[object ArrayBuffer]',
    dataViewTag = '[object DataView]',
    float32Tag = '[object Float32Array]',
    float64Tag = '[object Float64Array]',
    int8Tag = '[object Int8Array]',
    int16Tag = '[object Int16Array]',
    int32Tag = '[object Int32Array]',
    uint8Tag = '[object Uint8Array]',
    uint8ClampedTag = '[object Uint8ClampedArray]',
    uint16Tag = '[object Uint16Array]',
    uint32Tag = '[object Uint32Array]';

/**
 * Initializes an object clone based on its `toStringTag`.
 *
 * **Note:** This function only supports cloning values with tags of
 * `Boolean`, `Date`, `Error`, `Map`, `Number`, `RegExp`, `Set`, or `String`.
 *
 * @private
 * @param {Object} object The object to clone.
 * @param {string} tag The `toStringTag` of the object to clone.
 * @param {boolean} [isDeep] Specify a deep clone.
 * @returns {Object} Returns the initialized clone.
 */
function initCloneByTag(object, tag, isDeep) {
  var Ctor = object.constructor;
  switch (tag) {
    case arrayBufferTag:
      return cloneArrayBuffer(object);

    case boolTag:
    case dateTag:
      return new Ctor(+object);

    case dataViewTag:
      return cloneDataView(object, isDeep);

    case float32Tag: case float64Tag:
    case int8Tag: case int16Tag: case int32Tag:
    case uint8Tag: case uint8ClampedTag: case uint16Tag: case uint32Tag:
      return cloneTypedArray(object, isDeep);

    case mapTag:
      return new Ctor;

    case numberTag:
    case stringTag:
      return new Ctor(object);

    case regexpTag:
      return cloneRegExp(object);

    case setTag:
      return new Ctor;

    case symbolTag:
      return cloneSymbol(object);
  }
}

module.exports = initCloneByTag;


/***/ }),

/***/ "./node_modules/lodash/_initCloneObject.js":
/***/ (function(module, exports, __webpack_require__) {

var baseCreate = __webpack_require__("./node_modules/lodash/_baseCreate.js"),
    getPrototype = __webpack_require__("./node_modules/lodash/_getPrototype.js"),
    isPrototype = __webpack_require__("./node_modules/lodash/_isPrototype.js");

/**
 * Initializes an object clone.
 *
 * @private
 * @param {Object} object The object to clone.
 * @returns {Object} Returns the initialized clone.
 */
function initCloneObject(object) {
  return (typeof object.constructor == 'function' && !isPrototype(object))
    ? baseCreate(getPrototype(object))
    : {};
}

module.exports = initCloneObject;


/***/ }),

/***/ "./node_modules/lodash/_isFlattenable.js":
/***/ (function(module, exports, __webpack_require__) {

var Symbol = __webpack_require__("./node_modules/lodash/_Symbol.js"),
    isArguments = __webpack_require__("./node_modules/lodash/isArguments.js"),
    isArray = __webpack_require__("./node_modules/lodash/isArray.js");

/** Built-in value references. */
var spreadableSymbol = Symbol ? Symbol.isConcatSpreadable : undefined;

/**
 * Checks if `value` is a flattenable `arguments` object or array.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is flattenable, else `false`.
 */
function isFlattenable(value) {
  return isArray(value) || isArguments(value) ||
    !!(spreadableSymbol && value && value[spreadableSymbol]);
}

module.exports = isFlattenable;


/***/ }),

/***/ "./node_modules/lodash/_isIndex.js":
/***/ (function(module, exports) {

/** Used as references for various `Number` constants. */
var MAX_SAFE_INTEGER = 9007199254740991;

/** Used to detect unsigned integer values. */
var reIsUint = /^(?:0|[1-9]\d*)$/;

/**
 * Checks if `value` is a valid array-like index.
 *
 * @private
 * @param {*} value The value to check.
 * @param {number} [length=MAX_SAFE_INTEGER] The upper bounds of a valid index.
 * @returns {boolean} Returns `true` if `value` is a valid index, else `false`.
 */
function isIndex(value, length) {
  var type = typeof value;
  length = length == null ? MAX_SAFE_INTEGER : length;

  return !!length &&
    (type == 'number' ||
      (type != 'symbol' && reIsUint.test(value))) &&
        (value > -1 && value % 1 == 0 && value < length);
}

module.exports = isIndex;


/***/ }),

/***/ "./node_modules/lodash/_isIterateeCall.js":
/***/ (function(module, exports, __webpack_require__) {

var eq = __webpack_require__("./node_modules/lodash/eq.js"),
    isArrayLike = __webpack_require__("./node_modules/lodash/isArrayLike.js"),
    isIndex = __webpack_require__("./node_modules/lodash/_isIndex.js"),
    isObject = __webpack_require__("./node_modules/lodash/isObject.js");

/**
 * Checks if the given arguments are from an iteratee call.
 *
 * @private
 * @param {*} value The potential iteratee value argument.
 * @param {*} index The potential iteratee index or key argument.
 * @param {*} object The potential iteratee object argument.
 * @returns {boolean} Returns `true` if the arguments are from an iteratee call,
 *  else `false`.
 */
function isIterateeCall(value, index, object) {
  if (!isObject(object)) {
    return false;
  }
  var type = typeof index;
  if (type == 'number'
        ? (isArrayLike(object) && isIndex(index, object.length))
        : (type == 'string' && index in object)
      ) {
    return eq(object[index], value);
  }
  return false;
}

module.exports = isIterateeCall;


/***/ }),

/***/ "./node_modules/lodash/_isKeyable.js":
/***/ (function(module, exports) {

/**
 * Checks if `value` is suitable for use as unique object key.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is suitable, else `false`.
 */
function isKeyable(value) {
  var type = typeof value;
  return (type == 'string' || type == 'number' || type == 'symbol' || type == 'boolean')
    ? (value !== '__proto__')
    : (value === null);
}

module.exports = isKeyable;


/***/ }),

/***/ "./node_modules/lodash/_isMasked.js":
/***/ (function(module, exports, __webpack_require__) {

var coreJsData = __webpack_require__("./node_modules/lodash/_coreJsData.js");

/** Used to detect methods masquerading as native. */
var maskSrcKey = (function() {
  var uid = /[^.]+$/.exec(coreJsData && coreJsData.keys && coreJsData.keys.IE_PROTO || '');
  return uid ? ('Symbol(src)_1.' + uid) : '';
}());

/**
 * Checks if `func` has its source masked.
 *
 * @private
 * @param {Function} func The function to check.
 * @returns {boolean} Returns `true` if `func` is masked, else `false`.
 */
function isMasked(func) {
  return !!maskSrcKey && (maskSrcKey in func);
}

module.exports = isMasked;


/***/ }),

/***/ "./node_modules/lodash/_isPrototype.js":
/***/ (function(module, exports) {

/** Used for built-in method references. */
var objectProto = Object.prototype;

/**
 * Checks if `value` is likely a prototype object.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a prototype, else `false`.
 */
function isPrototype(value) {
  var Ctor = value && value.constructor,
      proto = (typeof Ctor == 'function' && Ctor.prototype) || objectProto;

  return value === proto;
}

module.exports = isPrototype;


/***/ }),

/***/ "./node_modules/lodash/_listCacheClear.js":
/***/ (function(module, exports) {

/**
 * Removes all key-value entries from the list cache.
 *
 * @private
 * @name clear
 * @memberOf ListCache
 */
function listCacheClear() {
  this.__data__ = [];
  this.size = 0;
}

module.exports = listCacheClear;


/***/ }),

/***/ "./node_modules/lodash/_listCacheDelete.js":
/***/ (function(module, exports, __webpack_require__) {

var assocIndexOf = __webpack_require__("./node_modules/lodash/_assocIndexOf.js");

/** Used for built-in method references. */
var arrayProto = Array.prototype;

/** Built-in value references. */
var splice = arrayProto.splice;

/**
 * Removes `key` and its value from the list cache.
 *
 * @private
 * @name delete
 * @memberOf ListCache
 * @param {string} key The key of the value to remove.
 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
 */
function listCacheDelete(key) {
  var data = this.__data__,
      index = assocIndexOf(data, key);

  if (index < 0) {
    return false;
  }
  var lastIndex = data.length - 1;
  if (index == lastIndex) {
    data.pop();
  } else {
    splice.call(data, index, 1);
  }
  --this.size;
  return true;
}

module.exports = listCacheDelete;


/***/ }),

/***/ "./node_modules/lodash/_listCacheGet.js":
/***/ (function(module, exports, __webpack_require__) {

var assocIndexOf = __webpack_require__("./node_modules/lodash/_assocIndexOf.js");

/**
 * Gets the list cache value for `key`.
 *
 * @private
 * @name get
 * @memberOf ListCache
 * @param {string} key The key of the value to get.
 * @returns {*} Returns the entry value.
 */
function listCacheGet(key) {
  var data = this.__data__,
      index = assocIndexOf(data, key);

  return index < 0 ? undefined : data[index][1];
}

module.exports = listCacheGet;


/***/ }),

/***/ "./node_modules/lodash/_listCacheHas.js":
/***/ (function(module, exports, __webpack_require__) {

var assocIndexOf = __webpack_require__("./node_modules/lodash/_assocIndexOf.js");

/**
 * Checks if a list cache value for `key` exists.
 *
 * @private
 * @name has
 * @memberOf ListCache
 * @param {string} key The key of the entry to check.
 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
 */
function listCacheHas(key) {
  return assocIndexOf(this.__data__, key) > -1;
}

module.exports = listCacheHas;


/***/ }),

/***/ "./node_modules/lodash/_listCacheSet.js":
/***/ (function(module, exports, __webpack_require__) {

var assocIndexOf = __webpack_require__("./node_modules/lodash/_assocIndexOf.js");

/**
 * Sets the list cache `key` to `value`.
 *
 * @private
 * @name set
 * @memberOf ListCache
 * @param {string} key The key of the value to set.
 * @param {*} value The value to set.
 * @returns {Object} Returns the list cache instance.
 */
function listCacheSet(key, value) {
  var data = this.__data__,
      index = assocIndexOf(data, key);

  if (index < 0) {
    ++this.size;
    data.push([key, value]);
  } else {
    data[index][1] = value;
  }
  return this;
}

module.exports = listCacheSet;


/***/ }),

/***/ "./node_modules/lodash/_mapCacheClear.js":
/***/ (function(module, exports, __webpack_require__) {

var Hash = __webpack_require__("./node_modules/lodash/_Hash.js"),
    ListCache = __webpack_require__("./node_modules/lodash/_ListCache.js"),
    Map = __webpack_require__("./node_modules/lodash/_Map.js");

/**
 * Removes all key-value entries from the map.
 *
 * @private
 * @name clear
 * @memberOf MapCache
 */
function mapCacheClear() {
  this.size = 0;
  this.__data__ = {
    'hash': new Hash,
    'map': new (Map || ListCache),
    'string': new Hash
  };
}

module.exports = mapCacheClear;


/***/ }),

/***/ "./node_modules/lodash/_mapCacheDelete.js":
/***/ (function(module, exports, __webpack_require__) {

var getMapData = __webpack_require__("./node_modules/lodash/_getMapData.js");

/**
 * Removes `key` and its value from the map.
 *
 * @private
 * @name delete
 * @memberOf MapCache
 * @param {string} key The key of the value to remove.
 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
 */
function mapCacheDelete(key) {
  var result = getMapData(this, key)['delete'](key);
  this.size -= result ? 1 : 0;
  return result;
}

module.exports = mapCacheDelete;


/***/ }),

/***/ "./node_modules/lodash/_mapCacheGet.js":
/***/ (function(module, exports, __webpack_require__) {

var getMapData = __webpack_require__("./node_modules/lodash/_getMapData.js");

/**
 * Gets the map value for `key`.
 *
 * @private
 * @name get
 * @memberOf MapCache
 * @param {string} key The key of the value to get.
 * @returns {*} Returns the entry value.
 */
function mapCacheGet(key) {
  return getMapData(this, key).get(key);
}

module.exports = mapCacheGet;


/***/ }),

/***/ "./node_modules/lodash/_mapCacheHas.js":
/***/ (function(module, exports, __webpack_require__) {

var getMapData = __webpack_require__("./node_modules/lodash/_getMapData.js");

/**
 * Checks if a map value for `key` exists.
 *
 * @private
 * @name has
 * @memberOf MapCache
 * @param {string} key The key of the entry to check.
 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
 */
function mapCacheHas(key) {
  return getMapData(this, key).has(key);
}

module.exports = mapCacheHas;


/***/ }),

/***/ "./node_modules/lodash/_mapCacheSet.js":
/***/ (function(module, exports, __webpack_require__) {

var getMapData = __webpack_require__("./node_modules/lodash/_getMapData.js");

/**
 * Sets the map `key` to `value`.
 *
 * @private
 * @name set
 * @memberOf MapCache
 * @param {string} key The key of the value to set.
 * @param {*} value The value to set.
 * @returns {Object} Returns the map cache instance.
 */
function mapCacheSet(key, value) {
  var data = getMapData(this, key),
      size = data.size;

  data.set(key, value);
  this.size += data.size == size ? 0 : 1;
  return this;
}

module.exports = mapCacheSet;


/***/ }),

/***/ "./node_modules/lodash/_nativeCreate.js":
/***/ (function(module, exports, __webpack_require__) {

var getNative = __webpack_require__("./node_modules/lodash/_getNative.js");

/* Built-in method references that are verified to be native. */
var nativeCreate = getNative(Object, 'create');

module.exports = nativeCreate;


/***/ }),

/***/ "./node_modules/lodash/_nativeKeys.js":
/***/ (function(module, exports, __webpack_require__) {

var overArg = __webpack_require__("./node_modules/lodash/_overArg.js");

/* Built-in method references for those with the same name as other `lodash` methods. */
var nativeKeys = overArg(Object.keys, Object);

module.exports = nativeKeys;


/***/ }),

/***/ "./node_modules/lodash/_nativeKeysIn.js":
/***/ (function(module, exports) {

/**
 * This function is like
 * [`Object.keys`](http://ecma-international.org/ecma-262/7.0/#sec-object.keys)
 * except that it includes inherited enumerable properties.
 *
 * @private
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of property names.
 */
function nativeKeysIn(object) {
  var result = [];
  if (object != null) {
    for (var key in Object(object)) {
      result.push(key);
    }
  }
  return result;
}

module.exports = nativeKeysIn;


/***/ }),

/***/ "./node_modules/lodash/_nodeUtil.js":
/***/ (function(module, exports, __webpack_require__) {

/* WEBPACK VAR INJECTION */(function(module) {var freeGlobal = __webpack_require__("./node_modules/lodash/_freeGlobal.js");

/** Detect free variable `exports`. */
var freeExports =  true && exports && !exports.nodeType && exports;

/** Detect free variable `module`. */
var freeModule = freeExports && typeof module == 'object' && module && !module.nodeType && module;

/** Detect the popular CommonJS extension `module.exports`. */
var moduleExports = freeModule && freeModule.exports === freeExports;

/** Detect free variable `process` from Node.js. */
var freeProcess = moduleExports && freeGlobal.process;

/** Used to access faster Node.js helpers. */
var nodeUtil = (function() {
  try {
    // Use `util.types` for Node.js 10+.
    var types = freeModule && freeModule.require && freeModule.require('util').types;

    if (types) {
      return types;
    }

    // Legacy `process.binding('util')` for Node.js < 10.
    return freeProcess && freeProcess.binding && freeProcess.binding('util');
  } catch (e) {}
}());

module.exports = nodeUtil;

/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__("./node_modules/webpack/buildin/module.js")(module)))

/***/ }),

/***/ "./node_modules/lodash/_objectToString.js":
/***/ (function(module, exports) {

/** Used for built-in method references. */
var objectProto = Object.prototype;

/**
 * Used to resolve the
 * [`toStringTag`](http://ecma-international.org/ecma-262/7.0/#sec-object.prototype.tostring)
 * of values.
 */
var nativeObjectToString = objectProto.toString;

/**
 * Converts `value` to a string using `Object.prototype.toString`.
 *
 * @private
 * @param {*} value The value to convert.
 * @returns {string} Returns the converted string.
 */
function objectToString(value) {
  return nativeObjectToString.call(value);
}

module.exports = objectToString;


/***/ }),

/***/ "./node_modules/lodash/_overArg.js":
/***/ (function(module, exports) {

/**
 * Creates a unary function that invokes `func` with its argument transformed.
 *
 * @private
 * @param {Function} func The function to wrap.
 * @param {Function} transform The argument transform.
 * @returns {Function} Returns the new function.
 */
function overArg(func, transform) {
  return function(arg) {
    return func(transform(arg));
  };
}

module.exports = overArg;


/***/ }),

/***/ "./node_modules/lodash/_overRest.js":
/***/ (function(module, exports, __webpack_require__) {

var apply = __webpack_require__("./node_modules/lodash/_apply.js");

/* Built-in method references for those with the same name as other `lodash` methods. */
var nativeMax = Math.max;

/**
 * A specialized version of `baseRest` which transforms the rest array.
 *
 * @private
 * @param {Function} func The function to apply a rest parameter to.
 * @param {number} [start=func.length-1] The start position of the rest parameter.
 * @param {Function} transform The rest array transform.
 * @returns {Function} Returns the new function.
 */
function overRest(func, start, transform) {
  start = nativeMax(start === undefined ? (func.length - 1) : start, 0);
  return function() {
    var args = arguments,
        index = -1,
        length = nativeMax(args.length - start, 0),
        array = Array(length);

    while (++index < length) {
      array[index] = args[start + index];
    }
    index = -1;
    var otherArgs = Array(start + 1);
    while (++index < start) {
      otherArgs[index] = args[index];
    }
    otherArgs[start] = transform(array);
    return apply(func, this, otherArgs);
  };
}

module.exports = overRest;


/***/ }),

/***/ "./node_modules/lodash/_root.js":
/***/ (function(module, exports, __webpack_require__) {

var freeGlobal = __webpack_require__("./node_modules/lodash/_freeGlobal.js");

/** Detect free variable `self`. */
var freeSelf = typeof self == 'object' && self && self.Object === Object && self;

/** Used as a reference to the global object. */
var root = freeGlobal || freeSelf || Function('return this')();

module.exports = root;


/***/ }),

/***/ "./node_modules/lodash/_safeGet.js":
/***/ (function(module, exports) {

/**
 * Gets the value at `key`, unless `key` is "__proto__" or "constructor".
 *
 * @private
 * @param {Object} object The object to query.
 * @param {string} key The key of the property to get.
 * @returns {*} Returns the property value.
 */
function safeGet(object, key) {
  if (key === 'constructor' && typeof object[key] === 'function') {
    return;
  }

  if (key == '__proto__') {
    return;
  }

  return object[key];
}

module.exports = safeGet;


/***/ }),

/***/ "./node_modules/lodash/_setCacheAdd.js":
/***/ (function(module, exports) {

/** Used to stand-in for `undefined` hash values. */
var HASH_UNDEFINED = '__lodash_hash_undefined__';

/**
 * Adds `value` to the array cache.
 *
 * @private
 * @name add
 * @memberOf SetCache
 * @alias push
 * @param {*} value The value to cache.
 * @returns {Object} Returns the cache instance.
 */
function setCacheAdd(value) {
  this.__data__.set(value, HASH_UNDEFINED);
  return this;
}

module.exports = setCacheAdd;


/***/ }),

/***/ "./node_modules/lodash/_setCacheHas.js":
/***/ (function(module, exports) {

/**
 * Checks if `value` is in the array cache.
 *
 * @private
 * @name has
 * @memberOf SetCache
 * @param {*} value The value to search for.
 * @returns {number} Returns `true` if `value` is found, else `false`.
 */
function setCacheHas(value) {
  return this.__data__.has(value);
}

module.exports = setCacheHas;


/***/ }),

/***/ "./node_modules/lodash/_setToString.js":
/***/ (function(module, exports, __webpack_require__) {

var baseSetToString = __webpack_require__("./node_modules/lodash/_baseSetToString.js"),
    shortOut = __webpack_require__("./node_modules/lodash/_shortOut.js");

/**
 * Sets the `toString` method of `func` to return `string`.
 *
 * @private
 * @param {Function} func The function to modify.
 * @param {Function} string The `toString` result.
 * @returns {Function} Returns `func`.
 */
var setToString = shortOut(baseSetToString);

module.exports = setToString;


/***/ }),

/***/ "./node_modules/lodash/_shortOut.js":
/***/ (function(module, exports) {

/** Used to detect hot functions by number of calls within a span of milliseconds. */
var HOT_COUNT = 800,
    HOT_SPAN = 16;

/* Built-in method references for those with the same name as other `lodash` methods. */
var nativeNow = Date.now;

/**
 * Creates a function that'll short out and invoke `identity` instead
 * of `func` when it's called `HOT_COUNT` or more times in `HOT_SPAN`
 * milliseconds.
 *
 * @private
 * @param {Function} func The function to restrict.
 * @returns {Function} Returns the new shortable function.
 */
function shortOut(func) {
  var count = 0,
      lastCalled = 0;

  return function() {
    var stamp = nativeNow(),
        remaining = HOT_SPAN - (stamp - lastCalled);

    lastCalled = stamp;
    if (remaining > 0) {
      if (++count >= HOT_COUNT) {
        return arguments[0];
      }
    } else {
      count = 0;
    }
    return func.apply(undefined, arguments);
  };
}

module.exports = shortOut;


/***/ }),

/***/ "./node_modules/lodash/_stackClear.js":
/***/ (function(module, exports, __webpack_require__) {

var ListCache = __webpack_require__("./node_modules/lodash/_ListCache.js");

/**
 * Removes all key-value entries from the stack.
 *
 * @private
 * @name clear
 * @memberOf Stack
 */
function stackClear() {
  this.__data__ = new ListCache;
  this.size = 0;
}

module.exports = stackClear;


/***/ }),

/***/ "./node_modules/lodash/_stackDelete.js":
/***/ (function(module, exports) {

/**
 * Removes `key` and its value from the stack.
 *
 * @private
 * @name delete
 * @memberOf Stack
 * @param {string} key The key of the value to remove.
 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
 */
function stackDelete(key) {
  var data = this.__data__,
      result = data['delete'](key);

  this.size = data.size;
  return result;
}

module.exports = stackDelete;


/***/ }),

/***/ "./node_modules/lodash/_stackGet.js":
/***/ (function(module, exports) {

/**
 * Gets the stack value for `key`.
 *
 * @private
 * @name get
 * @memberOf Stack
 * @param {string} key The key of the value to get.
 * @returns {*} Returns the entry value.
 */
function stackGet(key) {
  return this.__data__.get(key);
}

module.exports = stackGet;


/***/ }),

/***/ "./node_modules/lodash/_stackHas.js":
/***/ (function(module, exports) {

/**
 * Checks if a stack value for `key` exists.
 *
 * @private
 * @name has
 * @memberOf Stack
 * @param {string} key The key of the entry to check.
 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
 */
function stackHas(key) {
  return this.__data__.has(key);
}

module.exports = stackHas;


/***/ }),

/***/ "./node_modules/lodash/_stackSet.js":
/***/ (function(module, exports, __webpack_require__) {

var ListCache = __webpack_require__("./node_modules/lodash/_ListCache.js"),
    Map = __webpack_require__("./node_modules/lodash/_Map.js"),
    MapCache = __webpack_require__("./node_modules/lodash/_MapCache.js");

/** Used as the size to enable large array optimizations. */
var LARGE_ARRAY_SIZE = 200;

/**
 * Sets the stack `key` to `value`.
 *
 * @private
 * @name set
 * @memberOf Stack
 * @param {string} key The key of the value to set.
 * @param {*} value The value to set.
 * @returns {Object} Returns the stack cache instance.
 */
function stackSet(key, value) {
  var data = this.__data__;
  if (data instanceof ListCache) {
    var pairs = data.__data__;
    if (!Map || (pairs.length < LARGE_ARRAY_SIZE - 1)) {
      pairs.push([key, value]);
      this.size = ++data.size;
      return this;
    }
    data = this.__data__ = new MapCache(pairs);
  }
  data.set(key, value);
  this.size = data.size;
  return this;
}

module.exports = stackSet;


/***/ }),

/***/ "./node_modules/lodash/_strictIndexOf.js":
/***/ (function(module, exports) {

/**
 * A specialized version of `_.indexOf` which performs strict equality
 * comparisons of values, i.e. `===`.
 *
 * @private
 * @param {Array} array The array to inspect.
 * @param {*} value The value to search for.
 * @param {number} fromIndex The index to search from.
 * @returns {number} Returns the index of the matched value, else `-1`.
 */
function strictIndexOf(array, value, fromIndex) {
  var index = fromIndex - 1,
      length = array.length;

  while (++index < length) {
    if (array[index] === value) {
      return index;
    }
  }
  return -1;
}

module.exports = strictIndexOf;


/***/ }),

/***/ "./node_modules/lodash/_stringToArray.js":
/***/ (function(module, exports, __webpack_require__) {

var asciiToArray = __webpack_require__("./node_modules/lodash/_asciiToArray.js"),
    hasUnicode = __webpack_require__("./node_modules/lodash/_hasUnicode.js"),
    unicodeToArray = __webpack_require__("./node_modules/lodash/_unicodeToArray.js");

/**
 * Converts `string` to an array.
 *
 * @private
 * @param {string} string The string to convert.
 * @returns {Array} Returns the converted array.
 */
function stringToArray(string) {
  return hasUnicode(string)
    ? unicodeToArray(string)
    : asciiToArray(string);
}

module.exports = stringToArray;


/***/ }),

/***/ "./node_modules/lodash/_toSource.js":
/***/ (function(module, exports) {

/** Used for built-in method references. */
var funcProto = Function.prototype;

/** Used to resolve the decompiled source of functions. */
var funcToString = funcProto.toString;

/**
 * Converts `func` to its source code.
 *
 * @private
 * @param {Function} func The function to convert.
 * @returns {string} Returns the source code.
 */
function toSource(func) {
  if (func != null) {
    try {
      return funcToString.call(func);
    } catch (e) {}
    try {
      return (func + '');
    } catch (e) {}
  }
  return '';
}

module.exports = toSource;


/***/ }),

/***/ "./node_modules/lodash/_trimmedEndIndex.js":
/***/ (function(module, exports) {

/** Used to match a single whitespace character. */
var reWhitespace = /\s/;

/**
 * Used by `_.trim` and `_.trimEnd` to get the index of the last non-whitespace
 * character of `string`.
 *
 * @private
 * @param {string} string The string to inspect.
 * @returns {number} Returns the index of the last non-whitespace character.
 */
function trimmedEndIndex(string) {
  var index = string.length;

  while (index-- && reWhitespace.test(string.charAt(index))) {}
  return index;
}

module.exports = trimmedEndIndex;


/***/ }),

/***/ "./node_modules/lodash/_unicodeToArray.js":
/***/ (function(module, exports) {

/** Used to compose unicode character classes. */
var rsAstralRange = '\\ud800-\\udfff',
    rsComboMarksRange = '\\u0300-\\u036f',
    reComboHalfMarksRange = '\\ufe20-\\ufe2f',
    rsComboSymbolsRange = '\\u20d0-\\u20ff',
    rsComboRange = rsComboMarksRange + reComboHalfMarksRange + rsComboSymbolsRange,
    rsVarRange = '\\ufe0e\\ufe0f';

/** Used to compose unicode capture groups. */
var rsAstral = '[' + rsAstralRange + ']',
    rsCombo = '[' + rsComboRange + ']',
    rsFitz = '\\ud83c[\\udffb-\\udfff]',
    rsModifier = '(?:' + rsCombo + '|' + rsFitz + ')',
    rsNonAstral = '[^' + rsAstralRange + ']',
    rsRegional = '(?:\\ud83c[\\udde6-\\uddff]){2}',
    rsSurrPair = '[\\ud800-\\udbff][\\udc00-\\udfff]',
    rsZWJ = '\\u200d';

/** Used to compose unicode regexes. */
var reOptMod = rsModifier + '?',
    rsOptVar = '[' + rsVarRange + ']?',
    rsOptJoin = '(?:' + rsZWJ + '(?:' + [rsNonAstral, rsRegional, rsSurrPair].join('|') + ')' + rsOptVar + reOptMod + ')*',
    rsSeq = rsOptVar + reOptMod + rsOptJoin,
    rsSymbol = '(?:' + [rsNonAstral + rsCombo + '?', rsCombo, rsRegional, rsSurrPair, rsAstral].join('|') + ')';

/** Used to match [string symbols](https://mathiasbynens.be/notes/javascript-unicode). */
var reUnicode = RegExp(rsFitz + '(?=' + rsFitz + ')|' + rsSymbol + rsSeq, 'g');

/**
 * Converts a Unicode `string` to an array.
 *
 * @private
 * @param {string} string The string to convert.
 * @returns {Array} Returns the converted array.
 */
function unicodeToArray(string) {
  return string.match(reUnicode) || [];
}

module.exports = unicodeToArray;


/***/ }),

/***/ "./node_modules/lodash/assign.js":
/***/ (function(module, exports, __webpack_require__) {

var assignValue = __webpack_require__("./node_modules/lodash/_assignValue.js"),
    copyObject = __webpack_require__("./node_modules/lodash/_copyObject.js"),
    createAssigner = __webpack_require__("./node_modules/lodash/_createAssigner.js"),
    isArrayLike = __webpack_require__("./node_modules/lodash/isArrayLike.js"),
    isPrototype = __webpack_require__("./node_modules/lodash/_isPrototype.js"),
    keys = __webpack_require__("./node_modules/lodash/keys.js");

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/**
 * Assigns own enumerable string keyed properties of source objects to the
 * destination object. Source objects are applied from left to right.
 * Subsequent sources overwrite property assignments of previous sources.
 *
 * **Note:** This method mutates `object` and is loosely based on
 * [`Object.assign`](https://mdn.io/Object/assign).
 *
 * @static
 * @memberOf _
 * @since 0.10.0
 * @category Object
 * @param {Object} object The destination object.
 * @param {...Object} [sources] The source objects.
 * @returns {Object} Returns `object`.
 * @see _.assignIn
 * @example
 *
 * function Foo() {
 *   this.a = 1;
 * }
 *
 * function Bar() {
 *   this.c = 3;
 * }
 *
 * Foo.prototype.b = 2;
 * Bar.prototype.d = 4;
 *
 * _.assign({ 'a': 0 }, new Foo, new Bar);
 * // => { 'a': 1, 'c': 3 }
 */
var assign = createAssigner(function(object, source) {
  if (isPrototype(source) || isArrayLike(source)) {
    copyObject(source, keys(source), object);
    return;
  }
  for (var key in source) {
    if (hasOwnProperty.call(source, key)) {
      assignValue(object, key, source[key]);
    }
  }
});

module.exports = assign;


/***/ }),

/***/ "./node_modules/lodash/cloneDeep.js":
/***/ (function(module, exports, __webpack_require__) {

var baseClone = __webpack_require__("./node_modules/lodash/_baseClone.js");

/** Used to compose bitmasks for cloning. */
var CLONE_DEEP_FLAG = 1,
    CLONE_SYMBOLS_FLAG = 4;

/**
 * This method is like `_.clone` except that it recursively clones `value`.
 *
 * @static
 * @memberOf _
 * @since 1.0.0
 * @category Lang
 * @param {*} value The value to recursively clone.
 * @returns {*} Returns the deep cloned value.
 * @see _.clone
 * @example
 *
 * var objects = [{ 'a': 1 }, { 'b': 2 }];
 *
 * var deep = _.cloneDeep(objects);
 * console.log(deep[0] === objects[0]);
 * // => false
 */
function cloneDeep(value) {
  return baseClone(value, CLONE_DEEP_FLAG | CLONE_SYMBOLS_FLAG);
}

module.exports = cloneDeep;


/***/ }),

/***/ "./node_modules/lodash/compact.js":
/***/ (function(module, exports) {

/**
 * Creates an array with all falsey values removed. The values `false`, `null`,
 * `0`, `""`, `undefined`, and `NaN` are falsey.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Array
 * @param {Array} array The array to compact.
 * @returns {Array} Returns the new array of filtered values.
 * @example
 *
 * _.compact([0, 1, false, 2, '', 3]);
 * // => [1, 2, 3]
 */
function compact(array) {
  var index = -1,
      length = array == null ? 0 : array.length,
      resIndex = 0,
      result = [];

  while (++index < length) {
    var value = array[index];
    if (value) {
      result[resIndex++] = value;
    }
  }
  return result;
}

module.exports = compact;


/***/ }),

/***/ "./node_modules/lodash/constant.js":
/***/ (function(module, exports) {

/**
 * Creates a function that returns `value`.
 *
 * @static
 * @memberOf _
 * @since 2.4.0
 * @category Util
 * @param {*} value The value to return from the new function.
 * @returns {Function} Returns the new constant function.
 * @example
 *
 * var objects = _.times(2, _.constant({ 'a': 1 }));
 *
 * console.log(objects);
 * // => [{ 'a': 1 }, { 'a': 1 }]
 *
 * console.log(objects[0] === objects[1]);
 * // => true
 */
function constant(value) {
  return function() {
    return value;
  };
}

module.exports = constant;


/***/ }),

/***/ "./node_modules/lodash/difference.js":
/***/ (function(module, exports, __webpack_require__) {

var baseDifference = __webpack_require__("./node_modules/lodash/_baseDifference.js"),
    baseFlatten = __webpack_require__("./node_modules/lodash/_baseFlatten.js"),
    baseRest = __webpack_require__("./node_modules/lodash/_baseRest.js"),
    isArrayLikeObject = __webpack_require__("./node_modules/lodash/isArrayLikeObject.js");

/**
 * Creates an array of `array` values not included in the other given arrays
 * using [`SameValueZero`](http://ecma-international.org/ecma-262/7.0/#sec-samevaluezero)
 * for equality comparisons. The order and references of result values are
 * determined by the first array.
 *
 * **Note:** Unlike `_.pullAll`, this method returns a new array.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Array
 * @param {Array} array The array to inspect.
 * @param {...Array} [values] The values to exclude.
 * @returns {Array} Returns the new array of filtered values.
 * @see _.without, _.xor
 * @example
 *
 * _.difference([2, 1], [2, 3]);
 * // => [1]
 */
var difference = baseRest(function(array, values) {
  return isArrayLikeObject(array)
    ? baseDifference(array, baseFlatten(values, 1, isArrayLikeObject, true))
    : [];
});

module.exports = difference;


/***/ }),

/***/ "./node_modules/lodash/eq.js":
/***/ (function(module, exports) {

/**
 * Performs a
 * [`SameValueZero`](http://ecma-international.org/ecma-262/7.0/#sec-samevaluezero)
 * comparison between two values to determine if they are equivalent.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to compare.
 * @param {*} other The other value to compare.
 * @returns {boolean} Returns `true` if the values are equivalent, else `false`.
 * @example
 *
 * var object = { 'a': 1 };
 * var other = { 'a': 1 };
 *
 * _.eq(object, object);
 * // => true
 *
 * _.eq(object, other);
 * // => false
 *
 * _.eq('a', 'a');
 * // => true
 *
 * _.eq('a', Object('a'));
 * // => false
 *
 * _.eq(NaN, NaN);
 * // => true
 */
function eq(value, other) {
  return value === other || (value !== value && other !== other);
}

module.exports = eq;


/***/ }),

/***/ "./node_modules/lodash/functions.js":
/***/ (function(module, exports, __webpack_require__) {

var baseFunctions = __webpack_require__("./node_modules/lodash/_baseFunctions.js"),
    keys = __webpack_require__("./node_modules/lodash/keys.js");

/**
 * Creates an array of function property names from own enumerable properties
 * of `object`.
 *
 * @static
 * @since 0.1.0
 * @memberOf _
 * @category Object
 * @param {Object} object The object to inspect.
 * @returns {Array} Returns the function names.
 * @see _.functionsIn
 * @example
 *
 * function Foo() {
 *   this.a = _.constant('a');
 *   this.b = _.constant('b');
 * }
 *
 * Foo.prototype.c = _.constant('c');
 *
 * _.functions(new Foo);
 * // => ['a', 'b']
 */
function functions(object) {
  return object == null ? [] : baseFunctions(object, keys(object));
}

module.exports = functions;


/***/ }),

/***/ "./node_modules/lodash/identity.js":
/***/ (function(module, exports) {

/**
 * This method returns the first argument it receives.
 *
 * @static
 * @since 0.1.0
 * @memberOf _
 * @category Util
 * @param {*} value Any value.
 * @returns {*} Returns `value`.
 * @example
 *
 * var object = { 'a': 1 };
 *
 * console.log(_.identity(object) === object);
 * // => true
 */
function identity(value) {
  return value;
}

module.exports = identity;


/***/ }),

/***/ "./node_modules/lodash/includes.js":
/***/ (function(module, exports, __webpack_require__) {

var baseIndexOf = __webpack_require__("./node_modules/lodash/_baseIndexOf.js"),
    isArrayLike = __webpack_require__("./node_modules/lodash/isArrayLike.js"),
    isString = __webpack_require__("./node_modules/lodash/isString.js"),
    toInteger = __webpack_require__("./node_modules/lodash/toInteger.js"),
    values = __webpack_require__("./node_modules/lodash/values.js");

/* Built-in method references for those with the same name as other `lodash` methods. */
var nativeMax = Math.max;

/**
 * Checks if `value` is in `collection`. If `collection` is a string, it's
 * checked for a substring of `value`, otherwise
 * [`SameValueZero`](http://ecma-international.org/ecma-262/7.0/#sec-samevaluezero)
 * is used for equality comparisons. If `fromIndex` is negative, it's used as
 * the offset from the end of `collection`.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Collection
 * @param {Array|Object|string} collection The collection to inspect.
 * @param {*} value The value to search for.
 * @param {number} [fromIndex=0] The index to search from.
 * @param- {Object} [guard] Enables use as an iteratee for methods like `_.reduce`.
 * @returns {boolean} Returns `true` if `value` is found, else `false`.
 * @example
 *
 * _.includes([1, 2, 3], 1);
 * // => true
 *
 * _.includes([1, 2, 3], 1, 2);
 * // => false
 *
 * _.includes({ 'a': 1, 'b': 2 }, 1);
 * // => true
 *
 * _.includes('abcd', 'bc');
 * // => true
 */
function includes(collection, value, fromIndex, guard) {
  collection = isArrayLike(collection) ? collection : values(collection);
  fromIndex = (fromIndex && !guard) ? toInteger(fromIndex) : 0;

  var length = collection.length;
  if (fromIndex < 0) {
    fromIndex = nativeMax(length + fromIndex, 0);
  }
  return isString(collection)
    ? (fromIndex <= length && collection.indexOf(value, fromIndex) > -1)
    : (!!length && baseIndexOf(collection, value, fromIndex) > -1);
}

module.exports = includes;


/***/ }),

/***/ "./node_modules/lodash/isArguments.js":
/***/ (function(module, exports, __webpack_require__) {

var baseIsArguments = __webpack_require__("./node_modules/lodash/_baseIsArguments.js"),
    isObjectLike = __webpack_require__("./node_modules/lodash/isObjectLike.js");

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/** Built-in value references. */
var propertyIsEnumerable = objectProto.propertyIsEnumerable;

/**
 * Checks if `value` is likely an `arguments` object.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is an `arguments` object,
 *  else `false`.
 * @example
 *
 * _.isArguments(function() { return arguments; }());
 * // => true
 *
 * _.isArguments([1, 2, 3]);
 * // => false
 */
var isArguments = baseIsArguments(function() { return arguments; }()) ? baseIsArguments : function(value) {
  return isObjectLike(value) && hasOwnProperty.call(value, 'callee') &&
    !propertyIsEnumerable.call(value, 'callee');
};

module.exports = isArguments;


/***/ }),

/***/ "./node_modules/lodash/isArray.js":
/***/ (function(module, exports) {

/**
 * Checks if `value` is classified as an `Array` object.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is an array, else `false`.
 * @example
 *
 * _.isArray([1, 2, 3]);
 * // => true
 *
 * _.isArray(document.body.children);
 * // => false
 *
 * _.isArray('abc');
 * // => false
 *
 * _.isArray(_.noop);
 * // => false
 */
var isArray = Array.isArray;

module.exports = isArray;


/***/ }),

/***/ "./node_modules/lodash/isArrayLike.js":
/***/ (function(module, exports, __webpack_require__) {

var isFunction = __webpack_require__("./node_modules/lodash/isFunction.js"),
    isLength = __webpack_require__("./node_modules/lodash/isLength.js");

/**
 * Checks if `value` is array-like. A value is considered array-like if it's
 * not a function and has a `value.length` that's an integer greater than or
 * equal to `0` and less than or equal to `Number.MAX_SAFE_INTEGER`.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is array-like, else `false`.
 * @example
 *
 * _.isArrayLike([1, 2, 3]);
 * // => true
 *
 * _.isArrayLike(document.body.children);
 * // => true
 *
 * _.isArrayLike('abc');
 * // => true
 *
 * _.isArrayLike(_.noop);
 * // => false
 */
function isArrayLike(value) {
  return value != null && isLength(value.length) && !isFunction(value);
}

module.exports = isArrayLike;


/***/ }),

/***/ "./node_modules/lodash/isArrayLikeObject.js":
/***/ (function(module, exports, __webpack_require__) {

var isArrayLike = __webpack_require__("./node_modules/lodash/isArrayLike.js"),
    isObjectLike = __webpack_require__("./node_modules/lodash/isObjectLike.js");

/**
 * This method is like `_.isArrayLike` except that it also checks if `value`
 * is an object.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is an array-like object,
 *  else `false`.
 * @example
 *
 * _.isArrayLikeObject([1, 2, 3]);
 * // => true
 *
 * _.isArrayLikeObject(document.body.children);
 * // => true
 *
 * _.isArrayLikeObject('abc');
 * // => false
 *
 * _.isArrayLikeObject(_.noop);
 * // => false
 */
function isArrayLikeObject(value) {
  return isObjectLike(value) && isArrayLike(value);
}

module.exports = isArrayLikeObject;


/***/ }),

/***/ "./node_modules/lodash/isBuffer.js":
/***/ (function(module, exports, __webpack_require__) {

/* WEBPACK VAR INJECTION */(function(module) {var root = __webpack_require__("./node_modules/lodash/_root.js"),
    stubFalse = __webpack_require__("./node_modules/lodash/stubFalse.js");

/** Detect free variable `exports`. */
var freeExports =  true && exports && !exports.nodeType && exports;

/** Detect free variable `module`. */
var freeModule = freeExports && typeof module == 'object' && module && !module.nodeType && module;

/** Detect the popular CommonJS extension `module.exports`. */
var moduleExports = freeModule && freeModule.exports === freeExports;

/** Built-in value references. */
var Buffer = moduleExports ? root.Buffer : undefined;

/* Built-in method references for those with the same name as other `lodash` methods. */
var nativeIsBuffer = Buffer ? Buffer.isBuffer : undefined;

/**
 * Checks if `value` is a buffer.
 *
 * @static
 * @memberOf _
 * @since 4.3.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a buffer, else `false`.
 * @example
 *
 * _.isBuffer(new Buffer(2));
 * // => true
 *
 * _.isBuffer(new Uint8Array(2));
 * // => false
 */
var isBuffer = nativeIsBuffer || stubFalse;

module.exports = isBuffer;

/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__("./node_modules/webpack/buildin/module.js")(module)))

/***/ }),

/***/ "./node_modules/lodash/isElement.js":
/***/ (function(module, exports, __webpack_require__) {

var isObjectLike = __webpack_require__("./node_modules/lodash/isObjectLike.js"),
    isPlainObject = __webpack_require__("./node_modules/lodash/isPlainObject.js");

/**
 * Checks if `value` is likely a DOM element.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a DOM element, else `false`.
 * @example
 *
 * _.isElement(document.body);
 * // => true
 *
 * _.isElement('<body>');
 * // => false
 */
function isElement(value) {
  return isObjectLike(value) && value.nodeType === 1 && !isPlainObject(value);
}

module.exports = isElement;


/***/ }),

/***/ "./node_modules/lodash/isFunction.js":
/***/ (function(module, exports, __webpack_require__) {

var baseGetTag = __webpack_require__("./node_modules/lodash/_baseGetTag.js"),
    isObject = __webpack_require__("./node_modules/lodash/isObject.js");

/** `Object#toString` result references. */
var asyncTag = '[object AsyncFunction]',
    funcTag = '[object Function]',
    genTag = '[object GeneratorFunction]',
    proxyTag = '[object Proxy]';

/**
 * Checks if `value` is classified as a `Function` object.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a function, else `false`.
 * @example
 *
 * _.isFunction(_);
 * // => true
 *
 * _.isFunction(/abc/);
 * // => false
 */
function isFunction(value) {
  if (!isObject(value)) {
    return false;
  }
  // The use of `Object#toString` avoids issues with the `typeof` operator
  // in Safari 9 which returns 'object' for typed arrays and other constructors.
  var tag = baseGetTag(value);
  return tag == funcTag || tag == genTag || tag == asyncTag || tag == proxyTag;
}

module.exports = isFunction;


/***/ }),

/***/ "./node_modules/lodash/isLength.js":
/***/ (function(module, exports) {

/** Used as references for various `Number` constants. */
var MAX_SAFE_INTEGER = 9007199254740991;

/**
 * Checks if `value` is a valid array-like length.
 *
 * **Note:** This method is loosely based on
 * [`ToLength`](http://ecma-international.org/ecma-262/7.0/#sec-tolength).
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a valid length, else `false`.
 * @example
 *
 * _.isLength(3);
 * // => true
 *
 * _.isLength(Number.MIN_VALUE);
 * // => false
 *
 * _.isLength(Infinity);
 * // => false
 *
 * _.isLength('3');
 * // => false
 */
function isLength(value) {
  return typeof value == 'number' &&
    value > -1 && value % 1 == 0 && value <= MAX_SAFE_INTEGER;
}

module.exports = isLength;


/***/ }),

/***/ "./node_modules/lodash/isMap.js":
/***/ (function(module, exports, __webpack_require__) {

var baseIsMap = __webpack_require__("./node_modules/lodash/_baseIsMap.js"),
    baseUnary = __webpack_require__("./node_modules/lodash/_baseUnary.js"),
    nodeUtil = __webpack_require__("./node_modules/lodash/_nodeUtil.js");

/* Node.js helper references. */
var nodeIsMap = nodeUtil && nodeUtil.isMap;

/**
 * Checks if `value` is classified as a `Map` object.
 *
 * @static
 * @memberOf _
 * @since 4.3.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a map, else `false`.
 * @example
 *
 * _.isMap(new Map);
 * // => true
 *
 * _.isMap(new WeakMap);
 * // => false
 */
var isMap = nodeIsMap ? baseUnary(nodeIsMap) : baseIsMap;

module.exports = isMap;


/***/ }),

/***/ "./node_modules/lodash/isObject.js":
/***/ (function(module, exports) {

/**
 * Checks if `value` is the
 * [language type](http://www.ecma-international.org/ecma-262/7.0/#sec-ecmascript-language-types)
 * of `Object`. (e.g. arrays, functions, objects, regexes, `new Number(0)`, and `new String('')`)
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is an object, else `false`.
 * @example
 *
 * _.isObject({});
 * // => true
 *
 * _.isObject([1, 2, 3]);
 * // => true
 *
 * _.isObject(_.noop);
 * // => true
 *
 * _.isObject(null);
 * // => false
 */
function isObject(value) {
  var type = typeof value;
  return value != null && (type == 'object' || type == 'function');
}

module.exports = isObject;


/***/ }),

/***/ "./node_modules/lodash/isObjectLike.js":
/***/ (function(module, exports) {

/**
 * Checks if `value` is object-like. A value is object-like if it's not `null`
 * and has a `typeof` result of "object".
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is object-like, else `false`.
 * @example
 *
 * _.isObjectLike({});
 * // => true
 *
 * _.isObjectLike([1, 2, 3]);
 * // => true
 *
 * _.isObjectLike(_.noop);
 * // => false
 *
 * _.isObjectLike(null);
 * // => false
 */
function isObjectLike(value) {
  return value != null && typeof value == 'object';
}

module.exports = isObjectLike;


/***/ }),

/***/ "./node_modules/lodash/isPlainObject.js":
/***/ (function(module, exports, __webpack_require__) {

var baseGetTag = __webpack_require__("./node_modules/lodash/_baseGetTag.js"),
    getPrototype = __webpack_require__("./node_modules/lodash/_getPrototype.js"),
    isObjectLike = __webpack_require__("./node_modules/lodash/isObjectLike.js");

/** `Object#toString` result references. */
var objectTag = '[object Object]';

/** Used for built-in method references. */
var funcProto = Function.prototype,
    objectProto = Object.prototype;

/** Used to resolve the decompiled source of functions. */
var funcToString = funcProto.toString;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/** Used to infer the `Object` constructor. */
var objectCtorString = funcToString.call(Object);

/**
 * Checks if `value` is a plain object, that is, an object created by the
 * `Object` constructor or one with a `[[Prototype]]` of `null`.
 *
 * @static
 * @memberOf _
 * @since 0.8.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a plain object, else `false`.
 * @example
 *
 * function Foo() {
 *   this.a = 1;
 * }
 *
 * _.isPlainObject(new Foo);
 * // => false
 *
 * _.isPlainObject([1, 2, 3]);
 * // => false
 *
 * _.isPlainObject({ 'x': 0, 'y': 0 });
 * // => true
 *
 * _.isPlainObject(Object.create(null));
 * // => true
 */
function isPlainObject(value) {
  if (!isObjectLike(value) || baseGetTag(value) != objectTag) {
    return false;
  }
  var proto = getPrototype(value);
  if (proto === null) {
    return true;
  }
  var Ctor = hasOwnProperty.call(proto, 'constructor') && proto.constructor;
  return typeof Ctor == 'function' && Ctor instanceof Ctor &&
    funcToString.call(Ctor) == objectCtorString;
}

module.exports = isPlainObject;


/***/ }),

/***/ "./node_modules/lodash/isSet.js":
/***/ (function(module, exports, __webpack_require__) {

var baseIsSet = __webpack_require__("./node_modules/lodash/_baseIsSet.js"),
    baseUnary = __webpack_require__("./node_modules/lodash/_baseUnary.js"),
    nodeUtil = __webpack_require__("./node_modules/lodash/_nodeUtil.js");

/* Node.js helper references. */
var nodeIsSet = nodeUtil && nodeUtil.isSet;

/**
 * Checks if `value` is classified as a `Set` object.
 *
 * @static
 * @memberOf _
 * @since 4.3.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a set, else `false`.
 * @example
 *
 * _.isSet(new Set);
 * // => true
 *
 * _.isSet(new WeakSet);
 * // => false
 */
var isSet = nodeIsSet ? baseUnary(nodeIsSet) : baseIsSet;

module.exports = isSet;


/***/ }),

/***/ "./node_modules/lodash/isString.js":
/***/ (function(module, exports, __webpack_require__) {

var baseGetTag = __webpack_require__("./node_modules/lodash/_baseGetTag.js"),
    isArray = __webpack_require__("./node_modules/lodash/isArray.js"),
    isObjectLike = __webpack_require__("./node_modules/lodash/isObjectLike.js");

/** `Object#toString` result references. */
var stringTag = '[object String]';

/**
 * Checks if `value` is classified as a `String` primitive or object.
 *
 * @static
 * @since 0.1.0
 * @memberOf _
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a string, else `false`.
 * @example
 *
 * _.isString('abc');
 * // => true
 *
 * _.isString(1);
 * // => false
 */
function isString(value) {
  return typeof value == 'string' ||
    (!isArray(value) && isObjectLike(value) && baseGetTag(value) == stringTag);
}

module.exports = isString;


/***/ }),

/***/ "./node_modules/lodash/isSymbol.js":
/***/ (function(module, exports, __webpack_require__) {

var baseGetTag = __webpack_require__("./node_modules/lodash/_baseGetTag.js"),
    isObjectLike = __webpack_require__("./node_modules/lodash/isObjectLike.js");

/** `Object#toString` result references. */
var symbolTag = '[object Symbol]';

/**
 * Checks if `value` is classified as a `Symbol` primitive or object.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a symbol, else `false`.
 * @example
 *
 * _.isSymbol(Symbol.iterator);
 * // => true
 *
 * _.isSymbol('abc');
 * // => false
 */
function isSymbol(value) {
  return typeof value == 'symbol' ||
    (isObjectLike(value) && baseGetTag(value) == symbolTag);
}

module.exports = isSymbol;


/***/ }),

/***/ "./node_modules/lodash/isTypedArray.js":
/***/ (function(module, exports, __webpack_require__) {

var baseIsTypedArray = __webpack_require__("./node_modules/lodash/_baseIsTypedArray.js"),
    baseUnary = __webpack_require__("./node_modules/lodash/_baseUnary.js"),
    nodeUtil = __webpack_require__("./node_modules/lodash/_nodeUtil.js");

/* Node.js helper references. */
var nodeIsTypedArray = nodeUtil && nodeUtil.isTypedArray;

/**
 * Checks if `value` is classified as a typed array.
 *
 * @static
 * @memberOf _
 * @since 3.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a typed array, else `false`.
 * @example
 *
 * _.isTypedArray(new Uint8Array);
 * // => true
 *
 * _.isTypedArray([]);
 * // => false
 */
var isTypedArray = nodeIsTypedArray ? baseUnary(nodeIsTypedArray) : baseIsTypedArray;

module.exports = isTypedArray;


/***/ }),

/***/ "./node_modules/lodash/keys.js":
/***/ (function(module, exports, __webpack_require__) {

var arrayLikeKeys = __webpack_require__("./node_modules/lodash/_arrayLikeKeys.js"),
    baseKeys = __webpack_require__("./node_modules/lodash/_baseKeys.js"),
    isArrayLike = __webpack_require__("./node_modules/lodash/isArrayLike.js");

/**
 * Creates an array of the own enumerable property names of `object`.
 *
 * **Note:** Non-object values are coerced to objects. See the
 * [ES spec](http://ecma-international.org/ecma-262/7.0/#sec-object.keys)
 * for more details.
 *
 * @static
 * @since 0.1.0
 * @memberOf _
 * @category Object
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of property names.
 * @example
 *
 * function Foo() {
 *   this.a = 1;
 *   this.b = 2;
 * }
 *
 * Foo.prototype.c = 3;
 *
 * _.keys(new Foo);
 * // => ['a', 'b'] (iteration order is not guaranteed)
 *
 * _.keys('hi');
 * // => ['0', '1']
 */
function keys(object) {
  return isArrayLike(object) ? arrayLikeKeys(object) : baseKeys(object);
}

module.exports = keys;


/***/ }),

/***/ "./node_modules/lodash/keysIn.js":
/***/ (function(module, exports, __webpack_require__) {

var arrayLikeKeys = __webpack_require__("./node_modules/lodash/_arrayLikeKeys.js"),
    baseKeysIn = __webpack_require__("./node_modules/lodash/_baseKeysIn.js"),
    isArrayLike = __webpack_require__("./node_modules/lodash/isArrayLike.js");

/**
 * Creates an array of the own and inherited enumerable property names of `object`.
 *
 * **Note:** Non-object values are coerced to objects.
 *
 * @static
 * @memberOf _
 * @since 3.0.0
 * @category Object
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of property names.
 * @example
 *
 * function Foo() {
 *   this.a = 1;
 *   this.b = 2;
 * }
 *
 * Foo.prototype.c = 3;
 *
 * _.keysIn(new Foo);
 * // => ['a', 'b', 'c'] (iteration order is not guaranteed)
 */
function keysIn(object) {
  return isArrayLike(object) ? arrayLikeKeys(object, true) : baseKeysIn(object);
}

module.exports = keysIn;


/***/ }),

/***/ "./node_modules/lodash/merge.js":
/***/ (function(module, exports, __webpack_require__) {

var baseMerge = __webpack_require__("./node_modules/lodash/_baseMerge.js"),
    createAssigner = __webpack_require__("./node_modules/lodash/_createAssigner.js");

/**
 * This method is like `_.assign` except that it recursively merges own and
 * inherited enumerable string keyed properties of source objects into the
 * destination object. Source properties that resolve to `undefined` are
 * skipped if a destination value exists. Array and plain object properties
 * are merged recursively. Other objects and value types are overridden by
 * assignment. Source objects are applied from left to right. Subsequent
 * sources overwrite property assignments of previous sources.
 *
 * **Note:** This method mutates `object`.
 *
 * @static
 * @memberOf _
 * @since 0.5.0
 * @category Object
 * @param {Object} object The destination object.
 * @param {...Object} [sources] The source objects.
 * @returns {Object} Returns `object`.
 * @example
 *
 * var object = {
 *   'a': [{ 'b': 2 }, { 'd': 4 }]
 * };
 *
 * var other = {
 *   'a': [{ 'c': 3 }, { 'e': 5 }]
 * };
 *
 * _.merge(object, other);
 * // => { 'a': [{ 'b': 2, 'c': 3 }, { 'd': 4, 'e': 5 }] }
 */
var merge = createAssigner(function(object, source, srcIndex) {
  baseMerge(object, source, srcIndex);
});

module.exports = merge;


/***/ }),

/***/ "./node_modules/lodash/stubArray.js":
/***/ (function(module, exports) {

/**
 * This method returns a new empty array.
 *
 * @static
 * @memberOf _
 * @since 4.13.0
 * @category Util
 * @returns {Array} Returns the new empty array.
 * @example
 *
 * var arrays = _.times(2, _.stubArray);
 *
 * console.log(arrays);
 * // => [[], []]
 *
 * console.log(arrays[0] === arrays[1]);
 * // => false
 */
function stubArray() {
  return [];
}

module.exports = stubArray;


/***/ }),

/***/ "./node_modules/lodash/stubFalse.js":
/***/ (function(module, exports) {

/**
 * This method returns `false`.
 *
 * @static
 * @memberOf _
 * @since 4.13.0
 * @category Util
 * @returns {boolean} Returns `false`.
 * @example
 *
 * _.times(2, _.stubFalse);
 * // => [false, false]
 */
function stubFalse() {
  return false;
}

module.exports = stubFalse;


/***/ }),

/***/ "./node_modules/lodash/toFinite.js":
/***/ (function(module, exports, __webpack_require__) {

var toNumber = __webpack_require__("./node_modules/lodash/toNumber.js");

/** Used as references for various `Number` constants. */
var INFINITY = 1 / 0,
    MAX_INTEGER = 1.7976931348623157e+308;

/**
 * Converts `value` to a finite number.
 *
 * @static
 * @memberOf _
 * @since 4.12.0
 * @category Lang
 * @param {*} value The value to convert.
 * @returns {number} Returns the converted number.
 * @example
 *
 * _.toFinite(3.2);
 * // => 3.2
 *
 * _.toFinite(Number.MIN_VALUE);
 * // => 5e-324
 *
 * _.toFinite(Infinity);
 * // => 1.7976931348623157e+308
 *
 * _.toFinite('3.2');
 * // => 3.2
 */
function toFinite(value) {
  if (!value) {
    return value === 0 ? value : 0;
  }
  value = toNumber(value);
  if (value === INFINITY || value === -INFINITY) {
    var sign = (value < 0 ? -1 : 1);
    return sign * MAX_INTEGER;
  }
  return value === value ? value : 0;
}

module.exports = toFinite;


/***/ }),

/***/ "./node_modules/lodash/toInteger.js":
/***/ (function(module, exports, __webpack_require__) {

var toFinite = __webpack_require__("./node_modules/lodash/toFinite.js");

/**
 * Converts `value` to an integer.
 *
 * **Note:** This method is loosely based on
 * [`ToInteger`](http://www.ecma-international.org/ecma-262/7.0/#sec-tointeger).
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to convert.
 * @returns {number} Returns the converted integer.
 * @example
 *
 * _.toInteger(3.2);
 * // => 3
 *
 * _.toInteger(Number.MIN_VALUE);
 * // => 0
 *
 * _.toInteger(Infinity);
 * // => 1.7976931348623157e+308
 *
 * _.toInteger('3.2');
 * // => 3
 */
function toInteger(value) {
  var result = toFinite(value),
      remainder = result % 1;

  return result === result ? (remainder ? result - remainder : result) : 0;
}

module.exports = toInteger;


/***/ }),

/***/ "./node_modules/lodash/toNumber.js":
/***/ (function(module, exports, __webpack_require__) {

var baseTrim = __webpack_require__("./node_modules/lodash/_baseTrim.js"),
    isObject = __webpack_require__("./node_modules/lodash/isObject.js"),
    isSymbol = __webpack_require__("./node_modules/lodash/isSymbol.js");

/** Used as references for various `Number` constants. */
var NAN = 0 / 0;

/** Used to detect bad signed hexadecimal string values. */
var reIsBadHex = /^[-+]0x[0-9a-f]+$/i;

/** Used to detect binary string values. */
var reIsBinary = /^0b[01]+$/i;

/** Used to detect octal string values. */
var reIsOctal = /^0o[0-7]+$/i;

/** Built-in method references without a dependency on `root`. */
var freeParseInt = parseInt;

/**
 * Converts `value` to a number.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to process.
 * @returns {number} Returns the number.
 * @example
 *
 * _.toNumber(3.2);
 * // => 3.2
 *
 * _.toNumber(Number.MIN_VALUE);
 * // => 5e-324
 *
 * _.toNumber(Infinity);
 * // => Infinity
 *
 * _.toNumber('3.2');
 * // => 3.2
 */
function toNumber(value) {
  if (typeof value == 'number') {
    return value;
  }
  if (isSymbol(value)) {
    return NAN;
  }
  if (isObject(value)) {
    var other = typeof value.valueOf == 'function' ? value.valueOf() : value;
    value = isObject(other) ? (other + '') : other;
  }
  if (typeof value != 'string') {
    return value === 0 ? value : +value;
  }
  value = baseTrim(value);
  var isBinary = reIsBinary.test(value);
  return (isBinary || reIsOctal.test(value))
    ? freeParseInt(value.slice(2), isBinary ? 2 : 8)
    : (reIsBadHex.test(value) ? NAN : +value);
}

module.exports = toNumber;


/***/ }),

/***/ "./node_modules/lodash/toPlainObject.js":
/***/ (function(module, exports, __webpack_require__) {

var copyObject = __webpack_require__("./node_modules/lodash/_copyObject.js"),
    keysIn = __webpack_require__("./node_modules/lodash/keysIn.js");

/**
 * Converts `value` to a plain object flattening inherited enumerable string
 * keyed properties of `value` to own properties of the plain object.
 *
 * @static
 * @memberOf _
 * @since 3.0.0
 * @category Lang
 * @param {*} value The value to convert.
 * @returns {Object} Returns the converted plain object.
 * @example
 *
 * function Foo() {
 *   this.b = 2;
 * }
 *
 * Foo.prototype.c = 3;
 *
 * _.assign({ 'a': 1 }, new Foo);
 * // => { 'a': 1, 'b': 2 }
 *
 * _.assign({ 'a': 1 }, _.toPlainObject(new Foo));
 * // => { 'a': 1, 'b': 2, 'c': 3 }
 */
function toPlainObject(value) {
  return copyObject(value, keysIn(value));
}

module.exports = toPlainObject;


/***/ }),

/***/ "./node_modules/lodash/toString.js":
/***/ (function(module, exports, __webpack_require__) {

var baseToString = __webpack_require__("./node_modules/lodash/_baseToString.js");

/**
 * Converts `value` to a string. An empty string is returned for `null`
 * and `undefined` values. The sign of `-0` is preserved.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to convert.
 * @returns {string} Returns the converted string.
 * @example
 *
 * _.toString(null);
 * // => ''
 *
 * _.toString(-0);
 * // => '-0'
 *
 * _.toString([1, 2, 3]);
 * // => '1,2,3'
 */
function toString(value) {
  return value == null ? '' : baseToString(value);
}

module.exports = toString;


/***/ }),

/***/ "./node_modules/lodash/trim.js":
/***/ (function(module, exports, __webpack_require__) {

var baseToString = __webpack_require__("./node_modules/lodash/_baseToString.js"),
    baseTrim = __webpack_require__("./node_modules/lodash/_baseTrim.js"),
    castSlice = __webpack_require__("./node_modules/lodash/_castSlice.js"),
    charsEndIndex = __webpack_require__("./node_modules/lodash/_charsEndIndex.js"),
    charsStartIndex = __webpack_require__("./node_modules/lodash/_charsStartIndex.js"),
    stringToArray = __webpack_require__("./node_modules/lodash/_stringToArray.js"),
    toString = __webpack_require__("./node_modules/lodash/toString.js");

/**
 * Removes leading and trailing whitespace or specified characters from `string`.
 *
 * @static
 * @memberOf _
 * @since 3.0.0
 * @category String
 * @param {string} [string=''] The string to trim.
 * @param {string} [chars=whitespace] The characters to trim.
 * @param- {Object} [guard] Enables use as an iteratee for methods like `_.map`.
 * @returns {string} Returns the trimmed string.
 * @example
 *
 * _.trim('  abc  ');
 * // => 'abc'
 *
 * _.trim('-_-abc-_-', '_-');
 * // => 'abc'
 *
 * _.map(['  foo  ', '  bar  '], _.trim);
 * // => ['foo', 'bar']
 */
function trim(string, chars, guard) {
  string = toString(string);
  if (string && (guard || chars === undefined)) {
    return baseTrim(string);
  }
  if (!string || !(chars = baseToString(chars))) {
    return string;
  }
  var strSymbols = stringToArray(string),
      chrSymbols = stringToArray(chars),
      start = charsStartIndex(strSymbols, chrSymbols),
      end = charsEndIndex(strSymbols, chrSymbols) + 1;

  return castSlice(strSymbols, start, end).join('');
}

module.exports = trim;


/***/ }),

/***/ "./node_modules/lodash/values.js":
/***/ (function(module, exports, __webpack_require__) {

var baseValues = __webpack_require__("./node_modules/lodash/_baseValues.js"),
    keys = __webpack_require__("./node_modules/lodash/keys.js");

/**
 * Creates an array of the own enumerable string keyed property values of `object`.
 *
 * **Note:** Non-object values are coerced to objects.
 *
 * @static
 * @since 0.1.0
 * @memberOf _
 * @category Object
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of property values.
 * @example
 *
 * function Foo() {
 *   this.a = 1;
 *   this.b = 2;
 * }
 *
 * Foo.prototype.c = 3;
 *
 * _.values(new Foo);
 * // => [1, 2] (iteration order is not guaranteed)
 *
 * _.values('hi');
 * // => ['h', 'i']
 */
function values(object) {
  return object == null ? [] : baseValues(object, keys(object));
}

module.exports = values;


/***/ }),

/***/ "./node_modules/webpack/buildin/global.js":
/***/ (function(module, exports) {

var g;

// This works in non-strict mode
g = (function() {
	return this;
})();

try {
	// This works if eval is allowed (see CSP)
	g = g || new Function("return this")();
} catch (e) {
	// This works if the window reference is available
	if (typeof window === "object") g = window;
}

// g can still be undefined, but nothing to do about it...
// We return undefined, instead of nothing here, so it's
// easier to handle this case. if(!global) { ...}

module.exports = g;


/***/ }),

/***/ "./node_modules/webpack/buildin/module.js":
/***/ (function(module, exports) {

module.exports = function(module) {
	if (!module.webpackPolyfill) {
		module.deprecate = function() {};
		module.paths = [];
		// module.parent = undefined by default
		if (!module.children) module.children = [];
		Object.defineProperty(module, "loaded", {
			enumerable: true,
			get: function() {
				return module.l;
			}
		});
		Object.defineProperty(module, "id", {
			enumerable: true,
			get: function() {
				return module.i;
			}
		});
		module.webpackPolyfill = 1;
	}
	return module;
};


/***/ }),

/***/ "./src/namespace/cloudinary-core-shrinkwrap.js":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
// ESM COMPAT FLAG
__webpack_require__.r(__webpack_exports__);

// EXPORTS
__webpack_require__.d(__webpack_exports__, "ClientHintsMetaTag", function() { return /* reexport */ clienthintsmetatag; });
__webpack_require__.d(__webpack_exports__, "Cloudinary", function() { return /* reexport */ cloudinary; });
__webpack_require__.d(__webpack_exports__, "Condition", function() { return /* reexport */ condition; });
__webpack_require__.d(__webpack_exports__, "Configuration", function() { return /* reexport */ src_configuration; });
__webpack_require__.d(__webpack_exports__, "Expression", function() { return /* reexport */ expression; });
__webpack_require__.d(__webpack_exports__, "crc32", function() { return /* reexport */ src_crc32; });
__webpack_require__.d(__webpack_exports__, "FetchLayer", function() { return /* reexport */ fetchlayer; });
__webpack_require__.d(__webpack_exports__, "HtmlTag", function() { return /* reexport */ htmltag; });
__webpack_require__.d(__webpack_exports__, "ImageTag", function() { return /* reexport */ imagetag; });
__webpack_require__.d(__webpack_exports__, "Layer", function() { return /* reexport */ layer_layer; });
__webpack_require__.d(__webpack_exports__, "PictureTag", function() { return /* reexport */ picturetag; });
__webpack_require__.d(__webpack_exports__, "SubtitlesLayer", function() { return /* reexport */ subtitleslayer; });
__webpack_require__.d(__webpack_exports__, "TextLayer", function() { return /* reexport */ textlayer; });
__webpack_require__.d(__webpack_exports__, "Transformation", function() { return /* reexport */ src_transformation; });
__webpack_require__.d(__webpack_exports__, "utf8_encode", function() { return /* reexport */ src_utf8_encode; });
__webpack_require__.d(__webpack_exports__, "Util", function() { return /* reexport */ lodash_namespaceObject; });
__webpack_require__.d(__webpack_exports__, "VideoTag", function() { return /* reexport */ videotag; });

// NAMESPACE OBJECT: ./src/constants.js
var constants_namespaceObject = {};
__webpack_require__.r(constants_namespaceObject);
__webpack_require__.d(constants_namespaceObject, "VERSION", function() { return VERSION; });
__webpack_require__.d(constants_namespaceObject, "CF_SHARED_CDN", function() { return CF_SHARED_CDN; });
__webpack_require__.d(constants_namespaceObject, "OLD_AKAMAI_SHARED_CDN", function() { return OLD_AKAMAI_SHARED_CDN; });
__webpack_require__.d(constants_namespaceObject, "AKAMAI_SHARED_CDN", function() { return AKAMAI_SHARED_CDN; });
__webpack_require__.d(constants_namespaceObject, "SHARED_CDN", function() { return SHARED_CDN; });
__webpack_require__.d(constants_namespaceObject, "DEFAULT_TIMEOUT_MS", function() { return DEFAULT_TIMEOUT_MS; });
__webpack_require__.d(constants_namespaceObject, "DEFAULT_POSTER_OPTIONS", function() { return DEFAULT_POSTER_OPTIONS; });
__webpack_require__.d(constants_namespaceObject, "DEFAULT_VIDEO_SOURCE_TYPES", function() { return DEFAULT_VIDEO_SOURCE_TYPES; });
__webpack_require__.d(constants_namespaceObject, "SEO_TYPES", function() { return SEO_TYPES; });
__webpack_require__.d(constants_namespaceObject, "DEFAULT_IMAGE_PARAMS", function() { return DEFAULT_IMAGE_PARAMS; });
__webpack_require__.d(constants_namespaceObject, "DEFAULT_VIDEO_PARAMS", function() { return DEFAULT_VIDEO_PARAMS; });
__webpack_require__.d(constants_namespaceObject, "DEFAULT_VIDEO_SOURCES", function() { return DEFAULT_VIDEO_SOURCES; });
__webpack_require__.d(constants_namespaceObject, "DEFAULT_EXTERNAL_LIBRARIES", function() { return DEFAULT_EXTERNAL_LIBRARIES; });
__webpack_require__.d(constants_namespaceObject, "PLACEHOLDER_IMAGE_MODES", function() { return PLACEHOLDER_IMAGE_MODES; });
__webpack_require__.d(constants_namespaceObject, "ACCESSIBILITY_MODES", function() { return ACCESSIBILITY_MODES; });
__webpack_require__.d(constants_namespaceObject, "URL_KEYS", function() { return URL_KEYS; });

// NAMESPACE OBJECT: ./src/util/lodash.js
var lodash_namespaceObject = {};
__webpack_require__.r(lodash_namespaceObject);
__webpack_require__.d(lodash_namespaceObject, "getSDKAnalyticsSignature", function() { return getSDKAnalyticsSignature; });
__webpack_require__.d(lodash_namespaceObject, "getAnalyticsOptions", function() { return getAnalyticsOptions; });
__webpack_require__.d(lodash_namespaceObject, "assign", function() { return assign_default.a; });
__webpack_require__.d(lodash_namespaceObject, "cloneDeep", function() { return cloneDeep_default.a; });
__webpack_require__.d(lodash_namespaceObject, "compact", function() { return compact_default.a; });
__webpack_require__.d(lodash_namespaceObject, "difference", function() { return difference_default.a; });
__webpack_require__.d(lodash_namespaceObject, "functions", function() { return functions_default.a; });
__webpack_require__.d(lodash_namespaceObject, "identity", function() { return identity_default.a; });
__webpack_require__.d(lodash_namespaceObject, "includes", function() { return includes_default.a; });
__webpack_require__.d(lodash_namespaceObject, "isArray", function() { return isArray_default.a; });
__webpack_require__.d(lodash_namespaceObject, "isPlainObject", function() { return isPlainObject_default.a; });
__webpack_require__.d(lodash_namespaceObject, "isString", function() { return isString_default.a; });
__webpack_require__.d(lodash_namespaceObject, "merge", function() { return merge_default.a; });
__webpack_require__.d(lodash_namespaceObject, "contains", function() { return includes_default.a; });
__webpack_require__.d(lodash_namespaceObject, "isIntersectionObserverSupported", function() { return isIntersectionObserverSupported; });
__webpack_require__.d(lodash_namespaceObject, "isNativeLazyLoadSupported", function() { return isNativeLazyLoadSupported; });
__webpack_require__.d(lodash_namespaceObject, "detectIntersection", function() { return detectIntersection; });
__webpack_require__.d(lodash_namespaceObject, "omit", function() { return omit; });
__webpack_require__.d(lodash_namespaceObject, "allStrings", function() { return baseutil_allStrings; });
__webpack_require__.d(lodash_namespaceObject, "without", function() { return without; });
__webpack_require__.d(lodash_namespaceObject, "isNumberLike", function() { return isNumberLike; });
__webpack_require__.d(lodash_namespaceObject, "smartEscape", function() { return smartEscape; });
__webpack_require__.d(lodash_namespaceObject, "defaults", function() { return defaults; });
__webpack_require__.d(lodash_namespaceObject, "objectProto", function() { return objectProto; });
__webpack_require__.d(lodash_namespaceObject, "objToString", function() { return objToString; });
__webpack_require__.d(lodash_namespaceObject, "isObject", function() { return isObject; });
__webpack_require__.d(lodash_namespaceObject, "funcTag", function() { return funcTag; });
__webpack_require__.d(lodash_namespaceObject, "reWords", function() { return reWords; });
__webpack_require__.d(lodash_namespaceObject, "camelCase", function() { return camelCase; });
__webpack_require__.d(lodash_namespaceObject, "snakeCase", function() { return snakeCase; });
__webpack_require__.d(lodash_namespaceObject, "convertKeys", function() { return convertKeys; });
__webpack_require__.d(lodash_namespaceObject, "withCamelCaseKeys", function() { return withCamelCaseKeys; });
__webpack_require__.d(lodash_namespaceObject, "withSnakeCaseKeys", function() { return withSnakeCaseKeys; });
__webpack_require__.d(lodash_namespaceObject, "base64Encode", function() { return base64Encode; });
__webpack_require__.d(lodash_namespaceObject, "base64EncodeURL", function() { return base64EncodeURL; });
__webpack_require__.d(lodash_namespaceObject, "extractUrlParams", function() { return extractUrlParams; });
__webpack_require__.d(lodash_namespaceObject, "patchFetchFormat", function() { return patchFetchFormat; });
__webpack_require__.d(lodash_namespaceObject, "optionConsume", function() { return optionConsume; });
__webpack_require__.d(lodash_namespaceObject, "isEmpty", function() { return isEmpty; });
__webpack_require__.d(lodash_namespaceObject, "isAndroid", function() { return isAndroid; });
__webpack_require__.d(lodash_namespaceObject, "isEdge", function() { return isEdge; });
__webpack_require__.d(lodash_namespaceObject, "isChrome", function() { return isChrome; });
__webpack_require__.d(lodash_namespaceObject, "isSafari", function() { return isSafari; });
__webpack_require__.d(lodash_namespaceObject, "isElement", function() { return isElement_default.a; });
__webpack_require__.d(lodash_namespaceObject, "isFunction", function() { return isFunction_default.a; });
__webpack_require__.d(lodash_namespaceObject, "trim", function() { return trim_default.a; });
__webpack_require__.d(lodash_namespaceObject, "getData", function() { return lodash_getData; });
__webpack_require__.d(lodash_namespaceObject, "setData", function() { return lodash_setData; });
__webpack_require__.d(lodash_namespaceObject, "getAttribute", function() { return lodash_getAttribute; });
__webpack_require__.d(lodash_namespaceObject, "setAttribute", function() { return lodash_setAttribute; });
__webpack_require__.d(lodash_namespaceObject, "removeAttribute", function() { return lodash_removeAttribute; });
__webpack_require__.d(lodash_namespaceObject, "setAttributes", function() { return setAttributes; });
__webpack_require__.d(lodash_namespaceObject, "hasClass", function() { return lodash_hasClass; });
__webpack_require__.d(lodash_namespaceObject, "addClass", function() { return lodash_addClass; });
__webpack_require__.d(lodash_namespaceObject, "getStyles", function() { return getStyles; });
__webpack_require__.d(lodash_namespaceObject, "cssExpand", function() { return cssExpand; });
__webpack_require__.d(lodash_namespaceObject, "domStyle", function() { return domStyle; });
__webpack_require__.d(lodash_namespaceObject, "curCSS", function() { return curCSS; });
__webpack_require__.d(lodash_namespaceObject, "cssValue", function() { return cssValue; });
__webpack_require__.d(lodash_namespaceObject, "augmentWidthOrHeight", function() { return augmentWidthOrHeight; });
__webpack_require__.d(lodash_namespaceObject, "getWidthOrHeight", function() { return getWidthOrHeight; });
__webpack_require__.d(lodash_namespaceObject, "width", function() { return lodash_width; });

// CONCATENATED MODULE: ./src/utf8_encode.js
/**
 * UTF8 encoder
 * @private
 */
var utf8_encode;
/* harmony default export */ var src_utf8_encode = (utf8_encode = function utf8_encode(argString) {
  var c1, enc, end, n, start, string, stringl, utftext;
  // http://kevin.vanzonneveld.net
  // +   original by: Webtoolkit.info (http://www.webtoolkit.info/)
  // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
  // +   improved by: sowberry
  // +    tweaked by: Jack
  // +   bugfixed by: Onno Marsman
  // +   improved by: Yves Sucaet
  // +   bugfixed by: Onno Marsman
  // +   bugfixed by: Ulrich
  // +   bugfixed by: Rafal Kukawski
  // +   improved by: kirilloid
  // *     example 1: utf8_encode('Kevin van Zonneveld');
  // *     returns 1: 'Kevin van Zonneveld'
  if (argString === null || typeof argString === 'undefined') {
    return '';
  }
  string = argString + '';
  // .replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  utftext = '';
  start = void 0;
  end = void 0;
  stringl = 0;
  start = end = 0;
  stringl = string.length;
  n = 0;
  while (n < stringl) {
    c1 = string.charCodeAt(n);
    enc = null;
    if (c1 < 128) {
      end++;
    } else if (c1 > 127 && c1 < 2048) {
      enc = String.fromCharCode(c1 >> 6 | 192, c1 & 63 | 128);
    } else {
      enc = String.fromCharCode(c1 >> 12 | 224, c1 >> 6 & 63 | 128, c1 & 63 | 128);
    }
    if (enc !== null) {
      if (end > start) {
        utftext += string.slice(start, end);
      }
      utftext += enc;
      start = end = n + 1;
    }
    n++;
  }
  if (end > start) {
    utftext += string.slice(start, stringl);
  }
  return utftext;
});
// CONCATENATED MODULE: ./src/crc32.js


/**
 * CRC32 calculator
 * Depends on 'utf8_encode'
 * @private
 * @param {string} str - The string to calculate the CRC32 for.
 * @return {number}
 */
function crc32(str) {
  var crc, i, iTop, table, x, y;
  // http://kevin.vanzonneveld.net
  // +   original by: Webtoolkit.info (http://www.webtoolkit.info/)
  // +   improved by: T0bsn
  // +   improved by: http://stackoverflow.com/questions/2647935/javascript-crc32-function-and-php-crc32-not-matching
  // -    depends on: utf8_encode
  // *     example 1: crc32('Kevin van Zonneveld');
  // *     returns 1: 1249991249
  str = src_utf8_encode(str);
  table = '00000000 77073096 EE0E612C 990951BA 076DC419 706AF48F E963A535 9E6495A3 0EDB8832 79DCB8A4 E0D5E91E 97D2D988 09B64C2B 7EB17CBD E7B82D07 90BF1D91 1DB71064 6AB020F2 F3B97148 84BE41DE 1ADAD47D 6DDDE4EB F4D4B551 83D385C7 136C9856 646BA8C0 FD62F97A 8A65C9EC 14015C4F 63066CD9 FA0F3D63 8D080DF5 3B6E20C8 4C69105E D56041E4 A2677172 3C03E4D1 4B04D447 D20D85FD A50AB56B 35B5A8FA 42B2986C DBBBC9D6 ACBCF940 32D86CE3 45DF5C75 DCD60DCF ABD13D59 26D930AC 51DE003A C8D75180 BFD06116 21B4F4B5 56B3C423 CFBA9599 B8BDA50F 2802B89E 5F058808 C60CD9B2 B10BE924 2F6F7C87 58684C11 C1611DAB B6662D3D 76DC4190 01DB7106 98D220BC EFD5102A 71B18589 06B6B51F 9FBFE4A5 E8B8D433 7807C9A2 0F00F934 9609A88E E10E9818 7F6A0DBB 086D3D2D 91646C97 E6635C01 6B6B51F4 1C6C6162 856530D8 F262004E 6C0695ED 1B01A57B 8208F4C1 F50FC457 65B0D9C6 12B7E950 8BBEB8EA FCB9887C 62DD1DDF 15DA2D49 8CD37CF3 FBD44C65 4DB26158 3AB551CE A3BC0074 D4BB30E2 4ADFA541 3DD895D7 A4D1C46D D3D6F4FB 4369E96A 346ED9FC AD678846 DA60B8D0 44042D73 33031DE5 AA0A4C5F DD0D7CC9 5005713C 270241AA BE0B1010 C90C2086 5768B525 206F85B3 B966D409 CE61E49F 5EDEF90E 29D9C998 B0D09822 C7D7A8B4 59B33D17 2EB40D81 B7BD5C3B C0BA6CAD EDB88320 9ABFB3B6 03B6E20C 74B1D29A EAD54739 9DD277AF 04DB2615 73DC1683 E3630B12 94643B84 0D6D6A3E 7A6A5AA8 E40ECF0B 9309FF9D 0A00AE27 7D079EB1 F00F9344 8708A3D2 1E01F268 6906C2FE F762575D 806567CB 196C3671 6E6B06E7 FED41B76 89D32BE0 10DA7A5A 67DD4ACC F9B9DF6F 8EBEEFF9 17B7BE43 60B08ED5 D6D6A3E8 A1D1937E 38D8C2C4 4FDFF252 D1BB67F1 A6BC5767 3FB506DD 48B2364B D80D2BDA AF0A1B4C 36034AF6 41047A60 DF60EFC3 A867DF55 316E8EEF 4669BE79 CB61B38C BC66831A 256FD2A0 5268E236 CC0C7795 BB0B4703 220216B9 5505262F C5BA3BBE B2BD0B28 2BB45A92 5CB36A04 C2D7FFA7 B5D0CF31 2CD99E8B 5BDEAE1D 9B64C2B0 EC63F226 756AA39C 026D930A 9C0906A9 EB0E363F 72076785 05005713 95BF4A82 E2B87A14 7BB12BAE 0CB61B38 92D28E9B E5D5BE0D 7CDCEFB7 0BDBDF21 86D3D2D4 F1D4E242 68DDB3F8 1FDA836E 81BE16CD F6B9265B 6FB077E1 18B74777 88085AE6 FF0F6A70 66063BCA 11010B5C 8F659EFF F862AE69 616BFFD3 166CCF45 A00AE278 D70DD2EE 4E048354 3903B3C2 A7672661 D06016F7 4969474D 3E6E77DB AED16A4A D9D65ADC 40DF0B66 37D83BF0 A9BCAE53 DEBB9EC5 47B2CF7F 30B5FFE9 BDBDF21C CABAC28A 53B39330 24B4A3A6 BAD03605 CDD70693 54DE5729 23D967BF B3667A2E C4614AB8 5D681B02 2A6F2B94 B40BBE37 C30C8EA1 5A05DF1B 2D02EF8D';
  crc = 0;
  x = 0;
  y = 0;
  crc = crc ^ -1;
  i = 0;
  iTop = str.length;
  while (i < iTop) {
    y = (crc ^ str.charCodeAt(i)) & 0xFF;
    x = '0x' + table.substr(y * 9, 8);
    crc = crc >>> 8 ^ x;
    i++;
  }
  crc = crc ^ -1;
  //convert to unsigned 32-bit int if needed
  if (crc < 0) {
    crc += 4294967296;
  }
  return crc;
}
/* harmony default export */ var src_crc32 = (crc32);
// CONCATENATED MODULE: ./src/sdkAnalytics/stringPad.js
function stringPad(value, targetLength, padString) {
  targetLength = targetLength >> 0; //truncate if number or convert non-number to 0;
  padString = String(typeof padString !== 'undefined' ? padString : ' ');
  if (value.length > targetLength) {
    return String(value);
  } else {
    targetLength = targetLength - value.length;
    if (targetLength > padString.length) {
      padString += repeatStringNumTimes(padString, targetLength / padString.length);
    }
    return padString.slice(0, targetLength) + String(value);
  }
}
function repeatStringNumTimes(string, times) {
  var repeatedString = "";
  while (times > 0) {
    repeatedString += string;
    times--;
  }
  return repeatedString;
}
// CONCATENATED MODULE: ./src/sdkAnalytics/base64Map.js
function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }
function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }
function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && iter[Symbol.iterator] != null || iter["@@iterator"] != null) return Array.from(iter); }
function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }
function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i]; return arr2; }

var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
var base64Map_num = 0;
var map = {};
_toConsumableArray(chars).forEach(function (_char) {
  var key = base64Map_num.toString(2);
  key = stringPad(key, 6, '0');
  map[key] = _char;
  base64Map_num++;
});

/**
 * Map of six-bit binary codes to Base64 characters
 */
/* harmony default export */ var base64Map = (map);
// CONCATENATED MODULE: ./src/sdkAnalytics/reverseVersion.js


/**
 * @description A semVer like string, x.y.z or x.y is allowed
 *              Reverses the version positions, x.y.z turns to z.y.x
 *              Pads each segment with '0' so they have length of 2
 *              Example: 1.2.3 -> 03.02.01
 * @param {string} semVer Input can be either x.y.z or x.y
 * @return {string} in the form of zz.yy.xx (
 */
function reverseVersion(semVer) {
  if (semVer.split('.').length < 2) {
    throw new Error('invalid semVer, must have at least two segments');
  }

  // Split by '.', reverse, create new array with padded values and concat it together
  return semVer.split('.').reverse().map(function (segment) {
    return stringPad(segment, 2, '0');
  }).join('.');
}
// CONCATENATED MODULE: ./src/sdkAnalytics/encodeVersion.js




/**
 * @description Encodes a semVer-like version string
 * @param {string} semVer Input can be either x.y.z or x.y
 * @return {string} A string built from 3 characters of the base64 table that encode the semVer
 */
function encodeVersion(semVer) {
  var strResult = '';

  // support x.y or x.y.z by using 'parts' as a variable
  var parts = semVer.split('.').length;
  var paddedStringLength = parts * 6; // we pad to either 12 or 18 characters

  // reverse (but don't mirror) the version. 1.5.15 -> 15.5.1
  // Pad to two spaces, 15.5.1 -> 15.05.01
  var paddedReversedSemver = reverseVersion(semVer);

  // turn 15.05.01 to a string '150501' then to a number 150501
  var num = parseInt(paddedReversedSemver.split('.').join(''));

  // Represent as binary, add left padding to 12 or 18 characters.
  // 150,501 -> 100100101111100101

  var paddedBinary = num.toString(2);
  paddedBinary = stringPad(paddedBinary, paddedStringLength, '0');

  // Stop in case an invalid version number was provided
  // paddedBinary must be built from sections of 6 bits
  if (paddedBinary.length % 6 !== 0) {
    throw 'Version must be smaller than 43.21.26)';
  }

  // turn every 6 bits into a character using the base64Map
  paddedBinary.match(/.{1,6}/g).forEach(function (bitString) {
    // console.log(bitString);
    strResult += base64Map[bitString];
  });
  return strResult;
}
// CONCATENATED MODULE: ./src/sdkAnalytics/getSDKAnalyticsSignature.js


/**
 * @description Gets the SDK signature by encoding the SDK version and tech version
 * @param {{
 *    [techVersion]:string,
 *    [sdkSemver]: string,
 *    [sdkCode]: string,
 *    [feature]: string
 * }} analyticsOptions
 * @return {string} sdkAnalyticsSignature
 */
function getSDKAnalyticsSignature() {
  var analyticsOptions = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
  try {
    var twoPartVersion = removePatchFromSemver(analyticsOptions.techVersion);
    var encodedSDKVersion = encodeVersion(analyticsOptions.sdkSemver);
    var encodedTechVersion = encodeVersion(twoPartVersion);
    var featureCode = analyticsOptions.feature;
    var SDKCode = analyticsOptions.sdkCode;
    var algoVersion = 'A'; // The algo version is determined here, it should not be an argument

    return "".concat(algoVersion).concat(SDKCode).concat(encodedSDKVersion).concat(encodedTechVersion).concat(featureCode);
  } catch (e) {
    // Either SDK or Node versions were unparsable
    return 'E';
  }
}

/**
 * @description Removes patch version from the semver if it exists
 *              Turns x.y.z OR x.y into x.y
 * @param {'x.y.z' || 'x.y' || string} semVerStr
 */
function removePatchFromSemver(semVerStr) {
  var parts = semVerStr.split('.');
  return "".concat(parts[0], ".").concat(parts[1]);
}
// CONCATENATED MODULE: ./src/sdkAnalytics/getAnalyticsOptions.js
/**
 * @description Gets the analyticsOptions from options- should include sdkSemver, techVersion, sdkCode, and feature
 * @param options
 * @returns {{sdkSemver: (string), sdkCode, feature: string, techVersion: (string)} || {}}
 */
function getAnalyticsOptions(options) {
  var analyticsOptions = {
    sdkSemver: options.sdkSemver,
    techVersion: options.techVersion,
    sdkCode: options.sdkCode,
    feature: '0'
  };
  if (options.urlAnalytics) {
    if (options.accessibility) {
      analyticsOptions.feature = 'D';
    }
    if (options.loading === 'lazy') {
      analyticsOptions.feature = 'C';
    }
    if (options.responsive) {
      analyticsOptions.feature = 'A';
    }
    if (options.placeholder) {
      analyticsOptions.feature = 'B';
    }
    return analyticsOptions;
  } else {
    return {};
  }
}
// EXTERNAL MODULE: ./node_modules/lodash/assign.js
var lodash_assign = __webpack_require__("./node_modules/lodash/assign.js");
var assign_default = /*#__PURE__*/__webpack_require__.n(lodash_assign);

// EXTERNAL MODULE: ./node_modules/lodash/cloneDeep.js
var cloneDeep = __webpack_require__("./node_modules/lodash/cloneDeep.js");
var cloneDeep_default = /*#__PURE__*/__webpack_require__.n(cloneDeep);

// EXTERNAL MODULE: ./node_modules/lodash/compact.js
var compact = __webpack_require__("./node_modules/lodash/compact.js");
var compact_default = /*#__PURE__*/__webpack_require__.n(compact);

// EXTERNAL MODULE: ./node_modules/lodash/difference.js
var difference = __webpack_require__("./node_modules/lodash/difference.js");
var difference_default = /*#__PURE__*/__webpack_require__.n(difference);

// EXTERNAL MODULE: ./node_modules/lodash/functions.js
var functions = __webpack_require__("./node_modules/lodash/functions.js");
var functions_default = /*#__PURE__*/__webpack_require__.n(functions);

// EXTERNAL MODULE: ./node_modules/lodash/identity.js
var identity = __webpack_require__("./node_modules/lodash/identity.js");
var identity_default = /*#__PURE__*/__webpack_require__.n(identity);

// EXTERNAL MODULE: ./node_modules/lodash/includes.js
var includes = __webpack_require__("./node_modules/lodash/includes.js");
var includes_default = /*#__PURE__*/__webpack_require__.n(includes);

// EXTERNAL MODULE: ./node_modules/lodash/isArray.js
var isArray = __webpack_require__("./node_modules/lodash/isArray.js");
var isArray_default = /*#__PURE__*/__webpack_require__.n(isArray);

// EXTERNAL MODULE: ./node_modules/lodash/isPlainObject.js
var isPlainObject = __webpack_require__("./node_modules/lodash/isPlainObject.js");
var isPlainObject_default = /*#__PURE__*/__webpack_require__.n(isPlainObject);

// EXTERNAL MODULE: ./node_modules/lodash/isString.js
var isString = __webpack_require__("./node_modules/lodash/isString.js");
var isString_default = /*#__PURE__*/__webpack_require__.n(isString);

// EXTERNAL MODULE: ./node_modules/lodash/merge.js
var lodash_merge = __webpack_require__("./node_modules/lodash/merge.js");
var merge_default = /*#__PURE__*/__webpack_require__.n(lodash_merge);

// EXTERNAL MODULE: ./node_modules/lodash/isElement.js
var isElement = __webpack_require__("./node_modules/lodash/isElement.js");
var isElement_default = /*#__PURE__*/__webpack_require__.n(isElement);

// EXTERNAL MODULE: ./node_modules/lodash/isFunction.js
var isFunction = __webpack_require__("./node_modules/lodash/isFunction.js");
var isFunction_default = /*#__PURE__*/__webpack_require__.n(isFunction);

// EXTERNAL MODULE: ./node_modules/lodash/trim.js
var trim = __webpack_require__("./node_modules/lodash/trim.js");
var trim_default = /*#__PURE__*/__webpack_require__.n(trim);

// CONCATENATED MODULE: ./src/util/lazyLoad.js
function _typeof(o) { "@babel/helpers - typeof"; return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, _typeof(o); }
/*
 * Includes utility methods for lazy loading media
 */

/**
 * Check if IntersectionObserver is supported
 * @return {boolean} true if window.IntersectionObserver is defined
 */
function isIntersectionObserverSupported() {
  // Check that 'IntersectionObserver' property is defined on window
  return (typeof window === "undefined" ? "undefined" : _typeof(window)) === "object" && window.IntersectionObserver;
}

/**
 * Check if native lazy loading is supported
 * @return {boolean} true if 'loading' property is defined for HTMLImageElement
 */
function isNativeLazyLoadSupported() {
  return (typeof HTMLImageElement === "undefined" ? "undefined" : _typeof(HTMLImageElement)) === "object" && HTMLImageElement.prototype.loading;
}

/**
 * Calls onIntersect() when intersection is detected, or when
 * no native lazy loading or when IntersectionObserver isn't supported.
 * @param {Element} el - the element to observe
 * @param {function} onIntersect - called when the given element is in view
 */
function detectIntersection(el, onIntersect) {
  try {
    if (isNativeLazyLoadSupported() || !isIntersectionObserverSupported()) {
      // Return if there's no need or possibility to detect intersection
      onIntersect();
      return;
    }

    // Detect intersection with given element using IntersectionObserver
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          onIntersect();
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: [0, 0.01]
    });
    observer.observe(el);
  } catch (e) {
    onIntersect();
  }
}
// CONCATENATED MODULE: ./src/constants.js
var VERSION = "2.5.0";
var CF_SHARED_CDN = "d3jpl91pxevbkh.cloudfront.net";
var OLD_AKAMAI_SHARED_CDN = "cloudinary-a.akamaihd.net";
var AKAMAI_SHARED_CDN = "res.cloudinary.com";
var SHARED_CDN = AKAMAI_SHARED_CDN;
var DEFAULT_TIMEOUT_MS = 10000;
var DEFAULT_POSTER_OPTIONS = {
  format: 'jpg',
  resource_type: 'video'
};
var DEFAULT_VIDEO_SOURCE_TYPES = ['webm', 'mp4', 'ogv'];
var SEO_TYPES = {
  "image/upload": "images",
  "image/private": "private_images",
  "image/authenticated": "authenticated_images",
  "raw/upload": "files",
  "video/upload": "videos"
};

/**
* @const {Object} Cloudinary.DEFAULT_IMAGE_PARAMS
* Defaults values for image parameters.
*
* (Previously defined using option_consume() )
 */
var DEFAULT_IMAGE_PARAMS = {
  resource_type: "image",
  transformation: [],
  type: 'upload'
};

/**
* Defaults values for video parameters.
* @const {Object} Cloudinary.DEFAULT_VIDEO_PARAMS
* (Previously defined using option_consume() )
 */
var DEFAULT_VIDEO_PARAMS = {
  fallback_content: '',
  resource_type: "video",
  source_transformation: {},
  source_types: DEFAULT_VIDEO_SOURCE_TYPES,
  transformation: [],
  type: 'upload'
};

/**
 * Recommended sources for video tag
 * @const {Object} Cloudinary.DEFAULT_VIDEO_SOURCES
 */
var DEFAULT_VIDEO_SOURCES = [{
  type: "mp4",
  codecs: "hev1",
  transformations: {
    video_codec: "h265"
  }
}, {
  type: "webm",
  codecs: "vp9",
  transformations: {
    video_codec: "vp9"
  }
}, {
  type: "mp4",
  transformations: {
    video_codec: "auto"
  }
}, {
  type: "webm",
  transformations: {
    video_codec: "auto"
  }
}];
var DEFAULT_EXTERNAL_LIBRARIES = {
  seeThru: 'https://unpkg.com/seethru@4/dist/seeThru.min.js'
};

/**
 * Predefined placeholder transformations
 * @const {Object} Cloudinary.PLACEHOLDER_IMAGE_MODES
 */
var PLACEHOLDER_IMAGE_MODES = {
  'blur': [{
    effect: 'blur:2000',
    quality: 1,
    fetch_format: 'auto'
  }],
  // Default
  'pixelate': [{
    effect: 'pixelate',
    quality: 1,
    fetch_format: 'auto'
  }],
  // Generates a pixel size image which color is the predominant color of the original image.
  'predominant-color-pixel': [{
    width: 'iw_div_2',
    aspect_ratio: 1,
    crop: 'pad',
    background: 'auto'
  }, {
    crop: 'crop',
    width: 1,
    height: 1,
    gravity: 'north_east'
  }, {
    fetch_format: 'auto',
    quality: 'auto'
  }],
  // Generates an image which color is the predominant color of the original image.
  'predominant-color': [{
    variables: [['$currWidth', 'w'], ['$currHeight', 'h']]
  }, {
    width: 'iw_div_2',
    aspect_ratio: 1,
    crop: 'pad',
    background: 'auto'
  }, {
    crop: 'crop',
    width: 10,
    height: 10,
    gravity: 'north_east'
  }, {
    width: '$currWidth',
    height: '$currHeight',
    crop: 'fill'
  }, {
    fetch_format: 'auto',
    quality: 'auto'
  }],
  'vectorize': [{
    effect: 'vectorize:3:0.1',
    fetch_format: 'svg'
  }]
};

/**
 * Predefined accessibility transformations
 * @const {Object} Cloudinary.ACCESSIBILITY_MODES
 */
var ACCESSIBILITY_MODES = {
  darkmode: 'tint:75:black',
  brightmode: 'tint:50:white',
  monochrome: 'grayscale',
  colorblind: 'assist_colorblind'
};

/**
 * A list of keys used by the url() function.
 * @private
 */
var URL_KEYS = ['accessibility', 'api_secret', 'auth_token', 'cdn_subdomain', 'cloud_name', 'cname', 'format', 'placeholder', 'private_cdn', 'resource_type', 'secure', 'secure_cdn_subdomain', 'secure_distribution', 'shorten', 'sign_url', 'signature', 'ssl_detected', 'type', 'url_suffix', 'use_root_path', 'version'];

/**
 * The resource storage type
 * @typedef type
 * @enum {string}
 * @property  {string} 'upload' A resource uploaded directly to Cloudinary
 * @property  {string} 'fetch' A resource fetched by Cloudinary from a 3rd party storage
 * @property  {string} 'private'
 * @property  {string} 'authenticated'
 * @property  {string} 'sprite'
 * @property  {string} 'facebook'
 * @property  {string} 'twitter'
 * @property  {string} 'youtube'
 * @property  {string} 'vimeo'
 *
 */

/**
 * The resource type
 * @typedef resourceType
 * @enum {string}
 * @property {string} 'image' An image file
 * @property {string} 'video' A video file
 * @property {string} 'raw'   A raw file
 */
// CONCATENATED MODULE: ./src/util/baseutil.js
function baseutil_typeof(o) { "@babel/helpers - typeof"; return baseutil_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, baseutil_typeof(o); }
/*
 * Includes common utility methods and shims
 */


function omit(obj, keys) {
  obj = obj || {};
  var srcKeys = Object.keys(obj).filter(function (key) {
    return !includes_default()(keys, key);
  });
  var filtered = {};
  srcKeys.forEach(function (key) {
    return filtered[key] = obj[key];
  });
  return filtered;
}

/**
 * Return true if all items in list are strings
 * @function Util.allString
 * @param {Array} list - an array of items
 */
var baseutil_allStrings = function allStrings(list) {
  return list.length && list.every(isString_default.a);
};

/**
* Creates a new array without the given item.
* @function Util.without
* @param {Array} array - original array
* @param {*} item - the item to exclude from the new array
* @return {Array} a new array made of the original array's items except for `item`
 */
var without = function without(array, item) {
  return array.filter(function (v) {
    return v !== item;
  });
};

/**
* Return true is value is a number or a string representation of a number.
* @function Util.isNumberLike
* @param {*} value
* @returns {boolean} true if value is a number
* @example
*    Util.isNumber(0) // true
*    Util.isNumber("1.3") // true
*    Util.isNumber("") // false
*    Util.isNumber(undefined) // false
 */
var isNumberLike = function isNumberLike(value) {
  return value != null && !isNaN(parseFloat(value));
};

/**
 * Escape all characters matching unsafe in the given string
 * @function Util.smartEscape
 * @param {string} string - source string to escape
 * @param {RegExp} unsafe - characters that must be escaped
 * @return {string} escaped string
 */
var smartEscape = function smartEscape(string) {
  var unsafe = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : /([^a-zA-Z0-9_.\-\/:]+)/g;
  return string.replace(unsafe, function (match) {
    return match.split("").map(function (c) {
      return "%" + c.charCodeAt(0).toString(16).toUpperCase();
    }).join("");
  });
};

/**
 * Assign values from sources if they are not defined in the destination.
 * Once a value is set it does not change
 * @function Util.defaults
 * @param {Object} destination - the object to assign defaults to
 * @param {...Object} source - the source object(s) to assign defaults from
 * @return {Object} destination after it was modified
 */
var defaults = function defaults(destination) {
  for (var _len = arguments.length, sources = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
    sources[_key - 1] = arguments[_key];
  }
  return sources.reduce(function (dest, source) {
    var key, value;
    for (key in source) {
      value = source[key];
      if (dest[key] === void 0) {
        dest[key] = value;
      }
    }
    return dest;
  }, destination);
};

/*********** lodash functions */
var objectProto = Object.prototype;

/**
 * Used to resolve the [`toStringTag`](http://ecma-international.org/ecma-262/6.0/#sec-object.prototype.tostring)
 * of values.
 */
var objToString = objectProto.toString;

/**
 * Checks if `value` is the [language type](https://es5.github.io/#x8) of `Object`.
 * (e.g. arrays, functions, objects, regexes, `new Number(0)`, and `new String('')`)
 *
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is an object, else `false`.
 * @example
 *
#isObject({});
 * // => true
 *
#isObject([1, 2, 3]);
 * // => true
 *
#isObject(1);
 * // => false
 */
var isObject = function isObject(value) {
  var type;
  // Avoid a V8 JIT bug in Chrome 19-20.
  // See https://code.google.com/p/v8/issues/detail?id=2291 for more details.
  type = baseutil_typeof(value);
  return !!value && (type === 'object' || type === 'function');
};
var funcTag = '[object Function]';

/**
* Checks if `value` is classified as a `Function` object.
* @function Util.isFunction
* @param {*} value The value to check.
* @returns {boolean} Returns `true` if `value` is correctly classified, else `false`.
* @example
*
* function Foo(){};
* isFunction(Foo);
* // => true
*
* isFunction(/abc/);
* // => false
 */
var baseutil_isFunction = function isFunction(value) {
  // The use of `Object#toString` avoids issues with the `typeof` operator
  // in older versions of Chrome and Safari which return 'function' for regexes
  // and Safari 8 which returns 'object' for typed array constructors.
  return isObject(value) && objToString.call(value) === funcTag;
};

/*********** lodash functions */
/** Used to match words to create compound words. */
var reWords = function () {
  var lower, upper;
  upper = '[A-Z]';
  lower = '[a-z]+';
  return RegExp(upper + '+(?=' + upper + lower + ')|' + upper + '?' + lower + '|' + upper + '+|[0-9]+', 'g');
}();

/**
* Convert string to camelCase
* @function Util.camelCase
* @param {string} source - the string to convert
* @return {string} in camelCase format
 */
var camelCase = function camelCase(source) {
  var words = source.match(reWords);
  words = words.map(function (word) {
    return word.charAt(0).toLocaleUpperCase() + word.slice(1).toLocaleLowerCase();
  });
  words[0] = words[0].toLocaleLowerCase();
  return words.join('');
};

/**
 * Convert string to snake_case
 * @function Util.snakeCase
 * @param {string} source - the string to convert
 * @return {string} in snake_case format
 */
var snakeCase = function snakeCase(source) {
  var words = source.match(reWords);
  words = words.map(function (word) {
    return word.toLocaleLowerCase();
  });
  return words.join('_');
};

/**
 * Creates a new object from source, with the keys transformed using the converter.
 * @param {object} source
 * @param {function|null} converter
 * @returns {object}
 */
var convertKeys = function convertKeys(source, converter) {
  var result, value;
  result = {};
  for (var key in source) {
    value = source[key];
    if (converter) {
      key = converter(key);
    }
    if (!isEmpty(key)) {
      result[key] = value;
    }
  }
  return result;
};

/**
 * Create a copy of the source object with all keys in camelCase
 * @function Util.withCamelCaseKeys
 * @param {Object} value - the object to copy
 * @return {Object} a new object
 */
var withCamelCaseKeys = function withCamelCaseKeys(source) {
  return convertKeys(source, camelCase);
};

/**
 * Create a copy of the source object with all keys in snake_case
 * @function Util.withSnakeCaseKeys
 * @param {Object} value - the object to copy
 * @return {Object} a new object
 */
var withSnakeCaseKeys = function withSnakeCaseKeys(source) {
  return convertKeys(source, snakeCase);
};

// Browser
// Node.js
var base64Encode = typeof btoa !== 'undefined' && baseutil_isFunction(btoa) ? btoa : typeof Buffer !== 'undefined' && baseutil_isFunction(Buffer) ? function (input) {
  if (!(input instanceof Buffer)) {
    input = new Buffer.from(String(input), 'binary');
  }
  return input.toString('base64');
} : function (input) {
  throw new Error("No base64 encoding function found");
};

/**
* Returns the Base64-decoded version of url.<br>
* This method delegates to `btoa` if present. Otherwise it tries `Buffer`.
* @function Util.base64EncodeURL
* @param {string} url - the url to encode. the value is URIdecoded and then re-encoded before converting to base64 representation
* @return {string} the base64 representation of the URL
 */
var base64EncodeURL = function base64EncodeURL(url) {
  try {
    url = decodeURI(url);
  } finally {
    url = encodeURI(url);
  }
  return base64Encode(url);
};

/**
 * Create a new object with only URL parameters
 * @param {object} options The source object
 * @return {Object} An object containing only URL parameters
 */
function extractUrlParams(options) {
  return URL_KEYS.reduce(function (obj, key) {
    if (options[key] != null) {
      obj[key] = options[key];
    }
    return obj;
  }, {});
}

/**
 * Handle the format parameter for fetch urls
 * @private
 * @param options url and transformation options. This argument may be changed by the function!
 */
function patchFetchFormat(options) {
  if (options == null) {
    options = {};
  }
  if (options.type === "fetch") {
    if (options.fetch_format == null) {
      options.fetch_format = optionConsume(options, "format");
    }
  }
}

/**
 * Deletes `option_name` from `options` and return the value if present.
 * If `options` doesn't contain `option_name` the default value is returned.
 * @param {Object} options a collection
 * @param {String} option_name the name (key) of the desired value
 * @param {*} [default_value] the value to return is option_name is missing
 */
function optionConsume(options, option_name, default_value) {
  var result = options[option_name];
  delete options[option_name];
  if (result != null) {
    return result;
  } else {
    return default_value;
  }
}

/**
 * Returns true if value is empty:
 * <ul>
 *   <li>value is null or undefined</li>
 *   <li>value is an array or string of length 0</li>
 *   <li>value is an object with no keys</li>
 * </ul>
 * @function Util.isEmpty
 * @param value
 * @returns {boolean} true if value is empty
 */
function isEmpty(value) {
  if (value == null) {
    return true;
  }
  if (typeof value.length == "number") {
    return value.length === 0;
  }
  if (typeof value.size == "number") {
    return value.size === 0;
  }
  if (baseutil_typeof(value) == "object") {
    for (var key in value) {
      if (value.hasOwnProperty(key)) {
        return false;
      }
    }
    return true;
  }
  return true;
}
// CONCATENATED MODULE: ./src/util/browser.js
/**
 * Based on video.js implementation:
 * https://github.com/videojs/video.js/blob/4238f5c1d88890547153e7e1de7bd0d1d8e0b236/src/js/utils/browser.js
 */

/**
* Retrieve from the navigator the user agent property.
* @returns user agent property.
*/
function getUserAgent() {
  return navigator && navigator.userAgent || '';
}

/**
 * Detect if current browser is any Android
 * @returns true if current browser is Android, false otherwise.
 */
function isAndroid() {
  var userAgent = getUserAgent();
  return /Android/i.test(userAgent);
}

/**
 * Detect if current browser is any Edge
 * @returns true if current browser is Edge, false otherwise.
 */
function isEdge() {
  var userAgent = getUserAgent();
  return /Edg/i.test(userAgent);
}

/**
 * Detect if current browser is chrome.
 * @returns true if current browser is Chrome, false otherwise.
 */
function isChrome() {
  var userAgent = getUserAgent();
  return !isEdge() && (/Chrome/i.test(userAgent) || /CriOS/i.test(userAgent));
}

/**
 * Detect if current browser is Safari.
 * @returns true if current browser is Safari, false otherwise.
 */
function isSafari() {
  // User agents for other browsers might include "Safari" so we must exclude them.
  // For example - this is the chrome user agent on windows 10:
  // Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36
  var userAgent = getUserAgent();
  return /Safari/i.test(userAgent) && !isChrome() && !isAndroid() && !isEdge();
}
// CONCATENATED MODULE: ./src/util/lodash.js
var nodeContains;























/*
 * Includes utility methods and lodash / jQuery shims
 */
/**
 * Get data from the DOM element.
 *
 * This method will use jQuery's `data()` method if it is available, otherwise it will get the `data-` attribute
 * @param {Element} element - the element to get the data from
 * @param {string} name - the name of the data item
 * @returns the value associated with the `name`
 * @function Util.getData
 */
var lodash_getData = function getData(element, name) {
  switch (false) {
    case !(element == null):
      return void 0;
    case !isFunction_default()(element.getAttribute):
      return element.getAttribute("data-".concat(name));
    case !isFunction_default()(element.getAttr):
      return element.getAttr("data-".concat(name));
    case !isFunction_default()(element.data):
      return element.data(name);
    case !(isFunction_default()(typeof jQuery !== "undefined" && jQuery.fn && jQuery.fn.data) && isElement_default()(element)):
      return jQuery(element).data(name);
  }
};

/**
 * Set data in the DOM element.
 *
 * This method will use jQuery's `data()` method if it is available, otherwise it will set the `data-` attribute
 * @function Util.setData
 * @param {Element} element - the element to set the data in
 * @param {string} name - the name of the data item
 * @param {*} value - the value to be set
 *
 */
var lodash_setData = function setData(element, name, value) {
  switch (false) {
    case !(element == null):
      return void 0;
    case !isFunction_default()(element.setAttribute):
      return element.setAttribute("data-".concat(name), value);
    case !isFunction_default()(element.setAttr):
      return element.setAttr("data-".concat(name), value);
    case !isFunction_default()(element.data):
      return element.data(name, value);
    case !(isFunction_default()(typeof jQuery !== "undefined" && jQuery.fn && jQuery.fn.data) && isElement_default()(element)):
      return jQuery(element).data(name, value);
  }
};

/**
 * Get attribute from the DOM element.
 *
 * @function Util.getAttribute
 * @param {Element} element - the element to set the attribute for
 * @param {string} name - the name of the attribute
 * @returns {*} the value of the attribute
 *
 */
var lodash_getAttribute = function getAttribute(element, name) {
  switch (false) {
    case !(element == null):
      return void 0;
    case !isFunction_default()(element.getAttribute):
      return element.getAttribute(name);
    case !isFunction_default()(element.attr):
      return element.attr(name);
    case !isFunction_default()(element.getAttr):
      return element.getAttr(name);
  }
};

/**
 * Set attribute in the DOM element.
 *
 * @function Util.setAttribute
 * @param {Element} element - the element to set the attribute for
 * @param {string} name - the name of the attribute
 * @param {*} value - the value to be set
 */
var lodash_setAttribute = function setAttribute(element, name, value) {
  switch (false) {
    case !(element == null):
      return void 0;
    case !isFunction_default()(element.setAttribute):
      return element.setAttribute(name, value);
    case !isFunction_default()(element.attr):
      return element.attr(name, value);
    case !isFunction_default()(element.setAttr):
      return element.setAttr(name, value);
  }
};

/**
 * Remove an attribute in the DOM element.
 *
 * @function Util.removeAttribute
 * @param {Element} element - the element to set the attribute for
 * @param {string} name - the name of the attribute
 */
var lodash_removeAttribute = function removeAttribute(element, name) {
  switch (false) {
    case !(element == null):
      return void 0;
    case !isFunction_default()(element.removeAttribute):
      return element.removeAttribute(name);
    default:
      return lodash_setAttribute(element, void 0);
  }
};

/**
 * Set a group of attributes to the element
 * @function Util.setAttributes
 * @param {Element} element - the element to set the attributes for
 * @param {Object} attributes - a hash of attribute names and values
 */
var setAttributes = function setAttributes(element, attributes) {
  var name, results, value;
  results = [];
  for (name in attributes) {
    value = attributes[name];
    if (value != null) {
      results.push(lodash_setAttribute(element, name, value));
    } else {
      results.push(lodash_removeAttribute(element, name));
    }
  }
  return results;
};

/**
 * Checks if element has a css class
 * @function Util.hasClass
 * @param {Element} element - the element to check
 * @param {string} name - the class name
 @returns {boolean} true if the element has the class
 */
var lodash_hasClass = function hasClass(element, name) {
  if (isElement_default()(element)) {
    return element.className.match(new RegExp("\\b".concat(name, "\\b")));
  }
};

/**
 * Add class to the element
 * @function Util.addClass
 * @param {Element} element - the element
 * @param {string} name - the class name to add
 */
var lodash_addClass = function addClass(element, name) {
  if (!element.className.match(new RegExp("\\b".concat(name, "\\b")))) {
    return element.className = trim_default()("".concat(element.className, " ").concat(name));
  }
};

// The following code is taken from jQuery
var getStyles = function getStyles(elem) {
  // Support: IE<=11+, Firefox<=30+ (#15098, #14150)
  // IE throws on elements created in popups
  // FF meanwhile throws on frame elements through "defaultView.getComputedStyle"
  if (elem.ownerDocument.defaultView.opener) {
    return elem.ownerDocument.defaultView.getComputedStyle(elem, null);
  }
  return window.getComputedStyle(elem, null);
};
var cssExpand = ["Top", "Right", "Bottom", "Left"];
nodeContains = function nodeContains(a, b) {
  var adown, bup;
  adown = a.nodeType === 9 ? a.documentElement : a;
  bup = b && b.parentNode;
  return a === bup || !!(bup && bup.nodeType === 1 && adown.contains(bup));
};

// Truncated version of jQuery.style(elem, name)
var domStyle = function domStyle(elem, name) {
  if (!(!elem || elem.nodeType === 3 || elem.nodeType === 8 || !elem.style)) {
    return elem.style[name];
  }
};
var curCSS = function curCSS(elem, name, computed) {
  var maxWidth, minWidth, ret, rmargin, style, width;
  rmargin = /^margin/;
  width = void 0;
  minWidth = void 0;
  maxWidth = void 0;
  ret = void 0;
  style = elem.style;
  computed = computed || getStyles(elem);
  if (computed) {
    // Support: IE9
    // getPropertyValue is only needed for .css('filter') (#12537)
    ret = computed.getPropertyValue(name) || computed[name];
  }
  if (computed) {
    if (ret === "" && !nodeContains(elem.ownerDocument, elem)) {
      ret = domStyle(elem, name);
    }
    // Support: iOS < 6
    // A tribute to the "awesome hack by Dean Edwards"
    // iOS < 6 (at least) returns percentage for a larger set of values, but width seems to be reliably pixels
    // this is against the CSSOM draft spec: http://dev.w3.org/csswg/cssom/#resolved-values
    if (rnumnonpx.test(ret) && rmargin.test(name)) {
      // Remember the original values
      width = style.width;
      minWidth = style.minWidth;
      maxWidth = style.maxWidth;
      // Put in the new values to get a computed value out
      style.minWidth = style.maxWidth = style.width = ret;
      ret = computed.width;
      // Revert the changed values
      style.width = width;
      style.minWidth = minWidth;
      style.maxWidth = maxWidth;
    }
  }
  // Support: IE
  // IE returns zIndex value as an integer.
  if (ret !== undefined) {
    return ret + "";
  } else {
    return ret;
  }
};
var cssValue = function cssValue(elem, name, convert, styles) {
  var val;
  val = curCSS(elem, name, styles);
  if (convert) {
    return parseFloat(val);
  } else {
    return val;
  }
};
var augmentWidthOrHeight = function augmentWidthOrHeight(elem, name, extra, isBorderBox, styles) {
  var i, len, side, sides, val;
  // If we already have the right measurement, avoid augmentation
  // Otherwise initialize for horizontal or vertical properties
  if (extra === (isBorderBox ? "border" : "content")) {
    return 0;
  } else {
    sides = name === "width" ? ["Right", "Left"] : ["Top", "Bottom"];
    val = 0;
    for (i = 0, len = sides.length; i < len; i++) {
      side = sides[i];
      if (extra === "margin") {
        // Both box models exclude margin, so add it if we want it
        val += cssValue(elem, extra + side, true, styles);
      }
      if (isBorderBox) {
        if (extra === "content") {
          // border-box includes padding, so remove it if we want content
          val -= cssValue(elem, "padding".concat(side), true, styles);
        }
        if (extra !== "margin") {
          // At this point, extra isn't border nor margin, so remove border
          val -= cssValue(elem, "border".concat(side, "Width"), true, styles);
        }
      } else {
        // At this point, extra isn't content, so add padding
        val += cssValue(elem, "padding".concat(side), true, styles);
        if (extra !== "padding") {
          // At this point, extra isn't content nor padding, so add border
          val += cssValue(elem, "border".concat(side, "Width"), true, styles);
        }
      }
    }
    return val;
  }
};
var pnum = /[+-]?(?:\d*\.|)\d+(?:[eE][+-]?\d+|)/.source;
var rnumnonpx = new RegExp("^(" + pnum + ")(?!px)[a-z%]+$", "i");
var getWidthOrHeight = function getWidthOrHeight(elem, name, extra) {
  var isBorderBox, styles, val, valueIsBorderBox;
  // Start with offset property, which is equivalent to the border-box value
  valueIsBorderBox = true;
  val = name === "width" ? elem.offsetWidth : elem.offsetHeight;
  styles = getStyles(elem);
  isBorderBox = cssValue(elem, "boxSizing", false, styles) === "border-box";
  // Some non-html elements return undefined for offsetWidth, so check for null/undefined
  // svg - https://bugzilla.mozilla.org/show_bug.cgi?id=649285
  // MathML - https://bugzilla.mozilla.org/show_bug.cgi?id=491668
  if (val <= 0 || val == null) {
    // Fall back to computed then uncomputed css if necessary
    val = curCSS(elem, name, styles);
    if (val < 0 || val == null) {
      val = elem.style[name];
    }
    if (rnumnonpx.test(val)) {
      // Computed unit is not pixels. Stop here and return.
      return val;
    }
    // Check for style in case a browser which returns unreliable values
    // for getComputedStyle silently falls back to the reliable elem.style
    //    valueIsBorderBox = isBorderBox and (support.boxSizingReliable() or val is elem.style[name])
    valueIsBorderBox = isBorderBox && val === elem.style[name];
    // Normalize "", auto, and prepare for extra
    val = parseFloat(val) || 0;
  }
  // Use the active box-sizing model to add/subtract irrelevant styles
  return val + augmentWidthOrHeight(elem, name, extra || (isBorderBox ? "border" : "content"), valueIsBorderBox, styles);
};
var lodash_width = function width(element) {
  return getWidthOrHeight(element, "width", "content");
};

/**
 * @class Util
 */
/**
 * Returns true if item is a string
 * @function Util.isString
 * @param item
 * @returns {boolean} true if item is a string
 */
/**
 * Returns true if item is empty:
 * <ul>
 *   <li>item is null or undefined</li>
 *   <li>item is an array or string of length 0</li>
 *   <li>item is an object with no keys</li>
 * </ul>
 * @function Util.isEmpty
 * @param item
 * @returns {boolean} true if item is empty
 */
/**
 * Assign source properties to destination.
 * If the property is an object it is assigned as a whole, overriding the destination object.
 * @function Util.assign
 * @param {Object} destination - the object to assign to
 */
/**
 * Recursively assign source properties to destination
 * @function Util.merge
 * @param {Object} destination - the object to assign to
 * @param {...Object} [sources] The source objects.
 */
/**
 * Create a new copy of the given object, including all internal objects.
 * @function Util.cloneDeep
 * @param {Object} value - the object to clone
 * @return {Object} a new deep copy of the object
 */
/**
 * Creates a new array from the parameter with "falsey" values removed
 * @function Util.compact
 * @param {Array} array - the array to remove values from
 * @return {Array} a new array without falsey values
 */
/**
 * Check if a given item is included in the given array
 * @function Util.contains
 * @param {Array} array - the array to search in
 * @param {*} item - the item to search for
 * @return {boolean} true if the item is included in the array
 */
/**
 * Returns values in the given array that are not included in the other array
 * @function Util.difference
 * @param {Array} arr - the array to select from
 * @param {Array} values - values to filter from arr
 * @return {Array} the filtered values
 */
/**
 * Returns a list of all the function names in obj
 * @function Util.functions
 * @param {Object} object - the object to inspect
 * @return {Array} a list of functions of object
 */
/**
 * Returns the provided value. This functions is used as a default predicate function.
 * @function Util.identity
 * @param {*} value
 * @return {*} the provided value
 */
/**
 * Remove leading or trailing spaces from text
 * @function Util.trim
 * @param {string} text
 * @return {string} the `text` without leading or trailing spaces
 */
// CONCATENATED MODULE: ./src/expression.js
function expression_typeof(o) { "@babel/helpers - typeof"; return expression_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, expression_typeof(o); }
function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, _toPropertyKey(descriptor.key), descriptor); } }
function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == expression_typeof(i) ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != expression_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != expression_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
/**
 * Represents a transformation expression.
 * @param {string} expressionStr - An expression in string format.
 * @class Expression
 * Normally this class is not instantiated directly
 */
var Expression = /*#__PURE__*/function () {
  function Expression(expressionStr) {
    _classCallCheck(this, Expression);
    /**
     * @protected
     * @inner Expression-expressions
     */
    this.expressions = [];
    if (expressionStr != null) {
      this.expressions.push(Expression.normalize(expressionStr));
    }
  }

  /**
   * Convenience constructor method
   * @function Expression.new
   */
  return _createClass(Expression, [{
    key: "serialize",
    value:
    /**
     * Serialize the expression
     * @return {string} the expression as a string
     */
    function serialize() {
      return Expression.normalize(this.expressions.join("_"));
    }
  }, {
    key: "toString",
    value: function toString() {
      return this.serialize();
    }

    /**
     * Get the parent transformation of this expression
     * @return Transformation
     */
  }, {
    key: "getParent",
    value: function getParent() {
      return this.parent;
    }

    /**
     * Set the parent transformation of this expression
     * @param {Transformation} the parent transformation
     * @return {Expression} this expression
     */
  }, {
    key: "setParent",
    value: function setParent(parent) {
      this.parent = parent;
      return this;
    }

    /**
     * Add a expression
     * @function Expression#predicate
     * @internal
     */
  }, {
    key: "predicate",
    value: function predicate(name, operator, value) {
      if (Expression.OPERATORS[operator] != null) {
        operator = Expression.OPERATORS[operator];
      }
      this.expressions.push("".concat(name, "_").concat(operator, "_").concat(value));
      return this;
    }

    /**
     * @function Expression#and
     */
  }, {
    key: "and",
    value: function and() {
      this.expressions.push("and");
      return this;
    }

    /**
     * @function Expression#or
     */
  }, {
    key: "or",
    value: function or() {
      this.expressions.push("or");
      return this;
    }

    /**
     * Conclude expression
     * @function Expression#then
     * @return {Transformation} the transformation this expression is defined for
     */
  }, {
    key: "then",
    value: function then() {
      return this.getParent()["if"](this.toString());
    }

    /**
     * @function Expression#height
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Expression} this expression
     */
  }, {
    key: "height",
    value: function height(operator, value) {
      return this.predicate("h", operator, value);
    }

    /**
     * @function Expression#width
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Expression} this expression
     */
  }, {
    key: "width",
    value: function width(operator, value) {
      return this.predicate("w", operator, value);
    }

    /**
     * @function Expression#aspectRatio
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Expression} this expression
     */
  }, {
    key: "aspectRatio",
    value: function aspectRatio(operator, value) {
      return this.predicate("ar", operator, value);
    }

    /**
     * @function Expression#pages
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Expression} this expression
     */
  }, {
    key: "pageCount",
    value: function pageCount(operator, value) {
      return this.predicate("pc", operator, value);
    }

    /**
     * @function Expression#faces
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Expression} this expression
     */
  }, {
    key: "faceCount",
    value: function faceCount(operator, value) {
      return this.predicate("fc", operator, value);
    }
  }, {
    key: "value",
    value: function value(_value) {
      this.expressions.push(_value);
      return this;
    }

    /**
     */
  }], [{
    key: "new",
    value: function _new(expressionStr) {
      return new this(expressionStr);
    }

    /**
     * Normalize a string expression
     * @function Cloudinary#normalize
     * @param {string} expression a expression, e.g. "w gt 100", "width_gt_100", "width > 100"
     * @return {string} the normalized form of the value expression, e.g. "w_gt_100"
     */
  }, {
    key: "normalize",
    value: function normalize(expression) {
      if (expression == null) {
        return expression;
      }
      expression = String(expression);
      var operators = "\\|\\||>=|<=|&&|!=|>|=|<|/|-|\\+|\\*|\\^";

      // operators
      var operatorsPattern = "((" + operators + ")(?=[ _]))";
      var operatorsReplaceRE = new RegExp(operatorsPattern, "g");
      expression = expression.replace(operatorsReplaceRE, function (match) {
        return Expression.OPERATORS[match];
      });

      // predefined variables
      // The :${v} part is to prevent normalization of vars with a preceding colon (such as :duration),
      // It won't be found in PREDEFINED_VARS and so won't be normalized.
      // It is done like this because ie11 does not support regex lookbehind
      var predefinedVarsPattern = "(" + Object.keys(Expression.PREDEFINED_VARS).map(function (v) {
        return ":".concat(v, "|").concat(v);
      }).join("|") + ")";
      var userVariablePattern = '(\\$_*[^_ ]+)';
      var variablesReplaceRE = new RegExp("".concat(userVariablePattern, "|").concat(predefinedVarsPattern), "g");
      expression = expression.replace(variablesReplaceRE, function (match) {
        return Expression.PREDEFINED_VARS[match] || match;
      });
      return expression.replace(/[ _]+/g, '_');
    }
  }, {
    key: "variable",
    value: function variable(name, value) {
      return new this(name).value(value);
    }

    /**
     * @returns Expression a new expression with the predefined variable "width"
     * @function Expression.width
     */
  }, {
    key: "width",
    value: function width() {
      return new this("width");
    }

    /**
     * @returns Expression a new expression with the predefined variable "height"
     * @function Expression.height
     */
  }, {
    key: "height",
    value: function height() {
      return new this("height");
    }

    /**
     * @returns Expression a new expression with the predefined variable "initialWidth"
     * @function Expression.initialWidth
     */
  }, {
    key: "initialWidth",
    value: function initialWidth() {
      return new this("initialWidth");
    }

    /**
     * @returns Expression a new expression with the predefined variable "initialHeight"
     * @function Expression.initialHeight
     */
  }, {
    key: "initialHeight",
    value: function initialHeight() {
      return new this("initialHeight");
    }

    /**
     * @returns Expression a new expression with the predefined variable "aspectRatio"
     * @function Expression.aspectRatio
     */
  }, {
    key: "aspectRatio",
    value: function aspectRatio() {
      return new this("aspectRatio");
    }

    /**
     * @returns Expression a new expression with the predefined variable "initialAspectRatio"
     * @function Expression.initialAspectRatio
     */
  }, {
    key: "initialAspectRatio",
    value: function initialAspectRatio() {
      return new this("initialAspectRatio");
    }

    /**
     * @returns Expression a new expression with the predefined variable "pageCount"
     * @function Expression.pageCount
     */
  }, {
    key: "pageCount",
    value: function pageCount() {
      return new this("pageCount");
    }

    /**
     * @returns Expression new expression with the predefined variable "faceCount"
     * @function Expression.faceCount
     */
  }, {
    key: "faceCount",
    value: function faceCount() {
      return new this("faceCount");
    }

    /**
     * @returns Expression a new expression with the predefined variable "currentPage"
     * @function Expression.currentPage
     */
  }, {
    key: "currentPage",
    value: function currentPage() {
      return new this("currentPage");
    }

    /**
     * @returns Expression a new expression with the predefined variable "tags"
     * @function Expression.tags
     */
  }, {
    key: "tags",
    value: function tags() {
      return new this("tags");
    }

    /**
     * @returns Expression a new expression with the predefined variable "pageX"
     * @function Expression.pageX
     */
  }, {
    key: "pageX",
    value: function pageX() {
      return new this("pageX");
    }

    /**
     * @returns Expression a new expression with the predefined variable "pageY"
     * @function Expression.pageY
     */
  }, {
    key: "pageY",
    value: function pageY() {
      return new this("pageY");
    }
  }]);
}();
/**
 * @internal
 */
Expression.OPERATORS = {
  "=": 'eq',
  "!=": 'ne',
  "<": 'lt',
  ">": 'gt',
  "<=": 'lte',
  ">=": 'gte',
  "&&": 'and',
  "||": 'or',
  "*": "mul",
  "/": "div",
  "+": "add",
  "-": "sub",
  "^": "pow"
};

/**
 * @internal
 */
Expression.PREDEFINED_VARS = {
  "aspect_ratio": "ar",
  "aspectRatio": "ar",
  "current_page": "cp",
  "currentPage": "cp",
  "duration": "du",
  "face_count": "fc",
  "faceCount": "fc",
  "height": "h",
  "initial_aspect_ratio": "iar",
  "initial_duration": "idu",
  "initial_height": "ih",
  "initial_width": "iw",
  "initialAspectRatio": "iar",
  "initialDuration": "idu",
  "initialHeight": "ih",
  "initialWidth": "iw",
  "page_count": "pc",
  "page_x": "px",
  "page_y": "py",
  "pageCount": "pc",
  "pageX": "px",
  "pageY": "py",
  "tags": "tags",
  "width": "w"
};

/**
 * @internal
 */
Expression.BOUNDRY = "[ _]+";
/* harmony default export */ var expression = (Expression);
// CONCATENATED MODULE: ./src/condition.js
function condition_typeof(o) { "@babel/helpers - typeof"; return condition_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, condition_typeof(o); }
function condition_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function condition_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, condition_toPropertyKey(descriptor.key), descriptor); } }
function condition_createClass(Constructor, protoProps, staticProps) { if (protoProps) condition_defineProperties(Constructor.prototype, protoProps); if (staticProps) condition_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function condition_toPropertyKey(t) { var i = condition_toPrimitive(t, "string"); return "symbol" == condition_typeof(i) ? i : i + ""; }
function condition_toPrimitive(t, r) { if ("object" != condition_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != condition_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function _callSuper(t, o, e) { return o = _getPrototypeOf(o), _possibleConstructorReturn(t, _isNativeReflectConstruct() ? Reflect.construct(o, e || [], _getPrototypeOf(t).constructor) : o.apply(t, e)); }
function _possibleConstructorReturn(self, call) { if (call && (condition_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return _assertThisInitialized(self); }
function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }
function _isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }
function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) _setPrototypeOf(subClass, superClass); }
function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }


/**
 * Represents a transformation condition.
 * @param {string} conditionStr - a condition in string format
 * @class Condition
 * @example
 * // normally this class is not instantiated directly
 * var tr = cloudinary.Transformation.new()
 *    .if().width( ">", 1000).and().aspectRatio("<", "3:4").then()
 *      .width(1000)
 *      .crop("scale")
 *    .else()
 *      .width(500)
 *      .crop("scale")
 *
 * var tr = cloudinary.Transformation.new()
 *    .if("w > 1000 and aspectRatio < 3:4")
 *      .width(1000)
 *      .crop("scale")
 *    .else()
 *      .width(500)
 *      .crop("scale")
 *
 */
var Condition = /*#__PURE__*/function (_Expression) {
  function Condition(conditionStr) {
    condition_classCallCheck(this, Condition);
    return _callSuper(this, Condition, [conditionStr]);
  }

  /**
   * @function Condition#height
   * @param {string} operator the comparison operator (e.g. "<", "lt")
   * @param {string|number} value the right hand side value
   * @return {Condition} this condition
   */
  _inherits(Condition, _Expression);
  return condition_createClass(Condition, [{
    key: "height",
    value: function height(operator, value) {
      return this.predicate("h", operator, value);
    }

    /**
     * @function Condition#width
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Condition} this condition
     */
  }, {
    key: "width",
    value: function width(operator, value) {
      return this.predicate("w", operator, value);
    }

    /**
     * @function Condition#aspectRatio
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Condition} this condition
     */
  }, {
    key: "aspectRatio",
    value: function aspectRatio(operator, value) {
      return this.predicate("ar", operator, value);
    }

    /**
     * @function Condition#pages
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Condition} this condition
     */
  }, {
    key: "pageCount",
    value: function pageCount(operator, value) {
      return this.predicate("pc", operator, value);
    }

    /**
     * @function Condition#faces
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Condition} this condition
     */
  }, {
    key: "faceCount",
    value: function faceCount(operator, value) {
      return this.predicate("fc", operator, value);
    }

    /**
     * @function Condition#duration
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Condition} this condition
     */
  }, {
    key: "duration",
    value: function duration(operator, value) {
      return this.predicate("du", operator, value);
    }

    /**
     * @function Condition#initialDuration
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Condition} this condition
     */
  }, {
    key: "initialDuration",
    value: function initialDuration(operator, value) {
      return this.predicate("idu", operator, value);
    }
  }]);
}(expression);
/* harmony default export */ var condition = (Condition);
// CONCATENATED MODULE: ./src/configuration.js
function configuration_typeof(o) { "@babel/helpers - typeof"; return configuration_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, configuration_typeof(o); }
function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || configuration_unsupportedIterableToArray(arr, i) || _nonIterableRest(); }
function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function configuration_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return configuration_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return configuration_arrayLikeToArray(o, minLen); }
function configuration_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i]; return arr2; }
function _iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t["return"] && (u = t["return"](), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }
function configuration_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function configuration_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, configuration_toPropertyKey(descriptor.key), descriptor); } }
function configuration_createClass(Constructor, protoProps, staticProps) { if (protoProps) configuration_defineProperties(Constructor.prototype, protoProps); if (staticProps) configuration_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function configuration_toPropertyKey(t) { var i = configuration_toPrimitive(t, "string"); return "symbol" == configuration_typeof(i) ? i : i + ""; }
function configuration_toPrimitive(t, r) { if ("object" != configuration_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != configuration_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
/**
 * Class for defining account configuration options.
 * Depends on 'utils'
 */



/**
 * Class for defining account configuration options.
 * @constructor Configuration
 * @param {Object} options - The account configuration parameters to set.
 * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
 *  target="_new">Available configuration options</a>
 */
var configuration_Configuration = /*#__PURE__*/function () {
  function Configuration(options) {
    configuration_classCallCheck(this, Configuration);
    this.configuration = options == null ? {} : cloneDeep_default()(options);
    defaults(this.configuration, DEFAULT_CONFIGURATION_PARAMS);
  }

  /**
   * Initializes the configuration. This method is a convenience method that invokes both
   *  {@link Configuration#fromEnvironment|fromEnvironment()} (Node.js environment only)
   *  and {@link Configuration#fromDocument|fromDocument()}.
   *  It first tries to retrieve the configuration from the environment variable.
   *  If not available, it tries from the document meta tags.
   * @function Configuration#init
   * @return {Configuration} returns `this` for chaining
   * @see fromDocument
   * @see fromEnvironment
   */
  return configuration_createClass(Configuration, [{
    key: "init",
    value: function init() {
      this.fromEnvironment();
      this.fromDocument();
      return this;
    }

    /**
     * Set a new configuration item
     * @function Configuration#set
     * @param {string} name - the name of the item to set
     * @param {*} value - the value to be set
     * @return {Configuration}
     *
     */
  }, {
    key: "set",
    value: function set(name, value) {
      this.configuration[name] = value;
      return this;
    }

    /**
     * Get the value of a configuration item
     * @function Configuration#get
     * @param {string} name - the name of the item to set
     * @return {*} the configuration item
     */
  }, {
    key: "get",
    value: function get(name) {
      return this.configuration[name];
    }
  }, {
    key: "merge",
    value: function merge(config) {
      assign_default()(this.configuration, cloneDeep_default()(config));
      return this;
    }

    /**
     * Initialize Cloudinary from HTML meta tags.
     * @function Configuration#fromDocument
     * @return {Configuration}
     * @example <meta name="cloudinary_cloud_name" content="mycloud">
     *
     */
  }, {
    key: "fromDocument",
    value: function fromDocument() {
      var el, i, len, meta_elements;
      meta_elements = typeof document !== "undefined" && document !== null ? document.querySelectorAll('meta[name^="cloudinary_"]') : void 0;
      if (meta_elements) {
        for (i = 0, len = meta_elements.length; i < len; i++) {
          el = meta_elements[i];
          this.configuration[el.getAttribute('name').replace('cloudinary_', '')] = el.getAttribute('content');
        }
      }
      return this;
    }

    /**
     * Initialize Cloudinary from the `CLOUDINARY_URL` environment variable.
     *
     * This function will only run under Node.js environment.
     * @function Configuration#fromEnvironment
     * @requires Node.js
     */
  }, {
    key: "fromEnvironment",
    value: function fromEnvironment() {
      var _this = this;
      var cloudinary_url, query, uri, uriRegex;
      if (typeof process !== "undefined" && process !== null && process.env && process.env.CLOUDINARY_URL) {
        cloudinary_url = process.env.CLOUDINARY_URL;
        uriRegex = /cloudinary:\/\/(?:(\w+)(?:\:([\w-]+))?@)?([\w\.-]+)(?:\/([^?]*))?(?:\?(.+))?/;
        uri = uriRegex.exec(cloudinary_url);
        if (uri) {
          if (uri[3] != null) {
            this.configuration['cloud_name'] = uri[3];
          }
          if (uri[1] != null) {
            this.configuration['api_key'] = uri[1];
          }
          if (uri[2] != null) {
            this.configuration['api_secret'] = uri[2];
          }
          if (uri[4] != null) {
            this.configuration['private_cdn'] = uri[4] != null;
          }
          if (uri[4] != null) {
            this.configuration['secure_distribution'] = uri[4];
          }
          query = uri[5];
          if (query != null) {
            query.split('&').forEach(function (value) {
              var _value$split = value.split('='),
                _value$split2 = _slicedToArray(_value$split, 2),
                k = _value$split2[0],
                v = _value$split2[1];
              if (v == null) {
                v = true;
              }
              _this.configuration[k] = v;
            });
          }
        }
      }
      return this;
    }

    /**
     * Create or modify the Cloudinary client configuration
     *
     * Warning: `config()` returns the actual internal configuration object. modifying it will change the configuration.
     *
     * This is a backward compatibility method. For new code, use get(), merge() etc.
     * @function Configuration#config
     * @param {hash|string|boolean} new_config
     * @param {string} new_value
     * @returns {*} configuration, or value
     *
     * @see {@link fromEnvironment} for initialization using environment variables
     * @see {@link fromDocument} for initialization using HTML meta tags
     */
  }, {
    key: "config",
    value: function config(new_config, new_value) {
      switch (false) {
        case new_value === void 0:
          this.set(new_config, new_value);
          return this.configuration;
        case !isString_default()(new_config):
          return this.get(new_config);
        case !isPlainObject_default()(new_config):
          this.merge(new_config);
          return this.configuration;
        default:
          // Backward compatibility - return the internal object
          return this.configuration;
      }
    }

    /**
     * Returns a copy of the configuration parameters
     * @function Configuration#toOptions
     * @returns {Object} a key:value collection of the configuration parameters
     */
  }, {
    key: "toOptions",
    value: function toOptions() {
      return cloneDeep_default()(this.configuration);
    }
  }]);
}();
var DEFAULT_CONFIGURATION_PARAMS = {
  responsive_class: 'cld-responsive',
  responsive_use_breakpoints: true,
  round_dpr: true,
  secure: (typeof window !== "undefined" && window !== null ? window.location ? window.location.protocol : void 0 : void 0) === 'https:'
};
configuration_Configuration.CONFIG_PARAMS = ["api_key", "api_secret", "callback", "cdn_subdomain", "cloud_name", "cname", "private_cdn", "protocol", "resource_type", "responsive", "responsive_class", "responsive_use_breakpoints", "responsive_width", "round_dpr", "secure", "secure_cdn_subdomain", "secure_distribution", "shorten", "type", "upload_preset", "url_suffix", "use_root_path", "version", "externalLibraries", "max_timeout_ms"];
/* harmony default export */ var src_configuration = (configuration_Configuration);
// CONCATENATED MODULE: ./src/layer/layer.js
function layer_typeof(o) { "@babel/helpers - typeof"; return layer_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, layer_typeof(o); }
function layer_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function layer_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, layer_toPropertyKey(descriptor.key), descriptor); } }
function layer_createClass(Constructor, protoProps, staticProps) { if (protoProps) layer_defineProperties(Constructor.prototype, protoProps); if (staticProps) layer_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function layer_toPropertyKey(t) { var i = layer_toPrimitive(t, "string"); return "symbol" == layer_typeof(i) ? i : i + ""; }
function layer_toPrimitive(t, r) { if ("object" != layer_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != layer_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }

var layer_Layer = /*#__PURE__*/function () {
  /**
   * Layer
   * @constructor Layer
   * @param {Object} options - layer parameters
   */
  function Layer(options) {
    var _this = this;
    layer_classCallCheck(this, Layer);
    this.options = {};
    if (options != null) {
      ["resourceType", "type", "publicId", "format"].forEach(function (key) {
        var ref;
        return _this.options[key] = (ref = options[key]) != null ? ref : options[snakeCase(key)];
      });
    }
  }
  return layer_createClass(Layer, [{
    key: "resourceType",
    value: function resourceType(value) {
      this.options.resourceType = value;
      return this;
    }
  }, {
    key: "type",
    value: function type(value) {
      this.options.type = value;
      return this;
    }
  }, {
    key: "publicId",
    value: function publicId(value) {
      this.options.publicId = value;
      return this;
    }

    /**
     * Get the public ID, formatted for layer parameter
     * @function Layer#getPublicId
     * @return {String} public ID
     */
  }, {
    key: "getPublicId",
    value: function getPublicId() {
      var ref;
      return (ref = this.options.publicId) != null ? ref.replace(/\//g, ":") : void 0;
    }

    /**
     * Get the public ID, with format if present
     * @function Layer#getFullPublicId
     * @return {String} public ID
     */
  }, {
    key: "getFullPublicId",
    value: function getFullPublicId() {
      if (this.options.format != null) {
        return this.getPublicId() + "." + this.options.format;
      } else {
        return this.getPublicId();
      }
    }
  }, {
    key: "format",
    value: function format(value) {
      this.options.format = value;
      return this;
    }

    /**
     * generate the string representation of the layer
     * @function Layer#toString
     */
  }, {
    key: "toString",
    value: function toString() {
      var components;
      components = [];
      if (this.options.publicId == null) {
        throw "Must supply publicId";
      }
      if (!(this.options.resourceType === "image")) {
        components.push(this.options.resourceType);
      }
      if (!(this.options.type === "upload")) {
        components.push(this.options.type);
      }
      components.push(this.getFullPublicId());
      return compact_default()(components).join(":");
    }
  }, {
    key: "clone",
    value: function clone() {
      return new this.constructor(this.options);
    }
  }]);
}();
/* harmony default export */ var layer_layer = (layer_Layer);
// CONCATENATED MODULE: ./src/layer/textlayer.js
function textlayer_typeof(o) { "@babel/helpers - typeof"; return textlayer_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, textlayer_typeof(o); }
function textlayer_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function textlayer_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, textlayer_toPropertyKey(descriptor.key), descriptor); } }
function textlayer_createClass(Constructor, protoProps, staticProps) { if (protoProps) textlayer_defineProperties(Constructor.prototype, protoProps); if (staticProps) textlayer_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function textlayer_toPropertyKey(t) { var i = textlayer_toPrimitive(t, "string"); return "symbol" == textlayer_typeof(i) ? i : i + ""; }
function textlayer_toPrimitive(t, r) { if ("object" != textlayer_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != textlayer_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function textlayer_callSuper(t, o, e) { return o = textlayer_getPrototypeOf(o), textlayer_possibleConstructorReturn(t, textlayer_isNativeReflectConstruct() ? Reflect.construct(o, e || [], textlayer_getPrototypeOf(t).constructor) : o.apply(t, e)); }
function textlayer_possibleConstructorReturn(self, call) { if (call && (textlayer_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return textlayer_assertThisInitialized(self); }
function textlayer_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }
function textlayer_isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (textlayer_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function textlayer_getPrototypeOf(o) { textlayer_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return textlayer_getPrototypeOf(o); }
function textlayer_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) textlayer_setPrototypeOf(subClass, superClass); }
function textlayer_setPrototypeOf(o, p) { textlayer_setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return textlayer_setPrototypeOf(o, p); }


var textlayer_TextLayer = /*#__PURE__*/function (_Layer) {
  /**
   * @constructor TextLayer
   * @param {Object} options - layer parameters
   */
  function TextLayer(options) {
    var _this;
    textlayer_classCallCheck(this, TextLayer);
    var keys;
    _this = textlayer_callSuper(this, TextLayer, [options]);
    keys = ["resourceType", "resourceType", "fontFamily", "fontSize", "fontWeight", "fontStyle", "textDecoration", "textAlign", "stroke", "letterSpacing", "lineSpacing", "fontHinting", "fontAntialiasing", "text", "textStyle"];
    if (options != null) {
      keys.forEach(function (key) {
        var ref;
        return _this.options[key] = (ref = options[key]) != null ? ref : options[snakeCase(key)];
      });
    }
    _this.options.resourceType = "text";
    return _this;
  }
  textlayer_inherits(TextLayer, _Layer);
  return textlayer_createClass(TextLayer, [{
    key: "resourceType",
    value: function resourceType(_resourceType) {
      throw "Cannot modify resourceType for text layers";
    }
  }, {
    key: "type",
    value: function type(_type) {
      throw "Cannot modify type for text layers";
    }
  }, {
    key: "format",
    value: function format(_format) {
      throw "Cannot modify format for text layers";
    }
  }, {
    key: "fontFamily",
    value: function fontFamily(_fontFamily) {
      this.options.fontFamily = _fontFamily;
      return this;
    }
  }, {
    key: "fontSize",
    value: function fontSize(_fontSize) {
      this.options.fontSize = _fontSize;
      return this;
    }
  }, {
    key: "fontWeight",
    value: function fontWeight(_fontWeight) {
      this.options.fontWeight = _fontWeight;
      return this;
    }
  }, {
    key: "fontStyle",
    value: function fontStyle(_fontStyle) {
      this.options.fontStyle = _fontStyle;
      return this;
    }
  }, {
    key: "textDecoration",
    value: function textDecoration(_textDecoration) {
      this.options.textDecoration = _textDecoration;
      return this;
    }
  }, {
    key: "textAlign",
    value: function textAlign(_textAlign) {
      this.options.textAlign = _textAlign;
      return this;
    }
  }, {
    key: "stroke",
    value: function stroke(_stroke) {
      this.options.stroke = _stroke;
      return this;
    }
  }, {
    key: "letterSpacing",
    value: function letterSpacing(_letterSpacing) {
      this.options.letterSpacing = _letterSpacing;
      return this;
    }
  }, {
    key: "lineSpacing",
    value: function lineSpacing(_lineSpacing) {
      this.options.lineSpacing = _lineSpacing;
      return this;
    }
  }, {
    key: "fontHinting",
    value: function fontHinting(_fontHinting) {
      this.options.fontHinting = _fontHinting;
      return this;
    }
  }, {
    key: "fontAntialiasing",
    value: function fontAntialiasing(_fontAntialiasing) {
      this.options.fontAntialiasing = _fontAntialiasing;
      return this;
    }
  }, {
    key: "text",
    value: function text(_text) {
      this.options.text = _text;
      return this;
    }
  }, {
    key: "textStyle",
    value: function textStyle(_textStyle) {
      this.options.textStyle = _textStyle;
      return this;
    }

    /**
     * generate the string representation of the layer
     * @function TextLayer#toString
     * @return {String}
     */
  }, {
    key: "toString",
    value: function toString() {
      var components, hasPublicId, hasStyle, publicId, re, res, start, style, text, textSource;
      style = this.textStyleIdentifier();
      if (this.options.publicId != null) {
        publicId = this.getFullPublicId();
      }
      if (this.options.text != null) {
        hasPublicId = !isEmpty(publicId);
        hasStyle = !isEmpty(style);
        if (hasPublicId && hasStyle || !hasPublicId && !hasStyle) {
          throw "Must supply either style parameters or a public_id when providing text parameter in a text overlay/underlay, but not both!";
        }
        re = /\$\([a-zA-Z]\w*\)/g;
        start = 0;
        //        textSource = text.replace(new RegExp("[,/]", 'g'), (c)-> "%#{c.charCodeAt(0).toString(16).toUpperCase()}")
        textSource = smartEscape(this.options.text, /[,\/]/g);
        text = "";
        while (res = re.exec(textSource)) {
          text += smartEscape(textSource.slice(start, res.index));
          text += res[0];
          start = res.index + res[0].length;
        }
        text += smartEscape(textSource.slice(start));
      }
      components = [this.options.resourceType, style, publicId, text];
      return compact_default()(components).join(":");
    }
  }, {
    key: "textStyleIdentifier",
    value: function textStyleIdentifier() {
      // Note: if a text-style argument is provided as a whole, it overrides everything else, no mix and match.
      if (!isEmpty(this.options.textStyle)) {
        return this.options.textStyle;
      }
      var components;
      components = [];
      if (this.options.fontWeight !== "normal") {
        components.push(this.options.fontWeight);
      }
      if (this.options.fontStyle !== "normal") {
        components.push(this.options.fontStyle);
      }
      if (this.options.textDecoration !== "none") {
        components.push(this.options.textDecoration);
      }
      components.push(this.options.textAlign);
      if (this.options.stroke !== "none") {
        components.push(this.options.stroke);
      }
      if (!(isEmpty(this.options.letterSpacing) && !isNumberLike(this.options.letterSpacing))) {
        components.push("letter_spacing_" + this.options.letterSpacing);
      }
      if (!(isEmpty(this.options.lineSpacing) && !isNumberLike(this.options.lineSpacing))) {
        components.push("line_spacing_" + this.options.lineSpacing);
      }
      if (!isEmpty(this.options.fontAntialiasing)) {
        components.push("antialias_" + this.options.fontAntialiasing);
      }
      if (!isEmpty(this.options.fontHinting)) {
        components.push("hinting_" + this.options.fontHinting);
      }
      if (!isEmpty(compact_default()(components))) {
        if (isEmpty(this.options.fontFamily)) {
          throw "Must supply fontFamily. ".concat(components);
        }
        if (isEmpty(this.options.fontSize) && !isNumberLike(this.options.fontSize)) {
          throw "Must supply fontSize.";
        }
      }
      components.unshift(this.options.fontFamily, this.options.fontSize);
      components = compact_default()(components).join("_");
      return components;
    }
  }]);
}(layer_layer);
;
/* harmony default export */ var textlayer = (textlayer_TextLayer);
// CONCATENATED MODULE: ./src/layer/subtitleslayer.js
function subtitleslayer_typeof(o) { "@babel/helpers - typeof"; return subtitleslayer_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, subtitleslayer_typeof(o); }
function subtitleslayer_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, subtitleslayer_toPropertyKey(descriptor.key), descriptor); } }
function subtitleslayer_createClass(Constructor, protoProps, staticProps) { if (protoProps) subtitleslayer_defineProperties(Constructor.prototype, protoProps); if (staticProps) subtitleslayer_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function subtitleslayer_toPropertyKey(t) { var i = subtitleslayer_toPrimitive(t, "string"); return "symbol" == subtitleslayer_typeof(i) ? i : i + ""; }
function subtitleslayer_toPrimitive(t, r) { if ("object" != subtitleslayer_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != subtitleslayer_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function subtitleslayer_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function subtitleslayer_callSuper(t, o, e) { return o = subtitleslayer_getPrototypeOf(o), subtitleslayer_possibleConstructorReturn(t, subtitleslayer_isNativeReflectConstruct() ? Reflect.construct(o, e || [], subtitleslayer_getPrototypeOf(t).constructor) : o.apply(t, e)); }
function subtitleslayer_possibleConstructorReturn(self, call) { if (call && (subtitleslayer_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return subtitleslayer_assertThisInitialized(self); }
function subtitleslayer_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }
function subtitleslayer_isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (subtitleslayer_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function subtitleslayer_getPrototypeOf(o) { subtitleslayer_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return subtitleslayer_getPrototypeOf(o); }
function subtitleslayer_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) subtitleslayer_setPrototypeOf(subClass, superClass); }
function subtitleslayer_setPrototypeOf(o, p) { subtitleslayer_setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return subtitleslayer_setPrototypeOf(o, p); }

var SubtitlesLayer = /*#__PURE__*/function (_TextLayer) {
  /**
   * Represent a subtitles layer
   * @constructor SubtitlesLayer
   * @param {Object} options - layer parameters
   */
  function SubtitlesLayer(options) {
    var _this;
    subtitleslayer_classCallCheck(this, SubtitlesLayer);
    _this = subtitleslayer_callSuper(this, SubtitlesLayer, [options]);
    _this.options.resourceType = "subtitles";
    return _this;
  }
  subtitleslayer_inherits(SubtitlesLayer, _TextLayer);
  return subtitleslayer_createClass(SubtitlesLayer);
}(textlayer);
/* harmony default export */ var subtitleslayer = (SubtitlesLayer);
// CONCATENATED MODULE: ./src/layer/fetchlayer.js
function fetchlayer_typeof(o) { "@babel/helpers - typeof"; return fetchlayer_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, fetchlayer_typeof(o); }
function fetchlayer_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function fetchlayer_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, fetchlayer_toPropertyKey(descriptor.key), descriptor); } }
function fetchlayer_createClass(Constructor, protoProps, staticProps) { if (protoProps) fetchlayer_defineProperties(Constructor.prototype, protoProps); if (staticProps) fetchlayer_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function fetchlayer_toPropertyKey(t) { var i = fetchlayer_toPrimitive(t, "string"); return "symbol" == fetchlayer_typeof(i) ? i : i + ""; }
function fetchlayer_toPrimitive(t, r) { if ("object" != fetchlayer_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != fetchlayer_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function fetchlayer_callSuper(t, o, e) { return o = fetchlayer_getPrototypeOf(o), fetchlayer_possibleConstructorReturn(t, fetchlayer_isNativeReflectConstruct() ? Reflect.construct(o, e || [], fetchlayer_getPrototypeOf(t).constructor) : o.apply(t, e)); }
function fetchlayer_possibleConstructorReturn(self, call) { if (call && (fetchlayer_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return fetchlayer_assertThisInitialized(self); }
function fetchlayer_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }
function fetchlayer_isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (fetchlayer_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function fetchlayer_getPrototypeOf(o) { fetchlayer_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return fetchlayer_getPrototypeOf(o); }
function fetchlayer_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) fetchlayer_setPrototypeOf(subClass, superClass); }
function fetchlayer_setPrototypeOf(o, p) { fetchlayer_setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return fetchlayer_setPrototypeOf(o, p); }


var fetchlayer_FetchLayer = /*#__PURE__*/function (_Layer) {
  /**
   * @class FetchLayer
   * @classdesc Creates an image layer using a remote URL.
   * @param {Object|string} options - layer parameters or a url
   * @param {string} options.url the url of the image to fetch
   */
  function FetchLayer(options) {
    var _this;
    fetchlayer_classCallCheck(this, FetchLayer);
    _this = fetchlayer_callSuper(this, FetchLayer, [options]);
    if (isString_default()(options)) {
      _this.options.url = options;
    } else if (options != null ? options.url : void 0) {
      _this.options.url = options.url;
    }
    return _this;
  }
  fetchlayer_inherits(FetchLayer, _Layer);
  return fetchlayer_createClass(FetchLayer, [{
    key: "url",
    value: function url(_url) {
      this.options.url = _url;
      return this;
    }

    /**
     * generate the string representation of the layer
     * @function FetchLayer#toString
     * @return {String}
     */
  }, {
    key: "toString",
    value: function toString() {
      return "fetch:".concat(base64EncodeURL(this.options.url));
    }
  }]);
}(layer_layer);
/* harmony default export */ var fetchlayer = (fetchlayer_FetchLayer);
// CONCATENATED MODULE: ./src/parameters.js
function parameters_callSuper(t, o, e) { return o = parameters_getPrototypeOf(o), parameters_possibleConstructorReturn(t, parameters_isNativeReflectConstruct() ? Reflect.construct(o, e || [], parameters_getPrototypeOf(t).constructor) : o.apply(t, e)); }
function parameters_possibleConstructorReturn(self, call) { if (call && (parameters_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return parameters_assertThisInitialized(self); }
function parameters_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }
function parameters_isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (parameters_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function _get() { if (typeof Reflect !== "undefined" && Reflect.get) { _get = Reflect.get.bind(); } else { _get = function _get(target, property, receiver) { var base = _superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(arguments.length < 3 ? target : receiver); } return desc.value; }; } return _get.apply(this, arguments); }
function _superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = parameters_getPrototypeOf(object); if (object === null) break; } return object; }
function parameters_getPrototypeOf(o) { parameters_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return parameters_getPrototypeOf(o); }
function parameters_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) parameters_setPrototypeOf(subClass, superClass); }
function parameters_setPrototypeOf(o, p) { parameters_setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return parameters_setPrototypeOf(o, p); }
function parameters_typeof(o) { "@babel/helpers - typeof"; return parameters_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, parameters_typeof(o); }
function parameters_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function parameters_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, parameters_toPropertyKey(descriptor.key), descriptor); } }
function parameters_createClass(Constructor, protoProps, staticProps) { if (protoProps) parameters_defineProperties(Constructor.prototype, protoProps); if (staticProps) parameters_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function parameters_toPropertyKey(t) { var i = parameters_toPrimitive(t, "string"); return "symbol" == parameters_typeof(i) ? i : i + ""; }
function parameters_toPrimitive(t, r) { if ("object" != parameters_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != parameters_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }








/**
 * Transformation parameters
 * Depends on 'util', 'transformation'
 */
var parameters_Param = /*#__PURE__*/function () {
  /**
   * Represents a single parameter.
   * @class Param
   * @param {string} name - The name of the parameter in snake_case
   * @param {string} shortName - The name of the serialized form of the parameter.
   *                         If a value is not provided, the parameter will not be serialized.
   * @param {function} [process=Util.identity ] - Manipulate origValue when value is called
   * @ignore
   */
  function Param(name, shortName) {
    var process = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : identity_default.a;
    parameters_classCallCheck(this, Param);
    /**
     * The name of the parameter in snake_case
     * @member {string} Param#name
     */
    this.name = name;
    /**
     * The name of the serialized form of the parameter
     * @member {string} Param#shortName
     */
    this.shortName = shortName;
    /**
     * Manipulate origValue when value is called
     * @member {function} Param#process
     */
    this.process = process;
  }

  /**
   * Set a (unprocessed) value for this parameter
   * @function Param#set
   * @param {*} origValue - the value of the parameter
   * @return {Param} self for chaining
   */
  return parameters_createClass(Param, [{
    key: "set",
    value: function set(origValue) {
      this.origValue = origValue;
      return this;
    }

    /**
     * Generate the serialized form of the parameter
     * @function Param#serialize
     * @return {string} the serialized form of the parameter
     */
  }, {
    key: "serialize",
    value: function serialize() {
      var val, valid;
      val = this.value();
      valid = isArray_default()(val) || isPlainObject_default()(val) || isString_default()(val) ? !isEmpty(val) : val != null;
      if (this.shortName != null && valid) {
        return "".concat(this.shortName, "_").concat(val);
      } else {
        return '';
      }
    }

    /**
     * Return the processed value of the parameter
     * @function Param#value
     */
  }, {
    key: "value",
    value: function value() {
      return this.process(this.origValue);
    }
  }], [{
    key: "norm_color",
    value: function norm_color(value) {
      return value != null ? value.replace(/^#/, 'rgb:') : void 0;
    }
  }, {
    key: "build_array",
    value: function build_array(arg) {
      if (arg == null) {
        return [];
      } else if (isArray_default()(arg)) {
        return arg;
      } else {
        return [arg];
      }
    }

    /**
    * Covert value to video codec string.
    *
    * If the parameter is an object,
    * @param {(string|Object)} param - the video codec as either a String or a Hash
    * @return {string} the video codec string in the format codec:profile:level:b_frames
    * @example
    * vc_[ :profile : [level : [b_frames]]]
    * or
      { codec: 'h264', profile: 'basic', level: '3.1', b_frames: false }
    * @ignore
     */
  }, {
    key: "process_video_params",
    value: function process_video_params(param) {
      var video;
      switch (param.constructor) {
        case Object:
          video = "";
          if ('codec' in param) {
            video = param.codec;
            if ('profile' in param) {
              video += ":" + param.profile;
              if ('level' in param) {
                video += ":" + param.level;
                if ('b_frames' in param && param.b_frames === false) {
                  video += ":bframes_no";
                }
              }
            }
          }
          return video;
        case String:
          return param;
        default:
          return null;
      }
    }
  }]);
}();
var parameters_ArrayParam = /*#__PURE__*/function (_Param) {
  /**
   * A parameter that represents an array.
   * @param {string} name - The name of the parameter in snake_case.
   * @param {string} shortName - The name of the serialized form of the parameter
   *                         If a value is not provided, the parameter will not be serialized.
   * @param {string} [sep='.'] - The separator to use when joining the array elements together
   * @param {function} [process=Util.identity ] - Manipulate origValue when value is called
   * @class ArrayParam
   * @extends Param
   * @ignore
   */
  function ArrayParam(name, shortName) {
    var _this;
    var sep = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : '.';
    var process = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : undefined;
    parameters_classCallCheck(this, ArrayParam);
    _this = parameters_callSuper(this, ArrayParam, [name, shortName, process]);
    _this.sep = sep;
    return _this;
  }
  parameters_inherits(ArrayParam, _Param);
  return parameters_createClass(ArrayParam, [{
    key: "serialize",
    value: function serialize() {
      if (this.shortName != null) {
        var arrayValue = this.value();
        if (isEmpty(arrayValue)) {
          return '';
        } else if (isString_default()(arrayValue)) {
          return "".concat(this.shortName, "_").concat(arrayValue);
        } else {
          var flat = arrayValue.map(function (t) {
            return isFunction_default()(t.serialize) ? t.serialize() : t;
          }).join(this.sep);
          return "".concat(this.shortName, "_").concat(flat);
        }
      } else {
        return '';
      }
    }
  }, {
    key: "value",
    value: function value() {
      var _this2 = this;
      if (isArray_default()(this.origValue)) {
        return this.origValue.map(function (v) {
          return _this2.process(v);
        });
      } else {
        return this.process(this.origValue);
      }
    }
  }, {
    key: "set",
    value: function set(origValue) {
      if (origValue == null || isArray_default()(origValue)) {
        return _get(parameters_getPrototypeOf(ArrayParam.prototype), "set", this).call(this, origValue);
      } else {
        return _get(parameters_getPrototypeOf(ArrayParam.prototype), "set", this).call(this, [origValue]);
      }
    }
  }]);
}(parameters_Param);
var parameters_TransformationParam = /*#__PURE__*/function (_Param2) {
  /**
   * A parameter that represents a transformation
   * @param {string} name - The name of the parameter in snake_case
   * @param {string} [shortName='t'] - The name of the serialized form of the parameter
   * @param {string} [sep='.'] - The separator to use when joining the array elements together
   * @param {function} [process=Util.identity ] - Manipulate origValue when value is called
   * @class TransformationParam
   * @extends Param
   * @ignore
   */
  function TransformationParam(name) {
    var _this3;
    var shortName = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "t";
    var sep = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : '.';
    var process = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : undefined;
    parameters_classCallCheck(this, TransformationParam);
    _this3 = parameters_callSuper(this, TransformationParam, [name, shortName, process]);
    _this3.sep = sep;
    return _this3;
  }

  /**
   * Generate string representations of the transformation.
   * @returns {*} Returns either the transformation as a string, or an array of string representations.
   */
  parameters_inherits(TransformationParam, _Param2);
  return parameters_createClass(TransformationParam, [{
    key: "serialize",
    value: function serialize() {
      var _this4 = this;
      var result = '';
      var val = this.value();
      if (isEmpty(val)) {
        return result;
      }

      // val is an array of strings so join them
      if (baseutil_allStrings(val)) {
        var joined = val.join(this.sep); // creates t1.t2.t3 in case multiple named transformations were configured
        if (!isEmpty(joined)) {
          // in case options.transformation was not set with an empty string (val != ['']);
          result = "".concat(this.shortName, "_").concat(joined);
        }
      } else {
        // Convert val to an array of strings
        result = val.map(function (t) {
          if (isString_default()(t) && !isEmpty(t)) {
            return "".concat(_this4.shortName, "_").concat(t);
          }
          if (isFunction_default()(t.serialize)) {
            return t.serialize();
          }
          if (isPlainObject_default()(t) && !isEmpty(t)) {
            return new src_transformation(t).serialize();
          }
          return undefined;
        }).filter(function (t) {
          return t;
        });
      }
      return result;
    }
  }, {
    key: "set",
    value: function set(origValue1) {
      this.origValue = origValue1;
      if (isArray_default()(this.origValue)) {
        return _get(parameters_getPrototypeOf(TransformationParam.prototype), "set", this).call(this, this.origValue);
      } else {
        return _get(parameters_getPrototypeOf(TransformationParam.prototype), "set", this).call(this, [this.origValue]);
      }
    }
  }]);
}(parameters_Param);
var number_pattern = "([0-9]*)\\.([0-9]+)|([0-9]+)";
var offset_any_pattern = "(" + number_pattern + ")([%pP])?";
var parameters_RangeParam = /*#__PURE__*/function (_Param3) {
  /**
   * A parameter that represents a range
   * @param {string} name - The name of the parameter in snake_case
   * @param {string} shortName - The name of the serialized form of the parameter
   *                         If a value is not provided, the parameter will not be serialized.
   * @param {function} [process=norm_range_value ] - Manipulate origValue when value is called
   * @class RangeParam
   * @extends Param
   * @ignore
   */
  function RangeParam(name, shortName) {
    var process = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : RangeParam.norm_range_value;
    parameters_classCallCheck(this, RangeParam);
    return parameters_callSuper(this, RangeParam, [name, shortName, process]);
  }
  parameters_inherits(RangeParam, _Param3);
  return parameters_createClass(RangeParam, null, [{
    key: "norm_range_value",
    value: function norm_range_value(value) {
      var offset = String(value).match(new RegExp('^' + offset_any_pattern + '$'));
      if (offset) {
        var modifier = offset[5] != null ? 'p' : '';
        value = (offset[1] || offset[4]) + modifier;
      }
      return expression.normalize(value);
    }
  }]);
}(parameters_Param);
var parameters_RawParam = /*#__PURE__*/function (_Param4) {
  function RawParam(name, shortName) {
    var process = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : identity_default.a;
    parameters_classCallCheck(this, RawParam);
    return parameters_callSuper(this, RawParam, [name, shortName, process]);
  }
  parameters_inherits(RawParam, _Param4);
  return parameters_createClass(RawParam, [{
    key: "serialize",
    value: function serialize() {
      return this.value();
    }
  }]);
}(parameters_Param);
var parameters_LayerParam = /*#__PURE__*/function (_Param5) {
  function LayerParam() {
    parameters_classCallCheck(this, LayerParam);
    return parameters_callSuper(this, LayerParam, arguments);
  }
  parameters_inherits(LayerParam, _Param5);
  return parameters_createClass(LayerParam, [{
    key: "value",
    value:
    // Parse layer options
    // @return [string] layer transformation string
    // @private
    function value() {
      if (this.origValue == null) {
        return '';
      }
      var result;
      if (this.origValue instanceof layer_layer) {
        result = this.origValue;
      } else if (isPlainObject_default()(this.origValue)) {
        var layerOptions = withCamelCaseKeys(this.origValue);
        if (layerOptions.resourceType === "text" || layerOptions.text != null) {
          result = new textlayer(layerOptions);
        } else if (layerOptions.resourceType === "subtitles") {
          result = new subtitleslayer(layerOptions);
        } else if (layerOptions.resourceType === "fetch" || layerOptions.url != null) {
          result = new fetchlayer(layerOptions);
        } else {
          result = new layer_layer(layerOptions);
        }
      } else if (isString_default()(this.origValue)) {
        if (/^fetch:.+/.test(this.origValue)) {
          result = new fetchlayer(this.origValue.substr(6));
        } else {
          result = this.origValue;
        }
      } else {
        result = '';
      }
      return result.toString();
    }
  }], [{
    key: "textStyle",
    value: function textStyle(layer) {
      return new textlayer(layer).textStyleIdentifier();
    }
  }]);
}(parameters_Param);
var parameters_ExpressionParam = /*#__PURE__*/function (_Param6) {
  function ExpressionParam() {
    parameters_classCallCheck(this, ExpressionParam);
    return parameters_callSuper(this, ExpressionParam, arguments);
  }
  parameters_inherits(ExpressionParam, _Param6);
  return parameters_createClass(ExpressionParam, [{
    key: "serialize",
    value: function serialize() {
      return expression.normalize(_get(parameters_getPrototypeOf(ExpressionParam.prototype), "serialize", this).call(this));
    }
  }]);
}(parameters_Param);

// CONCATENATED MODULE: ./src/transformation.js
function transformation_callSuper(t, o, e) { return o = transformation_getPrototypeOf(o), transformation_possibleConstructorReturn(t, transformation_isNativeReflectConstruct() ? Reflect.construct(o, e || [], transformation_getPrototypeOf(t).constructor) : o.apply(t, e)); }
function transformation_possibleConstructorReturn(self, call) { if (call && (transformation_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return transformation_assertThisInitialized(self); }
function transformation_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }
function transformation_isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (transformation_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function transformation_getPrototypeOf(o) { transformation_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return transformation_getPrototypeOf(o); }
function transformation_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) transformation_setPrototypeOf(subClass, superClass); }
function transformation_setPrototypeOf(o, p) { transformation_setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return transformation_setPrototypeOf(o, p); }
function transformation_slicedToArray(arr, i) { return transformation_arrayWithHoles(arr) || transformation_iterableToArrayLimit(arr, i) || transformation_unsupportedIterableToArray(arr, i) || transformation_nonIterableRest(); }
function transformation_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function transformation_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return transformation_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return transformation_arrayLikeToArray(o, minLen); }
function transformation_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i]; return arr2; }
function transformation_iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t["return"] && (u = t["return"](), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function transformation_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }
function transformation_typeof(o) { "@babel/helpers - typeof"; return transformation_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, transformation_typeof(o); }
function transformation_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function transformation_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, transformation_toPropertyKey(descriptor.key), descriptor); } }
function transformation_createClass(Constructor, protoProps, staticProps) { if (protoProps) transformation_defineProperties(Constructor.prototype, protoProps); if (staticProps) transformation_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function transformation_toPropertyKey(t) { var i = transformation_toPrimitive(t, "string"); return "symbol" == transformation_typeof(i) ? i : i + ""; }
function transformation_toPrimitive(t, r) { if ("object" != transformation_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != transformation_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }







/**
 * Assign key, value to target, when value is not null.<br>
 *   This function mutates the target!
 * @param {object} target the object to assign the values to
 * @param {object} sources one or more objects to get values from
 * @returns {object} the target after the assignment
 */
function assignNotNull(target) {
  for (var _len = arguments.length, sources = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
    sources[_key - 1] = arguments[_key];
  }
  sources.forEach(function (source) {
    Object.keys(source).forEach(function (key) {
      if (source[key] != null) {
        target[key] = source[key];
      }
    });
  });
  return target;
}

/**
 * TransformationBase
 * Depends on 'configuration', 'parameters','util'
 * @internal
 */
var transformation_TransformationBase = /*#__PURE__*/function () {
  /**
   * The base class for transformations.
   * Members of this class are documented as belonging to the {@link Transformation} class for convenience.
   * @class TransformationBase
   */
  function TransformationBase(options) {
    transformation_classCallCheck(this, TransformationBase);
    /** @private */
    /** @private */
    var parent, trans;
    parent = void 0;
    trans = {};
    /**
     * Return an options object that can be used to create an identical Transformation
     * @function Transformation#toOptions
     * @return {Object} Returns a plain object representing this transformation
     */
    this.toOptions = function (withChain) {
      var opt = {};
      if (withChain == null) {
        withChain = true;
      }
      Object.keys(trans).forEach(function (key) {
        return opt[key] = trans[key].origValue;
      });
      assignNotNull(opt, this.otherOptions);
      if (withChain && !isEmpty(this.chained)) {
        var list = this.chained.map(function (tr) {
          return tr.toOptions();
        });
        list.push(opt);
        opt = {};
        assignNotNull(opt, this.otherOptions);
        opt.transformation = list;
      }
      return opt;
    };
    /**
     * Set a parent for this object for chaining purposes.
     *
     * @function Transformation#setParent
     * @param {Object} object - the parent to be assigned to
     * @returns {Transformation} Returns this instance for chaining purposes.
     */
    this.setParent = function (object) {
      parent = object;
      if (object != null) {
        this.fromOptions(typeof object.toOptions === "function" ? object.toOptions() : void 0);
      }
      return this;
    };
    /**
     * Returns the parent of this object in the chain
     * @function Transformation#getParent
     * @protected
     * @return {Object} Returns the parent of this object if there is any
     */
    this.getParent = function () {
      return parent;
    };

    // Helper methods to create parameter methods
    // These methods are defined here because they access `trans` which is
    // a private member of `TransformationBase`

    /** @protected */
    this.param = function (value, name, abbr, defaultValue, process) {
      if (process == null) {
        if (isFunction_default()(defaultValue)) {
          process = defaultValue;
        } else {
          process = identity_default.a;
        }
      }
      trans[name] = new parameters_Param(name, abbr, process).set(value);
      return this;
    };
    /** @protected */
    this.rawParam = function (value, name, abbr, defaultValue, process) {
      process = lastArgCallback(arguments);
      trans[name] = new parameters_RawParam(name, abbr, process).set(value);
      return this;
    };
    /** @protected */
    this.rangeParam = function (value, name, abbr, defaultValue, process) {
      process = lastArgCallback(arguments);
      trans[name] = new parameters_RangeParam(name, abbr, process).set(value);
      return this;
    };
    /** @protected */
    this.arrayParam = function (value, name, abbr) {
      var sep = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : ":";
      var defaultValue = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : [];
      var process = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : undefined;
      process = lastArgCallback(arguments);
      trans[name] = new parameters_ArrayParam(name, abbr, sep, process).set(value);
      return this;
    };
    /** @protected */
    this.transformationParam = function (value, name, abbr) {
      var sep = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : ".";
      var defaultValue = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : undefined;
      var process = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : undefined;
      process = lastArgCallback(arguments);
      trans[name] = new parameters_TransformationParam(name, abbr, sep, process).set(value);
      return this;
    };
    this.layerParam = function (value, name, abbr) {
      trans[name] = new parameters_LayerParam(name, abbr).set(value);
      return this;
    };

    // End Helper methods

    /**
     * Get the value associated with the given name.
     * @function Transformation#getValue
     * @param {string} name - the name of the parameter
     * @return {*} the processed value associated with the given name
     * @description Use {@link get}.origValue for the value originally provided for the parameter
     */
    this.getValue = function (name) {
      var value = trans[name] && trans[name].value();
      return value != null ? value : this.otherOptions[name];
    };
    /**
     * Get the parameter object for the given parameter name
     * @function Transformation#get
     * @param {string} name the name of the transformation parameter
     * @returns {Param} the param object for the given name, or undefined
     */
    this.get = function (name) {
      return trans[name];
    };
    /**
     * Remove a transformation option from the transformation.
     * @function Transformation#remove
     * @param {string} name - the name of the option to remove
     * @return {*} Returns the option that was removed or null if no option by that name was found. The type of the
     *              returned value depends on the value.
     */
    this.remove = function (name) {
      var temp;
      switch (false) {
        case trans[name] == null:
          temp = trans[name];
          delete trans[name];
          return temp.origValue;
        case this.otherOptions[name] == null:
          temp = this.otherOptions[name];
          delete this.otherOptions[name];
          return temp;
        default:
          return null;
      }
    };
    /**
     * Return an array of all the keys (option names) in the transformation.
     * @return {Array<string>} the keys in snakeCase format
     */
    this.keys = function () {
      var key;
      return function () {
        var results;
        results = [];
        for (key in trans) {
          if (key != null) {
            results.push(key.match(VAR_NAME_RE) ? key : snakeCase(key));
          }
        }
        return results;
      }().sort();
    };
    /**
     * Returns a plain object representation of the transformation. Values are processed.
     * @function Transformation#toPlainObject
     * @return {Object} the transformation options as plain object
     */
    this.toPlainObject = function () {
      var hash, key, list;
      hash = {};
      for (key in trans) {
        hash[key] = trans[key].value();
        if (isPlainObject_default()(hash[key])) {
          hash[key] = cloneDeep_default()(hash[key]);
        }
      }
      if (!isEmpty(this.chained)) {
        list = this.chained.map(function (tr) {
          return tr.toPlainObject();
        });
        list.push(hash);
        hash = {
          transformation: list
        };
      }
      return hash;
    };
    /**
     * Complete the current transformation and chain to a new one.
     * In the URL, transformations are chained together by slashes.
     * @function Transformation#chain
     * @return {Transformation} Returns this transformation for chaining
     * @example
     * var tr = cloudinary.Transformation.new();
     * tr.width(10).crop('fit').chain().angle(15).serialize()
     * // produces "c_fit,w_10/a_15"
     */
    this.chain = function () {
      var names, tr;
      names = Object.getOwnPropertyNames(trans);
      if (names.length !== 0) {
        tr = new this.constructor(this.toOptions(false));
        this.resetTransformations();
        this.chained.push(tr);
      }
      return this;
    };
    this.resetTransformations = function () {
      trans = {};
      return this;
    };
    this.otherOptions = {};
    this.chained = [];
    this.fromOptions(options);
  }

  /**
   * Merge the provided options with own's options
   * @param {Object} [options={}] key-value list of options
   * @returns {Transformation} Returns this instance for chaining
   */
  return transformation_createClass(TransformationBase, [{
    key: "fromOptions",
    value: function fromOptions() {
      var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      if (options instanceof TransformationBase) {
        this.fromTransformation(options);
      } else {
        if (isString_default()(options) || isArray_default()(options)) {
          options = {
            transformation: options
          };
        }
        options = cloneDeep_default()(options, function (value) {
          if (value instanceof TransformationBase || value instanceof Layer) {
            return new value.clone();
          }
        });
        // Handling of "if" statements precedes other options as it creates a chained transformation
        if (options["if"]) {
          this.set("if", options["if"]);
          delete options["if"];
        }
        for (var key in options) {
          var opt = options[key];
          if (opt != null) {
            if (key.match(VAR_NAME_RE)) {
              if (key !== '$attr') {
                this.set('variable', key, opt);
              }
            } else {
              this.set(key, opt);
            }
          }
        }
      }
      return this;
    }
  }, {
    key: "fromTransformation",
    value: function fromTransformation(other) {
      var _this = this;
      if (other instanceof TransformationBase) {
        other.keys().forEach(function (key) {
          return _this.set(key, other.get(key).origValue);
        });
      }
      return this;
    }

    /**
     * Set a parameter.
     * The parameter name `key` is converted to
     * @param {string} key - the name of the parameter
     * @param {*} values - the value of the parameter
     * @returns {Transformation} Returns this instance for chaining
     */
  }, {
    key: "set",
    value: function set(key) {
      var camelKey;
      camelKey = camelCase(key);
      for (var _len2 = arguments.length, values = new Array(_len2 > 1 ? _len2 - 1 : 0), _key2 = 1; _key2 < _len2; _key2++) {
        values[_key2 - 1] = arguments[_key2];
      }
      if (includes_default()(transformation_Transformation.methods, camelKey)) {
        this[camelKey].apply(this, values);
      } else {
        this.otherOptions[key] = values[0];
      }
      return this;
    }
  }, {
    key: "hasLayer",
    value: function hasLayer() {
      return this.getValue("overlay") || this.getValue("underlay");
    }

    /**
     * Generate a string representation of the transformation.
     * @function Transformation#serialize
     * @return {string} Returns the transformation as a string
     */
  }, {
    key: "serialize",
    value: function serialize() {
      var ifParam, j, len, paramList, ref, ref1, ref2, ref3, ref4, resultArray, t, transformationList, transformationString, transformations, value, variables, vars;
      resultArray = this.chained.map(function (tr) {
        return tr.serialize();
      });
      paramList = this.keys();
      transformations = (ref = this.get("transformation")) != null ? ref.serialize() : void 0;
      ifParam = (ref1 = this.get("if")) != null ? ref1.serialize() : void 0;
      variables = processVar((ref2 = this.get("variables")) != null ? ref2.value() : void 0);
      paramList = difference_default()(paramList, ["transformation", "if", "variables"]);
      vars = [];
      transformationList = [];
      for (j = 0, len = paramList.length; j < len; j++) {
        t = paramList[j];
        if (t.match(VAR_NAME_RE)) {
          vars.push(t + "_" + expression.normalize((ref3 = this.get(t)) != null ? ref3.value() : void 0));
        } else {
          transformationList.push((ref4 = this.get(t)) != null ? ref4.serialize() : void 0);
        }
      }
      switch (false) {
        case !isString_default()(transformations):
          transformationList.push(transformations);
          break;
        case !isArray_default()(transformations):
          resultArray = resultArray.concat(transformations);
      }
      transformationList = function () {
        var k, len1, results;
        results = [];
        for (k = 0, len1 = transformationList.length; k < len1; k++) {
          value = transformationList[k];
          if (isArray_default()(value) && !isEmpty(value) || !isArray_default()(value) && value) {
            results.push(value);
          }
        }
        return results;
      }();
      transformationList = vars.sort().concat(variables).concat(transformationList.sort());
      if (ifParam === "if_end") {
        transformationList.push(ifParam);
      } else if (!isEmpty(ifParam)) {
        transformationList.unshift(ifParam);
      }
      transformationString = compact_default()(transformationList).join(this.param_separator);
      if (!isEmpty(transformationString)) {
        resultArray.push(transformationString);
      }
      return compact_default()(resultArray).join(this.trans_separator);
    }

    /**
     * Provide a list of all the valid transformation option names
     * @function Transformation#listNames
     * @private
     * @return {Array<string>} a array of all the valid option names
     */
  }, {
    key: "toHtmlAttributes",
    value:
    /**
     * Returns the attributes for an HTML tag.
     * @function Cloudinary.toHtmlAttributes
     * @return PlainObject
     */
    function toHtmlAttributes() {
      var _this2 = this;
      var attrName, height, options, ref2, ref3, value, width;
      options = {};
      var snakeCaseKey;
      Object.keys(this.otherOptions).forEach(function (key) {
        value = _this2.otherOptions[key];
        snakeCaseKey = snakeCase(key);
        if (!includes_default()(transformation_Transformation.PARAM_NAMES, snakeCaseKey) && !includes_default()(URL_KEYS, snakeCaseKey)) {
          attrName = /^html_/.test(key) ? key.slice(5) : key;
          options[attrName] = value;
        }
      });
      // convert all "html_key" to "key" with the same value
      this.keys().forEach(function (key) {
        if (/^html_/.test(key)) {
          options[camelCase(key.slice(5))] = _this2.getValue(key);
        }
      });
      if (!(this.hasLayer() || this.getValue("angle") || includes_default()(["fit", "limit", "lfill"], this.getValue("crop")))) {
        width = (ref2 = this.get("width")) != null ? ref2.origValue : void 0;
        height = (ref3 = this.get("height")) != null ? ref3.origValue : void 0;
        if (parseFloat(width) >= 1.0) {
          if (options.width == null) {
            options.width = width;
          }
        }
        if (parseFloat(height) >= 1.0) {
          if (options.height == null) {
            options.height = height;
          }
        }
      }
      return options;
    }
  }, {
    key: "toHtml",
    value:
    /**
     * Delegate to the parent (up the call chain) to produce HTML
     * @function Transformation#toHtml
     * @return {string} HTML representation of the parent if possible.
     * @example
     * tag = cloudinary.ImageTag.new("sample", {cloud_name: "demo"})
     * // ImageTag {name: "img", publicId: "sample"}
     * tag.toHtml()
     * // <img src="http://res.cloudinary.com/demo/image/upload/sample">
     * tag.transformation().crop("fit").width(300).toHtml()
     * // <img src="http://res.cloudinary.com/demo/image/upload/c_fit,w_300/sample">
     */
    function toHtml() {
      var ref;
      return (ref = this.getParent()) != null ? typeof ref.toHtml === "function" ? ref.toHtml() : void 0 : void 0;
    }
  }, {
    key: "toString",
    value: function toString() {
      return this.serialize();
    }
  }, {
    key: "clone",
    value: function clone() {
      return new this.constructor(this.toOptions(true));
    }
  }], [{
    key: "listNames",
    value: function listNames() {
      return transformation_Transformation.methods;
    }
  }, {
    key: "isValidParamName",
    value: function isValidParamName(name) {
      return transformation_Transformation.methods.indexOf(camelCase(name)) >= 0;
    }
  }]);
}();
var VAR_NAME_RE = /^\$[a-zA-Z0-9]+$/;
transformation_TransformationBase.prototype.trans_separator = '/';
transformation_TransformationBase.prototype.param_separator = ',';
function lastArgCallback(args) {
  var callback;
  callback = args != null ? args[args.length - 1] : void 0;
  if (isFunction_default()(callback)) {
    return callback;
  } else {
    return void 0;
  }
}
function processVar(varArray) {
  var j, len, name, results, v;
  if (isArray_default()(varArray)) {
    results = [];
    for (j = 0, len = varArray.length; j < len; j++) {
      var _varArray$j = transformation_slicedToArray(varArray[j], 2);
      name = _varArray$j[0];
      v = _varArray$j[1];
      results.push("".concat(name, "_").concat(expression.normalize(v)));
    }
    return results;
  } else {
    return varArray;
  }
}
function processCustomFunction(_ref) {
  var function_type = _ref.function_type,
    source = _ref.source;
  if (function_type === 'remote') {
    return [function_type, btoa(source)].join(":");
  } else if (function_type === 'wasm') {
    return [function_type, source].join(":");
  }
}

/**
 * Transformation Class methods.
 * This is a list of the parameters defined in Transformation.
 * Values are camelCased.
 * @const Transformation.methods
 * @private
 * @ignore
 * @type {Array<string>}
 */
/**
 * Parameters that are filtered out before passing the options to an HTML tag.
 *
 * The list of parameters is a combination of `Transformation::methods` and `Configuration::CONFIG_PARAMS`
 * @const {Array<string>} Transformation.PARAM_NAMES
 * @private
 * @ignore
 * @see toHtmlAttributes
 */
var transformation_Transformation = /*#__PURE__*/function (_TransformationBase) {
  /**
   * Represents a single transformation.
   * @class Transformation
   * @example
   * t = new cloudinary.Transformation();
   * t.angle(20).crop("scale").width("auto");
   *
   * // or
   *
   * t = new cloudinary.Transformation( {angle: 20, crop: "scale", width: "auto"});
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference"
   *  target="_blank">Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/video_transformation_reference"
   *  target="_blank">Available video transformations</a>
   */
  function Transformation(options) {
    transformation_classCallCheck(this, Transformation);
    return transformation_callSuper(this, Transformation, [options]);
  }

  /**
   * Convenience constructor
   * @param {Object} options
   * @return {Transformation}
   * @example cl = cloudinary.Transformation.new( {angle: 20, crop: "scale", width: "auto"})
   */
  transformation_inherits(Transformation, _TransformationBase);
  return transformation_createClass(Transformation, [{
    key: "angle",
    value:
    /*
      Transformation Parameters
    */
    function angle(value) {
      return this.arrayParam(value, "angle", "a", ".", expression.normalize);
    }
  }, {
    key: "audioCodec",
    value: function audioCodec(value) {
      return this.param(value, "audio_codec", "ac");
    }
  }, {
    key: "audioFrequency",
    value: function audioFrequency(value) {
      return this.param(value, "audio_frequency", "af");
    }
  }, {
    key: "aspectRatio",
    value: function aspectRatio(value) {
      return this.param(value, "aspect_ratio", "ar", expression.normalize);
    }
  }, {
    key: "background",
    value: function background(value) {
      return this.param(value, "background", "b", parameters_Param.norm_color);
    }
  }, {
    key: "bitRate",
    value: function bitRate(value) {
      return this.param(value, "bit_rate", "br");
    }
  }, {
    key: "border",
    value: function border(value) {
      return this.param(value, "border", "bo", function (border) {
        if (isPlainObject_default()(border)) {
          border = assign_default()({}, {
            color: "black",
            width: 2
          }, border);
          return "".concat(border.width, "px_solid_").concat(parameters_Param.norm_color(border.color));
        } else {
          return border;
        }
      });
    }
  }, {
    key: "color",
    value: function color(value) {
      return this.param(value, "color", "co", parameters_Param.norm_color);
    }
  }, {
    key: "colorSpace",
    value: function colorSpace(value) {
      return this.param(value, "color_space", "cs");
    }
  }, {
    key: "crop",
    value: function crop(value) {
      return this.param(value, "crop", "c");
    }
  }, {
    key: "customFunction",
    value: function customFunction(value) {
      return this.param(value, "custom_function", "fn", function () {
        return processCustomFunction(value);
      });
    }
  }, {
    key: "customPreFunction",
    value: function customPreFunction(value) {
      if (this.get('custom_function')) {
        return;
      }
      return this.rawParam(value, "custom_function", "", function () {
        value = processCustomFunction(value);
        return value ? "fn_pre:".concat(value) : value;
      });
    }
  }, {
    key: "defaultImage",
    value: function defaultImage(value) {
      return this.param(value, "default_image", "d");
    }
  }, {
    key: "delay",
    value: function delay(value) {
      return this.param(value, "delay", "dl");
    }
  }, {
    key: "density",
    value: function density(value) {
      return this.param(value, "density", "dn");
    }
  }, {
    key: "duration",
    value: function duration(value) {
      return this.rangeParam(value, "duration", "du");
    }
  }, {
    key: "dpr",
    value: function dpr(value) {
      return this.param(value, "dpr", "dpr", function (dpr) {
        dpr = dpr.toString();
        if (dpr != null ? dpr.match(/^\d+$/) : void 0) {
          return dpr + ".0";
        } else {
          return expression.normalize(dpr);
        }
      });
    }
  }, {
    key: "effect",
    value: function effect(value) {
      return this.arrayParam(value, "effect", "e", ":", expression.normalize);
    }
  }, {
    key: "else",
    value: function _else() {
      return this["if"]('else');
    }
  }, {
    key: "endIf",
    value: function endIf() {
      return this["if"]('end');
    }
  }, {
    key: "endOffset",
    value: function endOffset(value) {
      return this.rangeParam(value, "end_offset", "eo");
    }
  }, {
    key: "fallbackContent",
    value: function fallbackContent(value) {
      return this.param(value, "fallback_content");
    }
  }, {
    key: "fetchFormat",
    value: function fetchFormat(value) {
      return this.param(value, "fetch_format", "f");
    }
  }, {
    key: "format",
    value: function format(value) {
      return this.param(value, "format");
    }
  }, {
    key: "flags",
    value: function flags(value) {
      return this.arrayParam(value, "flags", "fl", ".");
    }
  }, {
    key: "gravity",
    value: function gravity(value) {
      return this.param(value, "gravity", "g");
    }
  }, {
    key: "fps",
    value: function fps(value) {
      return this.param(value, "fps", "fps", function (fps) {
        if (isString_default()(fps)) {
          return fps;
        } else if (isArray_default()(fps)) {
          return fps.join("-");
        } else {
          return fps;
        }
      });
    }
  }, {
    key: "height",
    value: function height(value) {
      var _this3 = this;
      return this.param(value, "height", "h", function () {
        if (_this3.getValue("crop") || _this3.getValue("overlay") || _this3.getValue("underlay")) {
          return expression.normalize(value);
        } else {
          return null;
        }
      });
    }
  }, {
    key: "htmlHeight",
    value: function htmlHeight(value) {
      return this.param(value, "html_height");
    }
  }, {
    key: "htmlWidth",
    value: function htmlWidth(value) {
      return this.param(value, "html_width");
    }
  }, {
    key: "if",
    value: function _if() {
      var value = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : "";
      var i, ifVal, j, ref, trIf, trRest;
      switch (value) {
        case "else":
          this.chain();
          return this.param(value, "if", "if");
        case "end":
          this.chain();
          for (i = j = ref = this.chained.length - 1; j >= 0; i = j += -1) {
            ifVal = this.chained[i].getValue("if");
            if (ifVal === "end") {
              break;
            } else if (ifVal != null) {
              trIf = Transformation["new"]()["if"](ifVal);
              this.chained[i].remove("if");
              trRest = this.chained[i];
              this.chained[i] = Transformation["new"]().transformation([trIf, trRest]);
              if (ifVal !== "else") {
                break;
              }
            }
          }
          return this.param(value, "if", "if");
        case "":
          return condition["new"]().setParent(this);
        default:
          return this.param(value, "if", "if", function (value) {
            return condition["new"](value).toString();
          });
      }
    }
  }, {
    key: "keyframeInterval",
    value: function keyframeInterval(value) {
      return this.param(value, "keyframe_interval", "ki");
    }
  }, {
    key: "ocr",
    value: function ocr(value) {
      return this.param(value, "ocr", "ocr");
    }
  }, {
    key: "offset",
    value: function offset(value) {
      var end_o, start_o;
      var _ref2 = isFunction_default()(value != null ? value.split : void 0) ? value.split('..') : isArray_default()(value) ? value : [null, null];
      var _ref3 = transformation_slicedToArray(_ref2, 2);
      start_o = _ref3[0];
      end_o = _ref3[1];
      if (start_o != null) {
        this.startOffset(start_o);
      }
      if (end_o != null) {
        return this.endOffset(end_o);
      }
    }
  }, {
    key: "opacity",
    value: function opacity(value) {
      return this.param(value, "opacity", "o", expression.normalize);
    }
  }, {
    key: "overlay",
    value: function overlay(value) {
      return this.layerParam(value, "overlay", "l");
    }
  }, {
    key: "page",
    value: function page(value) {
      return this.param(value, "page", "pg");
    }
  }, {
    key: "poster",
    value: function poster(value) {
      return this.param(value, "poster");
    }
  }, {
    key: "prefix",
    value: function prefix(value) {
      return this.param(value, "prefix", "p");
    }
  }, {
    key: "quality",
    value: function quality(value) {
      return this.param(value, "quality", "q", expression.normalize);
    }
  }, {
    key: "radius",
    value: function radius(value) {
      return this.arrayParam(value, "radius", "r", ":", expression.normalize);
    }
  }, {
    key: "rawTransformation",
    value: function rawTransformation(value) {
      return this.rawParam(value, "raw_transformation");
    }
  }, {
    key: "size",
    value: function size(value) {
      var height, width;
      if (isFunction_default()(value != null ? value.split : void 0)) {
        var _value$split = value.split('x');
        var _value$split2 = transformation_slicedToArray(_value$split, 2);
        width = _value$split2[0];
        height = _value$split2[1];
        this.width(width);
        return this.height(height);
      }
    }
  }, {
    key: "sourceTypes",
    value: function sourceTypes(value) {
      return this.param(value, "source_types");
    }
  }, {
    key: "sourceTransformation",
    value: function sourceTransformation(value) {
      return this.param(value, "source_transformation");
    }
  }, {
    key: "startOffset",
    value: function startOffset(value) {
      return this.rangeParam(value, "start_offset", "so");
    }
  }, {
    key: "streamingProfile",
    value: function streamingProfile(value) {
      return this.param(value, "streaming_profile", "sp");
    }
  }, {
    key: "transformation",
    value: function transformation(value) {
      return this.transformationParam(value, "transformation", "t");
    }
  }, {
    key: "underlay",
    value: function underlay(value) {
      return this.layerParam(value, "underlay", "u");
    }
  }, {
    key: "variable",
    value: function variable(name, value) {
      return this.param(value, name, name);
    }
  }, {
    key: "variables",
    value: function variables(values) {
      return this.arrayParam(values, "variables");
    }
  }, {
    key: "videoCodec",
    value: function videoCodec(value) {
      return this.param(value, "video_codec", "vc", parameters_Param.process_video_params);
    }
  }, {
    key: "videoSampling",
    value: function videoSampling(value) {
      return this.param(value, "video_sampling", "vs");
    }
  }, {
    key: "width",
    value: function width(value) {
      var _this4 = this;
      return this.param(value, "width", "w", function () {
        if (_this4.getValue("crop") || _this4.getValue("overlay") || _this4.getValue("underlay")) {
          return expression.normalize(value);
        } else {
          return null;
        }
      });
    }
  }, {
    key: "x",
    value: function x(value) {
      return this.param(value, "x", "x", expression.normalize);
    }
  }, {
    key: "y",
    value: function y(value) {
      return this.param(value, "y", "y", expression.normalize);
    }
  }, {
    key: "zoom",
    value: function zoom(value) {
      return this.param(value, "zoom", "z", expression.normalize);
    }
  }], [{
    key: "new",
    value: function _new(options) {
      return new Transformation(options);
    }
  }]);
}(transformation_TransformationBase);
/**
 * Transformation Class methods.
 * This is a list of the parameters defined in Transformation.
 * Values are camelCased.
 */
transformation_Transformation.methods = ["angle", "audioCodec", "audioFrequency", "aspectRatio", "background", "bitRate", "border", "color", "colorSpace", "crop", "customFunction", "customPreFunction", "defaultImage", "delay", "density", "duration", "dpr", "effect", "else", "endIf", "endOffset", "fallbackContent", "fetchFormat", "format", "flags", "gravity", "fps", "height", "htmlHeight", "htmlWidth", "if", "keyframeInterval", "ocr", "offset", "opacity", "overlay", "page", "poster", "prefix", "quality", "radius", "rawTransformation", "size", "sourceTypes", "sourceTransformation", "startOffset", "streamingProfile", "transformation", "underlay", "variable", "variables", "videoCodec", "videoSampling", "width", "x", "y", "zoom"];

/**
 * Parameters that are filtered out before passing the options to an HTML tag.
 *
 * The list of parameters is a combination of `Transformation::methods` and `Configuration::CONFIG_PARAMS`
 */
transformation_Transformation.PARAM_NAMES = transformation_Transformation.methods.map(snakeCase).concat(src_configuration.CONFIG_PARAMS);
/* harmony default export */ var src_transformation = (transformation_Transformation);
// CONCATENATED MODULE: ./src/tags/htmltag.js
function htmltag_typeof(o) { "@babel/helpers - typeof"; return htmltag_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, htmltag_typeof(o); }
function htmltag_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function htmltag_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, htmltag_toPropertyKey(descriptor.key), descriptor); } }
function htmltag_createClass(Constructor, protoProps, staticProps) { if (protoProps) htmltag_defineProperties(Constructor.prototype, protoProps); if (staticProps) htmltag_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function htmltag_toPropertyKey(t) { var i = htmltag_toPrimitive(t, "string"); return "symbol" == htmltag_typeof(i) ? i : i + ""; }
function htmltag_toPrimitive(t, r) { if ("object" != htmltag_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != htmltag_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
/**
 * Generic HTML tag
 * Depends on 'transformation', 'util'
 */




/**
 * Represents an HTML (DOM) tag
 * @constructor HtmlTag
 * @param {string} name - the name of the tag
 * @param {string} [publicId]
 * @param {Object} options
 * @example tag = new HtmlTag( 'div', { 'width': 10})
 */
var htmltag_HtmlTag = /*#__PURE__*/function () {
  function HtmlTag(name, publicId, options) {
    htmltag_classCallCheck(this, HtmlTag);
    var transformation;
    this.name = name;
    this.publicId = publicId;
    if (options == null) {
      if (isPlainObject_default()(publicId)) {
        options = publicId;
        this.publicId = void 0;
      } else {
        options = {};
      }
    }
    transformation = new src_transformation(options);
    transformation.setParent(this);
    this.transformation = function () {
      return transformation;
    };
  }

  /**
   * Convenience constructor
   * Creates a new instance of an HTML (DOM) tag
   * @function HtmlTag.new
   * @param {string} name - the name of the tag
   * @param {string} [publicId]
   * @param {Object} options
   * @return {HtmlTag}
   * @example tag = HtmlTag.new( 'div', { 'width': 10})
   */
  return htmltag_createClass(HtmlTag, [{
    key: "htmlAttrs",
    value:
    /**
     * combine key and value from the `attr` to generate an HTML tag attributes string.
     * `Transformation::toHtmlTagOptions` is used to filter out transformation and configuration keys.
     * @protected
     * @param {Object} attrs
     * @return {string} the attributes in the format `'key1="value1" key2="value2"'`
     * @ignore
     */
    function htmlAttrs(attrs) {
      var key, pairs, value;
      return pairs = function () {
        var results;
        results = [];
        for (key in attrs) {
          value = escapeQuotes(attrs[key]);
          if (value) {
            results.push(htmltag_toAttribute(key, value));
          }
        }
        return results;
      }().sort().join(' ');
    }

    /**
     * Get all options related to this tag.
     * @function HtmlTag#getOptions
     * @returns {Object} the options
     *
     */
  }, {
    key: "getOptions",
    value: function getOptions() {
      return this.transformation().toOptions();
    }

    /**
     * Get the value of option `name`
     * @function HtmlTag#getOption
     * @param {string} name - the name of the option
     * @returns {*} Returns the value of the option
     *
     */
  }, {
    key: "getOption",
    value: function getOption(name) {
      return this.transformation().getValue(name);
    }

    /**
     * Get the attributes of the tag.
     * @function HtmlTag#attributes
     * @returns {Object} attributes
     */
  }, {
    key: "attributes",
    value: function attributes() {
      // The attributes are be computed from the options every time this method is invoked.
      var htmlAttributes = this.transformation().toHtmlAttributes();
      Object.keys(htmlAttributes).forEach(function (key) {
        if (isPlainObject_default()(htmlAttributes[key])) {
          delete htmlAttributes[key];
        }
      });
      if (htmlAttributes.attributes) {
        // Currently HTML attributes are defined both at the top level and under 'attributes'
        merge_default()(htmlAttributes, htmlAttributes.attributes);
        delete htmlAttributes.attributes;
      }
      return htmlAttributes;
    }

    /**
     * Set a tag attribute named `name` to `value`
     * @function HtmlTag#setAttr
     * @param {string} name - the name of the attribute
     * @param {string} value - the value of the attribute
     */
  }, {
    key: "setAttr",
    value: function setAttr(name, value) {
      this.transformation().set("html_".concat(name), value);
      return this;
    }

    /**
     * Get the value of the tag attribute `name`
     * @function HtmlTag#getAttr
     * @param {string} name - the name of the attribute
     * @returns {*}
     */
  }, {
    key: "getAttr",
    value: function getAttr(name) {
      return this.attributes()["html_".concat(name)] || this.attributes()[name];
    }

    /**
     * Remove the tag attributed named `name`
     * @function HtmlTag#removeAttr
     * @param {string} name - the name of the attribute
     * @returns {*}
     */
  }, {
    key: "removeAttr",
    value: function removeAttr(name) {
      var ref;
      return (ref = this.transformation().remove("html_".concat(name))) != null ? ref : this.transformation().remove(name);
    }

    /**
     * @function HtmlTag#content
     * @protected
     * @ignore
     */
  }, {
    key: "content",
    value: function content() {
      return "";
    }

    /**
     * @function HtmlTag#openTag
     * @protected
     * @ignore
     */
  }, {
    key: "openTag",
    value: function openTag() {
      var tag = "<" + this.name;
      var htmlAttrs = this.htmlAttrs(this.attributes());
      if (htmlAttrs && htmlAttrs.length > 0) {
        tag += " " + htmlAttrs;
      }
      return tag + ">";
    }

    /**
     * @function HtmlTag#closeTag
     * @protected
     * @ignore
     */
  }, {
    key: "closeTag",
    value: function closeTag() {
      return "</".concat(this.name, ">");
    }

    /**
     * Generates an HTML representation of the tag.
     * @function HtmlTag#toHtml
     * @returns {string} Returns HTML in string format
     */
  }, {
    key: "toHtml",
    value: function toHtml() {
      return this.openTag() + this.content() + this.closeTag();
    }

    /**
     * Creates a DOM object representing the tag.
     * @function HtmlTag#toDOM
     * @returns {Element}
     */
  }, {
    key: "toDOM",
    value: function toDOM() {
      var element, name, ref, value;
      if (!isFunction_default()(typeof document !== "undefined" && document !== null ? document.createElement : void 0)) {
        throw "Can't create DOM if document is not present!";
      }
      element = document.createElement(this.name);
      ref = this.attributes();
      for (name in ref) {
        value = ref[name];
        element.setAttribute(name, value);
      }
      return element;
    }
  }], [{
    key: "new",
    value: function _new(name, publicId, options) {
      return new this(name, publicId, options);
    }
  }, {
    key: "isResponsive",
    value: function isResponsive(tag, responsiveClass) {
      var dataSrc;
      dataSrc = lodash_getData(tag, 'src-cache') || lodash_getData(tag, 'src');
      return lodash_hasClass(tag, responsiveClass) && /\bw_auto\b/.exec(dataSrc);
    }
  }]);
}();
;

/**
 * Represent the given key and value as an HTML attribute.
 * @function toAttribute
 * @protected
 * @param {string} key - attribute name
 * @param {*|boolean} value - the value of the attribute. If the value is boolean `true`, return the key only.
 * @returns {string} the attribute
 *
 */
function htmltag_toAttribute(key, value) {
  if (!value) {
    return void 0;
  } else if (value === true) {
    return key;
  } else {
    return "".concat(key, "=\"").concat(value, "\"");
  }
}

/**
 * If given value is a string, replaces quotes with character entities (&#34;, &#39;)
 * @param value - value to change
 * @returns {*} changed value
 */
function escapeQuotes(value) {
  return isString_default()(value) ? value.replace('"', '&#34;').replace("'", '&#39;') : value;
}
/* harmony default export */ var htmltag = (htmltag_HtmlTag);
// CONCATENATED MODULE: ./src/url.js
var _excluded = ["placeholder", "accessibility"];
function _objectWithoutProperties(source, excluded) { if (source == null) return {}; var target = _objectWithoutPropertiesLoose(source, excluded); var key, i; if (Object.getOwnPropertySymbols) { var sourceSymbolKeys = Object.getOwnPropertySymbols(source); for (i = 0; i < sourceSymbolKeys.length; i++) { key = sourceSymbolKeys[i]; if (excluded.indexOf(key) >= 0) continue; if (!Object.prototype.propertyIsEnumerable.call(source, key)) continue; target[key] = source[key]; } } return target; }
function _objectWithoutPropertiesLoose(source, excluded) { if (source == null) return {}; var target = {}; var sourceKeys = Object.keys(source); var key, i; for (i = 0; i < sourceKeys.length; i++) { key = sourceKeys[i]; if (excluded.indexOf(key) >= 0) continue; target[key] = source[key]; } return target; }







/**
 * Adds protocol, host, pathname prefixes to given string
 * @param str
 * @returns {string}
 */
function makeUrl(str) {
  var prefix = document.location.protocol + '//' + document.location.host;
  if (str[0] === '?') {
    prefix += document.location.pathname;
  } else if (str[0] !== '/') {
    prefix += document.location.pathname.replace(/\/[^\/]*$/, '/');
  }
  return prefix + str;
}

/**
 * Check is given string is a url
 * @param str
 * @returns {boolean}
 */
function isUrl(str) {
  return str ? !!str.match(/^https?:\//) : false;
}

// Produce a number between 1 and 5 to be used for cdn sub domains designation
function cdnSubdomainNumber(publicId) {
  return src_crc32(publicId) % 5 + 1;
}

/**
 * Removes signature from options and returns the signature
 * Makes sure signature is empty or of this format: s--signature--
 * @param {object} options
 * @returns {string} the formatted signature
 */
function handleSignature(options) {
  var signature = options.signature;
  var isFormatted = !signature || signature.indexOf('s--') === 0 && signature.substr(-2) === '--';
  delete options.signature;
  return isFormatted ? signature : "s--".concat(signature, "--");
}

/**
 * Create the URL prefix for Cloudinary resources.
 * @param {string} publicId the resource public ID
 * @param {object} options additional options
 * @param {string} options.cloud_name - the cloud name.
 * @param {boolean} [options.cdn_subdomain=false] - Whether to automatically build URLs with
 *  multiple CDN sub-domains.
 * @param {string} [options.private_cdn] - Boolean (default: false). Should be set to true for Advanced plan's users
 *  that have a private CDN distribution.
 * @param {string} [options.protocol="http://"] - the URI protocol to use. If options.secure is true,
 *  the value is overridden to "https://"
 * @param {string} [options.secure_distribution] - The domain name of the CDN distribution to use for building HTTPS URLs.
 *  Relevant only for Advanced plan's users that have a private CDN distribution.
 * @param {string} [options.cname] - Custom domain name to use for building HTTP URLs.
 *  Relevant only for Advanced plan's users that have a private CDN distribution and a custom CNAME.
 * @param {boolean} [options.secure_cdn_subdomain=true] - When options.secure is true and this parameter is false,
 *  the subdomain is set to "res".
 * @param {boolean} [options.secure=false] - Force HTTPS URLs of images even if embedded in non-secure HTTP pages.
 *  When this value is true, options.secure_distribution will be used as host if provided, and options.protocol is set
 *  to "https://".
 * @returns {string} the URL prefix for the resource.
 * @private
 */
function handlePrefix(publicId, options) {
  if (options.cloud_name && options.cloud_name[0] === '/') {
    return '/res' + options.cloud_name;
  }
  // defaults
  var protocol = "http://";
  var cdnPart = "";
  var subdomain = "res";
  var host = ".cloudinary.com";
  var path = "/" + options.cloud_name;
  // modifications
  if (options.protocol) {
    protocol = options.protocol + '//';
  }
  if (options.private_cdn) {
    cdnPart = options.cloud_name + "-";
    path = "";
  }
  if (options.cdn_subdomain) {
    subdomain = "res-" + cdnSubdomainNumber(publicId);
  }
  if (options.secure) {
    protocol = "https://";
    if (options.secure_cdn_subdomain === false) {
      subdomain = "res";
    }
    if (options.secure_distribution != null && options.secure_distribution !== OLD_AKAMAI_SHARED_CDN && options.secure_distribution !== SHARED_CDN) {
      cdnPart = "";
      subdomain = "";
      host = options.secure_distribution;
    }
  } else if (options.cname) {
    protocol = "http://";
    cdnPart = "";
    subdomain = options.cdn_subdomain ? 'a' + (src_crc32(publicId) % 5 + 1) + '.' : '';
    host = options.cname;
  }
  return [protocol, cdnPart, subdomain, host, path].join("");
}

/**
 * Return the resource type and action type based on the given configuration
 * @function Cloudinary#handleResourceType
 * @param {Object|string} resource_type
 * @param {string} [type='upload']
 * @param {string} [url_suffix]
 * @param {boolean} [use_root_path]
 * @param {boolean} [shorten]
 * @returns {string} resource_type/type
 * @ignore
 */
function handleResourceType(_ref) {
  var _ref$resource_type = _ref.resource_type,
    resource_type = _ref$resource_type === void 0 ? "image" : _ref$resource_type,
    _ref$type = _ref.type,
    type = _ref$type === void 0 ? "upload" : _ref$type,
    url_suffix = _ref.url_suffix,
    use_root_path = _ref.use_root_path,
    shorten = _ref.shorten;
  var options,
    resourceType = resource_type;
  if (isPlainObject_default()(resourceType)) {
    options = resourceType;
    resourceType = options.resource_type;
    type = options.type;
    shorten = options.shorten;
  }
  if (type == null) {
    type = 'upload';
  }
  if (url_suffix != null) {
    resourceType = SEO_TYPES["".concat(resourceType, "/").concat(type)];
    type = null;
    if (resourceType == null) {
      throw new Error("URL Suffix only supported for ".concat(Object.keys(SEO_TYPES).join(', ')));
    }
  }
  if (use_root_path) {
    if (resourceType === 'image' && type === 'upload' || resourceType === "images") {
      resourceType = null;
      type = null;
    } else {
      throw new Error("Root path only supported for image/upload");
    }
  }
  if (shorten && resourceType === 'image' && type === 'upload') {
    resourceType = 'iu';
    type = null;
  }
  return [resourceType, type].join("/");
}

/**
 * Encode publicId
 * @param publicId
 * @returns {string} encoded publicId
 */
function encodePublicId(publicId) {
  return encodeURIComponent(publicId).replace(/%3A/g, ':').replace(/%2F/g, '/');
}

/**
 * Encode and format publicId
 * @param publicId
 * @param options
 * @returns {string} publicId
 */
function formatPublicId(publicId, options) {
  if (isUrl(publicId)) {
    publicId = encodePublicId(publicId);
  } else {
    try {
      // Make sure publicId is URI encoded.
      publicId = decodeURIComponent(publicId);
    } catch (error) {}
    publicId = encodePublicId(publicId);
    if (options.url_suffix) {
      publicId = publicId + '/' + options.url_suffix;
    }
    if (options.format) {
      if (!options.trust_public_id) {
        publicId = publicId.replace(/\.(jpg|png|gif|webp)$/, '');
      }
      publicId = publicId + '.' + options.format;
    }
  }
  return publicId;
}

/**
 * Get any error with url options
 * @param options
 * @returns {string} if error, otherwise return undefined
 */
function validate(options) {
  var cloud_name = options.cloud_name,
    url_suffix = options.url_suffix;
  if (!cloud_name) {
    return 'Unknown cloud_name';
  }
  if (url_suffix && url_suffix.match(/[\.\/]/)) {
    return 'url_suffix should not include . or /';
  }
}

/**
 * Get version part of the url
 * @param publicId
 * @param options
 * @returns {string}
 */
function handleVersion(publicId, options) {
  // force_version param means to make sure there is a version in the url (Default is true)
  var isForceVersion = options.force_version || typeof options.force_version === 'undefined';

  // Is version included in publicId or in options, or publicId is a url (doesn't need version)
  var isVersionExist = publicId.indexOf('/') < 0 || publicId.match(/^v[0-9]+/) || isUrl(publicId) || options.version;
  if (isForceVersion && !isVersionExist) {
    options.version = 1;
  }
  return options.version ? "v".concat(options.version) : '';
}

/**
 * Get final transformation component for url string
 * @param options
 * @returns {string}
 */
function handleTransformation(options) {
  var _ref2 = options || {},
    placeholder = _ref2.placeholder,
    accessibility = _ref2.accessibility,
    otherOptions = _objectWithoutProperties(_ref2, _excluded);
  var result = new src_transformation(otherOptions);

  // Append accessibility transformations
  if (accessibility && ACCESSIBILITY_MODES[accessibility]) {
    result.chain().effect(ACCESSIBILITY_MODES[accessibility]);
  }

  // Append placeholder transformations
  if (placeholder) {
    if (placeholder === "predominant-color" && result.getValue('width') && result.getValue('height')) {
      placeholder += '-pixel';
    }
    var placeholderTransformations = PLACEHOLDER_IMAGE_MODES[placeholder] || PLACEHOLDER_IMAGE_MODES.blur;
    placeholderTransformations.forEach(function (t) {
      return result.chain().transformation(t);
    });
  }
  return result.serialize();
}

/**
 * If type is 'fetch', update publicId to be a url
 * @param publicId
 * @param type
 * @returns {string}
 */
function preparePublicId(publicId, _ref3) {
  var type = _ref3.type;
  return !isUrl(publicId) && type === 'fetch' ? makeUrl(publicId) : publicId;
}

/**
 * Generate url string
 * @param publicId
 * @param options
 * @returns {string} final url
 */
function urlString(publicId, options) {
  if (isUrl(publicId) && (options.type === 'upload' || options.type === 'asset')) {
    return publicId;
  }
  var version = handleVersion(publicId, options);
  var transformationString = handleTransformation(options);
  var prefix = handlePrefix(publicId, options);
  var signature = handleSignature(options);
  var resourceType = handleResourceType(options);
  publicId = formatPublicId(publicId, options);
  return compact_default()([prefix, resourceType, signature, transformationString, version, publicId]).join('/').replace(/([^:])\/+/g, '$1/') // replace '///' with '//'
  .replace(' ', '%20');
}

/**
 * Merge options and config with defaults
 * update options fetch_format according to 'type' param
 * @param options
 * @param config
 * @returns {*} updated options
 */
function prepareOptions(options, config) {
  if (options instanceof src_transformation) {
    options = options.toOptions();
  }
  options = defaults({}, options, config, DEFAULT_IMAGE_PARAMS);
  if (options.type === 'fetch') {
    options.fetch_format = options.fetch_format || options.format;
  }
  return options;
}

/**
 * Generates a URL for any asset in your Media library.
 * @function url
 * @ignore
 * @param {string} publicId - The public ID of the media asset.
 * @param {Object} [options={}] - The {@link Transformation} parameters to include in the URL.
 * @param {object} [config={}] - URL configuration parameters
 * @param {type} [options.type='upload'] - The asset's storage type.
 *  For details on all fetch types, see
 * <a href="https://cloudinary.com/documentation/image_transformations#fetching_images_from_remote_locations"
 *  target="_blank">Fetch types</a>.
 * @param {Object} [options.resource_type='image'] - The type of asset. <p>Possible values:<br/>
 *  - `image`<br/>
 *  - `video`<br/>
 *  - `raw`
 * @param {signature} [options.signature='s--12345678--'] - The signature component of a
 *  signed delivery URL of the format: /s--SIGNATURE--/.
 *  For details on signatures, see
 * <a href="https://cloudinary.com/documentation/signatures" target="_blank">Signatures</a>.
 * @return {string} The media asset URL.
 * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
 *  Available image transformations</a>
 * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
 *  Available video transformations</a>
 */
function url_url(publicId) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var config = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
  if (!publicId) {
    return publicId;
  }
  options = prepareOptions(options, config);
  publicId = preparePublicId(publicId, options);
  var error = validate(options);
  if (error) {
    throw error;
  }
  var resultUrl = urlString(publicId, options);
  if (options.urlAnalytics) {
    var analyticsOptions = getAnalyticsOptions(options);
    var sdkAnalyticsSignature = getSDKAnalyticsSignature(analyticsOptions);
    // url might already have a '?' query param
    var appender = '?';
    if (resultUrl.indexOf('?') >= 0) {
      appender = '&';
    }
    resultUrl = "".concat(resultUrl).concat(appender, "_a=").concat(sdkAnalyticsSignature);
  }
  if (options.auth_token) {
    var _appender = resultUrl.indexOf('?') >= 0 ? '&' : '?';
    resultUrl = "".concat(resultUrl).concat(_appender, "__cld_token__=").concat(options.auth_token);
  }
  return resultUrl;
}
;
// CONCATENATED MODULE: ./src/util/generateBreakpoints.js
function generateBreakpoints_slicedToArray(arr, i) { return generateBreakpoints_arrayWithHoles(arr) || generateBreakpoints_iterableToArrayLimit(arr, i) || generateBreakpoints_unsupportedIterableToArray(arr, i) || generateBreakpoints_nonIterableRest(); }
function generateBreakpoints_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function generateBreakpoints_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return generateBreakpoints_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return generateBreakpoints_arrayLikeToArray(o, minLen); }
function generateBreakpoints_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i]; return arr2; }
function generateBreakpoints_iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t["return"] && (u = t["return"](), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function generateBreakpoints_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }
/**
 * Helper function. Gets or populates srcset breakpoints using provided parameters
 * Either the breakpoints or min_width, max_width, max_images must be provided.
 *
 * @private
 * @param {srcset} srcset Options with either `breakpoints` or `min_width`, `max_width`, and `max_images`
 *
 * @return {number[]} Array of breakpoints
 *
 */
function generateBreakpoints(srcset) {
  var breakpoints = srcset.breakpoints || [];
  if (breakpoints.length) {
    return breakpoints;
  }
  var _map = [srcset.min_width, srcset.max_width, srcset.max_images].map(Number),
    _map2 = generateBreakpoints_slicedToArray(_map, 3),
    min_width = _map2[0],
    max_width = _map2[1],
    max_images = _map2[2];
  if ([min_width, max_width, max_images].some(isNaN)) {
    throw 'Either (min_width, max_width, max_images) ' + 'or breakpoints must be provided to the image srcset attribute';
  }
  if (min_width > max_width) {
    throw 'min_width must be less than max_width';
  }
  if (max_images <= 0) {
    throw 'max_images must be a positive integer';
  } else if (max_images === 1) {
    min_width = max_width;
  }
  var stepSize = Math.ceil((max_width - min_width) / Math.max(max_images - 1, 1));
  for (var current = min_width; current < max_width; current += stepSize) {
    breakpoints.push(current);
  }
  breakpoints.push(max_width);
  return breakpoints;
}
// CONCATENATED MODULE: ./src/util/srcsetUtils.js

var srcsetUtils_isEmpty = isEmpty;




/**
 * Options used to generate the srcset attribute.
 * @typedef {object} srcset
 * @property {(number[]|string[])}   [breakpoints] An array of breakpoints.
 * @property {number}                [min_width]   Minimal width of the srcset images.
 * @property {number}                [max_width]   Maximal width of the srcset images.
 * @property {number}                [max_images]  Number of srcset images to generate.
 * @property {object|string}         [transformation] The transformation to use in the srcset urls.
 * @property {boolean}               [sizes] Whether to calculate and add the sizes attribute.
 */

/**
 * Helper function. Generates a single srcset item url
 *
 * @private
 * @param {string} public_id  Public ID of the resource.
 * @param {number} width      Width in pixels of the srcset item.
 * @param {object|string} transformation
 * @param {object} options    Additional options.
 *
 * @return {string} Resulting URL of the item
 */
function scaledUrl(public_id, width, transformation) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};
  var configParams = extractUrlParams(options);
  transformation = transformation || options;
  configParams.raw_transformation = new src_transformation([merge_default.a({}, transformation), {
    crop: 'scale',
    width: width
  }]).toString();
  return url_url(public_id, configParams);
}

/**
 * If cache is enabled, get the breakpoints from the cache. If the values were not found in the cache,
 * or cache is not enabled, generate the values.
 * @param {srcset} srcset The srcset configuration parameters
 * @param {string} public_id
 * @param {object} options
 * @return {*|Array}
 */
function getOrGenerateBreakpoints(public_id) {
  var srcset = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
  return generateBreakpoints(srcset);
}

/**
 * Helper function. Generates srcset attribute value of the HTML img tag
 * @private
 *
 * @param {string} public_id  Public ID of the resource
 * @param {number[]} breakpoints An array of breakpoints (in pixels)
 * @param {object} transformation The transformation
 * @param {object} options Includes html tag options, transformation options
 * @return {string} Resulting srcset attribute value
 */
function generateSrcsetAttribute(public_id, breakpoints, transformation, options) {
  options = cloneDeep_default.a(options);
  patchFetchFormat(options);
  return breakpoints.map(function (width) {
    return "".concat(scaledUrl(public_id, width, transformation, options), " ").concat(width, "w");
  }).join(', ');
}

/**
 * Helper function. Generates sizes attribute value of the HTML img tag
 * @private
 * @param {number[]} breakpoints An array of breakpoints.
 * @return {string} Resulting sizes attribute value
 */
function generateSizesAttribute(breakpoints) {
  if (breakpoints == null) {
    return '';
  }
  return breakpoints.map(function (width) {
    return "(max-width: ".concat(width, "px) ").concat(width, "px");
  }).join(', ');
}

/**
 * Helper function. Generates srcset and sizes attributes of the image tag
 *
 * Generated attributes are added to attributes argument
 *
 * @private
 * @param {string}    publicId  The public ID of the resource
 * @param {object}    attributes Existing HTML attributes.
 * @param {srcset}    srcsetData
 * @param {object}    options    Additional options.
 *
 * @return array The responsive attributes
 */
function generateImageResponsiveAttributes(publicId) {
  var attributes = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var srcsetData = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};
  // Create both srcset and sizes here to avoid fetching breakpoints twice

  var responsiveAttributes = {};
  if (srcsetUtils_isEmpty(srcsetData)) {
    return responsiveAttributes;
  }
  var generateSizes = !attributes.sizes && srcsetData.sizes === true;
  var generateSrcset = !attributes.srcset;
  if (generateSrcset || generateSizes) {
    var breakpoints = getOrGenerateBreakpoints(publicId, srcsetData, options);
    if (generateSrcset) {
      var transformation = srcsetData.transformation;
      var srcsetAttr = generateSrcsetAttribute(publicId, breakpoints, transformation, options);
      if (!srcsetUtils_isEmpty(srcsetAttr)) {
        responsiveAttributes.srcset = srcsetAttr;
      }
    }
    if (generateSizes) {
      var sizesAttr = generateSizesAttribute(breakpoints);
      if (!srcsetUtils_isEmpty(sizesAttr)) {
        responsiveAttributes.sizes = sizesAttr;
      }
    }
  }
  return responsiveAttributes;
}

/**
 * Generate a media query
 *
 * @private
 * @param {object} options configuration options
 * @param {number|string} options.min_width
 * @param {number|string} options.max_width
 * @return {string} a media query string
 */
function generateMediaAttr(options) {
  var mediaQuery = [];
  if (options != null) {
    if (options.min_width != null) {
      mediaQuery.push("(min-width: ".concat(options.min_width, "px)"));
    }
    if (options.max_width != null) {
      mediaQuery.push("(max-width: ".concat(options.max_width, "px)"));
    }
  }
  return mediaQuery.join(' and ');
}
var srcsetUrl = scaledUrl;
// CONCATENATED MODULE: ./src/tags/imagetag.js
function imagetag_typeof(o) { "@babel/helpers - typeof"; return imagetag_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, imagetag_typeof(o); }
function imagetag_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function imagetag_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, imagetag_toPropertyKey(descriptor.key), descriptor); } }
function imagetag_createClass(Constructor, protoProps, staticProps) { if (protoProps) imagetag_defineProperties(Constructor.prototype, protoProps); if (staticProps) imagetag_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function imagetag_toPropertyKey(t) { var i = imagetag_toPrimitive(t, "string"); return "symbol" == imagetag_typeof(i) ? i : i + ""; }
function imagetag_toPrimitive(t, r) { if ("object" != imagetag_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != imagetag_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function imagetag_callSuper(t, o, e) { return o = imagetag_getPrototypeOf(o), imagetag_possibleConstructorReturn(t, imagetag_isNativeReflectConstruct() ? Reflect.construct(o, e || [], imagetag_getPrototypeOf(t).constructor) : o.apply(t, e)); }
function imagetag_possibleConstructorReturn(self, call) { if (call && (imagetag_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return imagetag_assertThisInitialized(self); }
function imagetag_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }
function imagetag_isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (imagetag_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function imagetag_get() { if (typeof Reflect !== "undefined" && Reflect.get) { imagetag_get = Reflect.get.bind(); } else { imagetag_get = function _get(target, property, receiver) { var base = imagetag_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(arguments.length < 3 ? target : receiver); } return desc.value; }; } return imagetag_get.apply(this, arguments); }
function imagetag_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = imagetag_getPrototypeOf(object); if (object === null) break; } return object; }
function imagetag_getPrototypeOf(o) { imagetag_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return imagetag_getPrototypeOf(o); }
function imagetag_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) imagetag_setPrototypeOf(subClass, superClass); }
function imagetag_setPrototypeOf(o, p) { imagetag_setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return imagetag_setPrototypeOf(o, p); }
/**
 * Image Tag
 * Depends on 'tags/htmltag', 'cloudinary'
 */






/**
 * Creates an HTML (DOM) Image tag using Cloudinary as the source.
 * @constructor ImageTag
 * @extends HtmlTag
 * @param {string} [publicId]
 * @param {Object} [options]
 */
var imagetag_ImageTag = /*#__PURE__*/function (_HtmlTag) {
  function ImageTag(publicId) {
    var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    imagetag_classCallCheck(this, ImageTag);
    return imagetag_callSuper(this, ImageTag, ["img", publicId, options]);
  }

  /** @override */
  imagetag_inherits(ImageTag, _HtmlTag);
  return imagetag_createClass(ImageTag, [{
    key: "closeTag",
    value: function closeTag() {
      return "";
    }

    /** @override */
  }, {
    key: "attributes",
    value: function attributes() {
      var attr, options, srcAttribute;
      attr = imagetag_get(imagetag_getPrototypeOf(ImageTag.prototype), "attributes", this).call(this) || {};
      options = this.getOptions();
      var attributes = this.getOption('attributes') || {};
      var srcsetParam = this.getOption('srcset') || attributes.srcset;
      var responsiveAttributes = {};
      if (isString_default()(srcsetParam)) {
        responsiveAttributes.srcset = srcsetParam;
      } else {
        responsiveAttributes = generateImageResponsiveAttributes(this.publicId, attributes, srcsetParam, options);
      }
      if (!isEmpty(responsiveAttributes)) {
        delete attr.width;
        delete attr.height;
      }
      merge_default()(attr, responsiveAttributes);
      srcAttribute = options.responsive && !options.client_hints ? 'data-src' : 'src';
      if (attr[srcAttribute] == null) {
        attr[srcAttribute] = url_url(this.publicId, this.getOptions());
      }
      return attr;
    }
  }]);
}(htmltag);
;
/* harmony default export */ var imagetag = (imagetag_ImageTag);
// CONCATENATED MODULE: ./src/tags/sourcetag.js
function sourcetag_typeof(o) { "@babel/helpers - typeof"; return sourcetag_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, sourcetag_typeof(o); }
function sourcetag_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function sourcetag_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, sourcetag_toPropertyKey(descriptor.key), descriptor); } }
function sourcetag_createClass(Constructor, protoProps, staticProps) { if (protoProps) sourcetag_defineProperties(Constructor.prototype, protoProps); if (staticProps) sourcetag_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function sourcetag_toPropertyKey(t) { var i = sourcetag_toPrimitive(t, "string"); return "symbol" == sourcetag_typeof(i) ? i : i + ""; }
function sourcetag_toPrimitive(t, r) { if ("object" != sourcetag_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != sourcetag_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function sourcetag_callSuper(t, o, e) { return o = sourcetag_getPrototypeOf(o), sourcetag_possibleConstructorReturn(t, sourcetag_isNativeReflectConstruct() ? Reflect.construct(o, e || [], sourcetag_getPrototypeOf(t).constructor) : o.apply(t, e)); }
function sourcetag_possibleConstructorReturn(self, call) { if (call && (sourcetag_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return sourcetag_assertThisInitialized(self); }
function sourcetag_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }
function sourcetag_isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (sourcetag_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function sourcetag_get() { if (typeof Reflect !== "undefined" && Reflect.get) { sourcetag_get = Reflect.get.bind(); } else { sourcetag_get = function _get(target, property, receiver) { var base = sourcetag_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(arguments.length < 3 ? target : receiver); } return desc.value; }; } return sourcetag_get.apply(this, arguments); }
function sourcetag_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = sourcetag_getPrototypeOf(object); if (object === null) break; } return object; }
function sourcetag_getPrototypeOf(o) { sourcetag_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return sourcetag_getPrototypeOf(o); }
function sourcetag_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) sourcetag_setPrototypeOf(subClass, superClass); }
function sourcetag_setPrototypeOf(o, p) { sourcetag_setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return sourcetag_setPrototypeOf(o, p); }
/**
 * Image Tag
 * Depends on 'tags/htmltag', 'cloudinary'
 */





/**
 * Creates an HTML (DOM) Image tag using Cloudinary as the source.
 * @constructor SourceTag
 * @extends HtmlTag
 * @param {string} [publicId]
 * @param {Object} [options]
 */
var sourcetag_SourceTag = /*#__PURE__*/function (_HtmlTag) {
  function SourceTag(publicId) {
    var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    sourcetag_classCallCheck(this, SourceTag);
    return sourcetag_callSuper(this, SourceTag, ["source", publicId, options]);
  }

  /** @override */
  sourcetag_inherits(SourceTag, _HtmlTag);
  return sourcetag_createClass(SourceTag, [{
    key: "closeTag",
    value: function closeTag() {
      return "";
    }

    /** @override */
  }, {
    key: "attributes",
    value: function attributes() {
      var srcsetParam = this.getOption('srcset');
      var attr = sourcetag_get(sourcetag_getPrototypeOf(SourceTag.prototype), "attributes", this).call(this) || {};
      var options = this.getOptions();
      merge_default()(attr, generateImageResponsiveAttributes(this.publicId, attr, srcsetParam, options));
      if (!attr.srcset) {
        attr.srcset = url_url(this.publicId, options);
      }
      if (!attr.media && options.media) {
        attr.media = generateMediaAttr(options.media);
      }
      return attr;
    }
  }]);
}(htmltag);
;
/* harmony default export */ var sourcetag = (sourcetag_SourceTag);
// CONCATENATED MODULE: ./src/tags/picturetag.js
function picturetag_typeof(o) { "@babel/helpers - typeof"; return picturetag_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, picturetag_typeof(o); }
function picturetag_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function picturetag_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, picturetag_toPropertyKey(descriptor.key), descriptor); } }
function picturetag_createClass(Constructor, protoProps, staticProps) { if (protoProps) picturetag_defineProperties(Constructor.prototype, protoProps); if (staticProps) picturetag_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function picturetag_toPropertyKey(t) { var i = picturetag_toPrimitive(t, "string"); return "symbol" == picturetag_typeof(i) ? i : i + ""; }
function picturetag_toPrimitive(t, r) { if ("object" != picturetag_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != picturetag_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function picturetag_callSuper(t, o, e) { return o = picturetag_getPrototypeOf(o), picturetag_possibleConstructorReturn(t, picturetag_isNativeReflectConstruct() ? Reflect.construct(o, e || [], picturetag_getPrototypeOf(t).constructor) : o.apply(t, e)); }
function picturetag_possibleConstructorReturn(self, call) { if (call && (picturetag_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return picturetag_assertThisInitialized(self); }
function picturetag_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }
function picturetag_isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (picturetag_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function picturetag_get() { if (typeof Reflect !== "undefined" && Reflect.get) { picturetag_get = Reflect.get.bind(); } else { picturetag_get = function _get(target, property, receiver) { var base = picturetag_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(arguments.length < 3 ? target : receiver); } return desc.value; }; } return picturetag_get.apply(this, arguments); }
function picturetag_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = picturetag_getPrototypeOf(object); if (object === null) break; } return object; }
function picturetag_getPrototypeOf(o) { picturetag_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return picturetag_getPrototypeOf(o); }
function picturetag_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) picturetag_setPrototypeOf(subClass, superClass); }
function picturetag_setPrototypeOf(o, p) { picturetag_setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return picturetag_setPrototypeOf(o, p); }





var picturetag_PictureTag = /*#__PURE__*/function (_HtmlTag) {
  function PictureTag(publicId) {
    var _this;
    var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    var sources = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : [];
    picturetag_classCallCheck(this, PictureTag);
    _this = picturetag_callSuper(this, PictureTag, ['picture', publicId, options]);
    _this.widthList = sources;
    return _this;
  }

  /** @override */
  picturetag_inherits(PictureTag, _HtmlTag);
  return picturetag_createClass(PictureTag, [{
    key: "content",
    value: function content() {
      var _this2 = this;
      return this.widthList.map(function (_ref) {
        var min_width = _ref.min_width,
          max_width = _ref.max_width,
          transformation = _ref.transformation;
        var options = _this2.getOptions();
        var sourceTransformation = new src_transformation(options);
        sourceTransformation.chain().fromOptions(typeof transformation === 'string' ? {
          raw_transformation: transformation
        } : transformation);
        options = extractUrlParams(options);
        options.media = {
          min_width: min_width,
          max_width: max_width
        };
        options.transformation = sourceTransformation;
        return new sourcetag(_this2.publicId, options).toHtml();
      }).join('') + new imagetag(this.publicId, this.getOptions()).toHtml();
    }

    /** @override */
  }, {
    key: "attributes",
    value: function attributes() {
      var attr = picturetag_get(picturetag_getPrototypeOf(PictureTag.prototype), "attributes", this).call(this);
      delete attr.width;
      delete attr.height;
      return attr;
    }

    /** @override */
  }, {
    key: "closeTag",
    value: function closeTag() {
      return "</" + this.name + ">";
    }
  }]);
}(htmltag);
;
/* harmony default export */ var picturetag = (picturetag_PictureTag);
// CONCATENATED MODULE: ./src/tags/videotag.js
function videotag_typeof(o) { "@babel/helpers - typeof"; return videotag_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, videotag_typeof(o); }
function videotag_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function videotag_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, videotag_toPropertyKey(descriptor.key), descriptor); } }
function videotag_createClass(Constructor, protoProps, staticProps) { if (protoProps) videotag_defineProperties(Constructor.prototype, protoProps); if (staticProps) videotag_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function videotag_toPropertyKey(t) { var i = videotag_toPrimitive(t, "string"); return "symbol" == videotag_typeof(i) ? i : i + ""; }
function videotag_toPrimitive(t, r) { if ("object" != videotag_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != videotag_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function videotag_callSuper(t, o, e) { return o = videotag_getPrototypeOf(o), videotag_possibleConstructorReturn(t, videotag_isNativeReflectConstruct() ? Reflect.construct(o, e || [], videotag_getPrototypeOf(t).constructor) : o.apply(t, e)); }
function videotag_possibleConstructorReturn(self, call) { if (call && (videotag_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return videotag_assertThisInitialized(self); }
function videotag_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }
function videotag_isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (videotag_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function videotag_get() { if (typeof Reflect !== "undefined" && Reflect.get) { videotag_get = Reflect.get.bind(); } else { videotag_get = function _get(target, property, receiver) { var base = videotag_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(arguments.length < 3 ? target : receiver); } return desc.value; }; } return videotag_get.apply(this, arguments); }
function videotag_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = videotag_getPrototypeOf(object); if (object === null) break; } return object; }
function videotag_getPrototypeOf(o) { videotag_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return videotag_getPrototypeOf(o); }
function videotag_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) videotag_setPrototypeOf(subClass, superClass); }
function videotag_setPrototypeOf(o, p) { videotag_setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return videotag_setPrototypeOf(o, p); }
/**
 * Video Tag
 * Depends on 'tags/htmltag', 'util', 'cloudinary'
 */





var VIDEO_TAG_PARAMS = ['source_types', 'source_transformation', 'fallback_content', 'poster', 'sources'];
var videotag_DEFAULT_VIDEO_SOURCE_TYPES = ['webm', 'mp4', 'ogv'];
var videotag_DEFAULT_POSTER_OPTIONS = {
  format: 'jpg',
  resource_type: 'video'
};

/**
 * Creates an HTML (DOM) Video tag using Cloudinary as the source.
 * @constructor VideoTag
 * @extends HtmlTag
 * @param {string} [publicId]
 * @param {Object} [options]
 */
var videotag_VideoTag = /*#__PURE__*/function (_HtmlTag) {
  function VideoTag(publicId) {
    var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    videotag_classCallCheck(this, VideoTag);
    options = defaults({}, options, DEFAULT_VIDEO_PARAMS);
    return videotag_callSuper(this, VideoTag, ["video", publicId.replace(/\.(mp4|ogv|webm)$/, ''), options]);
  }

  /**
   * Set the transformation to apply on each source
   * @function VideoTag#setSourceTransformation
   * @param {Object} an object with pairs of source type and source transformation
   * @returns {VideoTag} Returns this instance for chaining purposes.
   */
  videotag_inherits(VideoTag, _HtmlTag);
  return videotag_createClass(VideoTag, [{
    key: "setSourceTransformation",
    value: function setSourceTransformation(value) {
      this.transformation().sourceTransformation(value);
      return this;
    }

    /**
     * Set the source types to include in the video tag
     * @function VideoTag#setSourceTypes
     * @param {Array<string>} an array of source types
     * @returns {VideoTag} Returns this instance for chaining purposes.
     */
  }, {
    key: "setSourceTypes",
    value: function setSourceTypes(value) {
      this.transformation().sourceTypes(value);
      return this;
    }

    /**
     * Set the poster to be used in the video tag
     * @function VideoTag#setPoster
     * @param {string|Object} value
     * - string: a URL to use for the poster
     * - Object: transformation parameters to apply to the poster. May optionally include a public_id to use instead of the video public_id.
     * @returns {VideoTag} Returns this instance for chaining purposes.
     */
  }, {
    key: "setPoster",
    value: function setPoster(value) {
      this.transformation().poster(value);
      return this;
    }

    /**
     * Set the content to use as fallback in the video tag
     * @function VideoTag#setFallbackContent
     * @param {string} value - the content to use, in HTML format
     * @returns {VideoTag} Returns this instance for chaining purposes.
     */
  }, {
    key: "setFallbackContent",
    value: function setFallbackContent(value) {
      this.transformation().fallbackContent(value);
      return this;
    }
  }, {
    key: "content",
    value: function content() {
      var _this = this;
      var sourceTypes = this.transformation().getValue('source_types');
      var sourceTransformation = this.transformation().getValue('source_transformation');
      var fallback = this.transformation().getValue('fallback_content');
      var sources = this.getOption('sources');
      var innerTags = [];
      if (isArray_default()(sources) && !isEmpty(sources)) {
        innerTags = sources.map(function (source) {
          var src = url_url(_this.publicId, defaults({}, source.transformations || {}, {
            resource_type: 'video',
            format: source.type
          }), _this.getOptions());
          return _this.createSourceTag(src, source.type, source.codecs);
        });
      } else {
        if (isEmpty(sourceTypes)) {
          sourceTypes = videotag_DEFAULT_VIDEO_SOURCE_TYPES;
        }
        if (isArray_default()(sourceTypes)) {
          innerTags = sourceTypes.map(function (srcType) {
            var src = url_url(_this.publicId, defaults({}, sourceTransformation[srcType] || {}, {
              resource_type: 'video',
              format: srcType
            }), _this.getOptions());
            return _this.createSourceTag(src, srcType);
          });
        }
      }
      return innerTags.join('') + fallback;
    }
  }, {
    key: "attributes",
    value: function attributes() {
      var sourceTypes = this.getOption('source_types');
      var poster = this.getOption('poster');
      if (poster === undefined) {
        poster = {};
      }
      if (isPlainObject_default()(poster)) {
        var defaultOptions = poster.public_id != null ? DEFAULT_IMAGE_PARAMS : videotag_DEFAULT_POSTER_OPTIONS;
        poster = url_url(poster.public_id || this.publicId, defaults({}, poster, defaultOptions, this.getOptions()));
      }
      var attr = videotag_get(videotag_getPrototypeOf(VideoTag.prototype), "attributes", this).call(this) || {};
      attr = omit(attr, VIDEO_TAG_PARAMS);
      var sources = this.getOption('sources');
      // In case of empty sourceTypes - fallback to default source types is used.
      var hasSourceTags = !isEmpty(sources) || isEmpty(sourceTypes) || isArray_default()(sourceTypes);
      if (!hasSourceTags) {
        attr["src"] = url_url(this.publicId, this.getOptions(), {
          resource_type: 'video',
          format: sourceTypes
        });
      }
      if (poster != null) {
        attr["poster"] = poster;
      }
      return attr;
    }
  }, {
    key: "createSourceTag",
    value: function createSourceTag(src, sourceType) {
      var codecs = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
      var mimeType = null;
      if (!isEmpty(sourceType)) {
        var videoType = sourceType === 'ogv' ? 'ogg' : sourceType;
        mimeType = 'video/' + videoType;
        if (!isEmpty(codecs)) {
          var codecsStr = isArray_default()(codecs) ? codecs.join(', ') : codecs;
          mimeType += '; codecs=' + codecsStr;
        }
      }
      return "<source " + this.htmlAttrs({
        src: src,
        type: mimeType
      }) + ">";
    }
  }]);
}(htmltag);
/* harmony default export */ var videotag = (videotag_VideoTag);
// CONCATENATED MODULE: ./src/tags/clienthintsmetatag.js
function clienthintsmetatag_typeof(o) { "@babel/helpers - typeof"; return clienthintsmetatag_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, clienthintsmetatag_typeof(o); }
function clienthintsmetatag_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function clienthintsmetatag_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, clienthintsmetatag_toPropertyKey(descriptor.key), descriptor); } }
function clienthintsmetatag_createClass(Constructor, protoProps, staticProps) { if (protoProps) clienthintsmetatag_defineProperties(Constructor.prototype, protoProps); if (staticProps) clienthintsmetatag_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function clienthintsmetatag_toPropertyKey(t) { var i = clienthintsmetatag_toPrimitive(t, "string"); return "symbol" == clienthintsmetatag_typeof(i) ? i : i + ""; }
function clienthintsmetatag_toPrimitive(t, r) { if ("object" != clienthintsmetatag_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != clienthintsmetatag_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function clienthintsmetatag_callSuper(t, o, e) { return o = clienthintsmetatag_getPrototypeOf(o), clienthintsmetatag_possibleConstructorReturn(t, clienthintsmetatag_isNativeReflectConstruct() ? Reflect.construct(o, e || [], clienthintsmetatag_getPrototypeOf(t).constructor) : o.apply(t, e)); }
function clienthintsmetatag_possibleConstructorReturn(self, call) { if (call && (clienthintsmetatag_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return clienthintsmetatag_assertThisInitialized(self); }
function clienthintsmetatag_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }
function clienthintsmetatag_isNativeReflectConstruct() { try { var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); } catch (t) {} return (clienthintsmetatag_isNativeReflectConstruct = function _isNativeReflectConstruct() { return !!t; })(); }
function clienthintsmetatag_getPrototypeOf(o) { clienthintsmetatag_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return clienthintsmetatag_getPrototypeOf(o); }
function clienthintsmetatag_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); Object.defineProperty(subClass, "prototype", { writable: false }); if (superClass) clienthintsmetatag_setPrototypeOf(subClass, superClass); }
function clienthintsmetatag_setPrototypeOf(o, p) { clienthintsmetatag_setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return clienthintsmetatag_setPrototypeOf(o, p); }
/**
 * Image Tag
 * Depends on 'tags/htmltag', 'cloudinary'
 */




/**
 * Creates an HTML (DOM) Meta tag that enables Client-Hints for the HTML page. <br/>
 *  See
 *  <a href="https://cloudinary.com/documentation/responsive_images#automating_responsive_images_with_client_hints"
 *  target="_new">Automating responsive images with Client Hints</a> for more details.
 * @constructor ClientHintsMetaTag
 * @extends HtmlTag
 * @param {object} options
 * @example
 * tag = new ClientHintsMetaTag()
 * //returns: <meta http-equiv="Accept-CH" content="DPR, Viewport-Width, Width">
 */
var clienthintsmetatag_ClientHintsMetaTag = /*#__PURE__*/function (_HtmlTag) {
  function ClientHintsMetaTag(options) {
    clienthintsmetatag_classCallCheck(this, ClientHintsMetaTag);
    return clienthintsmetatag_callSuper(this, ClientHintsMetaTag, ['meta', void 0, assign_default()({
      "http-equiv": "Accept-CH",
      content: "DPR, Viewport-Width, Width"
    }, options)]);
  }

  /** @override */
  clienthintsmetatag_inherits(ClientHintsMetaTag, _HtmlTag);
  return clienthintsmetatag_createClass(ClientHintsMetaTag, [{
    key: "closeTag",
    value: function closeTag() {
      return "";
    }
  }]);
}(htmltag);
;
/* harmony default export */ var clienthintsmetatag = (clienthintsmetatag_ClientHintsMetaTag);
// CONCATENATED MODULE: ./src/util/parse/normalizeToArray.js
function normalizeToArray_toConsumableArray(arr) { return normalizeToArray_arrayWithoutHoles(arr) || normalizeToArray_iterableToArray(arr) || normalizeToArray_unsupportedIterableToArray(arr) || normalizeToArray_nonIterableSpread(); }
function normalizeToArray_nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function normalizeToArray_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return normalizeToArray_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return normalizeToArray_arrayLikeToArray(o, minLen); }
function normalizeToArray_iterableToArray(iter) { if (typeof Symbol !== "undefined" && iter[Symbol.iterator] != null || iter["@@iterator"] != null) return Array.from(iter); }
function normalizeToArray_arrayWithoutHoles(arr) { if (Array.isArray(arr)) return normalizeToArray_arrayLikeToArray(arr); }
function normalizeToArray_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i]; return arr2; }


/**
 * @desc normalize elements, support a single element, array or nodelist, always outputs array
 * @param elements<HTMLElement[]>
 * @returns {[]}
 */
function normalizeToArray(elements) {
  if (isArray_default()(elements)) {
    return elements;
  } else if (elements.constructor.name === "NodeList") {
    return normalizeToArray_toConsumableArray(elements); // ensure an array is always returned, even if nodelist
  } else if (isString_default()(elements)) {
    return Array.prototype.slice.call(document.querySelectorAll(elements), 0);
  } else {
    return [elements];
  }
}
// CONCATENATED MODULE: ./src/util/features/transparentVideo/mountCloudinaryVideoTag.js
/**
 * @param {HTMLElement} htmlElContainer
 * @param {object} clInstance cloudinary instance
 * @param {string} publicId
 * @param {object} options - TransformationOptions
 * @returns Promise<HTMLElement>
 */
function mountCloudinaryVideoTag(htmlElContainer, clInstance, publicId, options) {
  return new Promise(function (resolve, reject) {
    htmlElContainer.innerHTML = clInstance.videoTag(publicId, options).toHtml();

    // All videos under the html container must have a width of 100%, or they might overflow from the container
    var cloudinaryVideoElement = htmlElContainer.querySelector('.cld-transparent-video');
    cloudinaryVideoElement.style.width = '100%';
    resolve(htmlElContainer);
  });
}
/* harmony default export */ var transparentVideo_mountCloudinaryVideoTag = (mountCloudinaryVideoTag);
// CONCATENATED MODULE: ./src/util/transformations/addFlag.js
/**
 * @description - Function will push a flag to incoming options
 * @param {{transformation} | {...transformation}} options - These options are the same options provided to all our SDK methods
 *                           We expect options to either be the transformation itself, or an object containing
 *                           an array of transformations
 *
 * @param {string} flag
 * @returns the mutated options object
 */

function addFlagToOptions(options, flag) {
  // Do we have transformation
  if (options.transformation) {
    options.transformation.push({
      flags: [flag]
    });
  } else {
    // no transformation
    // ensure the flags are extended
    if (!options.flags) {
      options.flags = [];
    }
    if (typeof options.flags === 'string') {
      options.flags = [options.flags];
    }
    options.flags.push(flag);
  }
}
/* harmony default export */ var addFlag = (addFlagToOptions);
// CONCATENATED MODULE: ./src/util/features/transparentVideo/enforceOptionsForTransparentVideo.js



/**
 * @description - Enforce option structure, sets defaults and ensures alpha flag exists
 * @param options {TransformationOptions}
 */
function enforceOptionsForTransparentVideo(options) {
  options.autoplay = true;
  options.muted = true;
  options.controls = false;
  options.max_timeout_ms = options.max_timeout_ms || DEFAULT_TIMEOUT_MS;
  options["class"] = options["class"] || '';
  options["class"] += ' cld-transparent-video';
  options.externalLibraries = options.externalLibraries || {};
  if (!options.externalLibraries.seeThru) {
    options.externalLibraries.seeThru = DEFAULT_EXTERNAL_LIBRARIES.seeThru;
  }

  // ensure there's an alpha transformation present
  // this is a non documented internal flag
  addFlag(options, 'alpha');
}
/* harmony default export */ var transparentVideo_enforceOptionsForTransparentVideo = (enforceOptionsForTransparentVideo);
// CONCATENATED MODULE: ./src/util/xhr/loadScript.js
/**
 * @description - Given a string URL, this function will load the script and resolve the promise.
 *                The function doesn't resolve any value,
 *                this is not a UMD loader where you can get your library name back.
 * @param scriptURL {string}
 * @param {number} max_timeout_ms - Time to elapse before promise is rejected
 * @param isAlreadyLoaded {boolean} if true, the loadScript resolves immediately
 *                                  this is used for multiple invocations - prevents the script from being loaded multiple times
 * @return {Promise<any | {status:string, message:string}>}
 */
function loadScript(scriptURL, max_timeout_ms, isAlreadyLoaded) {
  return new Promise(function (resolve, reject) {
    if (isAlreadyLoaded) {
      resolve();
    } else {
      var scriptTag = document.createElement('script');
      scriptTag.src = scriptURL;
      var timerID = setTimeout(function () {
        reject({
          status: 'error',
          message: "Timeout loading script ".concat(scriptURL)
        });
      }, max_timeout_ms); // 10 seconds for timeout

      scriptTag.onerror = function () {
        clearTimeout(timerID); // clear timeout reject error
        reject({
          status: 'error',
          message: "Error loading ".concat(scriptURL)
        });
      };
      scriptTag.onload = function () {
        clearTimeout(timerID); // clear timeout reject error
        resolve();
      };
      document.head.appendChild(scriptTag);
    }
  });
}
/* harmony default export */ var xhr_loadScript = (loadScript);
// CONCATENATED MODULE: ./src/util/xhr/getBlobFromURL.js
/**
 * Reject on timeout
 * @param maxTimeoutMS
 * @param reject
 * @returns {number} timerID
 */
function rejectOnTimeout(maxTimeoutMS, reject) {
  return setTimeout(function () {
    reject({
      status: 'error',
      message: 'Timeout loading Blob URL'
    });
  }, maxTimeoutMS);
}

/**
 * @description Converts a URL to a BLOB URL
 * @param {string} urlToLoad
 * @param {number} max_timeout_ms - Time to elapse before promise is rejected
 * @return {Promise<{
 *   status: 'success' | 'error'
 *   message?: string,
 *    payload: {
 *      url: string
 *    }
 * }>}
 */
function getBlobFromURL(urlToLoad, maxTimeoutMS) {
  return new Promise(function (resolve, reject) {
    var timerID = rejectOnTimeout(maxTimeoutMS, reject);

    // If fetch exists, use it to fetch blob, otherwise use XHR.
    // XHR causes issues on safari 14.1 so we prefer fetch
    var fetchBlob = typeof fetch !== 'undefined' && fetch ? loadUrlUsingFetch : loadUrlUsingXhr;
    fetchBlob(urlToLoad).then(function (blob) {
      resolve({
        status: 'success',
        payload: {
          blobURL: URL.createObjectURL(blob)
        }
      });
    })["catch"](function () {
      reject({
        status: 'error',
        message: 'Error loading Blob URL'
      });
    })["finally"](function () {
      // Clear the timeout timer on fail or success.
      clearTimeout(timerID);
    });
  });
}

/**
 * Use fetch function to fetch file
 * @param urlToLoad
 * @returns {Promise<unknown>}
 */
function loadUrlUsingFetch(urlToLoad) {
  return new Promise(function (resolve, reject) {
    fetch(urlToLoad).then(function (response) {
      response.blob().then(function (blob) {
        resolve(blob);
      });
    })["catch"](function () {
      reject('error');
    });
  });
}

/**
 * Use XHR to fetch file
 * @param urlToLoad
 * @returns {Promise<unknown>}
 */
function loadUrlUsingXhr(urlToLoad) {
  return new Promise(function (resolve, reject) {
    var xhr = new XMLHttpRequest();
    xhr.responseType = 'blob';
    xhr.onload = function (response) {
      resolve(xhr.response);
    };
    xhr.onerror = function () {
      reject('error');
    };
    xhr.open('GET', urlToLoad, true);
    xhr.send();
  });
}
/* harmony default export */ var xhr_getBlobFromURL = (getBlobFromURL);
// CONCATENATED MODULE: ./src/util/features/transparentVideo/createHiddenVideoTag.js
/**
 * @description Creates a hidden HTMLVideoElement with the specified videoOptions
 * @param {{autoplay, playsinline, loop, muted, poster, blobURL, videoURL }} videoOptions
 * @param {boolean} videoOptions.autoplay - autoplays the video if true
 * @param {string} videoOptions.blobURL - the blobURL to set as video.src
 * @param {string} videoOptions.videoURL - the original videoURL the user created (with transformations)
 * @return {HTMLVideoElement}
 */
function createHiddenVideoTag(videoOptions) {
  var autoplay = videoOptions.autoplay,
    playsinline = videoOptions.playsinline,
    loop = videoOptions.loop,
    muted = videoOptions.muted,
    poster = videoOptions.poster,
    blobURL = videoOptions.blobURL,
    videoURL = videoOptions.videoURL;
  var el = document.createElement('video');
  el.style.visibility = 'hidden';
  el.position = 'absolute';
  el.x = 0;
  el.y = 0;
  el.src = blobURL;
  el.setAttribute('data-video-url', videoURL); // for debugging/testing

  autoplay && el.setAttribute('autoplay', autoplay);
  playsinline && el.setAttribute('playsinline', playsinline);
  loop && el.setAttribute('loop', loop);
  muted && el.setAttribute('muted', muted);
  muted && (el.muted = muted); // this is also needed for autoplay, on top of setAttribute
  poster && el.setAttribute('poster', poster);

  // Free memory at the end of the file loading.
  el.onload = function () {
    URL.revokeObjectURL(blobURL);
  };
  return el;
}
/* harmony default export */ var transparentVideo_createHiddenVideoTag = (createHiddenVideoTag);
// CONCATENATED MODULE: ./src/util/features/transparentVideo/instantiateSeeThru.js
/**
 * @description This function creates a new instanc eof seeThru (seeThru.create()) and returns a promise of the seeThru instance
 * @param {HTMLVideoElement} videoElement
 * @param {number} max_timeout_ms - Time to elapse before promise is rejected
 * @param {string} customClass - A classname to be added to the canvas element created by seeThru
 * @param {boolean} autoPlay
 * @return {Promise<any>} SeeThru instance or rejection error
 */
function instantiateSeeThru(videoElement, max_timeout_ms, customClass, autoPlay) {
  var _window = window,
    seeThru = _window.seeThru,
    setTimeout = _window.setTimeout,
    clearTimeout = _window.clearTimeout;
  return new Promise(function (resolve, reject) {
    var timerID = setTimeout(function () {
      reject({
        status: 'error',
        message: 'Timeout instantiating seeThru instance'
      });
    }, max_timeout_ms);
    if (seeThru) {
      var seeThruInstance = seeThru.create(videoElement).ready(function () {
        // clear timeout reject error
        clearTimeout(timerID);

        // force container width, else the canvas can overflow out
        var canvasElement = seeThruInstance.getCanvas();
        canvasElement.style.width = '100%';
        canvasElement.className += ' ' + customClass;

        // start the video if autoplay is set
        if (autoPlay) {
          seeThruInstance.play();
        }
        resolve(seeThruInstance);
      });
    } else {
      reject({
        status: 'error',
        message: 'Error instantiating seeThru instance'
      });
    }
  });
}
/* harmony default export */ var transparentVideo_instantiateSeeThru = (instantiateSeeThru);
// CONCATENATED MODULE: ./src/util/features/transparentVideo/mountSeeThruCanvasTag.js





/**
 *
 * @param {HTMLElement} htmlElContainer
 * @param {string} videoURL
 * @param {TransformationOptions} options
 * @return {Promise<any>}
 */
function mountSeeThruCanvasTag(htmlElContainer, videoURL, options) {
  var poster = options.poster,
    autoplay = options.autoplay,
    playsinline = options.playsinline,
    loop = options.loop,
    muted = options.muted;
  videoURL = videoURL + '.mp4'; // seeThru always uses mp4
  return new Promise(function (resolve, reject) {
    xhr_loadScript(options.externalLibraries.seeThru, options.max_timeout_ms, window.seeThru).then(function () {
      xhr_getBlobFromURL(videoURL, options.max_timeout_ms).then(function (_ref) {
        var payload = _ref.payload;
        var videoElement = transparentVideo_createHiddenVideoTag({
          blobURL: payload.blobURL,
          videoURL: videoURL,
          // for debugging/testing
          poster: poster,
          autoplay: autoplay,
          playsinline: playsinline,
          loop: loop,
          muted: muted
        });
        htmlElContainer.appendChild(videoElement);
        transparentVideo_instantiateSeeThru(videoElement, options.max_timeout_ms, options["class"], options.autoplay).then(function () {
          resolve(htmlElContainer);
        })["catch"](function (err) {
          reject(err);
        });

        // catch for getBlobFromURL()
      })["catch"](function (_ref2) {
        var status = _ref2.status,
          message = _ref2.message;
        reject({
          status: status,
          message: message
        });
      });
      // catch for loadScript()
    })["catch"](function (_ref3) {
      var status = _ref3.status,
        message = _ref3.message;
      reject({
        status: status,
        message: message
      });
    });
  });
}
/* harmony default export */ var transparentVideo_mountSeeThruCanvasTag = (mountSeeThruCanvasTag);
// CONCATENATED MODULE: ./src/util/features/transparentVideo/checkSupportForTransparency.js
/**
 * @return {Promise<boolean>} - Whether the browser supports transparent videos or not
 */

function checkSupportForTransparency() {
  return new Promise(function (resolve, reject) {
    // Resolve early for safari.
    // Currently (29 December 2021) Safari can play webm/vp9,
    // but it does not support transparent video in the format we're outputting
    if (isSafari()) {
      resolve(false);
    }
    var video = document.createElement('video');
    var canPlay = video.canPlayType && video.canPlayType('video/webm; codecs="vp9"');
    resolve(canPlay === 'maybe' || canPlay === 'probably');
  });
}
/* harmony default export */ var transparentVideo_checkSupportForTransparency = (checkSupportForTransparency);
// CONCATENATED MODULE: ./src/cloudinary.js
function cloudinary_typeof(o) { "@babel/helpers - typeof"; return cloudinary_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, cloudinary_typeof(o); }
function cloudinary_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function cloudinary_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, cloudinary_toPropertyKey(descriptor.key), descriptor); } }
function cloudinary_createClass(Constructor, protoProps, staticProps) { if (protoProps) cloudinary_defineProperties(Constructor.prototype, protoProps); if (staticProps) cloudinary_defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function cloudinary_toPropertyKey(t) { var i = cloudinary_toPrimitive(t, "string"); return "symbol" == cloudinary_typeof(i) ? i : i + ""; }
function cloudinary_toPrimitive(t, r) { if ("object" != cloudinary_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != cloudinary_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }

var applyBreakpoints, closestAbove, defaultBreakpoints, cloudinary_findContainerWidth, cloudinary_maxWidth, updateDpr;










//





defaultBreakpoints = function defaultBreakpoints(width) {
  var steps = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 100;
  return steps * Math.ceil(width / steps);
};
closestAbove = function closestAbove(list, value) {
  var i;
  i = list.length - 2;
  while (i >= 0 && list[i] >= value) {
    i--;
  }
  return list[i + 1];
};
applyBreakpoints = function applyBreakpoints(tag, width, steps, options) {
  var ref, ref1, ref2, responsive_use_breakpoints;
  responsive_use_breakpoints = (ref = (ref1 = (ref2 = options['responsive_use_breakpoints']) != null ? ref2 : options['responsive_use_stoppoints']) != null ? ref1 : this.config('responsive_use_breakpoints')) != null ? ref : this.config('responsive_use_stoppoints');
  if (!responsive_use_breakpoints || responsive_use_breakpoints === 'resize' && !options.resizing) {
    return width;
  } else {
    return this.calc_breakpoint(tag, width, steps);
  }
};
cloudinary_findContainerWidth = function findContainerWidth(element) {
  var containerWidth, style;
  containerWidth = 0;
  while ((element = element != null ? element.parentNode : void 0) instanceof Element && !containerWidth) {
    style = window.getComputedStyle(element);
    if (!/^inline/.test(style.display)) {
      containerWidth = lodash_width(element);
    }
  }
  return containerWidth;
};
updateDpr = function updateDpr(dataSrc, roundDpr) {
  return dataSrc.replace(/\bdpr_(1\.0|auto)\b/g, 'dpr_' + this.device_pixel_ratio(roundDpr));
};
cloudinary_maxWidth = function maxWidth(requiredWidth, tag) {
  var imageWidth;
  imageWidth = lodash_getData(tag, 'width') || 0;
  if (requiredWidth > imageWidth) {
    imageWidth = requiredWidth;
    lodash_setData(tag, 'width', requiredWidth);
  }
  return imageWidth;
};
var cloudinary_Cloudinary = /*#__PURE__*/function () {
  /**
   * Creates a new Cloudinary instance.
   * @class Cloudinary
   * @classdesc Main class for accessing Cloudinary functionality.
   * @param {Object} options - A {@link Configuration} object for globally configuring Cloudinary account settings.
   * @example<br/>
   *  var cl = new cloudinary.Cloudinary( { cloud_name: "mycloud"});<br/>
   *  var imgTag = cl.image("myPicID");
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters" target="_blank">
   *  Available configuration options</a>
   */
  function Cloudinary(options) {
    cloudinary_classCallCheck(this, Cloudinary);
    var configuration;
    this.devicePixelRatioCache = {};
    this.responsiveConfig = {};
    this.responsiveResizeInitialized = false;
    configuration = new src_configuration(options);
    // Provided for backward compatibility
    this.config = function (newConfig, newValue) {
      return configuration.config(newConfig, newValue);
    };
    /**
     * Use \<meta\> tags in the document to configure this `cloudinary` instance.
     * @return This {Cloudinary} instance for chaining.
     */
    this.fromDocument = function () {
      configuration.fromDocument();
      return this;
    };
    /**
     * Use environment variables to configure this `cloudinary` instance.
     * @return This {Cloudinary} instance for chaining.
     */
    this.fromEnvironment = function () {
      configuration.fromEnvironment();
      return this;
    };
    /**
     * Initializes the configuration of this `cloudinary` instance.
     *  This is a convenience method that invokes both {@link Configuration#fromEnvironment|fromEnvironment()}
     *  (Node.js environment only) and {@link Configuration#fromDocument|fromDocument()}.
     *  It first tries to retrieve the configuration from the environment variable.
     *  If not available, it tries from the document meta tags.
     * @function Cloudinary#init
     * @see Configuration#init
     * @return This {Cloudinary} instance for chaining.
     */
    this.init = function () {
      configuration.init();
      return this;
    };
  }

  /**
   * Convenience constructor
   * @param {Object} options
   * @return {Cloudinary}
   * @example cl = cloudinary.Cloudinary.new( { cloud_name: "mycloud"})
   */
  return cloudinary_createClass(Cloudinary, [{
    key: "url",
    value:
    /**
     * Generates a URL for any asset in your Media library.
     * @function Cloudinary#url
     * @param {string} publicId - The public ID of the media asset.
     * @param {Object} [options] - The {@link Transformation} parameters to include in the URL.
     * @param {type} [options.type='upload'] - The asset's storage type.
     *  For details on all fetch types, see
     * <a href="https://cloudinary.com/documentation/image_transformations#fetching_images_from_remote_locations"
     *  target="_blank">Fetch types</a>.
     * @param {resourceType} [options.resource_type='image'] - The type of asset. Possible values:<br/>
     *  - `image`<br/>
     *  - `video`<br/>
     *  - `raw`
     * @return {string} The media asset URL.
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
     *  Available video transformations</a>
     */
    function url(publicId) {
      var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
      return url_url(publicId, options, this.config());
    }

    /**
     * Generates a video asset URL.
     * @function Cloudinary#video_url
     * @param {string} publicId - The public ID of the video.
     * @param {Object} [options] - The {@link Transformation} parameters to include in the URL.
     * @param {type} [options.type='upload'] - The asset's storage type.
     *  For details on all fetch types, see
     *  <a href="https://cloudinary.com/documentation/image_transformations#fetching_images_from_remote_locations"
     *  target="_blank">Fetch types</a>.
     * @return {string} The video URL.
     * @see <a href="https://cloudinary.com/documentation/video_transformation_reference"
     *  target="_blank">Available video transformations</a>
     */
  }, {
    key: "video_url",
    value: function video_url(publicId, options) {
      options = assign_default()({
        resource_type: 'video'
      }, options);
      return this.url(publicId, options);
    }

    /**
     * Generates a URL for an image intended to be used as a thumbnail for the specified video.
     *  Identical to {@link Cloudinary#url|url}, except that the `resource_type` is `video`
     *  and the default `format` is `jpg`.
     * @function Cloudinary#video_thumbnail_url
     * @param {string} publicId -  The unique identifier of the video from which you want to generate a thumbnail image.
     * @param {Object} [options] - The image {@link Transformation} parameters to apply to the thumbnail.
     * In addition to standard image transformations, you can also use the `start_offset` transformation parameter
     * to instruct Cloudinary to generate the thumbnail from a frame other than the middle frame of the video.
     * For details, see
     * <a href="https://cloudinary.com/documentation/video_manipulation_and_delivery#generating_video_thumbnails"
     * target="_blank">Generating video thumbnails</a> in the Cloudinary documentation.
     * @param {type} [options.type='upload'] - The asset's storage type.
     * @return {string} The URL of the video thumbnail image.
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     */
  }, {
    key: "video_thumbnail_url",
    value: function video_thumbnail_url(publicId, options) {
      options = assign_default()({}, DEFAULT_POSTER_OPTIONS, options);
      return this.url(publicId, options);
    }

    /**
     * Generates a string representation of the specified transformation options.
     * @function Cloudinary#transformation_string
     * @param {Object} options - The {@link Transformation} options.
     * @returns {string} The transformation string.
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
     *  Available video transformations</a>
     */
  }, {
    key: "transformation_string",
    value: function transformation_string(options) {
      return new src_transformation(options).serialize();
    }

    /**
     * Generates an image tag.
     * @function Cloudinary#image
     * @param {string} publicId - The public ID of the image.
     * @param {Object} options - The {@link Transformation} parameters, {@link Configuration} parameters,
     *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
     * @return {HTMLImageElement} An image tag DOM element.
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
     *  target="_blank">Available configuration options</a>
     */
  }, {
    key: "image",
    value: function image(publicId) {
      var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
      var client_hints, img, ref;
      img = this.imageTag(publicId, options);
      client_hints = (ref = options.client_hints != null ? options.client_hints : this.config('client_hints')) != null ? ref : false;
      if (options.src == null && !client_hints) {
        // src must be removed before creating the DOM element to avoid loading the image
        img.setAttr("src", '');
      }
      img = img.toDOM();
      if (!client_hints) {
        // cache the image src
        lodash_setData(img, 'src-cache', this.url(publicId, options));
        // set image src taking responsiveness in account
        this.cloudinary_update(img, options);
      }
      return img;
    }

    /**
     * Creates a new ImageTag instance using the configuration defined for this `cloudinary` instance.
     * @function Cloudinary#imageTag
     * @param {string} publicId - The public ID of the image.
     * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
     *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
     * @return {ImageTag} An ImageTag instance that is attached (chained) to this Cloudinary instance.
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
     *  target="_blank">Available configuration options</a>
     */
  }, {
    key: "imageTag",
    value: function imageTag(publicId, options) {
      var tag;
      tag = new imagetag(publicId, this.config());
      tag.transformation().fromOptions(options);
      return tag;
    }

    /**
     * Creates a new PictureTag instance, configured using this `cloudinary` instance.
     * @function Cloudinary#PictureTag
     * @param {string} publicId - the public ID of the resource
     * @param {Object} options - additional options to pass to the new ImageTag instance
     * @param {Array<Object>} sources - the sources definitions
     * @return {PictureTag} A PictureTag that is attached (chained) to this Cloudinary instance
     */
  }, {
    key: "pictureTag",
    value: function pictureTag(publicId, options, sources) {
      var tag;
      tag = new picturetag(publicId, this.config(), sources);
      tag.transformation().fromOptions(options);
      return tag;
    }

    /**
     * Creates a new SourceTag instance, configured using this `cloudinary` instance.
     * @function Cloudinary#SourceTag
     * @param {string} publicId - the public ID of the resource.
     * @param {Object} options - additional options to pass to the new instance.
     * @return {SourceTag} A SourceTag that is attached (chained) to this Cloudinary instance
     */
  }, {
    key: "sourceTag",
    value: function sourceTag(publicId, options) {
      var tag;
      tag = new sourcetag(publicId, this.config());
      tag.transformation().fromOptions(options);
      return tag;
    }

    /**
     * Generates a video thumbnail URL from the specified remote video and includes it in an image tag.
     * @function Cloudinary#video_thumbnail
     * @param {string} publicId - The unique identifier of the video from the relevant video site.
     *  Additionally, either append the image extension type to the identifier value or set
     *  the image delivery format in the 'options' parameter using the 'format' transformation option.
     *  For example, a YouTube video might have the identifier: 'o-urnlaJpOA.jpg'.
     * @param {Object} [options] - The {@link Transformation} parameters to apply.
     * @return {HTMLImageElement} An HTML image tag element
     * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
     *  Available video transformations</a>
     * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
     *  target="_blank">Available configuration options</a>
     */
  }, {
    key: "video_thumbnail",
    value: function video_thumbnail(publicId, options) {
      return this.image(publicId, merge_default()({}, DEFAULT_POSTER_OPTIONS, options));
    }

    /**
     * Fetches a facebook profile image and delivers it in an image tag element.
     * @function Cloudinary#facebook_profile_image
     * @param {string} publicId - The Facebook numeric ID. Additionally, either append the image extension type
     *  to the ID or set the image delivery format in the 'options' parameter using the 'format' transformation option.
     * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
     *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
     * @return {HTMLImageElement} An image tag element.
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
     *  target="_blank">Available configuration options</a>
     */
  }, {
    key: "facebook_profile_image",
    value: function facebook_profile_image(publicId, options) {
      return this.image(publicId, assign_default()({
        type: 'facebook'
      }, options));
    }

    /**
     * Fetches a Twitter profile image by ID and delivers it in an image tag element.
     * @function Cloudinary#twitter_profile_image
     * @param {string} publicId - The Twitter numeric ID. Additionally, either append the image extension type
     *  to the ID or set the image delivery format in the 'options' parameter using the 'format' transformation option.
     * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
     *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
     * @return {HTMLImageElement} An image tag element.
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
     *  target="_blank">Available configuration options</a>
     */
  }, {
    key: "twitter_profile_image",
    value: function twitter_profile_image(publicId, options) {
      return this.image(publicId, assign_default()({
        type: 'twitter'
      }, options));
    }

    /**
     * Fetches a Twitter profile image by name and delivers it in an image tag element.
     * @function Cloudinary#twitter_name_profile_image
     * @param {string} publicId - The Twitter screen name. Additionally, either append the image extension type
     *  to the screen name or set the image delivery format in the 'options' parameter using the 'format' transformation option.
     * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
     *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
     * @return {HTMLImageElement} An image tag element.
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
     *  target="_blank">Available configuration options</a>
     */
  }, {
    key: "twitter_name_profile_image",
    value: function twitter_name_profile_image(publicId, options) {
      return this.image(publicId, assign_default()({
        type: 'twitter_name'
      }, options));
    }

    /**
     * Fetches a Gravatar profile image and delivers it in an image tag element.
     * @function Cloudinary#gravatar_image
     * @param {string} publicId - The calculated hash for the Gravatar email address.
     *  Additionally, either append the image extension type to the screen name or set the image delivery format
     *  in the 'options' parameter using the 'format' transformation option.
     * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
     *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
     * @return {HTMLImageElement} An image tag element.
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
     *  target="_blank">Available configuration options</a>
     */
  }, {
    key: "gravatar_image",
    value: function gravatar_image(publicId, options) {
      return this.image(publicId, assign_default()({
        type: 'gravatar'
      }, options));
    }

    /**
     * Fetches an image from a remote URL and delivers it in an image tag element.
     * @function Cloudinary#fetch_image
     * @param {string} publicId - The full URL of the image to fetch, including the extension.
     * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
     *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
     * @return {HTMLImageElement} An image tag element.
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
     *  target="_blank">Available configuration options</a>
     */
  }, {
    key: "fetch_image",
    value: function fetch_image(publicId, options) {
      return this.image(publicId, assign_default()({
        type: 'fetch'
      }, options));
    }

    /**
     * Generates a video tag.
     * @function Cloudinary#video
     * @param {string} publicId - The public ID of the video.
     * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
     *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
     * @return {HTMLVideoElement} A video tag DOM element.
     * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
     *  Available video transformations</a>
     * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
     *  target="_blank">Available configuration options</a>
     */
  }, {
    key: "video",
    value: function video(publicId) {
      var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
      return this.videoTag(publicId, options).toHtml();
    }

    /**
     * Creates a new VideoTag instance using the configuration defined for this `cloudinary` instance.
     * @function Cloudinary#videoTag
     * @param {string} publicId - The public ID of the video.
     * @param {Object} options - The {@link Transformation} parameters, {@link Configuration} parameters,
     *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
     * @return {VideoTag} A VideoTag that is attached (chained) to this `cloudinary` instance.
     * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
     *  Available video transformations</a>
     * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
     *  target="_blank">Available configuration options</a>
     */
  }, {
    key: "videoTag",
    value: function videoTag(publicId, options) {
      options = defaults({}, options, this.config());
      return new videotag(publicId, options);
    }

    /**
     * Generates a sprite PNG image that contains all images with the specified tag and the corresponding css file.
     * @function Cloudinary#sprite_css
     * @param {string} publicId - The tag on which to base the sprite image.
     * @param {Object} [options] - The {@link Transformation} parameters to include in the URL.
     * @return {string} The URL of the generated CSS file. The sprite image has the same URL, but with a PNG extension.
     * @see <a href="https://cloudinary.com/documentation/sprite_generation" target="_blank">
     *  Sprite generation</a>
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     */
  }, {
    key: "sprite_css",
    value: function sprite_css(publicId, options) {
      options = assign_default()({
        type: 'sprite'
      }, options);
      if (!publicId.match(/.css$/)) {
        options.format = 'css';
      }
      return this.url(publicId, options);
    }

    /**
     * Initializes responsive image behavior for all image tags with the 'cld-responsive'
     *  (or other defined {@link Cloudinary#responsive|responsive} class).<br/>
     *  This method should be invoked after the page has loaded.<br/>
     *  <b>Note</b>: Calls {@link Cloudinary#cloudinary_update|cloudinary_update} to modify image tags.
     * @function Cloudinary#responsive
     * @param {Object} options
     * @param {String} [options.responsive_class='cld-responsive'] - An alternative class
     *  to locate the relevant &lt;img&gt; tags.
     * @param {number} [options.responsive_debounce=100] - The debounce interval in milliseconds.
     * @param {boolean} [bootstrap=true] If true, processes the &lt;img&gt; tags by calling
     *  {@link Cloudinary#cloudinary_update|cloudinary_update}. When false, the tags are processed
     *  only after a resize event.
     * @see {@link Cloudinary#cloudinary_update|cloudinary_update} for additional configuration parameters
     * @see <a href="https://cloudinary.com/documentation/responsive_images#automating_responsive_images_with_javascript"
     *  target="_blank">Automating responsive images with JavaScript</a>
     * @return {function} that when called, removes the resize EventListener added by this function
     */
  }, {
    key: "responsive",
    value: function responsive(options) {
      var _this = this;
      var bootstrap = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : true;
      var ref, ref1, ref2, responsiveClass, responsiveResize, timeout;
      this.responsiveConfig = merge_default()(this.responsiveConfig || {}, options);
      responsiveClass = (ref = this.responsiveConfig.responsive_class) != null ? ref : this.config('responsive_class');
      if (bootstrap) {
        this.cloudinary_update("img.".concat(responsiveClass, ", img.cld-hidpi"), this.responsiveConfig);
      }
      responsiveResize = (ref1 = (ref2 = this.responsiveConfig.responsive_resize) != null ? ref2 : this.config('responsive_resize')) != null ? ref1 : true;
      if (responsiveResize && !this.responsiveResizeInitialized) {
        this.responsiveConfig.resizing = this.responsiveResizeInitialized = true;
        timeout = null;
        var makeResponsive = function makeResponsive() {
          var debounce, ref3, ref4, reset, run, wait, waitFunc;
          debounce = (ref3 = (ref4 = _this.responsiveConfig.responsive_debounce) != null ? ref4 : _this.config('responsive_debounce')) != null ? ref3 : 100;
          reset = function reset() {
            if (timeout) {
              clearTimeout(timeout);
              timeout = null;
            }
          };
          run = function run() {
            return _this.cloudinary_update("img.".concat(responsiveClass), _this.responsiveConfig);
          };
          waitFunc = function waitFunc() {
            reset();
            return run();
          };
          wait = function wait() {
            reset();
            timeout = setTimeout(waitFunc, debounce);
          };
          if (debounce) {
            return wait();
          } else {
            return run();
          }
        };
        window.addEventListener('resize', makeResponsive);
        return function () {
          return window.removeEventListener('resize', makeResponsive);
        };
      }
    }

    /**
     * @function Cloudinary#calc_breakpoint
     * @private
     * @ignore
     */
  }, {
    key: "calc_breakpoint",
    value: function calc_breakpoint(element, width, steps) {
      var breakpoints = lodash_getData(element, 'breakpoints') || lodash_getData(element, 'stoppoints') || this.config('breakpoints') || this.config('stoppoints') || defaultBreakpoints;
      if (isFunction_default()(breakpoints)) {
        return breakpoints(width, steps);
      } else {
        if (isString_default()(breakpoints)) {
          breakpoints = breakpoints.split(',').map(function (point) {
            return parseInt(point);
          }).sort(function (a, b) {
            return a - b;
          });
        }
        return closestAbove(breakpoints, width);
      }
    }

    /**
     * @function Cloudinary#calc_stoppoint
     * @deprecated Use {@link calc_breakpoint} instead.
     * @private
     * @ignore
     */
  }, {
    key: "calc_stoppoint",
    value: function calc_stoppoint(element, width, steps) {
      return this.calc_breakpoint(element, width, steps);
    }

    /**
     * @function Cloudinary#device_pixel_ratio
     * @private
     */
  }, {
    key: "device_pixel_ratio",
    value: function device_pixel_ratio(roundDpr) {
      roundDpr = roundDpr == null ? true : roundDpr;
      var dpr = (typeof window !== "undefined" && window !== null ? window.devicePixelRatio : void 0) || 1;
      if (roundDpr) {
        dpr = Math.ceil(dpr);
      }
      if (dpr <= 0 || dpr === 0 / 0) {
        dpr = 1;
      }
      var dprString = dpr.toString();
      if (dprString.match(/^\d+$/)) {
        dprString += '.0';
      }
      return dprString;
    }

    /**
    * Applies responsiveness to all <code>&lt;img&gt;</code> tags under each relevant node
    *  (regardless of whether the tag contains the {@link Cloudinary#responsive|responsive} class).
    * @param {Element[]} nodes The parent nodes where you want to search for &lt;img&gt; tags.
    * @param {Object} [options] The {@link Cloudinary#cloudinary_update|cloudinary_update} options to apply.
    * @see <a href="https://cloudinary.com/documentation/image_transformation_reference"
    *  target="_blank">Available image transformations</a>
    * @function Cloudinary#processImageTags
    */
  }, {
    key: "processImageTags",
    value: function processImageTags(nodes, options) {
      if (isEmpty(nodes)) {
        // similar to `$.fn.cloudinary`
        return this;
      }
      options = defaults({}, options || {}, this.config());
      var images = nodes.filter(function (node) {
        return /^img$/i.test(node.tagName);
      }).map(function (node) {
        var imgOptions = assign_default()({
          width: node.getAttribute('width'),
          height: node.getAttribute('height'),
          src: node.getAttribute('src')
        }, options);
        var publicId = imgOptions['source'] || imgOptions['src'];
        delete imgOptions['source'];
        delete imgOptions['src'];
        var attr = new src_transformation(imgOptions).toHtmlAttributes();
        lodash_setData(node, 'src-cache', url_url(publicId, imgOptions));
        node.setAttribute('width', attr.width);
        node.setAttribute('height', attr.height);
        return node;
      });
      this.cloudinary_update(images, options);
      return this;
    }

    /**
    * Updates the dpr (for `dpr_auto`) and responsive (for `w_auto`) fields according to
    *  the current container size and the device pixel ratio.<br/>
    *  <b>Note</b>:`w_auto` is updated only for images marked with the `cld-responsive`
    *  (or other defined {@link Cloudinary#responsive|responsive}) class.
    * @function Cloudinary#cloudinary_update
    * @param {(Array|string|NodeList)} elements - The HTML image elements to modify.
    * @param {Object} options
    * @param {boolean|string} [options.responsive_use_breakpoints=true]
    * Possible values:<br/>
    *  - `true`: Always use breakpoints for width.<br/>
    *  - `resize`: Use exact width on first render and breakpoints on resize.<br/>
    *  - `false`: Always use exact width.
    * @param {boolean} [options.responsive] - If `true`, enable responsive on all specified elements.
    *  Alternatively, you can define specific HTML elements to modify by adding the `cld-responsive`
    *  (or other custom-defined {@link Cloudinary#responsive|responsive_class}) class to those elements.
    * @param {boolean} [options.responsive_preserve_height] - If `true`, original css height is preserved.
    *  Should be used only if the transformation supports different aspect ratios.
    */
  }, {
    key: "cloudinary_update",
    value: function cloudinary_update(elements, options) {
      var _this2 = this;
      var containerWidth, dataSrc, match, ref4, requiredWidth;
      if (elements === null) {
        return this;
      }
      if (options == null) {
        options = {};
      }
      var responsive = options.responsive != null ? options.responsive : this.config('responsive');
      elements = normalizeToArray(elements);
      var responsiveClass;
      if (this.responsiveConfig && this.responsiveConfig.responsive_class != null) {
        responsiveClass = this.responsiveConfig.responsive_class;
      } else if (options.responsive_class != null) {
        responsiveClass = options.responsive_class;
      } else {
        responsiveClass = this.config('responsive_class');
      }
      var roundDpr = options.round_dpr != null ? options.round_dpr : this.config('round_dpr');
      elements.forEach(function (tag) {
        if (/img/i.test(tag.tagName)) {
          var setUrl = true;
          if (responsive) {
            lodash_addClass(tag, responsiveClass);
          }
          dataSrc = lodash_getData(tag, 'src-cache') || lodash_getData(tag, 'src');
          if (!isEmpty(dataSrc)) {
            // Update dpr according to the device's devicePixelRatio
            dataSrc = updateDpr.call(_this2, dataSrc, roundDpr);
            if (htmltag.isResponsive(tag, responsiveClass)) {
              containerWidth = cloudinary_findContainerWidth(tag);
              if (containerWidth !== 0) {
                if (/w_auto:breakpoints/.test(dataSrc)) {
                  requiredWidth = cloudinary_maxWidth(containerWidth, tag);
                  if (requiredWidth) {
                    dataSrc = dataSrc.replace(/w_auto:breakpoints([_0-9]*)(:[0-9]+)?/, "w_auto:breakpoints$1:".concat(requiredWidth));
                  } else {
                    setUrl = false;
                  }
                } else {
                  match = /w_auto(:(\d+))?/.exec(dataSrc);
                  if (match) {
                    requiredWidth = applyBreakpoints.call(_this2, tag, containerWidth, match[2], options);
                    requiredWidth = cloudinary_maxWidth(requiredWidth, tag);
                    if (requiredWidth) {
                      dataSrc = dataSrc.replace(/w_auto[^,\/]*/g, "w_".concat(requiredWidth));
                    } else {
                      setUrl = false;
                    }
                  }
                }
                lodash_removeAttribute(tag, 'width');
                if (!options.responsive_preserve_height) {
                  lodash_removeAttribute(tag, 'height');
                }
              } else {
                // Container doesn't know the size yet - usually because the image is hidden or outside the DOM.
                setUrl = false;
              }
            }
            var isLazyLoading = options.loading === 'lazy' && !_this2.isNativeLazyLoadSupported() && _this2.isLazyLoadSupported() && !elements[0].getAttribute('src');
            if (setUrl || isLazyLoading) {
              // If data-width exists, set width to be data-width
              _this2.setAttributeIfExists(elements[0], 'width', 'data-width');
            }
            if (setUrl && !isLazyLoading) {
              lodash_setAttribute(tag, 'src', dataSrc);
            }
          }
        }
      });
      return this;
    }

    /**
     * Sets element[toAttribute] = element[fromAttribute] if element[fromAttribute] is set
     * @param element
     * @param toAttribute
     * @param fromAttribute
     */
  }, {
    key: "setAttributeIfExists",
    value: function setAttributeIfExists(element, toAttribute, fromAttribute) {
      var attributeValue = element.getAttribute(fromAttribute);
      if (attributeValue != null) {
        lodash_setAttribute(element, toAttribute, attributeValue);
      }
    }

    /**
     * Returns true if Intersection Observer API is supported
     * @returns {boolean}
     */
  }, {
    key: "isLazyLoadSupported",
    value: function isLazyLoadSupported() {
      return window && 'IntersectionObserver' in window;
    }

    /**
     * Returns true if using Chrome
     * @returns {boolean}
     */
  }, {
    key: "isNativeLazyLoadSupported",
    value: function isNativeLazyLoadSupported() {
      return 'loading' in HTMLImageElement.prototype;
    }

    /**
     * Returns a {@link Transformation} object, initialized with the specified options, for chaining purposes.
     * @function Cloudinary#transformation
     * @param {Object} options The {@link Transformation} options to apply.
     * @return {Transformation}
     * @see Transformation
     * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
     *  Available image transformations</a>
     * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
     *  Available video transformations</a>
     */
  }, {
    key: "transformation",
    value: function transformation(options) {
      return src_transformation["new"](this.config()).fromOptions(options).setParent(this);
    }

    /**
     * @description This function will append a TransparentVideo element to the htmlElContainer passed to it.
     *              TransparentVideo can either be an HTML Video tag, or an HTML Canvas Tag.
     * @param {HTMLElement} htmlElContainer
     * @param {string} publicId
     * @param {object} options The {@link TransparentVideoOptions} options to apply - Extends TransformationOptions
     *                 options.playsinline    - HTML Video Tag's native playsinline - passed to video element.
     *                 options.poster         - HTML Video Tag's native poster - passed to video element.
     *                 options.loop           - HTML Video Tag's native loop - passed to video element.
     *                 options?.externalLibraries = { [key: string]: string} - map of external libraries to be loaded
     * @return {Promise<HTMLElement | {status:string, message:string}>}
     */
  }, {
    key: "injectTransparentVideoElement",
    value: function injectTransparentVideoElement(htmlElContainer, publicId) {
      var _this3 = this;
      var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
      return new Promise(function (resolve, reject) {
        if (!htmlElContainer) {
          reject({
            status: 'error',
            message: 'Expecting htmlElContainer to be HTMLElement'
          });
        }
        transparentVideo_enforceOptionsForTransparentVideo(options);
        var videoURL = _this3.video_url(publicId, options);
        transparentVideo_checkSupportForTransparency().then(function (isNativelyTransparent) {
          var mountPromise;
          if (isNativelyTransparent) {
            mountPromise = transparentVideo_mountCloudinaryVideoTag(htmlElContainer, _this3, publicId, options);
            resolve(htmlElContainer);
          } else {
            mountPromise = transparentVideo_mountSeeThruCanvasTag(htmlElContainer, videoURL, options);
          }
          mountPromise.then(function () {
            resolve(htmlElContainer);
          })["catch"](function (_ref) {
            var status = _ref.status,
              message = _ref.message;
            reject({
              status: status,
              message: message
            });
          });

          // catch for checkSupportForTransparency()
        })["catch"](function (_ref2) {
          var status = _ref2.status,
            message = _ref2.message;
          reject({
            status: status,
            message: message
          });
        });
      });
    }
  }], [{
    key: "new",
    value: function _new(options) {
      return new this(options);
    }
  }]);
}();
assign_default()(cloudinary_Cloudinary, constants_namespaceObject);
/* harmony default export */ var cloudinary = (cloudinary_Cloudinary);
// CONCATENATED MODULE: ./src/namespace/cloudinary-core-shrinkwrap.js
/**
 * Creates the namespace for Cloudinary
 */

















/* harmony default export */ var cloudinary_core_shrinkwrap = __webpack_exports__["default"] = ({
  ClientHintsMetaTag: clienthintsmetatag,
  Cloudinary: cloudinary,
  Condition: condition,
  Configuration: src_configuration,
  Expression: expression,
  crc32: src_crc32,
  FetchLayer: fetchlayer,
  HtmlTag: htmltag,
  ImageTag: imagetag,
  Layer: layer_layer,
  PictureTag: picturetag,
  SubtitlesLayer: subtitleslayer,
  TextLayer: textlayer,
  Transformation: src_transformation,
  utf8_encode: src_utf8_encode,
  Util: lodash_namespaceObject,
  VideoTag: videotag
});


/***/ })

/******/ });
});
//# sourceMappingURL=cloudinary-core-shrinkwrap.js.map