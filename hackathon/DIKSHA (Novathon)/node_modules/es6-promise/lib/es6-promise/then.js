import {
  invokeCallback,
  subscribe,
  FULFILLED,
  REJECTED,
  noop,
  makePromise,
  PROMISE_ID
} from './-internal';

import { asap } from './asap';

export default function then(onFulfillment, onRejection) {
  var parent = this;

  var child = new this.constructor(noop);

  if (child[PROMISE_ID] === undefined) {
    makePromise(child);
  }

  var state = parent._state;

  if (state) {
    var callback = arguments[state - 1];
    asap(function(){
      invokeCallback(state, child, callback, parent._result);
    });
  } else {
    subscribe(parent, child, onFulfillment, onRejection);
  }

  return child;
}
