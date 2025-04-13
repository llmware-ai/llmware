var ReplSetManager = require('mongodb-topology-manager').ReplSet,
  f = require('util').format;

var rsOptions = {
  server: {
    keyFile: __dirname + '/test/functional/data/keyfile.txt',
    auth: null,
    replSet: 'rs'
  },
  client: {
    replSet: 'rs'
  }
}

// Set up the nodes
var nodes = [{
  options: {
    bind_ip: 'localhost', port: 31000,
    dbpath: f('%s/../db/31000', __dirname),
  }
}, {
  options: {
    bind_ip: 'localhost', port: 31001,
    dbpath: f('%s/../db/31001', __dirname),
  }
}, {
  options: {
    bind_ip: 'localhost', port: 31002,
    dbpath: f('%s/../db/31002', __dirname),
  }
}]

// Merge in any node start up options
for(var i = 0; i < nodes.length; i++) {
  for(var name in rsOptions.server) {
    nodes[i].options[name] = rsOptions.server[name];
  }
}

// Create a manager
var replicasetManager = new ReplSetManager('mongod', nodes, rsOptions.client);
// Purge the set
replicasetManager.purge().then(function() {
  // Start the server
  replicasetManager.start().then(function() {
    process.exit(0);
  }).catch(function(e) {
    console.log("====== ")
    console.dir(e)
    // // console.dir(e);
  });
});
