'use strict';
var util = require('util');
var EventEmitter = require('events').EventEmitter;
function toArray(arr, start, end) {
  return Array.prototype.slice.call(arr, start, end)
}
function strongUnshift(x, arrLike) {
  var arr = toArray(arrLike);
  arr.unshift(x);
  return arr;
}


/**
 * MPromise constructor.
 *
 * _NOTE: The success and failure event names can be overridden by setting `Promise.SUCCESS` and `Promise.FAILURE` respectively._
 *
 * @param {Function} back a function that accepts `fn(err, ...){}` as signature
 * @inherits NodeJS EventEmitter http://nodejs.org/api/events.html#events_class_events_eventemitter
 * @event `reject`: Emits when the promise is rejected (event name may be overridden)
 * @event `fulfill`: Emits when the promise is fulfilled (event name may be overridden)
 * @api public
 */
function Promise(back) {
  this.emitter = new EventEmitter();
  this.emitted = {};
  this.ended = false;
  if ('function' == typeof back) {
    this.ended = true;
    this.onResolve(back);
  }
}


/*
 * Module exports.
 */
module.exports = Promise;


/*!
 * event names
 */
Promise.SUCCESS = 'fulfill';
Promise.FAILURE = 'reject';


/**
 * Adds `listener` to the `event`.
 *
 * If `event` is either the success or failure event and the event has already been emitted, the`listener` is called immediately and passed the results of the original emitted event.
 *
 * @param {String} event
 * @param {Function} callback
 * @return {MPromise} this
 * @api private
 */
Promise.prototype.on = function (event, callback) {
  if (this.emitted[event])
    callback.apply(undefined, this.emitted[event]);
  else
    this.emitter.on(event, callback);

  return this;
};


/**
 * Keeps track of emitted events to run them on `on`.
 *
 * @api private
 */
Promise.prototype.safeEmit = function (event) {
  // ensures a promise can't be fulfill() or reject() more than once
  if (event == Promise.SUCCESS || event == Promise.FAILURE) {
    if (this.emitted[Promise.SUCCESS] || this.emitted[Promise.FAILURE]) {
      return this;
    }
    this.emitted[event] = toArray(arguments, 1);
  }

  this.emitter.emit.apply(this.emitter, arguments);
  return this;
};


/**
 * @api private
 */
Promise.prototype.hasRejectListeners = function () {
  return EventEmitter.listenerCount(this.emitter, Promise.FAILURE) > 0;
};


/**
 * Fulfills this promise with passed arguments.
 *
 * If this promise has already been fulfilled or rejected, no action is taken.
 *
 * @api public
 */
Promise.prototype.fulfill = function () {
  return this.safeEmit.apply(this, strongUnshift(Promise.SUCCESS, arguments));
};


/**
 * Rejects this promise with `reason`.
 *
 * If this promise has already been fulfilled or rejected, no action is taken.
 *
 * @api public
 * @param {Object|String} reason
 * @return {MPromise} this
 */
Promise.prototype.reject = function (reason) {
  if (this.ended && !this.hasRejectListeners())
    throw reason;
  return this.safeEmit(Promise.FAILURE, reason);
};


/**
 * Resolves this promise to a rejected state if `err` is passed or
 * fulfilled state if no `err` is passed.
 *
 * @param {Error} [err] error or null
 * @param {Object} [val] value to fulfill the promise with
 * @api public
 */
Promise.prototype.resolve = function (err, val) {
  if (err) return this.reject(err);
  return this.fulfill(val);
};


/**
 * Adds a listener to the SUCCESS event.
 *
 * @return {MPromise} this
 * @api public
 */
Promise.prototype.onFulfill = function (fn) {
  if (!fn) return this;
  if ('function' != typeof fn) throw new TypeError("fn should be a function");
  return this.on(Promise.SUCCESS, fn);
};


/**
 * Adds a listener to the FAILURE event.
 *
 * @return {MPromise} this
 * @api public
 */
Promise.prototype.onReject = function (fn) {
  if (!fn) return this;
  if ('function' != typeof fn) throw new TypeError("fn should be a function");
  return this.on(Promise.FAILURE, fn);
};


/**
 * Adds a single function as a listener to both SUCCESS and FAILURE.
 *
 * It will be executed with traditional node.js argument position:
 * function (err, args...) {}
 *
 * Also marks the promise as `end`ed, since it's the common use-case, and yet has no
 * side effects unless `fn` is undefined or null.
 *
 * @param {Function} fn
 * @return {MPromise} this
 */
Promise.prototype.onResolve = function (fn) {
  if (!fn) return this;
  if ('function' != typeof fn) throw new TypeError("fn should be a function");
  this.on(Promise.FAILURE, function (err) { fn.call(this, err); });
  this.on(Promise.SUCCESS, function () { fn.apply(this, strongUnshift(null, arguments)); });
  return this;
};


/**
 * Creates a new promise and returns it. If `onFulfill` or
 * `onReject` are passed, they are added as SUCCESS/ERROR callbacks
 * to this promise after the next tick.
 *
 * Conforms to [promises/A+](https://github.com/promises-aplus/promises-spec) specification. Read for more detail how to use this method.
 *
 * ####Example:
 *
 *     var p = new Promise;
 *     p.then(function (arg) {
 *       return arg + 1;
 *     }).then(function (arg) {
 *       throw new Error(arg + ' is an error!');
 *     }).then(null, function (err) {
 *       assert.ok(err instanceof Error);
 *       assert.equal('2 is an error', err.message);
 *     });
 *     p.complete(1);
 *
 * @see promises-A+ https://github.com/promises-aplus/promises-spec
 * @param {Function} onFulfill
 * @param {Function} [onReject]
 * @return {MPromise} newPromise
 */
Promise.prototype.then = function (onFulfill, onReject) {
  var newPromise = new Promise;

  if ('function' == typeof onFulfill) {
    this.onFulfill(handler(newPromise, onFulfill));
  } else {
    this.onFulfill(newPromise.fulfill.bind(newPromise));
  }

  if ('function' == typeof onReject) {
    this.onReject(handler(newPromise, onReject));
  } else {
    this.onReject(newPromise.reject.bind(newPromise));
  }

  return newPromise;
};


function handler(promise, fn) {
  function newTickHandler() {
    var pDomain = promise.emitter.domain;
    if (pDomain && pDomain !== process.domain) pDomain.enter();
    try {
      var x = fn.apply(undefined, boundHandler.args);
    } catch (err) {
      promise.reject(err);
      return;
    }
    resolve(promise, x);
  }
  function boundHandler() {
    boundHandler.args = arguments;
    process.nextTick(newTickHandler);
  }
  return boundHandler;
}


function resolve(promise, x) {
  function fulfillOnce() {
    if (done++) return;
    resolve.apply(undefined, strongUnshift(promise, arguments));
  }
  function rejectOnce(reason) {
    if (done++) return;
    promise.reject(reason);
  }

  if (promise === x) {
    promise.reject(new TypeError("promise and x are the same"));
    return;
  }
  var rest = toArray(arguments, 1);
  var type = typeof x;
  if ('undefined' == type || null == x || !('object' == type || 'function' == type)) {
    promise.fulfill.apply(promise, rest);
    return;
  }

  try {
    var theThen = x.then;
  } catch (err) {
    promise.reject(err);
    return;
  }

  if ('function' != typeof theThen) {
    promise.fulfill.apply(promise, rest);
    return;
  }

  var done = 0;
  try {
    var ret = theThen.call(x, fulfillOnce, rejectOnce);
    return ret;
  } catch (err) {
    if (done++) return;
    promise.reject(err);
  }
}


/**
 * Signifies that this promise was the last in a chain of `then()s`: if a handler passed to the call to `then` which produced this promise throws, the exception will go uncaught.
 *
 * ####Example:
 *
 *     var p = new Promise;
 *     p.then(function(){ throw new Error('shucks') });
 *     setTimeout(function () {
 *       p.fulfill();
 *       // error was caught and swallowed by the promise returned from
 *       // p.then(). we either have to always register handlers on
 *       // the returned promises or we can do the following...
 *     }, 10);
 *
 *     // this time we use .end() which prevents catching thrown errors
 *     var p = new Promise;
 *     var p2 = p.then(function(){ throw new Error('shucks') }).end(); // <--
 *     setTimeout(function () {
 *       p.fulfill(); // throws "shucks"
 *     }, 10);
 *
 * @api public
 * @param {Function} [onReject]
 * @return {MPromise} this
 */
Promise.prototype.end = Promise.prototype['catch'] = function (onReject) {
  if (!onReject && !this.hasRejectListeners())
    onReject = function idRejector(e) { throw e; };
  this.onReject(onReject);
  this.ended = true;
  return this;
};


/**
 * A debug utility function that adds handlers to a promise that will log some output to the `console`
 *
 * ####Example:
 *
 *     var p = new Promise;
 *     p.then(function(){ throw new Error('shucks') });
 *     setTimeout(function () {
 *       p.fulfill();
 *       // error was caught and swallowed by the promise returned from
 *       // p.then(). we either have to always register handlers on
 *       // the returned promises or we can do the following...
 *     }, 10);
 *
 *     // this time we use .end() which prevents catching thrown errors
 *     var p = new Promise;
 *     var p2 = p.then(function(){ throw new Error('shucks') }).end(); // <--
 *     setTimeout(function () {
 *       p.fulfill(); // throws "shucks"
 *     }, 10);
 *
 * @api public
 * @param {MPromise} p
 * @param {String} name
 * @return {MPromise} this
 */
Promise.trace = function (p, name) {
  p.then(
    function () {
      console.log("%s fulfill %j", name, toArray(arguments));
    },
    function () {
      console.log("%s reject %j", name, toArray(arguments));
    }
  )
};


Promise.prototype.chain = function (p2) {
  var p1 = this;
  p1.onFulfill(p2.fulfill.bind(p2));
  p1.onReject(p2.reject.bind(p2));
  return p2;
};


Promise.prototype.all = function (promiseOfArr) {
  var pRet = new Promise;
  this.then(promiseOfArr).then(
    function (promiseArr) {
      var count = 0;
      var ret = [];
      var errSentinel;
      if (!promiseArr.length) pRet.resolve();
      promiseArr.forEach(function (promise, index) {
        if (errSentinel) return;
        count++;
        promise.then(
          function (val) {
            if (errSentinel) return;
            ret[index] = val;
            --count;
            if (count == 0) pRet.fulfill(ret);
          },
          function (err) {
            if (errSentinel) return;
            errSentinel = err;
            pRet.reject(err);
          }
        );
      });
      return pRet;
    }
    , pRet.reject.bind(pRet)
  );
  return pRet;
};


Promise.hook = function (arr) {
  var p1 = new Promise;
  var pFinal = new Promise;
  var signalP = function () {
    --count;
    if (count == 0)
      pFinal.fulfill();
    return pFinal;
  };
  var count = 1;
  var ps = p1;
  arr.forEach(function (hook) {
    ps = ps.then(
      function () {
        var p = new Promise;
        count++;
        hook(p.resolve.bind(p), signalP);
        return p;
      }
    )
  });
  ps = ps.then(signalP);
  p1.resolve();
  return ps;
};


/* This is for the A+ tests, but it's very useful as well */
Promise.fulfilled = function fulfilled() { var p = new Promise; p.fulfill.apply(p, arguments); return p; };
Promise.rejected = function rejected(reason) { return new Promise().reject(reason); };
Promise.deferred = function deferred() {
  var p = new Promise;
  return {
    promise: p,
    reject: p.reject.bind(p),
    resolve: p.fulfill.bind(p),
    callback: p.resolve.bind(p)
  }
};
/* End A+ tests adapter bit */
