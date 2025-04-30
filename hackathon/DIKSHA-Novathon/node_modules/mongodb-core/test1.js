var Server = require('./lib/topologies/server');

// Attempt to connect
var server = new Server({
  host: 'localhost', port: 27017, socketTimeout: 500
});

// function executeCursors(_server, cb) {
//   var count = 100;
//
//   for(var i = 0; i < 100; i++) {
//     // Execute the write
//     var cursor = _server.cursor('test.test', {
//         find: 'test.test'
//       , query: {a:1}
//     }, {readPreference: new ReadPreference('secondary')});
//
//     // Get the first document
//     cursor.next(function(err, doc) {
//       count = count - 1;
//       if(err) console.dir(err)
//       if(count == 0) return cb();
//     });
//   }
// }

server.on('connect', function(_server) {

  setInterval(function() {
    _server.insert('test.test', [{a:1}], function(err, r) {
      console.log("insert")
    });
  }, 1000)
  // console.log("---------------------------------- 0")
  // // Attempt authentication
  // _server.auth('scram-sha-1', 'admin', 'root', 'root', function(err, r) {
  //   console.log("---------------------------------- 1")
  //   // console.dir(err)
  //   // console.dir(r)
  //
  //   _server.insert('test.test', [{a:1}], function(err, r) {
  //     console.log("---------------------------------- 2")
  //     console.dir(err)
  //     if(r)console.dir(r.result)
  //     var name = null;
  //
  //     _server.on('joined', function(_t, _server) {
  //       if(name == _server.name) {
  //         console.log("=========== joined :: " + _t + " :: " + _server.name)
  //         executeCursors(_server, function() {
  //         });
  //       }
  //     })
  //
  //     // var s = _server.s.replicaSetState.secondaries[0];
  //     // s.destroy({emitClose:true});
  //     executeCursors(_server, function() {
  //       console.log("============== 0")
  //       // Attempt to force a server reconnect
  //       var s = _server.s.replicaSetState.secondaries[0];
  //       name = s.name;
  //       s.destroy({emitClose:true});
  //       // console.log("============== 1")
  //
  //       // _server.destroy();
  //       // test.done();
  //     });
  //   });
  // });
});

server.connect();
