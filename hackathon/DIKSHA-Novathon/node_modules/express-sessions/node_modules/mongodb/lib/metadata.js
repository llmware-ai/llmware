var f = require('util').format;

var Define = function(name, object, stream) {
  this.name = name;
  this.object = object;
  this.stream = typeof stream == 'boolean' ? stream : false;
  this.instrumentations = {};
}

Define.prototype.classMethod = function(name, options) {
  var keys = Object.keys(options).sort();
  var key = generateKey(keys, options);

  // Add a list of instrumentations
  if(this.instrumentations[key] == null) {
    this.instrumentations[key] = {
      methods: [], options: options
    }
  }

  // Push to list of method for this instrumentation
  this.instrumentations[key].methods.push(name);
}

var generateKey = function(keys, options) {
  var parts = [];
  for(var i = 0; i < keys.length; i++) {
    parts.push(f('%s=%s', keys[i], options[keys[i]]));
  }

  return parts.join();
}

Define.prototype.staticMethod = function(name, options) {
  options.static = true;
  var keys = Object.keys(options).sort();
  var key = generateKey(keys, options);

  // Add a list of instrumentations
  if(this.instrumentations[key] == null) {
    this.instrumentations[key] = {
      methods: [], options: options
    }
  }

  // Push to list of method for this instrumentation
  this.instrumentations[key].methods.push(name);
}

Define.prototype.generate = function() {
  // Generate the return object
  var object = {
    name: this.name, obj: this.object, stream: this.stream,
    instrumentations: []
  }

  for(var name in this.instrumentations) {
    object.instrumentations.push(this.instrumentations[name]);
  }

  return object;
}

module.exports = Define;
