Testing setup
=============

Single Server
-------------
mongod --dbpath=./db

Replicaset
----------
mongo --nodb
var x = new ReplSetTest({"useHostName":"false", "nodes" : {node0 : {}, node1 : {}, node2 : {}}})
x.startSet();
var config = x.getReplSetConfig()
x.initiate(config);

Mongos
------
var s = new ShardingTest( "auth1", 1 , 0 , 2 , {rs: true, noChunkSize : true});