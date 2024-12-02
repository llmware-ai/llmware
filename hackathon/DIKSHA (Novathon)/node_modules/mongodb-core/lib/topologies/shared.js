"use strict"

var os = require('os'),
  f = require('util').format;

/**
 * Emit event if it exists
 * @method
 */
function emitSDAMEvent(self, event, description) {
  if(self.listeners(event).length > 0) {
    self.emit(event, description);
  }
}

// Get package.json variable
var driverVersion = require('../../package.json').version;
var nodejsversion = f('Node.js %s, %s', process.version, os.endianness());
var type = os.type();
var name = process.platform;
var architecture = process.arch;
var release = os.release();

function createClientInfo(options) {
  // Build default client information
  var clientInfo = options.clientInfo ? clone(options.clientInfo) : {
    driver: {
      name: "nodejs-core",
      version: driverVersion
    },
    os: {
      type: type,
      name: name,
      architecture: architecture,
      version: release
    }
  }

  // Is platform specified
  if(clientInfo.platform && clientInfo.platform.indexOf('mongodb-core') == -1) {
    clientInfo.platform = f('%s, mongodb-core: %s', clientInfo.platform, driverVersion);
  } else if(!clientInfo.platform){
    clientInfo.platform = nodejsversion;
  }

  // Do we have an application specific string
  if(options.appname) {
    // Cut at 128 bytes
    var buffer = new Buffer(options.appname);
    // Return the truncated appname
    var appname = buffer.length > 128 ? buffer.slice(0, 128).toString('utf8') : options.appname;
    // Add to the clientInfo
    clientInfo.application = { name: appname };
  }

  return clientInfo;
}

function clone(object) {
  return JSON.parse(JSON.stringify(object));
}

var getPreviousDescription = function(self) {
  if(!self.s.serverDescription) {
    self.s.serverDescription = {
      address: self.name,
      arbiters: [], hosts: [], passives: [], type: 'Unknown'
    }
  }

  return self.s.serverDescription;
}

var emitServerDescriptionChanged = function(self, description) {
  if(self.listeners('serverDescriptionChanged').length > 0) {
    // Emit the server description changed events
    self.emit('serverDescriptionChanged', {
      topologyId: self.s.topologyId != -1 ? self.s.topologyId : self.id, address: self.name,
      previousDescription: getPreviousDescription(self),
      newDescription: description
    });

    self.s.serverDescription = description;
  }
}

var getPreviousTopologyDescription = function(self) {
  if(!self.s.topologyDescription) {
    self.s.topologyDescription = {
      topologyType: 'Unknown',
      servers: [{
        address: self.name, arbiters: [], hosts: [], passives: [], type: 'Unknown'
      }]
    }
  }

  return self.s.topologyDescription;
}

var emitTopologyDescriptionChanged = function(self, description) {
  if(self.listeners('topologyDescriptionChanged').length > 0) {
    // Emit the server description changed events
    self.emit('topologyDescriptionChanged', {
      topologyId: self.s.topologyId != -1 ? self.s.topologyId : self.id, address: self.name,
      previousDescription: getPreviousTopologyDescription(self),
      newDescription: description
    });

    self.s.serverDescription = description;
  }
}

var changedIsMaster = function(self, currentIsmaster, ismaster) {
  var currentType = getTopologyType(self, currentIsmaster);
  var newType = getTopologyType(self, ismaster);
  if(newType != currentType) return true;
  return false;
}

var getTopologyType = function(self, ismaster) {
  if(!ismaster) {
    ismaster = self.ismaster;
  }

  if(!ismaster) return 'Unknown';
  if(ismaster.ismaster && ismaster.msg == 'isdbgrid') return 'Mongos';
  if(ismaster.ismaster && !ismaster.hosts) return 'Standalone';
  if(ismaster.ismaster) return 'RSPrimary';
  if(ismaster.secondary) return 'RSSecondary';
  if(ismaster.arbiterOnly) return 'RSArbiter';
  return 'Unknown';
}

var inquireServerState = function(self) {
  return function(callback) {
    if(self.s.state == 'destroyed') return;
    // Record response time
    var start = new Date().getTime();

    // emitSDAMEvent
    emitSDAMEvent(self, 'serverHeartbeatStarted', { connectionId: self.name });

    // Attempt to execute ismaster command
    self.command('admin.$cmd', { ismaster:true },  { monitoring:true }, function(err, r) {
      if(!err) {
        // Legacy event sender
        self.emit('ismaster', r, self);

        // Calculate latencyMS
        var latencyMS = new Date().getTime() - start;

        // Server heart beat event
        emitSDAMEvent(self, 'serverHeartbeatSucceeded', { durationMS: latencyMS, reply: r.result, connectionId: self.name });

        // Did the server change
        if(changedIsMaster(self, self.s.ismaster, r.result)) {
          // Emit server description changed if something listening
          emitServerDescriptionChanged(self, {
            address: self.name, arbiters: [], hosts: [], passives: [], type: !self.s.inTopology ? 'Standalone' : getTopologyType(self)
          });
        }

        // Updat ismaster view
        self.s.ismaster = r.result;

        // Set server response time
        self.s.isMasterLatencyMS = latencyMS;
      } else {
        emitSDAMEvent(self, 'serverHeartbeatFailed', { durationMS: latencyMS, failure: err, connectionId: self.name });
      }

      // Peforming an ismaster monitoring callback operation
      if(typeof callback == 'function') {
        return callback(err, r);
      }

      // Perform another sweep
      self.s.inquireServerStateTimeout = setTimeout(inquireServerState(self), self.s.haInterval);
    });
  };
}

//
// Clone the options
var cloneOptions = function(options) {
  var opts = {};
  for(var name in options) {
    opts[name] = options[name];
  }
  return opts;
}

function Interval(fn, time) {
  var timer = false;

  this.start = function () {
    if (!this.isRunning()) {
      timer = setInterval(fn, time);
    }

    return this;
  };

  this.stop = function () {
    clearInterval(timer);
    timer = false;
    return this;
  };

  this.isRunning = function () {
    return timer !== false;
  };
}

function Timeout(fn, time) {
  var timer = false;

  this.start = function () {
    if (!this.isRunning()) {
      timer = setTimeout(function() {
        fn();
        if (timer && timer._called === undefined) {
          // The artificial _called is set here for compatibility with node.js 0.10.x/0.12.x versions
          timer._called = true;
        }
      }, time);
    }
    return this;
  };

  this.stop = function () {
    clearTimeout(timer);
    timer = false;
    return this;
  };

  this.isRunning = function () {
    if(timer && timer._called) return false;
    return timer !== false;
  };
}

function diff(previous, current) {
  // Difference document
  var diff = {
    servers: []
  }

  // Previous entry
  if(!previous) {
    previous = { servers: [] };
  }

  // Check if we have any previous servers missing in the current ones
  for(var i = 0; i < previous.servers.length; i++) {
    var found = false;

    for(var j = 0; j < current.servers.length; j++) {
      if(current.servers[j].address.toLowerCase()
        === previous.servers[i].address.toLowerCase()) {
          found = true;
          break;
        }
    }

    if(!found) {
      // Add to the diff
      diff.servers.push({
        address: previous.servers[i].address,
        from: previous.servers[i].type,
        to: 'Unknown',
      });
    }
  }

  // Check if there are any severs that don't exist
  for(var j = 0; j < current.servers.length; j++) {
    var found = false;

    // Go over all the previous servers
    for(var i = 0; i < previous.servers.length; i++) {
      if(previous.servers[i].address.toLowerCase()
        === current.servers[j].address.toLowerCase()) {
        found = true;
        break;
      }
    }

    // Add the server to the diff
    if(!found) {
      diff.servers.push({
        address: current.servers[j].address,
        from: 'Unknown',
        to: current.servers[j].type,
      });
    }
  }

  // Got through all the servers
  for(var i = 0; i < previous.servers.length; i++) {
    var prevServer = previous.servers[i];

    // Go through all current servers
    for(var j = 0; j < current.servers.length; j++) {
      var currServer = current.servers[j];

      // Matching server
      if(prevServer.address.toLowerCase() === currServer.address.toLowerCase()) {
        // We had a change in state
        if(prevServer.type != currServer.type) {
          diff.servers.push({
            address: prevServer.address,
            from: prevServer.type,
            to: currServer.type
          });
        }
      }
    }
  }

  // Return difference
  return diff;
}

module.exports.inquireServerState = inquireServerState
module.exports.getTopologyType = getTopologyType;
module.exports.emitServerDescriptionChanged = emitServerDescriptionChanged;
module.exports.emitTopologyDescriptionChanged = emitTopologyDescriptionChanged;
module.exports.cloneOptions = cloneOptions;
module.exports.createClientInfo = createClientInfo;
module.exports.clone = clone;
module.exports.diff = diff;
module.exports.Interval = Interval;
module.exports.Timeout = Timeout;
