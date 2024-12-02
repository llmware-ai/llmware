<a name="2.2.34"></a>
## [2.2.34](https://github.com/mongodb/node-mongodb-native/compare/v2.2.33...v2.2.34) (2018-01-03)


### Bug Fixes

* **collection:** allow { upsert: 1 } for findOneAndUpdate() and update() ([#1580](https://github.com/mongodb/node-mongodb-native/issues/1580)) ([0f338c8](https://github.com/mongodb/node-mongodb-native/commit/0f338c8)), closes [Automattic/mongoose#5839](https://github.com/Automattic/mongoose/issues/5839)
* **GridFS:** fix TypeError: doc.data.length is not a function ([811de0c](https://github.com/mongodb/node-mongodb-native/commit/811de0c))
* **import:** adds missing import to lib/authenticate.js ([10db9a2](https://github.com/mongodb/node-mongodb-native/commit/10db9a2))
* **list-collections:** ensure default of primary ReadPreference ([0935306](https://github.com/mongodb/node-mongodb-native/commit/0935306))


### Features

* **ssl:** adds missing ssl options ssl options for `ciphers` and `ecdhCurve` ([bd4fb53](https://github.com/mongodb/node-mongodb-native/commit/bd4fb53))
* **url parser:** add dns seedlist support ([2d357bc](https://github.com/mongodb/node-mongodb-native/commit/2d357bc))
* **core**: update mongodb-core to 2.1.18


2.2.33 2017-10-12
-----------------
* update to mongodb-core 2.1.17

2.2.32 2017-10-11
-----------------
* update to mongodb-core 2.1.16
* ensure that the `cursor` key is always present in aggregation commands
* `Cursor.prototype.hasNext` now propagates errors when using callback
* allow passing `noCursorTimeout` as an option to `find()`
* bubble up `reconnectFailed` event from Server topology

2.2.31 2017-08-08
-----------------
* update mongodb-core to 2.1.15
* allow auth option in MongoClient.connect
* remove duplicate option `promoteLongs` from MongoClient's `connect`
* bulk operations should not throw an error on empty batch

2.2.30 2017-07-07
-----------------
* Update mongodb-core to 2.1.14
* MongoClient
  * add `appname` to list of valid option names
  * added test for passing appname as option
* NODE-1052 ensure user options are applied while parsing connection string uris

2.2.29 2017-06-19
-----------------
* Update mongodb-core to 2.1.13
  * NODE-1039 ensure we force destroy server instances, forcing queue to be flushed.
  *  Use actual server type in standalone SDAM events.
* Allow multiple map calls (Issue #1521, https://github.com/Robbilie).
* Clone insertMany options before mutating (Issue #1522, https://github.com/vkarpov15).
* NODE-1034 Fix GridStore issue caused by Node 8.0.0 breaking backward compatible fs.read API.
* NODE-1026, use  operator instead of skip function in order to avoid useless fetch stage.

2.2.28 2017-06-02
-----------------
* Update mongodb-core to 2.1.12
  * NODE-1019 Set keepAlive to 300 seconds or 1/2 of socketTimeout if socketTimeout < keepAlive.
  * Minor fix to report the correct state on error.
  * NODE-1020 'family' was added to options to provide high priority for ipv6 addresses (Issue #1518, https://github.com/firej).
  * Fix require_optional loading of bson-ext.
  * Ensure no errors are thrown by replset if topology is destroyed before it finished connecting.
  * NODE-999 SDAM fixes for Mongos and single Server event emitting.
  * NODE-1014 Set socketTimeout to default to 360 seconds.
  * NODE-1019 Set keepAlive to 300 seconds or 1/2 of socketTimeout if socketTimeout < keepAlive.
* Just handle Collection name errors distinctly from general callback errors avoiding double callbacks in Db.collection.
* NODE-999 SDAM fixes for Mongos and single Server event emitting.
* NODE-1000 Added guard condition for upload.js checkDone function in case of race condition caused by late arriving chunk write.

2.2.27 2017-05-22
-----------------
* Updated mongodb-core to 2.1.11
    * NODE-987 Clear out old intervalIds on when calling topologyMonitor.
    * NODE-987 Moved filtering to pingServer method and added test case.
    * Check for connection destroyed just before writing out and flush out operations correctly if it is (Issue #179, https://github.com/jmholzinger).
    * NODE-989 Refactored Replicaset monitoring to correcly monitor newly added servers, Also extracted setTimeout and setInterval to use custom wrappers Timeout and Interval.
* NODE-985 Deprecated Db.authenticate and Admin.authenticate and moved auth methods into authenticate.js to ensure MongoClient.connect does not print deprecation warnings.
* NODE-988 Merged readConcern and hint correctly on collection(...).find(...).count()
* Fix passing the readConcern option to MongoClient.connect (Issue #1514, https://github.com/bausmeier).
* NODE-996 Propegate all events up to a MongoClient instance.
* Allow saving doc with null `_id` (Issue #1517, https://github.com/vkarpov15).
* NODE-993 Expose hasNext for command cursor and add docs for both CommandCursor and Aggregation Cursor.

2.2.26 2017-04-18
-----------------
* Updated mongodb-core to 2.1.10
    * NODE-981 delegate auth to replset/mongos if inTopology is set.
    * NODE-978 Wrap connection.end in try/catch for node 0.10.x issue causing exceptions to be thrown, Also surfaced getConnection for mongos and replset.
    * Remove dynamic require (Issue #175, https://github.com/tellnes).
    * NODE-696 Handle interrupted error for createIndexes.
    * Fixed isse when user is executing find command using Server.command and it get interpreted as a wire protcol message, #172.
    * NODE-966 promoteValues not being promoted correctly to getMore.
    * Merged in fix for flushing out monitoring operations.
* NODE-983 Add cursorId to aggregate and listCollections commands (Issue, #1510).
* Mark group and profilingInfo as deprecated methods
* NODE-956 DOCS Examples.
* Update readable-stream to version 2.2.7.
* NODE-978 Added test case to uncover connection.end issue for node 0.10.x.
* NODE-972 Fix(db): don't remove database name if collectionName == dbName (Issue, #1502)
* Fixed merging of writeConcerns on db.collection method.
* NODE-970 mix in readPreference for strict mode listCollections callback.
* NODE-966 added testcase for promoteValues being applied to getMore commands.
* NODE-962 Merge in ignoreUndefined from collection level for find/findOne.
* Remove multi option from updateMany tests/docs (Issue #1499, https://github.com/spratt).
* NODE-963 Correctly handle cursor.count when using APM.

2.2.25 2017-03-17
-----------------
* Don't rely on global toString() for checking if object (Issue #1494, https://github.com/vkarpov15).
* Remove obsolete option uri_decode_auth (Issue #1488, https://github.com/kamagatos).
* NODE-936 Correctly translate ReadPreference to CoreReadPreference for mongos queries.
* Exposed BSONRegExp type.
* NODE-950 push correct index for INSERT ops (https://github.com/mbroadst).
* NODE-951 Added support for sslCRL option and added a test case for it.
* NODE-953 Made batchSize issue general at cursor level.
* NODE-954 Remove write concern from reindex helper as it will not be supported in 3.6.
* Updated mongodb-core to 2.1.9.
    * Return lastIsMaster correctly when connecting with secondaryOnlyConnectionAllowed is set to true and only a secondary is available in replica state.
    * Clone options when passed to wireProtocol handler to avoid intermittent modifications causing errors.
    * Ensure SSL error propegates better for Replset connections when there is a SSL validation error.
    * NODE-957 Fixed issue where < batchSize not causing cursor to be closed on execution of first batch.
    * NODE-958 Store reconnectConnection on pool object to allow destroy to close immediately.

2.2.24 2017-02-14
-----------------
* NODE-935, NODE-931 Make MongoClient strict options validation optional and instead print annoying console.warn entries.

2.2.23 2017-02-13
-----------------
* Updated mongodb-core to 2.1.8.
  * NODE-925 ensure we reschedule operations while pool is < poolSize while pool is growing and there are no connections with not currently performing work.
  * NODE-927 fixes issue where authentication was performed against arbiter instances.
  * NODE-915 Normalize all host names to avoid comparison issues.
  * Fixed issue where pool.destroy would never finish due to a single operation not being executed and keeping it open.
* NODE-931 Validates all the options for MongoClient.connect and fixes missing connection settings.
* NODE-929 Update SSL tutorial to correctly reflect the non-need for server/mongos/replset subobjects
* Fix sensitive command check (Issue #1473, https://github.com/Annoraaq)

2.2.22 2017-01-24
-----------------
* Updated mongodb-core to 2.1.7.
  * NODE-919 ReplicaSet connection does not close immediately (Issue #156).
  * NODE-901 Fixed bug when normalizing host names.
  * NODE-909 Fixed readPreference issue caused by direct connection to primary.
  * NODE-910 Fixed issue when bufferMaxEntries == 0 and read preference set to nearest.
* Add missing unref implementations for replset, mongos (Issue #1455, https://github.com/zbjornson)

2.2.21 2017-01-13
-----------------
* Updated mongodb-core to 2.1.6.
  * NODE-908 Keep auth contexts in replset and mongos topology to ensure correct application of authentication credentials when primary is first server to be detected causing an immediate connect event to happen.

2.2.20 2017-01-11
-----------------
* Updated mongodb-core to 2.1.5 to include bson 1.0.4 and bson-ext 1.0.4 due to Buffer.from being broken in early node 4.x versions.

2.2.19 2017-01-03
-----------------
* Corrupted Npm release fix.

2.2.18 2017-01-03
-----------------
* Updated mongodb-core to 2.1.4 to fix bson ObjectId toString issue with utils.inspect messing with toString parameters in node 6.

2.2.17 2017-01-02
-----------------
* updated createCollection doc options and linked to create command.
* Updated mongodb-core to 2.1.3.
  * Monitoring operations are re-scheduled in pool if it cannot find a connection that does not already have scheduled work on it, this is to avoid the monitoring socket timeout being applied to any existing operations on the socket due to pipelining
  * Moved replicaset monitoring away from serial mode and to parallel mode.
  * updated bson and bson-ext dependencies to 1.0.2.

2.2.16 2016-12-13
-----------------
* NODE-899 reversed upsertedId change to bring back old behavior.

2.2.15 2016-12-10
-----------------
* Updated mongodb-core to 2.1.2.
  * Delay topologyMonitoring on successful attemptReconnect as no need to run a full scan immediately.
  * Emit reconnect event in primary joining when in connected status for a replicaset (Fixes mongoose reconnect issue).

2.2.14 2016-12-08
-----------------
* Updated mongodb-core to 2.1.1.
* NODE-892 Passthrough options.readPreference to mongodb-core ReplSet instance.

2.2.13 2016-12-05
-----------------
* Updated mongodb-core to 2.1.0.
* NODE-889 Fixed issue where legacy killcursor wire protocol messages would not be sent when APM is enabled.
* Expose parserType as property on topology objects.

2.2.12 2016-11-29
-----------------
* Updated mongodb-core to 2.0.14.
  * Updated bson library to 0.5.7.
  * Dont leak connection.workItems elments when killCursor is called (Issue #150, https://github.com/mdlavin).
  * Remove unnecessary errors formatting (Issue #149, https://github.com/akryvomaz).
  * Only check isConnected against availableConnections (Issue #142).
  * NODE-838 Provide better error message on failed to connect on first retry for Mongos topology.
  * Set default servername to host is not passed through for sni.
  * Made monitoring happen on exclusive connection and using connectionTimeout to handle the wait time before failure (Issue #148).
  * NODE-859 Make minimum value of maxStalenessSeconds 90 seconds.
  * NODE-852 Fix Kerberos module deprecations on linux and windows and release new kerberos version.
  * NODE-850 Update Max Staleness implementation.
  * NODE-849 username no longer required for MONGODB-X509 auth.
  * NODE-848 BSON Regex flags must be alphabetically ordered.
  * NODE-846 Create notice for all third party libraries.
  * NODE-843 Executing bulk operations overwrites write concern parameter.
  * NODE-842 Re-sync SDAM and SDAM Monitoring tests from Specs repo.
  * NODE-840 Resync CRUD spec tests.
  * Unescapable while(true) loop (Issue #152).
* NODE-864 close event not emits during network issues using single server topology.
* Introduced maxStalenessSeconds.
* NODE-840 Added CRUD specification test cases and fix minor issues with upserts reporting matchedCount > 0.
* Don't ignore Db-level authSource when using auth method.  (https://github.com/donaldguy).

2.2.11 2016-10-21
-----------------
* Updated mongodb-core to 2.0.13.
  - Fire callback when topology was destroyed (Issue #147, https://github.com/vkarpov15).
  - Refactoring to support pipelining ala 1.4.x branch will retaining the benefits of the growing/shrinking pool (Issue #146).
  - Fix typo in serverHeartbeatFailed event name (Issue #143, https://github.com/jakesjews).
  - NODE-798 Driver hangs on count command in replica set with one member (Issue #141, https://github.com/isayme).
* Updated bson library to 0.5.6.
  - Included cyclic dependency detection
* Fix typo in serverHeartbeatFailed event name (Issue #1418, https://github.com/jakesjews).
* NODE-824, readPreference "nearest" does not work when specified at collection level.
* NODE-822, GridFSBucketWriteStream end method does not handle optional parameters.
* NODE-823, GridFSBucketWriteStream end: callback is invoked with invalid parameters.
* NODE-829, Using Start/End offset option in GridFSBucketReadStream doesn't return the right sized buffer.

2.2.10 2016-09-15
-----------------
* Updated mongodb-core to 2.0.12.
* fix debug logging message not printing server name.
* fixed application metadata being sent by wrong ismaster.
* NODE-812 Fixed mongos stall due to proxy monitoring ismaster failure causing reconnect.
* NODE-818 Replicaset timeouts in initial connect sequence can "no primary found".
* Updated bson library to 0.5.5.
* Added DBPointer up conversion to DBRef.
* MongoDB 3.4-RC Pass **appname** through MongoClient.connect uri or options to allow metadata to be passed.
* MongoDB 3.4-RC Pass collation options on update, findOne, find, createIndex, aggregate.
* MongoDB 3.4-RC Allow write concerns to be passed to all supporting server commands.
* MongoDB 3.4-RC Allow passing of **servername** as SSL options to support SNI.

2.2.9 2016-08-29
----------------
* Updated mongodb-core to 2.0.11.
* NODE-803, Fixed issue in how the latency window is calculated for Mongos topology causing issues for single proxy connections.
* Avoid timeout in attemptReconnect causing multiple attemptReconnect attempts to happen (Issue #134, https://github.com/dead-horse).
* Ensure promoteBuffers is propegated in same fashion as promoteValues and promoteLongs.
* Don't treat ObjectId as object for mapReduce scope (Issue #1397, https://github.com/vkarpov15).

2.2.8 2016-08-23
----------------
* Updated mongodb-core to 2.0.10.
* Added promoteValues flag (default to true) to allow user to specify they only want wrapped BSON values back instead of promotion to native types.
* Do not close mongos proxy connection on failed ismaster check in ha process (Issue #130).

2.2.7 2016-08-19
----------------
* If only a single mongos is provided in the seedlist, fix issue where it would be assigned as single standalone server instead of mongos topology (Issue #130).
* Updated mongodb-core to 2.0.9.
* Allow promoteLongs to be passed in through Response.parse method and overrides default set on the connection.
* NODE-798 Driver hangs on count command in replica set with one member.
* Allow promoteLongs to be passed in through Response.parse method and overrides default set on the connection.
* Allow passing in servername for TLS connections for SNI support.

2.2.6 2016-08-16
----------------
* Updated mongodb-core to 2.0.8.
* Allow execution of store operations independent of having both a primary and secondary available (Issue #123).
* Fixed command execution issue for mongos to ensure buffering of commands when no mongos available.
* Allow passing in an array of tags to ReadPreference constructor (Issue #1382, https://github.com/vkarpov15)
* Added hashed connection names and fullResult.
* Updated bson library to 0.5.3.
* Enable maxTimeMS in count, distinct, findAndModify.

2.2.5 2016-07-28
----------------
* Updated mongodb-core to 2.0.7.
* Allow primary to be returned when secondaryPreferred is passed (Issue #117, https://github.com/dhendo).
* Added better warnings when passing in illegal seed list members to a Mongos topology.
* Minor attemptReconnect bug that would cause multiple attemptReconnect to run in parallel.
* Fix wrong opType passed to disconnectHandler.add (Issue #121, https://github.com/adrian-gierakowski)
* Implemented domain backward comp support enabled via domainsEnabled options on Server/ReplSet/Mongos and MongoClient.connect.

2.2.4 2016-07-19
----------------
* NPM corrupted upload fix.

2.2.3 2016-07-19
----------------
* Updated mongodb-core to 2.0.6.
* Destroy connection on socket timeout due to newer node versions not closing the socket.

2.2.2 2016-07-15
----------------
* Updated mongodb-core to 2.0.5.
* Minor fixes to handle faster MongoClient connectivity from the driver, allowing single server instances to detect if they are a proxy.
* Added numberOfConsecutiveTimeouts to pool that will destroy the pool if the number of consecutive timeouts > reconnectTries.
* Print warning if seedlist servers host name does not match the one provided in it's ismaster.me field for Replicaset members.
* Fix issue where Replicaset connection would not succeeed if there the replicaset was a single primary server setup.

2.2.1 2016-07-11
----------------
* Updated mongodb-core to 2.0.4.
* handle situation where user is providing seedlist names that do not match host list. fix allows for a single full discovery connection sweep before erroring out.
* NODE-747 Polyfill for Object.assign for 0.12.x or 0.10.x.
* NODE-746 Improves replicaset errors for wrong setName.

2.2.0 2016-07-05
----------------
* Updated mongodb-core to 2.0.3.
* Moved all authentication and handling of growing/shrinking of pool connections into actual pool.
* All authentication methods now handle both auth/reauthenticate and logout events.
* Introduced logout method to get rid of onAll option for logout command.
* Updated bson to 0.5.0 that includes Decimal128 support.
* Fixed logger error serialization issue.
* Documentation fixes.
* Implemented Server Selection Specification test suite.
* Added warning level to logger.
* Added warning message when sockeTimeout < haInterval for Replset/Mongos.
* Mongos emits close event on no proxies available or when reconnect attempt fails.
* Replset emits close event when no servers available or when attemptReconnect fails to reconnect.
* Don't throw in auth methods but return error in callback.

2.1.21 2016-05-30
-----------------
* Updated mongodb-core to 1.3.21.
* Pool gets stuck if a connection marked for immediateRelease times out (Issue #99, https://github.com/nbrachet).
* Make authentication process retry up to authenticationRetries at authenticationRetryIntervalMS interval.
* Made ismaster replicaset calls operate with connectTimeout or monitorSocketTimeout to lower impact of big socketTimeouts on monitoring performance.
* Make sure connections mark as "immediateRelease" don't linger the inUserConnections list. Otherwise, after that connection times out, getAll() incorrectly returns more connections than are effectively present, causing the pool to not get restarted by reconnectServer. (Issue #99, https://github.com/nbrachet).
* Make cursor getMore or killCursor correctly trigger pool reconnect to single server if pool has not been destroyed.
* Make ismaster monitoring for single server connection default to avoid user confusion due to change in behavior.

2.1.20 2016-05-25
-----------------
* Refactored MongoClient options handling to simplify the logic, unifying it.
* NODE-707 Implemented openUploadStreamWithId on GridFS to allow for custom fileIds so users are able to customize shard key and shard distribution.
* NODE-710 Allow setting driver loggerLevel and logger function from MongoClient options.
* Updated mongodb-core to 1.3.20.
* Minor fix for SSL errors on connection attempts, minor fix to reconnect handler for the server.
* Don't write to socket before having registered the callback for commands, work around for windows issuing error events twice on node.js when socket gets destroyed by firewall.
* Fix minor issue where connectingServers would not be removed correctly causing single server connections to not auto-reconnect.

2.1.19 2016-05-17
----------------
* Handle situation where a server connection in a replicaset sometimes fails to be destroyed properly due to being in the middle of authentication when the destroy method is called on the replicaset causing it to be orphaned and never collected.
* Ensure replicaset topology destroy is never called by SDAM.
* Ensure all paths are correctly returned on inspectServer in replset.
* Updated mongodb-core to 1.3.19 to fix minor connectivity issue on quick open/close of MongoClient connections on auth enabled mongodb Replicasets.

2.1.18 2016-04-27
-----------------
* Updated mongodb-core to 1.3.18 to fix Node 6.0 issues.

2.1.17 2016-04-26
-----------------
* Updated mongodb-core to 1.3.16 to work around issue with early versions of node 0.10.x due to missing unref method on ClearText streams.
* INT-1308: Allow listIndexes to inherit readPreference from Collection or DB.
* Fix timeout issue using new flags #1361.
* Updated mongodb-core to 1.3.17.
* Better handling of unique createIndex error.
* Emit error only if db instance has an error listener.
* DEFAULT authMechanism; don't throw error if explicitly set by user.

2.1.16 2016-04-06
-----------------
* Updated mongodb-core to 1.3.16.

2.1.15 2016-04-06
-----------------
* Updated mongodb-core to 1.3.15.
* Set ssl, sslValidate etc to mongosOptions on url_parser (Issue #1352, https://github.com/rubenstolk).
- NODE-687 Fixed issue where a server object failed to be destroyed if the replicaset state did not update successfully. This could leave active connections accumulating over time.
- Fixed some situations where all connections are flushed due to a single connection in the connection pool closing.

2.1.14 2016-03-29
-----------------
* Updated mongodb-core to 1.3.13.
* Handle missing cursor on getMore when going through a mongos proxy by pinning to socket connection and not server.

2.1.13 2016-03-29
-----------------
* Updated mongodb-core to 1.3.12.

2.1.12 2016-03-29
-----------------
* Updated mongodb-core to 1.3.11.
* Mongos setting acceptableLatencyMS exposed to control the latency women for mongos selection.
* Mongos pickProxies fall back to closest mongos if no proxies meet latency window specified.
* isConnected method for mongos uses same selection code as getServer.
* Exceptions in cursor getServer trapped and correctly delegated to high level handler.

2.1.11 2016-03-23
-----------------
* Updated mongodb-core to 1.3.10.
* Introducing simplified connections settings.

2.1.10 2016-03-21
-----------------
* Updated mongodb-core to 1.3.9.
* Fixing issue that prevented mapReduce stats from being resolved (Issue #1351, https://github.com/davidgtonge)
* Forwards SDAM monitoring events from mongodb-core.

2.1.9 2016-03-16
----------------
* Updated mongodb-core to 1.3.7 to fix intermittent race condition that causes some users to experience big amounts of socket connections.
* Makde bson parser in ordered/unordered bulk be directly from mongodb-core to avoid intermittent null error on mongoose.

2.1.8 2016-03-14
----------------
* Updated mongodb-core to 1.3.5.
* NODE-660 TypeError: Cannot read property 'noRelease' of undefined.
* Harden MessageHandler in server.js to avoid issues where we cannot find a callback for an operation.
* Ensure RequestId can never be larger than Max Number integer size.
* NODE-661 typo in url_parser.js resulting in replSetServerOptions is not defined when connecting over ssl.
* Confusing error with invalid partial index filter (Issue #1341, https://github.com/vkarpov15).
* NODE-669 Should only error out promise for bulkWrite when error is a driver level error not a write error or write concern error.
* NODE-662 shallow copy options on methods that are not currently doing it to avoid passed in options mutiation.
* NODE-663 added lookup helper on aggregation cursor.
* NODE-585 Result object specified incorrectly for findAndModify?.
* NODE-666 harden validation for findAndModify CRUD methods.

2.1.7 2016-02-09
----------------
* NODE-656 fixed corner case where cursor count command could be left without a connection available.
* NODE-658 Work around issue that bufferMaxEntries:-1 for js gets interpreted wrongly due to double nature of Javascript numbers.
* Fix: GridFS always returns the oldest version due to incorrect field name (Issue #1338, https://github.com/mdebruijne).
* NODE-655 GridFS stream support for cancelling upload streams and download streams (Issue #1339, https://github.com/vkarpov15).
* NODE-657 insertOne don`t return promise in some cases.
* Added destroy alias for abort function on GridFSBucketWriteStream.

2.1.6 2016-02-05
----------------
* Updated mongodb-core to 1.3.1.

2.1.5 2016-02-04
----------------
* Updated mongodb-core to 1.3.0.
* Added raw support for the command function on topologies.
* Fixed issue where raw results that fell on batchSize boundaries failed (Issue #72)
* Copy over all the properties to the callback returned from bindToDomain, (Issue #72)
* Added connection hash id to be able to reference connection host/name without leaking it outside of driver.
* NODE-638, Cannot authenticate database user with utf-8 password.
* Refactored pool to be worker queue based, minimizing the impact a slow query have on throughput as long as # slow queries < # connections in the pool.
* Pool now grows and shrinks correctly depending on demand not causing a full pool reconnect.
* Improvements in monitoring of a Replicaset where in certain situations the inquiry process could get exited.
* Switched to using Array.push instead of concat for use cases of a lot of documents.
* Fixed issue where re-authentication could loose the credentials if whole Replicaset disconnected at once.
* Added peer optional dependencies support using require_optional module.
* Bug is listCollections for collection names that start with db name (Issue #1333, https://github.com/flyingfisher)
* Emit error before closing stream (Issue #1335, https://github.com/eagleeye)

2.1.4 2016-01-12
----------------
* Restricted node engine to >0.10.3 (https://jira.mongodb.org/browse/NODE-635).
* Multiple database names ignored without a warning (https://jira.mongodb.org/browse/NODE-636, Issue #1324, https://github.com/yousefhamza).
* Convert custom readPreference objects in collection.js (Issue #1326, https://github.com/Machyne).

2.1.3 2016-01-04
----------------
* Updated mongodb-core to 1.2.31.
* Allow connection to secondary if primaryPreferred or secondaryPreferred (Issue #70, https://github.com/leichter)

2.1.2 2015-12-23
----------------
* Updated mongodb-core to 1.2.30.
* Pool allocates size + 1 connections when using replicasets, reserving additional pool connection for monitoring exclusively.
* Fixes bug when all replicaset members are down, that would cause it to fail to reconnect using the originally provided seedlist.

2.1.1 2015-12-13
----------------
* Surfaced checkServerIdentity options for MongoClient, Server, ReplSet and Mongos to allow for control of the checkServerIdentity method available in Node.s 0.12.x or higher.
* Added readPreference support to listCollections and listIndexes helpers.
* Updated mongodb-core to 1.2.28.

2.1.0 2015-12-06
----------------
* Implements the connection string specification, https://github.com/mongodb/specifications/blob/master/source/connection-string/connection-string-spec.rst.
* Implements the new GridFS specification, https://github.com/mongodb/specifications/blob/master/source/gridfs/gridfs-spec.rst.
* Full MongoDB 3.2 support.
* NODE-601 Added maxAwaitTimeMS support for 3.2 getMore to allow for custom timeouts on tailable cursors.
* Updated mongodb-core to 1.2.26.
* Return destination in GridStore pipe function.
* NODE-606 better error handling on destroyed topology for db.js methods.
* Added isDestroyed method to server, replset and mongos topologies.
* Upgraded test suite to run using mongodb-topology-manager.

2.0.53 2015-12-23
-----------------
* Updated mongodb-core to 1.2.30.
* Pool allocates size + 1 connections when using replicasets, reserving additional pool connection for monitoring exclusively.
* Fixes bug when all replicaset members are down, that would cause it to fail to reconnect using the originally provided seedlist.

2.0.52 2015-12-14
-----------------
* removed remove from Gridstore.close.

2.0.51 2015-12-13
-----------------
* Surfaced checkServerIdentity options for MongoClient, Server, ReplSet and Mongos to allow for control of the checkServerIdentity method available in Node.s 0.12.x or higher.
* Added readPreference support to listCollections and listIndexes helpers.
* Updated mongodb-core to 1.2.28.

2.0.50 2015-12-06
-----------------
* Updated mongodb-core to 1.2.26.

2.0.49 2015-11-20
-----------------
* Updated mongodb-core to 1.2.24 with several fixes.
  * Fix Automattic/mongoose#3481; flush callbacks on error, (Issue #57, https://github.com/vkarpov15).
  * $explain query for wire protocol 2.6 and 2.4 does not set number of returned documents to -1 but to 0.
  * ismaster runs against admin.$cmd instead of system.$cmd.
  * Fixes to handle getMore command errors for MongoDB 3.2
  * Allows the process to properly close upon a Db.close() call on the replica set by shutting down the haTimer and closing arbiter connections.

2.0.48 2015-11-07
-----------------
* GridFS no longer performs any deletes when writing a brand new file that does not have any previous <db>.fs.chunks or <db>.fs.files documents.
* Updated mongodb-core to 1.2.21.
* Hardened the checking for replicaset equality checks.
* OpReplay flag correctly set on Wire protocol query.
* Mongos load balancing added, introduced localThresholdMS to control the feature.
* Kerberos now a peerDependency, making it not install it by default in Node 5.0 or higher.

2.0.47 2015-10-28
-----------------
* Updated mongodb-core to 1.2.20.
* Fixed bug in arbiter connection capping code.
* NODE-599 correctly handle arrays of server tags in order of priority.
* Fix for 2.6 wire protocol handler related to readPreference handling.
* Added maxAwaitTimeMS support for 3.2 getMore to allow for custom timeouts on tailable cursors.
* Make CoreCursor check for $err before saying that 'next' succeeded (Issue #53, https://github.com/vkarpov15).

2.0.46 2015-10-15
-----------------
* Updated mongodb-core to 1.2.19.
* NODE-578 Order of sort fields is lost for numeric field names.
* Expose BSON Map (ES6 Map or polyfill).
* Minor fixes for APM support to pass extended APM test suite.

2.0.45 2015-09-30
-----------------
* NODE-566 Fix issue with rewind on capped collections causing cursor state to be reset on connection loss.

2.0.44 2015-09-28
-----------------
* Bug fixes for APM upconverting of legacy INSERT/UPDATE/REMOVE wire protocol messages.
* NODE-562, fixed issue where a Replicaset MongoDB URI with a single seed and replSet name set would cause a single direct connection instead of topology discovery.
* Updated mongodb-core to 1.2.14.
* NODE-563 Introduced options.ignoreUndefined for db class and MongoClient db options, made serialize undefined to null default again but allowing for overrides on insert/update/delete operations.
* Use handleCallback if result is an error for count queries. (Issue #1298, https://github.com/agclever)
* Rewind cursor to correctly force reconnect on capped collections when first query comes back empty.
* NODE-571 added code 59 to legacy server errors when SCRAM-SHA-1 mechanism fails.
* NODE-572 Remove examples that use the second parameter to `find()`.

2.0.43 2015-09-14
-----------------
* Propagate timeout event correctly to db instances.
* Application Monitoring API (APM) implemented.
* NOT providing replSet name in MongoClient connection URI will force single server connection. Fixes issue where it was impossible to directly connect to a replicaset member server.
* Updated mongodb-core to 1.2.12.
* NODE-541 Initial Support "read committed" isolation level where "committed" means confimed by the voting majority of a replica set.
* GridStore doesn't share readPreference setting from connection string. (Issue #1295, https://github.com/zhangyaoxing)
* fixed forceServerObjectId calls (Issue #1292, https://github.com/d-mon-)
* Pass promise library through to DB function (Issue #1294, https://github.com/RovingCodeMonkey)

2.0.42 2015-08-18
-----------------
* Added test case to exercise all non-crud methods on mongos topologies, fixed numberOfConnectedServers on mongos topology instance.

2.0.41 2015-08-14
-----------------
* Added missing Mongos.prototype.parserType function.
* Updated mongodb-core to 1.2.10.

2.0.40 2015-07-14
-----------------
* Updated mongodb-core to 1.2.9 for 2.4 wire protocol error handler fix.
* NODE-525 Reset connectionTimeout after it's overwritten by tls.connect.
* NODE-518 connectTimeoutMS is doubled in 2.0.39.
* NODE-506 Ensures that errors from bulk unordered and ordered are instanceof Error (Issue #1282, https://github.com/owenallenaz).
* NODE-526 Unique index not throwing duplicate key error.
* NODE-528 Ignore undefined fields in Collection.find().
* NODE-527 The API example for collection.createIndex shows Db.createIndex functionality.

2.0.39 2015-07-14
-----------------
* Updated mongodb-core to 1.2.6 for NODE-505.

2.0.38 2015-07-14
-----------------
* NODE-505 Query fails to find records that have a 'result' property with an array value.

2.0.37 2015-07-14
-----------------
* NODE-504 Collection * Default options when using promiseLibrary.
* NODE-500 Accidental repeat of hostname in seed list multiplies total connections persistently.
* Updated mongodb-core to 1.2.5 to fix NODE-492.

2.0.36 2015-07-07
-----------------
* Fully promisified allowing the use of ES6 generators and libraries like co. Also allows for BYOP (Bring your own promises).
* NODE-493 updated mongodb-core to 1.2.4 to ensure we cannot DDOS the mongod or mongos process on large connection pool sizes.

2.0.35 2015-06-17
-----------------
* Upgraded to mongodb-core 1.2.2 including removing warnings when C++ bson parser is not available and a fix for SCRAM authentication.

2.0.34 2015-06-17
-----------------
* Upgraded to mongodb-core 1.2.1 speeding up serialization and removing the need for the c++ bson extension.
* NODE-486 fixed issue related to limit and skip when calling toArray in 2.0 driver.
* NODE-483 throw error if capabilities of topology is queries before topology has performed connection setup.
* NODE-482 fixed issue where MongoClient.connect would incorrectly identify a replset seed list server as a non replicaset member.
* NODE-487 fixed issue where killcursor command was not being sent correctly on limit and skip queries.

2.0.33 2015-05-20
-----------------
* Bumped mongodb-core to 1.1.32.

2.0.32 2015-05-19
-----------------
* NODE-463 db.close immediately executes its callback.
* Don't only emit server close event once (Issue #1276, https://github.com/vkarpov15).
* NODE-464 Updated mongodb-core to 1.1.31 that uses a single socket connection to arbiters and hidden servers as well as emitting all event correctly.

2.0.31 2015-05-08
-----------------
* NODE-461 Tripping on error "no chunks found for file, possibly corrupt" when there is no error.

2.0.30 2015-05-07
-----------------
* NODE-460 fix; don't set authMechanism for user in db.authenticate() to avoid mongoose authentication issue.

2.0.29 2015-05-07
-----------------
* NODE-444 Possible memory leak, too many listeners added.
* NODE-459 Auth failure using Node 0.8.28, MongoDB 3.0.2 & mongodb-node-native 1.4.35.
* Bumped mongodb-core to 1.1.26.

2.0.28 2015-04-24
-----------------
* Bumped mongodb-core to 1.1.25
* Added Cursor.prototype.setCursorOption to allow for setting node specific cursor options for tailable cursors.
* NODE-430 Cursor.count() opts argument masked by var opts = {}
* NODE-406 Implemented Cursor.prototype.map function tapping into MongoClient cursor transforms.
* NODE-438 replaceOne is not returning the result.ops property as described in the docs.
* NODE-433 _read, pipe and write all open gridstore automatically if not open.
* NODE-426 ensure drain event is emitted after write function returns, fixes intermittent issues in writing files to gridstore.
* NODE-440 GridStoreStream._read() doesn't check GridStore.read() error.
* Always use readPreference = primary for findAndModify command (ignore passed in read preferences) (Issue #1274, https://github.com/vkarpov15).
* Minor fix in GridStore.exists for dealing with regular expressions searches.

2.0.27 2015-04-07
-----------------
* NODE-410 Correctly handle issue with pause/resume in Node 0.10.x that causes exceptions when using the Node 0.12.0 style streams.

2.0.26 2015-04-07
-----------------
* Implements the Common Index specification Standard API at https://github.com/mongodb/specifications/blob/master/source/index-management.rst.
* NODE-408 Expose GridStore.currentChunk.chunkNumber.

2.0.25 2015-03-26
-----------------
* Upgraded mongodb-core to 1.1.21, making the C++ bson code an optional dependency to the bson module.

2.0.24 2015-03-24
-----------------
* NODE-395 Socket Not Closing, db.close called before full set finished initalizing leading to server connections in progress not being closed properly.
* Upgraded mongodb-core to 1.1.20.

2.0.23 2015-03-21
-----------------
* NODE-380 Correctly return MongoError from toError method.
* Fixed issue where addCursorFlag was not correctly setting the flag on the command for mongodb-core.
* NODE-388 Changed length from method to property on order.js/unordered.js bulk operations.
* Upgraded mongodb-core to 1.1.19.

2.0.22 2015-03-16
-----------------
* NODE-377, fixed issue where tags would correctly be checked on secondary and nearest to filter out eligible server candidates.
* Upgraded mongodb-core to 1.1.17.

2.0.21 2015-03-06
-----------------
* Upgraded mongodb-core to 1.1.16 making sslValidate default to true to force validation on connection unless overriden by the user.

2.0.20 2015-03-04
-----------------
* Updated mongodb-core 1.1.15 to relax pickserver method.

2.0.19 2015-03-03
-----------------
* NODE-376 Fixes issue * Unordered batch incorrectly tracks batch size when switching batch types (Issue #1261, https://github.com/meirgottlieb)
* NODE-379 Fixes bug in cursor.count() that causes the result to always be zero for dotted collection names (Issue #1262, https://github.com/vsivsi)
* Expose MongoError from mongodb-core (Issue #1260, https://github.com/tjconcept)

2.0.18 2015-02-27
-----------------
* Bumped mongodb-core 1.1.14 to ensure passives are correctly added as secondaries.

2.0.17 2015-02-27
-----------------
* NODE-336 Added length function to ordered and unordered bulk operations to be able know the amount of current operations in bulk.
* Bumped mongodb-core 1.1.13 to ensure passives are correctly added as secondaries.

2.0.16 2015-02-16
-----------------
* listCollection now returns filtered result correctly removing db name for 2.6 or earlier servers.
* Bumped mongodb-core 1.1.12 to correctly work for node 0.12.0 and io.js.
* Add ability to get collection name from cursor (Issue #1253, https://github.com/vkarpov15)

2.0.15 2015-02-02
-----------------
* Unified behavior of listCollections results so 3.0 and pre 3.0 return same type of results.
* Bumped mongodb-core to 1.1.11 to support per document tranforms in cursors as well as relaxing the setName requirement.
* NODE-360 Aggregation cursor and command correctly passing down the maxTimeMS property.
* Added ~1.0 mongodb-tools module for test running.
* Remove the required setName for replicaset connections, if not set it will pick the first setName returned.

2.0.14 2015-01-21
-----------------
* Fixed some MongoClient.connect options pass through issues and added test coverage.
* Bumped mongodb-core to 1.1.9 including fixes for io.js

2.0.13 2015-01-09
-----------------
* Bumped mongodb-core to 1.1.8.
* Optimized query path for performance, moving Object.defineProperty outside of constructors.

2.0.12 2014-12-22
-----------------
* Minor fixes to listCollections to ensure correct querying of a collection when using a string.

2.0.11 2014-12-19
-----------------
* listCollections filters out index namespaces on < 2.8 correctly
* Bumped mongo-client to 1.1.7

2.0.10 2014-12-18
-----------------
* NODE-328 fixed db.open return when no callback available issue and added test.
* NODE-327 Refactored listCollections to return cursor to support 2.8.
* NODE-327 Added listIndexes method and refactored internal methods to use the new command helper.
* NODE-335 Cannot create index for nested objects fixed by relaxing key checking for createIndex helper.
* Enable setting of connectTimeoutMS (Issue #1235, https://github.com/vkarpov15)
* Bumped mongo-client to 1.1.6

2.0.9 2014-12-01
----------------
* Bumped mongodb-core to 1.1.3 fixing global leaked variables and introducing strict across all classes.
* All classes are now strict (Issue #1233)
* NODE-324 Refactored insert/update/remove and all other crud opts to rely on internal methods to avoid any recursion.
* Fixed recursion issues in debug logging due to JSON.stringify()
* Documentation fixes (Issue #1232, https://github.com/wsmoak)
* Fix writeConcern in Db.prototype.ensureIndex (Issue #1231, https://github.com/Qard)

2.0.8 2014-11-28
----------------
* NODE-322 Finished up prototype refactoring of Db class.
* NODE-322 Exposed Cursor in index.js for New Relic.

2.0.7 2014-11-20
----------------
* Bumped mongodb-core to 1.1.2 fixing a UTF8 encoding issue for collection names.
* NODE-318 collection.update error while setting a function with serializeFunctions option.
* Documentation fixes.

2.0.6 2014-11-14
----------------
* Refactored code to be prototype based instead of privileged methods.
* Bumped mongodb-core to 1.1.1 to take advantage of the prototype based refactorings.
* Implemented missing aspects of the CRUD specification.
* Fixed documentation issues.
* Fixed global leak REFERENCE_BY_ID in gridfs grid_store (Issue #1225, https://github.com/j)
* Fix LearnBoost/mongoose#2313: don't let user accidentally clobber geoNear params (Issue #1223, https://github.com/vkarpov15)

2.0.5 2014-10-29
----------------
* Minor fixes to documentation and generation of documentation.
* NODE-306 (No results in aggregation cursor when collection name contains a dot), Merged code for cursor and aggregation cursor.

2.0.4 2014-10-23
----------------
* Allow for single replicaset seed list with no setName specified (Issue #1220, https://github.com/imaman)
* Made each rewind on each call allowing for re-using the cursor.
* Fixed issue where incorrect iterations would happen on each for extensive batchSizes.
* NODE-301 specifying maxTimeMS on find causes all fields to be omitted from result.

2.0.3 2014-10-14
----------------
* NODE-297 Aggregate Broken for case of pipeline with no options.

2.0.2 2014-10-08
----------------
* Bumped mongodb-core to 1.0.2.
* Fixed bson module dependency issue by relying on the mongodb-core one.
* Use findOne instead of find followed by nextObject (Issue #1216, https://github.com/sergeyksv)

2.0.1 2014-10-07
----------------
* Dependency fix

2.0.0 2014-10-07
----------------
* First release of 2.0 driver

2.0.0-alpha2 2014-10-02
-----------------------
* CRUD API (insertOne, insertMany, updateOne, updateMany, removeOne, removeMany, bulkWrite, findOneAndDelete, findOneAndUpdate, findOneAndReplace)
* Cluster Management Spec compatible.

2.0.0-alpha1 2014-09-08
-----------------------
* Insert method allows only up 1000 pr batch for legacy as well as 2.6 mode
* Streaming behavior is 0.10.x or higher with backwards compatibility using readable-stream npm package
* Gridfs stream only available through .stream() method due to overlapping names on Gridstore object and streams in 0.10.x and higher of node
* remove third result on update and remove and return the whole result document instead (getting rid of the weird 3 result parameters)
    * Might break some application
* Returns the actual mongodb-core result instead of just the number of records changed for insert/update/remove
* MongoClient only has the connect method (no ability instantiate with Server, ReplSet or similar)
* Removed Grid class
* GridStore only supports w+ for metadata updates, no appending to file as it's not thread safe and can cause corruption of the data
    + seek will fail if attempt to use with w or w+
    + write will fail if attempted with w+ or r
    + w+ only works for updating metadata on a file
* Cursor toArray and each resets and re-runs the cursor
* FindAndModify returns whole result document instead of just value
* Extend cursor to allow for setting all the options via methods instead of dealing with the current messed up find
* Removed db.dereference method
* Removed db.cursorInfo method
* Removed db.stats method
* Removed db.collectionNames not needed anymore as it's just a specialized case of listCollections
* Removed db.collectionInfo removed due to not being compatible with new storage engines in 2.8 as they need to use the listCollections command due to system collections not working for namespaces.
* Added db.listCollections to replace several methods above

1.4.10 2014-09-04
-----------------
* Fixed BSON and Kerberos compilation issues
* Bumped BSON to ~0.2 always installing latest BSON 0.2.x series
* Fixed Kerberos and bumped to 0.0.4

1.4.9 2014-08-26
----------------
* Check _bsonType for Binary (Issue #1202, https://github.com/mchapman)
* Remove duplicate Cursor constructor (Issue #1201, https://github.com/KenPowers)
* Added missing parameter in the documentation (Issue #1199, https://github.com/wpjunior)
* Documented third parameter on the update callback(Issue #1196, https://github.com/gabmontes)
* NODE-240 Operations on SSL connection hang on node 0.11.x
* NODE-235 writeResult is not being passed on when error occurs in insert
* NODE-229 Allow count to work with query hints
* NODE-233 collection.save() does not support fullResult
* NODE-244 Should parseError also emit a `disconnected` event?
* NODE-246 Cursors are inefficiently constructed and consequently cannot be promisified.
* NODE-248 Crash with X509 auth
* NODE-252 Uncaught Exception in Base.__executeAllServerSpecificErrorCallbacks
* Bumped BSON parser to 0.2.12


1.4.8 2014-08-01
----------------
* NODE-205 correctly emit authenticate event
* NODE-210 ensure no undefined connection error when checking server state
* NODE-212 correctly inherit socketTimeoutMS from replicaset when HA process adds new servers or reconnects to existing ones
* NODE-220 don't throw error if ensureIndex errors out in Gridstore
* Updated bson to 0.2.11 to ensure correct toBSON behavior when returning non object in nested classes
* Fixed test running filters
* Wrap debug log in a call to format (Issue #1187, https://github.com/andyroyle)
* False option values should not trigger w:1 (Issue #1186, https://github.com/jsdevel)
* Fix aggregatestream.close(Issue #1194, https://github.com/jonathanong)
* Fixed parsing issue for w:0 in url parser when in connection string
* Modified collection.geoNear to support a geoJSON point or legacy coordinate pair (Issue #1198, https://github.com/mmacmillan)

1.4.7 2014-06-18
----------------
* Make callbacks to be executed in right domain when server comes back up (Issue #1184, https://github.com/anton-kotenko)
* Fix issue where currentOp query against mongos would fail due to mongos passing through $readPreference field to mongod (CS-X)

1.4.6 2014-06-12
----------------
* Added better support for MongoClient IP6 parsing (Issue #1181, https://github.com/micovery)
* Remove options check on index creation (Issue #1179, Issue #1183, https://github.com/jdesboeufs, https://github.com/rubenvereecken)
* Added missing type check before calling optional callback function (Issue #1180)

1.4.5 2014-05-21
----------------
* Added fullResult flag to insert/update/remove which will pass raw result document back. Document contents will vary depending on the server version the driver is talking to. No attempt is made to coerce a joint response.
* Fix to avoid MongoClient.connect hanging during auth when secondaries building indexes pre 2.6.
* return the destination stream in GridStore.pipe (Issue #1176, https://github.com/iamdoron)

1.4.4 2014-05-13
----------------
* Bumped BSON version to use the NaN 1.0 package, fixed strict comparison issue for ObjectID
* Removed leaking global variable (Issue #1174, https://github.com/dainis)
* MongoClient respects connectTimeoutMS for initial discovery process (NODE-185)
* Fix bug with return messages larger than 16MB but smaller than max BSON Message Size (NODE-184)

1.4.3 2014-05-01
----------------
* Clone options for commands to avoid polluting original options passed from Mongoose (Issue #1171, https://github.com/vkarpov15)
* Made geoNear and geoHaystackSearch only clean out allowed options from command generation (Issue #1167)
* Fixed typo for allowDiskUse (Issue #1168, https://github.com/joaofranca)
* A 'mapReduce' function changed 'function' to instance '\<Object\>' of 'Code' class (Issue #1165, https://github.com/exabugs)
* Made findAndModify set sort only when explicitly set (Issue #1163, https://github.com/sars)
* Rewriting a gridStore file by id should use a new filename if provided (Issue #1169, https://github.com/vsivsi)

1.4.2 2014-04-15
----------------
* Fix for inheritance of readPreferences from MongoClient NODE-168/NODE-169
* Merged in fix for ping strategy to avoid hitting non-pinged servers (Issue #1161, https://github.com/vaseker)
* Merged in fix for correct debug output for connection messages (Issue #1158, https://github.com/vaseker)
* Fixed global variable leak (Issue #1160, https://github.com/vaseker)

1.4.1 2014-04-09
----------------
* Correctly emit joined event when primary change
* Add _id to documents correctly when using bulk operations

1.4.0 2014-04-03
----------------
* All node exceptions will no longer be caught if on('error') is defined
* Added X509 auth support
* Fix for MongoClient connection timeout issue (NODE-97)
* Pass through error messages from parseError instead of just text (Issue #1125)
* Close db connection on error (Issue #1128, https://github.com/benighted)
* Fixed documentation generation
* Added aggregation cursor for 2.6 and emulated cursor for pre 2.6 (uses stream2)
* New Bulk API implementation using write commands for 2.6 and down converts for pre 2.6
* Insert/Update/Remove using new write commands when available
* Added support for new roles based API's in 2.6 for addUser/removeUser
* Added bufferMaxEntries to start failing if the buffer hits the specified number of entries
* Upgraded BSON parser to version 0.2.7 to work with < 0.11.10 C++ API changes
* Support for OP_LOG_REPLAY flag (NODE-94)
* Fixes for SSL HA ping and discovery.
* Uses createIndexes if available for ensureIndex/createIndex
* Added parallelCollectionScan method to collection returning CommandCursor instances for cursors
* Made CommandCursor behave as Readable stream.
* Only Db honors readPreference settings, removed Server.js legacy readPreference settings due to user confusion.
* Reconnect event emitted by ReplSet/Mongos/Server after reconnect and before replaying of buffered operations.
* GridFS buildMongoObject returns error on illegal md5 (NODE-157, https://github.com/iantocristian)
* Default GridFS chunk size changed to (255 * 1024) bytes to optimize for collections defaulting to power of 2 sizes on 2.6.
* Refactored commands to all go through command function ensuring consistent command execution.
* Fixed issues where readPreferences where not correctly passed to mongos.
* Catch error == null and make err detection more prominent (NODE-130)
* Allow reads from arbiter for single server connection (NODE-117)
* Handle error coming back with no documents (NODE-130)
* Correctly use close parameter in Gridstore.write() (NODE-125)
* Throw an error on a bulk find with no selector (NODE-129, https://github.com/vkarpov15)
* Use a shallow copy of options in find() (NODE-124, https://github.com/vkarpov15)
* Fix statistical strategy (NODE-158, https://github.com/vkarpov15)
* GridFS off-by-one bug in lastChunkNumber() causes uncaught throw and data loss (Issue #1154, https://github.com/vsivsi)
* GridStore drops passed `aliases` option, always results in `null` value in GridFS files (Issue #1152, https://github.com/vsivsi)
* Remove superfluous connect object copying in index.js (Issue #1145, https://github.com/thomseddon)
* Do not return false when the connection buffer is still empty (Issue #1143, https://github.com/eknkc)
* Check ReadPreference object on ReplSet.canRead (Issue #1142, https://github.com/eknkc)
* Fix unpack error on _executeQueryCommand (Issue #1141, https://github.com/eknkc)
* Close db on failed connect so node can exit (Issue #1128, https://github.com/benighted)
* Fix global leak with _write_concern (Issue #1126, https://github.com/shanejonas)

1.3.19 2013-08-21
-----------------
* Correctly rethrowing errors after change from event emission to callbacks, compatibility with 0.10.X domains without breaking 0.8.X support.
* Small fix to return the entire findAndModify result as the third parameter (Issue #1068)
* No removal of "close" event handlers on server reconnect, emits "reconnect" event when reconnection happens. Reconnect Only applies for single server connections as of now as semantics for ReplSet and Mongos is not clear (Issue #1056)

1.3.18 2013-08-10
-----------------
* Fixed issue when throwing exceptions in MongoClient.connect/Db.open (Issue #1057)
* Fixed an issue where _events is not cleaned up correctly causing a slow steady memory leak.

1.3.17 2013-08-07
-----------------
* Ignore return commands that have no registered callback
* Made collection.count not use the db.command function
* Fix throw exception on ping command (Issue #1055)

1.3.16 2013-08-02
-----------------
* Fixes connection issue where lots of connections would happen if a server is in recovery mode during connection (Issue #1050, NODE-50, NODE-51)
* Bug in unlink mulit filename (Issue #1054)

1.3.15 2013-08-01
-----------------
* Memory leak issue due to node Issue #4390 where _events[id] is set to undefined instead of deleted leading to leaks in the Event Emitter over time

1.3.14 2013-08-01
-----------------
* Fixed issue with checkKeys where it would error on X.X

1.3.13 2013-07-31
-----------------
* Added override for checkKeys on insert/update (Warning will expose you to injection attacks) (Issue #1046)
* BSON size checking now done pre serialization (Issue #1037)
* Added isConnected returns false when no connection Pool exists (Issue #1043)
* Unified command handling to ensure same handling (Issue #1041, #1042)
* Correctly emit "open" and "fullsetup" across all Db's associated with Mongos, ReplSet or Server (Issue #1040)
* Correctly handles bug in authentication when attempting to connect to a recovering node in a replicaset.
* Correctly remove recovering servers from available servers in replicaset. Piggybacks on the ping command.
* Removed findAndModify chaining to be compliant with behavior in other official drivers and to fix a known mongos issue.
* Fixed issue with Kerberos authentication on Windows for re-authentication.
* Fixed Mongos failover behavior to correctly throw out old servers.
* Ensure stored queries/write ops are executed correctly after connection timeout
* Added promoteLongs option for to allow for overriding the promotion of Longs to Numbers and return the actual Long.

1.3.12 2013-07-19
-----------------
* Fixed issue where timeouts sometimes would behave wrongly (Issue #1032)
* Fixed bug with callback third parameter on some commands (Issue #1033)
* Fixed possible issue where killcursor command might leave hanging functions
* Fixed issue where Mongos was not correctly removing dead servers from the pool of eligable servers
* Throw error if dbName or collection name contains null character (at command level and at collection level)
* Updated bson parser to 0.2.1 with security fix and non-promotion of Long values to javascript Numbers (once a long always a long)

1.3.11 2013-07-04
-----------------
* Fixed errors on geoNear and geoSearch (Issue #1024, https://github.com/ebensing)
* Add driver version to export (Issue #1021, https://github.com/aheckmann)
* Add text to readpreference obedient commands (Issue #1019)
* Drivers should check the query failure bit even on getmore response (Issue #1018)
* Map reduce has incorrect expectations of 'inline' value for 'out' option (Issue #1016, https://github.com/rcotter)
* Support SASL PLAIN authentication (Issue #1009)
* Ability to use different Service Name on the driver for Kerberos Authentication (Issue #1008)
* Remove unnecessary octal literal to allow the code to run in strict mode (Issue #1005, https://github.com/jamesallardice)
* Proper handling of recovering nodes (when they go into recovery and when they return from recovery, Issue #1027)

1.3.10 2013-06-17
-----------------
* Guard against possible undefined in server::canCheckoutWriter (Issue #992, https://github.com/willyaranda)
* Fixed some duplicate test names (Issue #993, https://github.com/kawanet)
* Introduced write and read concerns for GridFS (Issue #996)
* Fixed commands not correctly respecting Collection level read preference (Issue #995, #999)
* Fixed issue with pool size on replicaset connections (Issue #1000)
* Execute all query commands on master switch (Issue #1002, https://github.com/fogaztuc)

1.3.9 2013-06-05
----------------
* Fixed memory leak when findAndModify errors out on w>1 and chained callbacks not properly cleaned up.

1.3.8 2013-05-31
----------------
* Fixed issue with socket death on windows where it emits error event instead of close event (Issue #987)
* Emit authenticate event on db after authenticate method has finished on db instance (Issue #984)
* Allows creation of MongoClient and do new MongoClient().connect(..). Emits open event when connection correct allowing for apps to react on event.

1.3.7 2013-05-29
----------------
* After reconnect, tailable getMores go on inconsistent connections (Issue #981, #982, https://github.com/glasser)
* Updated Bson to 0.1.9 to fix ARM support (Issue #985)

1.3.6 2013-05-21
----------------
* Fixed issue where single server reconnect attempt would throw due to missing options variable (Issue #979)
* Fixed issue where difference in ismaster server name and seed list caused connections issues, (Issue #976)

1.3.5 2013-05-14
----------------
* Fixed issue where HA for replicaset would pick the same broken connection when attempting to ping the replicaset causing the replicaset to never recover.

1.3.4 2013-05-14
----------------
* Fixed bug where options not correctly passed in for uri parser (Issue #973, https://github.com/supershabam)
* Fixed bug when passing a named index hint (Issue #974)

1.3.3 2013-05-09
----------------
* Fixed auto-reconnect issue with single server instance.

1.3.2 2013-05-08
----------------
* Fixes for an issue where replicaset would be pronounced dead when high priority primary caused double elections.

1.3.1 2013-05-06
----------------
* Fix for replicaset consisting of primary/secondary/arbiter with priority applied failing to reconnect properly
* Applied auth before server instance is set as connected when single server connection
* Throw error if array of documents passed to save method

1.3.0 2013-04-25
----------------
* Whole High availability handling for Replicaset, Server and Mongos connections refactored to ensure better handling of failover cases.
* Fixed issue where findAndModify would not correctly skip issuing of chained getLastError (Issue #941)
* Fixed throw error issue on errors with findAndModify during write out operation (Issue #939, https://github.com/autopulated)
* Gridstore.prototype.writeFile now returns gridstore object correctly (Issue #938)
* Kerberos support is now an optional module that allows for use of GSSAPI authentication using MongoDB Subscriber edition
* Fixed issue where cursor.toArray could blow the stack on node 0.10.X (#950)

1.2.14 2013-03-14
-----------------
* Refactored test suite to speed up running of replicaset tests
* Fix of async error handling when error happens in callback (Issue #909, https://github.com/medikoo)
* Corrected a slaveOk setting issue (Issue #906, #905)
* Fixed HA issue where ping's would not go to correct server on HA server connection failure.
* Uses setImmediate if on 0.10 otherwise nextTick for cursor stream
* Fixed race condition in Cursor stream (NODE-31)
* Fixed issues related to node 0.10 and process.nextTick now correctly using setImmediate where needed on node 0.10
* Added support for maxMessageSizeBytes if available (DRIVERS-1)
* Added support for authSource (2.4) to MongoClient URL and db.authenticate method (DRIVER-69/NODE-34)
* Fixed issue in GridStore seek and GridStore read to correctly work on multiple seeks (Issue #895)

1.2.13 2013-02-22
-----------------
* Allow strategy 'none' for repliaset if no strategy wanted (will default to round robin selection of servers on a set readPreference)
* Fixed missing MongoErrors on some cursor methods (Issue #882)
* Correctly returning a null for the db instance on MongoClient.connect when auth fails (Issue #890)
* Added dropTarget option support for renameCollection/rename (Issue #891, help from https://github.com/jbottigliero)
* Fixed issue where connection using MongoClient.connect would fail if first server did not exist (Issue #885)

1.2.12 2013-02-13
-----------------
* Added limit/skip options to Collection.count (Issue #870)
* Added applySkipLimit option to Cursor.count (Issue #870)
* Enabled ping strategy as default for Replicaset if none specified (Issue #876)
* Should correctly pick nearest server for SECONDARY/SECONDARY_PREFERRED/NEAREST (Issue #878)

1.2.11 2013-01-29
-----------------
* Added fixes for handling type 2 binary due to PHP driver (Issue #864)
* Moved callBackStore to Base class to have single unified store (Issue #866)
* Ping strategy now reuses sockets unless they are closed by the server to avoid overhead

1.2.10 2013-01-25
-----------------
* Merged in SSL support for 2.4 supporting certificate validation and presenting certificates to the server.
* Only open a new HA socket when previous one dead (Issue #859, #857)
* Minor fixes

1.2.9 2013-01-15
----------------
* Fixed bug in SSL support for MongoClient/Db.connect when discovering servers (Issue #849)
* Connection string with no db specified should default to admin db (Issue #848)
* Support port passed as string to Server class (Issue #844)
* Removed noOpen support for MongoClient/Db.connect as auto discovery of servers for Mongod/Mongos makes it not possible (Issue #842)
* Included toError wrapper code moved to utils.js file (Issue #839, #840)
* Rewrote cursor handling to avoid process.nextTick using trampoline instead to avoid stack overflow, speedup about 40%

1.2.8 2013-01-07
----------------
* Accept function in a Map Reduce scope object not only a function string (Issue #826, https://github.com/aheckmann)
* Typo in db.authenticate caused a check (for provided connection) to return false, causing a connection AND onAll=true to be passed into __executeQueryCommand downstream (Issue #831, https://github.com/m4tty)
* Allow gridfs objects to use non ObjectID ids (Issue #825, https://github.com/nailgun)
* Removed the double wrap, by not passing an Error object to the wrap function (Issue #832, https://github.com/m4tty)
* Fix connection leak (gh-827) for HA replicaset health checks (Issue #833, https://github.com/aheckmann)
* Modified findOne to use nextObject instead of toArray avoiding a nextTick operation (Issue #836)
* Fixes for cursor stream to avoid multiple getmore issues when one in progress (Issue #818)
* Fixes .open replaying all backed up commands correctly if called after operations performed, (Issue #829 and #823)

1.2.7 2012-12-23
----------------
* Rolled back batches as they hang in certain situations
* Fixes for NODE-25, keep reading from secondaries when primary goes down

1.2.6 2012-12-21
----------------
* domain sockets shouldn't require a port arg (Issue #815, https://github.com/aheckmann)
* Cannot read property 'info' of null (Issue #809, https://github.com/thesmart)
* Cursor.each should work in batches (Issue #804, https://github.com/Swatinem)
* Cursor readPreference bug for non-supported read preferences (Issue #817)

1.2.5 2012-12-12
----------------
* Fixed ssl regression, added more test coverage (Issue #800)
* Added better error reporting to the Db.connect if no valid serverConfig setup found (Issue #798)

1.2.4 2012-12-11
----------------
* Fix to ensure authentication is correctly applied across all secondaries when using MongoClient.

1.2.3 2012-12-10
----------------
* Fix for new replicaset members correctly authenticating when being added (Issue #791, https://github.com/m4tty)
* Fixed seek issue in gridstore when using stream (Issue #790)

1.2.2 2012-12-03
----------------
* Fix for journal write concern not correctly being passed under some circumstances.
* Fixed correct behavior and re-auth for servers that get stepped down (Issue #779).

1.2.1 2012-11-30
----------------
* Fix for double callback on insert with w:0 specified (Issue #783)
* Small cleanup of urlparser.

1.2.0 2012-11-27
----------------
* Honor connectTimeoutMS option for replicasets (Issue #750, https://github.com/aheckmann)
* Fix ping strategy regression (Issue #738, https://github.com/aheckmann)
* Small cleanup of code (Issue #753, https://github.com/sokra/node-mongodb-native)
* Fixed index declaration using objects/arrays from other contexts (Issue #755, https://github.com/sokra/node-mongodb-native)
* Intermittent (and rare) null callback exception when using ReplicaSets (Issue #752)
* Force correct setting of read_secondary based on the read preference (Issue #741)
* If using read preferences with secondaries queries will not fail if primary is down (Issue #744)
* noOpen connection for Db.connect removed as not compatible with autodetection of Mongo type
* Mongos connection with auth not working (Issue #737)
* Use the connect method directly from the require. require('mongodb')("mongodb://localhost:27017/db")
* new MongoClient introduced as the point of connecting to MongoDB's instead of the Db
  * open/close/db/connect methods implemented
* Implemented common URL connection format using MongoClient.connect allowing for simialar interface across all drivers.
* Fixed a bug with aggregation helper not properly accepting readPreference

1.1.11 2012-10-10
-----------------
* Removed strict mode and introduced normal handling of safe at DB level.

1.1.10 2012-10-08
-----------------
* fix Admin.serverStatus (Issue #723, https://github.com/Contra)
* logging on connection open/close(Issue #721, https://github.com/asiletto)
* more fixes for windows bson install (Issue #724)

1.1.9 2012-10-05
----------------
* Updated bson to 0.1.5 to fix build problem on sunos/windows.

1.1.8 2012-10-01
----------------
* Fixed db.eval to correctly handle system.js global javascript functions (Issue #709)
* Cleanup of non-closing connections (Issue #706)
* More cleanup of connections under replicaset (Issue #707, https://github.com/elbert3)
* Set keepalive on as default, override if not needed
* Cleanup of jsbon install to correctly build without install.js script (https://github.com/shtylman)
* Added domain socket support new Server("/tmp/mongodb.sock") style

1.1.7 2012-09-10
----------------
* Protect against starting PingStrategy being called more than once (Issue #694, https://github.com/aheckmann)
* Make PingStrategy interval configurable (was 1 second, relaxed to 5) (Issue #693, https://github.com/aheckmann)
* Made PingStrategy api more consistant, callback to start/stop methods are optional (Issue #693, https://github.com/aheckmann)
* Proper stopping of strategy on replicaset stop
* Throw error when gridstore file is not found in read mode (Issue #702, https://github.com/jbrumwell)
* Cursor stream resume now using nextTick to avoid duplicated records (Issue #696)

1.1.6 2012-09-01
----------------
* Fix for readPreference NEAREST for replicasets (Issue #693, https://github.com/aheckmann)
* Emit end correctly on stream cursor (Issue #692, https://github.com/Raynos)

1.1.5 2012-08-29
----------------
* Fix for eval on replicaset Issue #684
* Use helpful error msg when native parser not compiled (Issue #685, https://github.com/aheckmann)
* Arbiter connect hotfix (Issue #681, https://github.com/fengmk2)
* Upgraded bson parser to 0.1.2 using gyp, deprecated support for node 0.4.X
* Added name parameter to createIndex/ensureIndex to be able to override index names larger than 128 bytes
* Added exhaust option for find for feature completion (not recommended for normal use)
* Added tailableRetryInterval to find for tailable cursors to allow to control getMore retry time interval
* Fixes for read preferences when using MongoS to correctly handle no read preference set when iterating over a cursor (Issue #686)

1.1.4 2012-08-12
----------------
* Added Mongos connection type with a fallback list for mongos proxies, supports ha (on by default) and will attempt to reconnect to failed proxies.
* Documents can now have a toBSON method that lets the user control the serialization behavior for documents being saved.
* Gridstore instance object now works as a readstream or writestream (thanks to code from Aaron heckmann (https://github.com/aheckmann/gridfs-stream)).
* Fix gridfs readstream (Issue #607, https://github.com/tedeh).
* Added disableDriverBSONSizeCheck property to Server.js for people who wish to push the inserts to the limit (Issue #609).
* Fixed bug where collection.group keyf given as Code is processed as a regular object (Issue #608, https://github.com/rrusso2007).
* Case mismatch between driver's ObjectID and mongo's ObjectId, allow both (Issue #618).
* Cleanup map reduce (Issue #614, https://github.com/aheckmann).
* Add proper error handling to gridfs (Issue #615, https://github.com/aheckmann).
* Ensure cursor is using same connection for all operations to avoid potential jump of servers when using replicasets.
* Date identification handled correctly in bson js parser when running in vm context.
* Documentation updates
* GridStore filename not set on read (Issue #621)
* Optimizations on the C++ bson parser to fix a potential memory leak and avoid non-needed calls
* Added support for awaitdata for tailable cursors (Issue #624)
* Implementing read preference setting at collection and cursor level
   * collection.find().setReadPreference(Server.SECONDARY_PREFERRED)
   * db.collection("some", {readPreference:Server.SECONDARY})
* Replicaset now returns when the master is discovered on db.open and lets the rest of the connections happen asynchronous.
  * ReplSet/ReplSetServers emits "fullsetup" when all servers have been connected to
* Prevent callback from executing more than once in getMore function (Issue #631, https://github.com/shankar0306)
* Corrupt bson messages now errors out to all callbacks and closes up connections correctly, Issue #634
* Replica set member status update when primary changes bug (Issue #635, https://github.com/alinsilvian)
* Fixed auth to work better when multiple connections are involved.
* Default connection pool size increased to 5 connections.
* Fixes for the ReadStream class to work properly with 0.8 of Node.js
* Added explain function support to aggregation helper
* Added socketTimeoutMS and connectTimeoutMS to socket options for repl_set.js and server.js
* Fixed addUser to correctly handle changes in 2.2 for getLastError authentication required
* Added index to gridstore chunks on file_id (Issue #649, https://github.com/jacobbubu)
* Fixed Always emit db events (Issue #657)
* Close event not correctly resets DB openCalled variable to allow reconnect
* Added open event on connection established for replicaset, mongos and server
* Much faster BSON C++ parser thanks to Lucasfilm Singapore.
* Refactoring of replicaset connection logic to simplify the code.
* Add `options.connectArbiter` to decide connect arbiters or not (Issue #675)
* Minor optimization for findAndModify when not using j,w or fsync for safe

1.0.2 2012-05-15
----------------
* Reconnect functionality for replicaset fix for mongodb 2.0.5

1.0.1 2012-05-12
----------------
* Passing back getLastError object as 3rd parameter on findAndModify command.
* Fixed a bunch of performance regressions in objectId and cursor.
* Fixed issue #600 allowing for single document delete to be passed in remove command.

1.0.0 2012-04-25
----------------
* Fixes to handling of failover on server error
* Only emits error messages if there are error listeners to avoid uncaught events
* Server.isConnected using the server state variable not the connection pool state

0.9.9.8 2012-04-12
------------------
* _id=0 is being turned into an ObjectID (Issue #551)
* fix for error in GridStore write method (Issue #559)
* Fix for reading a GridStore from arbitrary, non-chunk aligned offsets, added test (Issue #563, https://github.com/subroutine)
* Modified limitRequest to allow negative limits to pass through to Mongo, added test (Issue #561)
* Corrupt GridFS files when chunkSize < fileSize, fixed concurrency issue (Issue #555)
* Handle dead tailable cursors (Issue #568, https://github.com/aheckmann)
* Connection pools handles closing themselves down and clearing the state
* Check bson size of documents against maxBsonSize and throw client error instead of server error, (Issue #553)
* Returning update status document at the end of the callback for updates, (Issue #569)
* Refactor use of Arguments object to gain performance (Issue #574, https://github.com/AaronAsAChimp)

0.9.9.7 2012-03-16
------------------
* Stats not returned from map reduce with inline results (Issue #542)
* Re-enable testing of whether or not the callback is called in the multi-chunk seek, fix small GridStore bug (Issue #543, https://github.com/pgebheim)
* Streaming large files from GridFS causes truncation (Issue #540)
* Make callback type checks agnostic to V8 context boundaries (Issue #545)
* Correctly throw error if an attempt is made to execute an insert/update/remove/createIndex/ensureIndex with safe enabled and no callback
* Db.open throws if the application attemps to call open again without calling close first

0.9.9.6 2012-03-12
------------------
* BSON parser is externalized in it's own repository, currently using git master
* Fixes for Replicaset connectivity issue (Issue #537)
* Fixed issues with node 0.4.X vs 0.6.X (Issue #534)
* Removed SimpleEmitter and replaced with standard EventEmitter
* GridStore.seek fails to change chunks and call callback when in read mode (Issue #532)

0.9.9.5 2012-03-07
------------------
* Merged in replSetGetStatus helper to admin class (Issue #515, https://github.com/mojodna)
* Merged in serverStatus helper to admin class (Issue #516, https://github.com/mojodna)
* Fixed memory leak in C++ bson parser (Issue #526)
* Fix empty MongoError "message" property (Issue #530, https://github.com/aheckmann)
* Cannot save files with the same file name to GridFS (Issue #531)

0.9.9.4 2012-02-26
------------------
* bugfix for findAndModify: Error: corrupt bson message < 5 bytes long (Issue #519)

0.9.9.3 2012-02-23
------------------
* document: save callback arguments are both undefined, (Issue #518)
* Native BSON parser install error with npm, (Issue #517)

0.9.9.2 2012-02-17
------------------
* Improved detection of Buffers using Buffer.isBuffer instead of instanceof.
* Added wrap error around db.dropDatabase to catch all errors (Issue #512)
* Added aggregate helper to collection, only for MongoDB >= 2.1

0.9.9.1 2012-02-15
------------------
* Better handling of safe when using some commands such as createIndex, ensureIndex, addUser, removeUser, createCollection.
* Mapreduce now throws error if out parameter is not specified.

0.9.9 2012-02-13
----------------
* Added createFromTime method on ObjectID to allow for queries against _id more easily using the timestamp.
* Db.close(true) now makes connection unusable as it's been force closed by app.
* Fixed mapReduce and group functions to correctly send slaveOk on queries.
* Fixes for find method to correctly work with find(query, fields, callback) (Issue #506).
* A fix for connection error handling when using the SSL on MongoDB.

0.9.8-7 2012-02-06
------------------
* Simplified findOne to use the find command instead of the custom code (Issue #498).
* BSON JS parser not also checks for _bsonType variable in case BSON object is in weird scope (Issue #495).

0.9.8-6 2012-02-04
------------------
* Removed the check for replicaset change code as it will never work with node.js.

0.9.8-5 2012-02-02
------------------
* Added geoNear command to Collection.
* Added geoHaystackSearch command to Collection.
* Added indexes command to collection to retrieve the indexes on a Collection.
* Added stats command to collection to retrieve the statistics on a Collection.
* Added listDatabases command to admin object to allow retrieval of all available dbs.
* Changed createCreateIndexCommand to work better with options.
* Fixed dereference method on Db class to correctly dereference Db reference objects.
* Moved connect object onto Db class(Db.connect) as well as keeping backward compatibility.
* Removed writeBuffer method from gridstore, write handles switching automatically now.
* Changed readBuffer to read on Gridstore, Gridstore now only supports Binary Buffers no Strings anymore.
* Moved Long class to bson directory.

0.9.8-4 2012-01-28
------------------
* Added reIndex command to collection and db level.
* Added support for $returnKey, $maxScan, $min, $max, $showDiskLoc, $comment to cursor and find/findOne methods.
* Added dropDups and v option to createIndex and ensureIndex.
* Added isCapped method to Collection.
* Added indexExists method to Collection.
* Added findAndRemove method to Collection.
* Fixed bug for replicaset connection when no active servers in the set.
* Fixed bug for replicaset connections when errors occur during connection.
* Merged in patch for BSON Number handling from Lee Salzman, did some small fixes and added test coverage.

0.9.8-3 2012-01-21
------------------
* Workaround for issue with Object.defineProperty (Issue #484)
* ObjectID generation with date does not set rest of fields to zero (Issue #482)

0.9.8-2 2012-01-20
------------------
* Fixed a missing this in the ReplSetServers constructor.

0.9.8-1 2012-01-17
------------------
* FindAndModify bug fix for duplicate errors (Issue #481)

0.9.8 2012-01-17
----------------
* Replicasets now correctly adjusts to live changes in the replicaset configuration on the servers, reconnecting correctly.
  * Set the interval for checking for changes setting the replicaSetCheckInterval property when creating the ReplSetServers instance or on db.serverConfig.replicaSetCheckInterval. (default 1000 miliseconds)
* Fixes formattedOrderClause in collection.js to accept a plain hash as a parameter (Issue #469) https://github.com/tedeh
* Removed duplicate code for formattedOrderClause and moved to utils module
* Pass in poolSize for ReplSetServers to set default poolSize for new replicaset members
* Bug fix for BSON JS deserializer. Isolating the eval functions in separate functions to avoid V8 deoptimizations
* Correct handling of illegal BSON messages during deserialization
* Fixed Infinite loop when reading GridFs file with no chunks (Issue #471)
* Correctly update existing user password when using addUser (Issue #470)

0.9.7.3-5 2012-01-04
--------------------
* Fix for RegExp serialization for 0.4.X where typeof /regexp/ == 'function' vs in 0.6.X typeof /regexp/ == 'object'
* Don't allow keepAlive and setNoDelay for 0.4.X as it throws errors

0.9.7.3-4 2012-01-04
--------------------
* Chased down potential memory leak on findAndModify, Issue #467 (node.js removeAllListeners leaves the key in the _events object, node.js bug on eventlistener?, leads to extremely slow memory leak on listener object)
* Sanity checks for GridFS performance with benchmark added

0.9.7.3-3 2012-01-04
--------------------
* Bug fixes for performance issues going form 0.9.6.X to 0.9.7.X on linux
* BSON bug fixes for performance

0.9.7.3-2 2012-01-02
--------------------
* Fixed up documentation to reflect the preferred way of instantiating bson types
* GC bug fix for JS bson parser to avoid stop-and-go GC collection

0.9.7.3-1 2012-01-02
--------------------
* Fix to make db.bson_serializer and db.bson_deserializer work as it did previously

0.9.7.3 2011-12-30
--------------------
* Moved BSON_BINARY_SUBTYPE_DEFAULT from BSON object to Binary object and removed the BSON_BINARY_ prefixes
* Removed Native BSON types, C++ parser uses JS types (faster due to cost of crossing the JS-C++ barrier for each call)
* Added build fix for 0.4.X branch of Node.js where GetOwnPropertyNames is not defined in v8
* Fix for wire protocol parser for corner situation where the message is larger than the maximum socket buffer in node.js (Issue #464, #461, #447)
* Connection pool status set to connected on poolReady, isConnected returns false on anything but connected status (Issue #455)

0.9.7.2-5 2011-12-22
--------------------
* Brand spanking new Streaming Cursor support Issue #458 (https://github.com/christkv/node-mongodb-native/pull/458) thanks to Mr Aaron Heckmann

0.9.7.2-4 2011-12-21
--------------------
* Refactoring of callback code to work around performance regression on linux
* Fixed group function to correctly use the command mode as default

0.9.7.2-3 2011-12-18
--------------------
* Fixed error handling for findAndModify while still working for mongodb 1.8.6 (Issue #450).
* Allow for force send query to primary, pass option (read:'primary') on find command.
    * ``find({a:1}, {read:'primary'}).toArray(function(err, items) {});``

0.9.7.2-2 2011-12-16
--------------------
* Fixes infinite streamRecords QueryFailure fix when using Mongos (Issue #442)

0.9.7.2-1 2011-12-16
--------------------
* ~10% perf improvement for ObjectId#toHexString (Issue #448, https://github.com/aheckmann)
* Only using process.nextTick on errors emitted on callbacks not on all parsing, reduces number of ticks in the driver
* Changed parsing off bson messages to use process.nextTick to do bson parsing in batches if the message is over 10K as to yield more time to the event look increasing concurrency on big mongoreply messages with multiple documents

0.9.7.2 2011-12-15
------------------
* Added SSL support for future version of mongodb (VERY VERY EXPERIMENTAL)
    * pass in the ssl:true option to the server or replicaset server config to enable
    * a bug either in mongodb or node.js does not allow for more than 1 connection pr db instance (poolSize:1).
* Added getTimestamp() method to objectID that returns a date object
* Added finalize function to collection.group
    * function group (keys, condition, initial, reduce, finalize, command, callback)
* Reaper no longer using setTimeout to handle reaping. Triggering is done in the general flow leading to predictable behavior.
    * reaperInterval, set interval for reaper (default 10000 miliseconds)
    * reaperTimeout, set timeout for calls (default 30000 miliseconds)
    * reaper, enable/disable reaper (default false)
* Work around for issues with findAndModify during high concurrency load, insure that the behavior is the same across the 1.8.X branch and 2.X branch of MongoDb
* Reworked multiple db's sharing same connection pool to behave correctly on error, timeout and close
* EnsureIndex command can be executed without a callback (Issue #438)
* Eval function no accepts options including nolock (Issue #432)
    * eval(code, parameters, options, callback) (where options = {nolock:true})

0.9.7.1-4 2011-11-27
--------------------
* Replaced install.sh with install.js to install correctly on all supported os's

0.9.7.1-3 2011-11-27
--------------------
* Fixes incorrect scope for ensureIndex error wrapping (Issue #419) https://github.com/ritch

0.9.7.1-2 2011-11-27
--------------------
* Set statistical selection strategy as default for secondary choice.

0.9.7.1-1 2011-11-27
--------------------
* Better handling of single server reconnect (fixes some bugs)
* Better test coverage of single server failure
* Correct handling of callbacks on replicaset servers when firewall dropping packets, correct reconnect

0.9.7.1 2011-11-24
------------------
* Better handling of dead server for single server instances
* FindOne and find treats selector == null as {}, Issue #403
* Possible to pass in a strategy for the replicaset to pick secondary reader node
    * parameter strategy
        * ping (default), pings the servers and picks the one with the lowest ping time
        * statistical, measures each request and pick the one with the lowest mean and std deviation
* Set replicaset read preference replicaset.setReadPreference()
    * Server.READ_PRIMARY (use primary server for reads)
    * Server.READ_SECONDARY (from a secondary server (uses the strategy set))
    * tags, {object of tags}
* Added replay of commands issued to a closed connection when the connection is re-established
* Fix isConnected and close on unopened connections. Issue #409, fix by (https://github.com/sethml)
* Moved reaper to db.open instead of constructor (Issue #406)
* Allows passing through of socket connection settings to Server or ReplSetServer under the option socketOptions
    * timeout = set seconds before connection times out (default 0)
    * noDelay = Disables the Nagle algorithm (default true)
    * keepAlive = Set if keepAlive is used (default 0, which means no keepAlive, set higher than 0 for keepAlive)
    * encoding = ['ascii', 'utf8', or 'base64'] (default null)
* Fixes for handling of errors during shutdown off a socket connection
* Correctly applies socket options including timeout
* Cleanup of test management code to close connections correctly
* Handle parser errors better, closing down the connection and emitting an error
* Correctly emit errors from server.js only wrapping errors that are strings

0.9.7 2011-11-10
----------------
* Added priority setting to replicaset manager
* Added correct handling of passive servers in replicaset
* Reworked socket code for simpler clearer handling
* Correct handling of connections in test helpers
* Added control of retries on failure
    * control with parameters retryMiliSeconds and numberOfRetries when creating a db instance
* Added reaper that will timeout and cleanup queries that never return
    * control with parameters reaperInterval and reaperTimeout when creating a db instance
* Refactored test helper classes for replicaset tests
* Allows raw (no bson parser mode for insert, update, remove, find and findOne)
    * control raw mode passing in option raw:true on the commands
    * will return buffers with the binary bson objects
* Fixed memory leak in cursor.toArray
* Fixed bug in command creation for mongodb server with wrong scope of call
* Added db(dbName) method to db.js to allow for reuse of connections against other databases
* Serialization of functions in an object is off by default, override with parameter
    * serializeFunctions [true/false] on db level, collection level or individual insert/update/findAndModify
* Added Long.fromString to c++ class and fixed minor bug in the code (Test case for $gt operator on 64-bit integers, Issue #394)
* FindOne and find now share same code execution and will work in the same manner, Issue #399
* Fix for tailable cursors, Issue #384
* Fix for Cursor rewind broken, Issue #389
* Allow Gridstore.exist to query using regexp, Issue #387, fix by (https://github.com/kaij)
* Updated documentation on https://github.com/christkv/node-mongodb-native
* Fixed toJSON methods across all objects for BSON, Binary return Base64 Encoded data

0.9.6-22 2011-10-15
-------------------
* Fixed bug in js bson parser that could cause wrong object size on serialization, Issue #370
* Fixed bug in findAndModify that did not throw error on replicaset timeout, Issue #373

0.9.6-21 2011-10-05
-------------------
* Reworked reconnect code to work correctly
* Handling errors in different parts of the code to ensure that it does not lock the connection
* Consistent error handling for Object.createFromHexString for JS and C++

0.9.6-20 2011-10-04
-------------------
* Reworked bson.js parser to get rid off Array.shift() due to it allocating new memory for each call. Speedup varies between 5-15% depending on doc
* Reworked bson.cc to throw error when trying to serialize js bson types
* Added MinKey, MaxKey and Double support for JS and C++ parser
* Reworked socket handling code to emit errors on unparsable messages
* Added logger option for Db class, lets you pass in a function in the shape
    {
        log : function(message, object) {},
        error : function(errorMessage, errorObject) {},
        debug : function(debugMessage, object) {},
    }

  Usage is new Db(new Server(..), {logger: loggerInstance})

0.9.6-19 2011-09-29
-------------------
* Fixing compatibility issues between C++ bson parser and js parser
* Added Symbol support to C++ parser
* Fixed socket handling bug for seldom misaligned message from mongodb
* Correctly handles serialization of functions using the C++ bson parser

0.9.6-18 2011-09-22
-------------------
* Fixed bug in waitForConnection that would lead to 100% cpu usage, Issue #352

0.9.6-17 2011-09-21
-------------------
* Fixed broken exception test causing bamboo to hang
* Handling correctly command+lastError when both return results as in findAndModify, Issue #351

0.9.6-16 2011-09-14
-------------------
* Fixing a bunch of issues with compatibility with MongoDB 2.0.X branch. Some fairly big changes in behavior from 1.8.X to 2.0.X on the server.
* Error Connection MongoDB V2.0.0 with Auth=true, Issue #348

0.9.6-15 2011-09-09
-------------------
* Fixed issue where pools would not be correctly cleaned up after an error, Issue #345
* Fixed authentication issue with secondary servers in Replicaset, Issue #334
* Duplicate replica-set servers when omitting port, Issue #341
* Fixing findAndModify to correctly work with Replicasets ensuring proper error handling, Issue #336
* Merged in code from (https://github.com/aheckmann) that checks for global variable leaks

0.9.6-14 2011-09-05
-------------------
* Minor fixes for error handling in cursor streaming (https://github.com/sethml), Issue #332
* Minor doc fixes
* Some more cursor sort tests added, Issue #333
* Fixes to work with 0.5.X branch
* Fix Db not removing reconnect listener from serverConfig, (https://github.com/sbrekken), Issue #337
* Removed node_events.h includes (https://github.com/jannehietamaki), Issue #339
* Implement correct safe/strict mode for findAndModify.

0.9.6-13 2011-08-24
-------------------
* Db names correctly error checked for illegal characters

0.9.6-12 2011-08-24
-------------------
* Nasty bug in GridFS if you changed the default chunk size
* Fixed error handling bug in findOne

0.9.6-11 2011-08-23
-------------------
* Timeout option not correctly making it to the cursor, Issue #320, Fix from (https://github.com/year2013)
* Fixes for memory leaks when using buffers and C++ parser
* Fixes to make tests pass on 0.5.X
* Cleanup of bson.js to remove duplicated code paths
* Fix for errors occurring in ensureIndex, Issue #326
* Removing require.paths to make tests work with the 0.5.X branch

0.9.6-10 2011-08-11
-------------------
* Specific type Double for capped collections (https://github.com/mbostock), Issue #312
* Decorating Errors with all all object info from Mongo (https://github.com/laurie71), Issue #308
* Implementing fixes for mongodb 1.9.1 and higher to make tests pass
* Admin validateCollection now takes an options argument for you to pass in full option
* Implemented keepGoing parameter for mongodb 1.9.1 or higher, Issue #310
* Added test for read_secondary count issue, merged in fix from (https://github.com/year2013), Issue #317

0.9.6-9
-------
* Bug fix for bson parsing the key '':'' correctly without crashing

0.9.6-8
-------
* Changed to using node.js crypto library MD5 digest
* Connect method support documented mongodb: syntax by (https://github.com/sethml)
* Support Symbol type for BSON, serializes to it's own type Symbol, Issue #302, #288
* Code object without scope serializing to correct BSON type
* Lot's of fixes to avoid double callbacks (https://github.com/aheckmann) Issue #304
* Long deserializes as Number for values in the range -2^53 to 2^53, Issue #305 (https://github.com/sethml)
* Fixed C++ parser to reflect JS parser handling of long deserialization
* Bson small optimizations

0.9.6-7 2011-07-13
------------------
* JS Bson deserialization bug #287

0.9.6-6 2011-07-12
------------------
* FindAndModify not returning error message as other methods Issue #277
* Added test coverage for $push, $pushAll and $inc atomic operations
* Correct Error handling for non 12/24 bit ids on Pure JS ObjectID class Issue #276
* Fixed terrible deserialization bug in js bson code #285
* Fix by andrewjstone to avoid throwing errors when this.primary not defined

0.9.6-5 2011-07-06
------------------
* Rewritten BSON js parser now faster than the C parser on my core2duo laptop
* Added option full to indexInformation to get all index info Issue #265
* Passing in ObjectID for new Gridstore works correctly Issue #272

0.9.6-4 2011-07-01
------------------
* Added test and bug fix for insert/update/remove without callback supplied

0.9.6-3 2011-07-01
------------------
* Added simple grid class called Grid with put, get, delete methods
* Fixed writeBuffer/readBuffer methods on GridStore so they work correctly
* Automatic handling of buffers when using write method on GridStore
* GridStore now accepts a ObjectID instead of file name for write and read methods
* GridStore.list accepts id option to return of file ids instead of filenames
* GridStore close method returns document for the file allowing user to reference _id field

0.9.6-2 2011-06-30
------------------
* Fixes for reconnect logic for server object (replays auth correctly)
* More testcases for auth
* Fixes in error handling for replicaset
* Fixed bug with safe parameter that would fail to execute safe when passing w or wtimeout
* Fixed slaveOk bug for findOne method
* Implemented auth support for replicaset and test cases
* Fixed error when not passing in rs_name

0.9.6-1 2011-06-25
------------------
* Fixes for test to run properly using c++ bson parser
* Fixes for dbref in native parser (correctly handles ref without db component)
* Connection fixes for replicasets to avoid runtime conditions in cygwin (https://github.com/vincentcr)
* Fixes for timestamp in js bson parser (distinct timestamp type now)

0.9.6 2011-06-21
----------------
* Worked around npm version handling bug
* Race condition fix for cygwin (https://github.com/vincentcr)

0.9.5-1 2011-06-21
------------------
* Extracted Timestamp as separate class for bson js parser to avoid instanceof problems
* Fixed driver strict mode issue

0.9.5 2011-06-20
----------------
* Replicaset support (failover and reading from secondary servers)
* Removed ServerPair and ServerCluster
* Added connection pool functionality
* Fixed serious bug in C++ bson parser where bytes > 127 would generate 2 byte sequences
* Allows for forcing the server to assign ObjectID's using the option {forceServerObjectId: true}

0.6.8
-----
* Removed multiple message concept from bson
* Changed db.open(db) to be db.open(err, db)

0.1 2010-01-30
--------------
* Initial release support of driver using native node.js interface
* Supports gridfs specification
* Supports admin functionality
