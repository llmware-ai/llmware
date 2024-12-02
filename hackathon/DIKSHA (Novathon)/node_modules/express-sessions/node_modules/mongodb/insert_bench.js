var MongoClient = require('./').MongoClient,
  assert = require('assert');

// var memwatch = require('memwatch-next');
// memwatch.on('leak', function(info) {
//   console.log("======== leak")
// });
//
// memwatch.on('stats', function(stats) {
//   console.log("======== stats")
//   console.dir(stats)
// });

// // Take first snapshot
// var hd = new memwatch.HeapDiff();

MongoClient.connect('mongodb://localhost:27017/bench', function(err, db) {
  var docs = [];
  var total = 1000;
  var count = total;
  var measurements = [];

  // Insert a bunch of documents
  for(var i = 0; i < 100; i++) {
    docs.push(JSON.parse(data));
  }

  var col = db.collection('inserts');

  function execute(col, callback) {
    var start = new Date().getTime();

    col.find({}).limit(100).toArray(function(e, docs) {
      measurements.push(new Date().getTime() - start);
      assert.equal(null, e);
      callback();
    });
  }

  console.log("== insert documents")
  col.insert(docs, function(e, r) {
    docs = [];
    assert.equal(null, e);

    console.log("== start bench")
    for(var i = 0; i < total; i++) {
      execute(col, function(e) {
        count = count - 1;

        if(count == 0) {
          // Calculate total execution time for operations
          var totalTime = measurements.reduce(function(prev, curr) {
            return prev + curr;
          }, 0);

          console.log("===========================================");
          console.log("total time: " + totalTime)

          // var diff = hd.end();
          // console.log("===========================================");
          // console.log(JSON.stringify(diff, null, 2))

          db.close();
          process.exit(0)
        }
      });
    }
  });
});

var data = JSON.stringify({
  "data": [
    {
      "_id": 1,
      "x": 11
    },
    {
      "_id": 2,
      "x": 22
    },
    {
      "_id": 3,
      "x": 33
    }
  ],
  "collection_name": "test",
  "database_name": "command-monitoring-tests",
  "tests": [
    {
      "description": "A successful mixed bulk write",
      "operation": {
        "name": "bulkWrite",
        "arguments": {
          "requests": [
            {
              "insertOne": {
                "document": {
                  "_id": 4,
                  "x": 44
                }
              }
            },
            {
              "updateOne": {
                "filter": {
                  "_id": 3
                },
                "update": {
                  "set": {
                    "x": 333
                  }
                }
              }
            }
          ]
        }
      },
      "expectations": [
        {
          "command_started_event": {
            "command": {
              "insert": "test",
              "documents": [
                {
                  "_id": 4,
                  "x": 44
                }
              ],
              "ordered": true
            },
            "command_name": "insert",
            "database_name": "command-monitoring-tests"
          }
        },
        {
          "command_succeeded_event": {
            "reply": {
              "ok": 1.0,
              "n": 1
            },
            "command_name": "insert"
          }
        },
        {
          "command_started_event": {
            "command": {
              "update": "test",
              "updates": [
                {
                  "q": {
                    "_id": 3
                  },
                  "u": {
                    "set": {
                      "x": 333
                    }
                  },
                  "upsert": false,
                  "multi": false
                }
              ],
              "ordered": true
            },
            "command_name": "update",
            "database_name": "command-monitoring-tests"
          }
        },
        {
          "command_succeeded_event": {
            "reply": {
              "ok": 1.0,
              "n": 1
            },
            "command_name": "update"
          }
        }
      ]
    },
    {
      "description": "A successful unordered bulk write with an unacknowledged write concern",
      "operation": {
        "name": "bulkWrite",
        "arguments": {
          "requests": [
            {
              "insertOne": {
                "document": {
                  "_id": 4,
                  "x": 44
                }
              }
            }
          ],
          "ordered": false,
          "writeConcern": {
            "w": 0
          }
        }
      },
      "expectations": [
        {
          "command_started_event": {
            "command": {
              "insert": "test",
              "documents": [
                {
                  "_id": 4,
                  "x": 44
                }
              ],
              "ordered": false,
              "writeConcern": {
                "w": 0
              }
            },
            "command_name": "insert",
            "database_name": "command-monitoring-tests"
          }
        },
        {
          "command_succeeded_event": {
            "reply": {
              "ok": 1.0
            },
            "command_name": "insert"
          }
        }
      ]
    }
  ]
});
