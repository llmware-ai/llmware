import {
  isArray,
  isMaybeThenable
} from './utils';

import {
  noop,
  reject,
  fulfill,
  subscribe,
  FULFILLED,
  REJECTED,
  PENDING,
  getThen,
  handleMaybeThenable
} from './-internal';

import then from './then';
import Promise from './promise';
import originalResolve from './promise/resolve';
import originalThen from './then';
import { makePromise, PROMISE_ID } from './-internal';

export default Enumerator;
function Enumerator(Constructor, input) {
  this._instanceConstructor = Constructor;
  this.promise = new Constructor(noop);

  if (!this.promise[PROMISE_ID]) {
    makePromise(this.promise);
  }

  if (isArray(input)) {
    this._input     = input;
    this.length     = input.length;
    this._remaining = input.length;

    this._result = new Array(this.length);

    if (this.length === 0) {
      fulfill(this.promise, this._result);
    } else {
      this.length = this.length || 0;
      this._enumerate();
      if (this._remaining === 0) {
        fulfill(this.promise, this._result);
      }
    }
  } else {
    reject(this.promise, validationError());
  }
}

function validationError() {
  return new Error('Array Methods must be provided an Array');
};

Enumerator.prototype._enumerate = function() {
  var length  = this.length;
  var input   = this._input;

  for (var i = 0; this._state === PENDING && i < length; i++) {
    this._eachEntry(input[i], i);
  }
};

Enumerator.prototype._eachEntry = function(entry, i) {
  var c = this._instanceConstructor;
  var resolve = c.resolve;

  if (resolve === originalResolve) {
    var then = getThen(entry);

    if (then === originalThen &&
        entry._state !== PENDING) {
      this._settledAt(entry._state, i, entry._result);
    } else if (typeof then !== 'function') {
      this._remaining--;
      this._result[i] = entry;
    } else if (c === Promise) {
      var promise = new c(noop);
      handleMaybeThenable(promise, entry, then);
      this._willSettleAt(promise, i);
    } else {
      this._willSettleAt(new c(function(resolve) { resolve(entry); }), i);
    }
  } else {
    this._willSettleAt(resolve(entry), i);
  }
};

Enumerator.prototype._settledAt = function(state, i, value) {
  var promise = this.promise;

  if (promise._state === PENDING) {
    this._remaining--;

    if (state === REJECTED) {
      reject(promise, value);
    } else {
      this._result[i] = value;
    }
  }

  if (this._remaining === 0) {
    fulfill(promise, this._result);
  }
};

Enumerator.prototype._willSettleAt = function(promise, i) {
  var enumerator = this;

  subscribe(promise, undefined, function(value) {
    enumerator._settledAt(FULFILLED, i, value);
  }, function(reason) {
    enumerator._settledAt(REJECTED, i, reason);
  });
};
