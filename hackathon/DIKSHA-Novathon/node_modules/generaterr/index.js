/* jshint expr: true */
var util = require('util');

module.exports = function(name, parameters, options) {
  options = options || {};
  options.captureStackTrace = options.captureStackTrace === undefined ? true : false;
  options.inherits = options.inherits || Error;

  var ctor = function() {
    if (!(this instanceof ctor)) {
      var constructorArgs = Array.prototype.slice.call(arguments);
      constructorArgs.unshift(ctor);

      return new (ctor.bind.apply(ctor, constructorArgs))();
    }

    options.inherits.call(this);

    if (options.captureStackTrace) {
      Error.captureStackTrace && Error.captureStackTrace(this, arguments.callee);
    }

    copy(parameters, this);

    var msg = arguments[0];
    if (msg) {
      var args = Array.prototype.slice.call(arguments);

      if (args.length > 1 && typeof args[args.length - 1] == 'object') {
        var instanceParams = args.pop();

        copy(instanceParams, this);
      }

      this.message = util.format.apply(util, args);
    }

    this.name = name;
  };

  util.inherits(ctor, options.inherits);

  return ctor;
};

function copy(from, to) {
  if (from) {
    for (var key in from) {
      if (from.hasOwnProperty(key)) {
        to[key] = from[key];
      }
    }
  }

  return to;
}
