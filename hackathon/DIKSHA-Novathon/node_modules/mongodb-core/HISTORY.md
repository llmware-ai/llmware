<a name="2.1.18"></a>
## [2.1.18](https://github.com/christkv/mongodb-core/compare/v2.1.17...v2.1.18) (2018-01-02)


### Bug Fixes

* **auth:** don't redeclare BSON variable in plain auth ([4fc77e3](https://github.com/christkv/mongodb-core/commit/4fc77e3))
* **auth:** remove extra bson include ([4411d2c](https://github.com/christkv/mongodb-core/commit/4411d2c))
* **connection:** accept incoming missed ssl options from mongo-native-driver ([fd543eb](https://github.com/christkv/mongodb-core/commit/fd543eb))
* **connection:** added missed tls option ecdhCurve ([ca1d909](https://github.com/christkv/mongodb-core/commit/ca1d909))
* **connection:** default `family` to undefined rather than 4 ([09916ae](https://github.com/christkv/mongodb-core/commit/09916ae))
* **connection:** fixing leaky connection ([#234](https://github.com/christkv/mongodb-core/issues/234)) ([7633f10](https://github.com/christkv/mongodb-core/commit/7633f10))
* **cursor:** check for autoReconnect option only for single server ([c841eb5](https://github.com/christkv/mongodb-core/commit/c841eb5))
* **secondaries:** fixes connection with secondary readPreference ([5763f5c](https://github.com/christkv/mongodb-core/commit/5763f5c))
* **timeout:** fixed compatibility with node <=0.12.x ([c7c72b2](https://github.com/christkv/mongodb-core/commit/c7c72b2)), closes [mongodb-js/mongodb-core#247](https://github.com/mongodb-js/mongodb-core/issues/247) [mongodb-js/mongodb-core#247](https://github.com/mongodb-js/mongodb-core/issues/247) [mongodb-js/mongodb-core#248](https://github.com/mongodb-js/mongodb-core/issues/248) [#248](https://github.com/christkv/mongodb-core/issues/248)


### Features

* **replicaset:** More verbose replica set errors emission: ([#231](https://github.com/christkv/mongodb-core/issues/231)) ([de6d220](https://github.com/christkv/mongodb-core/commit/de6d220))



2.1.17 2017-10-11
-----------------
* fix a typo that completely broke SCRAM-SHA1 authentication

2.1.16 2017-10-11
-----------------
* avoid waiting for reconnect if reconnect disabled in Server topology
* avoid waiting for reconnect if reconnect disabled in Cursor
* NODE-990 cache the ScramSHA1 salted passwords up to 200 entries
* NODE-1153 ensure that errors are propagated on force destroy
* NODE-1153 ensure inUse and connecting queues are cleared on reauth

2.1.15 2017-08-08
-----------------
* Emit SDAM events on close and reconnect

2.1.14 2017-07-07
-----------------
* NODE-1073 updates scram.js hi() algorithm to utilize crypto.pbkdf2Sync()
* NODE-1049 only include primary server if there are no secondary servers for
  readPrefrence secondaryPreferred
* moved `assign` polyfill to shared utils, replace usage of `extend` in tests

2.1.13 2017-06-19
-----------------
* NODE-1039 ensure we force destroy server instances, forcing queue to be flushed.
*  Use actual server type in standalone SDAM events.

2.1.12 2017-06-02
-----------------
* NODE-1019 Set keepAlive to 300 seconds or 1/2 of socketTimeout if socketTimeout < keepAlive.
* Minor fix to report the correct state on error.
* NODE-1020 'family' was added to options to provide high priority for ipv6 addresses (Issue #1518, https://github.com/firej).
* Fix require_optional loading of bson-ext.
* Ensure no errors are thrown by replset if topology is destroyed before it finished connecting.
* NODE-999 SDAM fixes for Mongos and single Server event emitting.
* NODE-1014 Set socketTimeout to default to 360 seconds.
* NODE-1019 Set keepAlive to 300 seconds or 1/2 of socketTimeout if socketTimeout < keepAlive.

2.1.11 2017-05-22
-----------------
* NODE-987 Clear out old intervalIds on when calling topologyMonitor.
* NODE-987 Moved filtering to pingServer method and added test case.
* Check for connection destroyed just before writing out and flush out operations correctly if it is (Issue #179, https://github.com/jmholzinger).
* NODE-989 Refactored Replicaset monitoring to correcly monitor newly added servers, Also extracted setTimeout and setInterval to use custom wrappers Timeout and Interva.

2.1.10 2017-04-18
-----------------
* NODE-981 delegate auth to replset/mongos if inTopology is set.
* NODE-978 Wrap connection.end in try/catch for node 0.10.x issue causing exceptions to be thrown, Also surfaced getConnection for mongos and replset.
* Remove dynamic require (Issue #175, https://github.com/tellnes).
* NODE-696 Handle interrupted error for createIndexes.
* Fixed isse when user is executing find command using Server.command and it get interpreted as a wire protcol message, #172.
* NODE-966 promoteValues not being promoted correctly to getMore.
* Merged in fix for flushing out monitoring operations.

2.1.9 2017-03-17
----------------
* Return lastIsMaster correctly when connecting with secondaryOnlyConnectionAllowed is set to true and only a secondary is available in replica state.
* Clone options when passed to wireProtocol handler to avoid intermittent modifications causing errors.
* Ensure SSL error propegates better for Replset connections when there is a SSL validation error.
* NODE-957 Fixed issue where < batchSize not causing cursor to be closed on execution of first batch.
* NODE-958 Store reconnectConnection on pool object to allow destroy to close immediately.

2.1.8 2017-02-13
----------------
* NODE-925 ensure we reschedule operations while pool is < poolSize while pool is growing and there are no connections with not currently performing work.
* NODE-927 fixes issue where authentication was performed against arbiter instances.
* NODE-915 Normalize all host names to avoid comparison issues.
* Fixed issue where pool.destroy would never finish due to a single operation not being executed and keeping it open.

2.1.7 2017-01-24
----------------
* NODE-919 ReplicaSet connection does not close immediately (Issue #156).
* NODE-901 Fixed bug when normalizing host names.
* NODE-909 Fixed readPreference issue caused by direct connection to primary.
* NODE-910 Fixed issue when bufferMaxEntries == 0 and read preference set to nearest.

2.1.6 2017-01-13
----------------
* NODE-908 Keep auth contexts in replset and mongos topology to ensure correct application of authentication credentials when primary is first server to be detected causing an immediate connect event to happen.

2.1.5 2017-01-11
----------------
* updated bson and bson-ext dependencies to 1.0.4 to work past early node 4.x.x version having a broken Buffer.from implementation.

2.1.4 2017-01-03
----------------
* updated bson and bson-ext dependencies to 1.0.3 due to util.inspect issue with ObjectId optimizations.

2.1.3 2017-01-03
----------------
* Monitoring operations are re-scheduled in pool if it cannot find a connection that does not already have scheduled work on it, this is to avoid the monitoring socket timeout being applied to any existing operations on the socket due to pipelining
* Moved replicaset monitoring away from serial mode and to parallel mode.
* updated bson and bson-ext dependencies to 1.0.2.

2.1.2 2016-12-10
----------------
* Delay topologyMonitoring on successful attemptReconnect as no need to run a full scan immediately.
* Emit reconnect event in primary joining when in connected status for a replicaset.

2.1.1 2016-12-08
----------------
* Updated bson library to 1.0.1.
* Added optional support for bson-ext 1.0.1.

2.1.0 2016-12-05
----------------
* Updated bson library to 1.0.0.
* Added optional support for bson-ext 1.0.0.
* Expose property parserType allowing for identification of currently configured parser.

2.0.14 2016-11-29
-----------------
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

2.0.13 2016-10-21
-----------------
* Updated bson library to 0.5.6.
  - Included cyclic dependency detection
* Fire callback when topology was destroyed (Issue #147, https://github.com/vkarpov15).
* Refactoring to support pipelining ala 1.4.x branch will retaining the benefits of the growing/shrinking pool (Issue #146).
* Fix typo in serverHeartbeatFailed event name (Issue #143, https://github.com/jakesjews).
* NODE-798 Driver hangs on count command in replica set with one member (Issue #141, https://github.com/isayme).

2.0.12 2016-09-15
-----------------
* fix debug logging message not printing server name.
* fixed application metadata being sent by wrong ismaster.
* NODE-812 Fixed mongos stall due to proxy monitoring ismaster failure causing reconnect.
* NODE-818 Replicaset timeouts in initial connect sequence can "no primary found".
* Updated bson library to 0.5.5.
* Added DBPointer up conversion to DBRef.

2.0.11 2016-08-29
-----------------
* NODE-803, Fixed issue in how the latency window is calculated for Mongos topology causing issues for single proxy connections.
* Avoid timeout in attemptReconnect causing multiple attemptReconnect attempts to happen (Issue #134, https://github.com/dead-horse).
* Ensure promoteBuffers is propagated in same fashion as promoteValues and promoteLongs

2.0.10 2016-08-23
-----------------
* Added promoteValues flag (default to true) to allow user to specify they only want wrapped BSON values back instead of promotion to native types.
* Do not close mongos proxy connection on failed ismaster check in ha process (Issue #130).

2.0.9 2016-08-19
----------------
* Allow promoteLongs to be passed in through Response.parse method and overrides default set on the connection.
* NODE-798 Driver hangs on count command in replica set with one member.
* Allow promoteLongs to be passed in through Response.parse method and overrides default set on the connection.
* Allow passing in servername for TLS connections for SNI support.

2.0.8 2016-08-16
----------------
* Allow execution of store operations indepent of having both a primary and secondary available (Issue #123).
* Fixed command execution issue for mongos to ensure buffering of commands when no mongos available.
* Added hashed connection names and fullResult.
* Updated bson library to 0.5.3.
* Wrap callback in nextTick to ensure exceptions are thrown correctly.

2.0.7 2016-07-28
----------------
* Allow primary to be returned when secondaryPreferred is passed (Issue #117, https://github.com/dhendo).
* Added better warnings when passing in illegal seed list members to a Mongos topology.
* Minor attemptReconnect bug that would cause multiple attemptReconnect to run in parallel.
* Fix wrong opType passed to disconnectHandler.add (Issue #121, https://github.com/adrian-gierakowski)
* Implemented domain backward comp support enabled via domainsEnabled options on Server/ReplSet/Mongos and MongoClient.connect.
* Initial max staleness implementation for ReplSet and Mongos for 3.4 support.
* Added handling of collation for 3.4 support.

2.0.6 2016-07-19
----------------
* Destroy connection on socket timeout due to newer node versions not closing the socket.

2.0.5 2016-07-15
----------------
* Minor fixes to handle faster MongoClient connectivity from the driver, allowing single server instances to detect if they are a proxy.
* Added numberOfConsecutiveTimeouts to pool that will destroy the pool if the number of consecutive timeouts > reconnectTries.
* Print warning if seedlist servers host name does not match the one provided in it's ismaster.me field for Replicaset members.
* Fix issue where Replicaset connection would not succeeed if there the replicaset was a single primary server setup.

2.0.4 2016-07-11
-----------------
* Updated bson to version 0.5.1.
* handle situation where user is providing seedlist names that do not match host list. fix allows for a single full discovery connection sweep before erroring out.
* NODE-747 Polyfill for Object.assign for 0.12.x or 0.10.x.
* NODE-746 Improves replicaset errors for wrong setName.

2.0.3 2016-07-08
-----------------
* Implemented Server Selection Specification test suite.
* Added warning level to logger.
* Added warning message when sockeTimeout < haInterval for Replset/Mongos.

2.0.2 2016-07-06
-----------------
* Mongos emits close event on no proxies available or when reconnect attempt fails.
* Replset emits close event when no servers available or when attemptReconnect fails to reconnect.
* Don't throw in auth methods but return error in callback.

2.0.1 2016-07-05
-----------------
* Added missing logout method on mongos proxy topology.
* Fixed logger error serialization issue.
* Documentation fixes.

2.0.0 2016-07-05
-----------------
* Moved all authentication and handling of growing/shrinking of pool connections into actual pool.
* All authentication methods now handle both auth/reauthenticate and logout events.
* Introduced logout method to get rid of onAll option for logout command.
* Updated bson to 0.5.0 that includes Decimal128 support.

1.3.21 2016-05-30
-----------------
* Pool gets stuck if a connection marked for immediateRelease times out (Issue #99, https://github.com/nbrachet).
* Make authentication process retry up to authenticationRetries at authenticationRetryIntervalMS interval.
* Made ismaster replicaset calls operate with connectTimeout or monitorSocketTimeout to lower impact of big socketTimeouts on monitoring performance.
* Make sure connections mark as "immediateRelease" don't linger the inUserConnections list. Otherwise, after that connection times out, getAll() incorrectly returns more connections than are effectively present, causing the pool to not get restarted by reconnectServer. (Issue #99, https://github.com/nbrachet).
* Make cursor getMore or killCursor correctly trigger pool reconnect to single server if pool has not been destroyed.
* Make ismaster monitoring for single server connection default to avoid user confusion due to change in behavior.

1.3.20 2016-05-25
-----------------
* NODE-710 Allow setting driver loggerLevel and logger function from MongoClient options.
* Minor fix for SSL errors on connection attempts, minor fix to reconnect handler for the server.
* Don't write to socket before having registered the callback for commands, work around for windows issuing error events twice on node.js when socket gets destroyed by firewall.
* Fix minor issue where connectingServers would not be removed correctly causing single server connections to not auto-reconnect.

1.3.19 2016-05-17
-----------------
- Handle situation where a server connection in a replicaset sometimes fails to be destroyed properly due to being in the middle of authentication when the destroy method is called on the replicaset causing it to be orphaned and never collected.
- Set keepAlive to false by default to work around bug in node.js for Windows XP and Windows 2003.
- Ensure replicaset topology destroy is never called by SDAM.
- Ensure all paths are correctly returned on inspectServer in replset.

1.3.18 2016-04-27
-----------------
- Hardened cursor connection handling for getMore and killCursor to ensure mid operation connection kill does not throw null exception.
- Fixes for Node 6.0 support.

1.3.17 2016-04-26
-----------------
- Added improved handling of reconnect when topology is a single server.
- Added better handling of $query queries passed down for 3.2 or higher.
- Introduced getServerFrom method to topologies to let cursor grab a new pool for getMore and killCursors commands and not use connection pipelining.
- NODE-693 Move authentication to be after ismaster call to avoid authenticating against arbiters.

1.3.16 2016-04-07
-----------------
- Only call unref on destroy if it exists to ensure proper working destroy method on early node v0.10.x versions.

1.3.15 2016-04-06
-----------------
- NODE-687 Fixed issue where a server object failed to be destroyed if the replicaset state did not update successfully. This could leave active connections accumulating over time.
- Fixed some situations where all connections are flushed due to a single connection in the connection pool closing.

1.3.14 2016-04-01
-----------------
- Ensure server inquireServerState exits immediately on server.destroy call.
- Refactored readPreference handling in 2.4, 2.6 and 3.2 wire protocol handling.

1.3.13 2016-03-30
-----------------
- Handle missing cursor on getMore when going through a mongos proxy by pinning to socket connection and not server.

1.3.12 2016-03-29
-----------------
- Mongos pickProxies fall back to closest mongos if no proxies meet latency window specified.

1.3.11 2016-03-29
-----------------
- isConnected method for mongos uses same selection code as getServer.
- Exceptions in cursor getServer trapped and correctly delegated to high level handler.

1.3.10 2016-03-22
-----------------
- SDAM Monitoring emits diff for Replicasets to simplify detecting the state changes.
- SDAM Monitoring correctly emits Mongos as serverDescriptionEvent.

1.3.9 2016-03-20
----------------
- Removed monitoring exclusive connection, should resolve timeouts and reconnects on idle replicasets where haInteval > socketTimeout.

1.3.8 2016-03-18
----------------
- Implements the SDAM monitoring specification.
- Fix issue where cursor would error out and not be buffered when primary is not connected.

1.3.7 2016-03-16
----------------
- Fixed issue with replicasetInquirer where it could stop performing monitoring if there was no servers available.

1.3.6 2016-03-15
----------------
- Fixed raise condition where multiple replicasetInquirer operations could be started in parallel creating redundant connections.

1.3.5 2016-03-14
----------------
- Handle rogue SSL exceptions (Issue #85, https://github.com/durran).

1.3.4 2016-03-14
----------------
- Added unref options on server, replicaset and mongos (Issue #81, https://github.com/allevo)
- cursorNotFound flag always false (Issue #83, https://github.com/xgfd)
- refactor of events emission of fullsetup and all events (Issue #84, https://github.com/xizhibei)

1.3.3 2016-03-08
----------------
- Added support for promoteLongs option for command function.
- Return connection if no callback available
- Emit connect event when server reconnects after initial connection failed (Issue #76, https://github.com/vkarpov15)
- Introduced optional monitoringSocketTimeout option to allow better control of SDAM monitoring timeouts.
- Made monitoringSocketTimeout default to 30000 if no connectionTimeout value specified or if set to 0.
- Fixed issue where tailable cursor would not retry even though cursor was still alive.
- Disabled exhaust flag support to avoid issues where users could easily write code that would cause memory to run out.
- Handle the case where the first command result document returns an empty list of documents but a live cursor.
- Allow passing down off CANONICALIZE_HOST_NAME and SERVICE_REALM options for kerberos.

1.3.2 2016-02-09
----------------
- Harden MessageHandler in server.js to avoid issues where we cannot find a callback for an operation.
- Ensure RequestId can never be larger than Max Number integer size.

1.3.1 2016-02-05
----------------
- Removed annoying missing Kerberos error (NODE-654).

1.3.0 2016-02-03
----------------
- Added raw support for the command function on topologies.
- Fixed issue where raw results that fell on batchSize boundaries failed (Issue #72)
- Copy over all the properties to the callback returned from bindToDomain, (Issue #72)
- Added connection hash id to be able to reference connection host/name without leaking it outside of driver.
- NODE-638, Cannot authenticate database user with utf-8 password.
- Refactored pool to be worker queue based, minimizing the impact a slow query have on throughput as long as # slow queries < # connections in the pool.
- Pool now grows and shrinks correctly depending on demand not causing a full pool reconnect.
- Improvements in monitoring of a Replicaset where in certain situations the inquiry process could get exited.
- Switched to using Array.push instead of concat for use cases of a lot of documents.
- Fixed issue where re-authentication could loose the credentials if whole Replicaset disconnected at once.
- Added peer optional dependencies support using require_optional module.

1.2.32 2016-01-12
-----------------
- Bumped bson to V0.4.21 to allow using minor optimizations.

1.2.31 2016-01-04
-----------------
- Allow connection to secondary if primaryPreferred or secondaryPreferred (Issue #70, https://github.com/leichter)

1.2.30 2015-12-23
-----------------
- Pool allocates size + 1 connections when using replicasets, reserving additional pool connection for monitoring exclusively.
- Fixes bug when all replicaset members are down, that would cause it to fail to reconnect using the originally provided seedlist.

1.2.29 2015-12-17
-----------------
- Correctly emit close event when calling destroy on server topology.

1.2.28 2015-12-13
-----------------
- Backed out Prevent Maximum call stack exceeded by calling all callbacks on nextTick, (Issue #64, https://github.com/iamruinous) as it breaks node 0.10.x support.

1.2.27 2015-12-13
-----------------
- Added [options.checkServerIdentity=true] {boolean|function}. Ensure we check server identify during SSL, set to false to disable checking. Only works for Node 0.12.x or higher. You can pass in a boolean or your own checkServerIdentity override function, (Issue #29).
- Prevent Maximum call stack exceeded by calling all callbacks on nextTick, (Issue #64, https://github.com/iamruinous).
- State is not defined in mongos, (Issue #63, https://github.com/flyingfisher).
- Fixed corner case issue on exhaust cursors on pre 3.0.x MongoDB.

1.2.26 2015-11-23
-----------------
- Converted test suite to use mongodb-topology-manager.
- Upgraded bson library to V0.4.20.
- Minor fixes for 3.2 readPreferences.

1.2.25 2015-11-23
-----------------
- Correctly error out when passed a seedlist of non-valid server members.

1.2.24 2015-11-20
-----------------
- Fix Automattic/mongoose#3481; flush callbacks on error, (Issue #57, https://github.com/vkarpov15).
- $explain query for wire protocol 2.6 and 2.4 does not set number of returned documents to -1 but to 0.

1.2.23 2015-11-16
-----------------
- ismaster runs against admin.$cmd instead of system.$cmd.

1.2.22 2015-11-16
-----------------
- Fixes to handle getMore command errors for MongoDB 3.2
- Allows the process to properly close upon a Db.close() call on the replica set by shutting down the haTimer and closing arbiter connections.

1.2.21 2015-11-07
-----------------
- Hardened the checking for replicaset equality checks.
- OpReplay flag correctly set on Wire protocol query.
- Mongos load balancing added, introduced localThresholdMS to control the feature.
- Kerberos now a peerDependency, making it not install it by default in Node 5.0 or higher.

1.2.20 2015-10-28
-----------------
- Fixed bug in arbiter connection capping code.
- NODE-599 correctly handle arrays of server tags in order of priority.
- Fix for 2.6 wire protocol handler related to readPreference handling.
- Added maxAwaitTimeMS support for 3.2 getMore to allow for custom timeouts on tailable cursors.
- Make CoreCursor check for $err before saying that 'next' succeeded (Issue #53, https://github.com/vkarpov15).

1.2.19 2015-10-15
-----------------
- Make batchSize always be > 0 for 3.2 wire protocol to make it work consistently with pre 3.2 servers.
- Locked to bson 0.4.19.

1.2.18 2015-10-15
-----------------
- Minor 3.2 fix for handling readPreferences on sharded commands.
- Minor fixes to correctly pass APM specification test suite.

1.2.17 2015-10-08
-----------------
- Connections to arbiters only maintain a single connection.

1.2.15 2015-10-06
-----------------
- Set slaveOk to true for getMore and killCursors commands.
- Don't swallow callback errors for 2.4 single server (Issue #49, https://github.com/vkarpov15).
- Apply toString('hex') to each buffer in an array when logging (Issue #48, https://github.com/nbrachet).

1.2.14 2015-09-28
-----------------
- NODE-547 only emit error if there are any listeners.
- Fixed APM issue with issuing readConcern.

1.2.13 2015-09-18
-----------------
- Added BSON serializer ignoreUndefined option for insert/update/remove/command/cursor.

1.2.12 2015-09-08
-----------------
- NODE-541 Added initial support for readConcern.

1.2.11 2015-08-31
-----------------
- NODE-535 If connectWithNoPrimary is true then primary-only connection is not allowed.
- NODE-534 Passive secondaries are not allowed for secondaryOnlyConnectionAllowed.
- Fixed filtering bug for logging (Issue 30, https://github.com/christkv/mongodb-core/issues/30).

1.2.10 2015-08-14
-----------------
- Added missing Mongos.prototype.parserType function.

1.2.9 2015-08-05
----------------
- NODE-525 Reset connectionTimeout after it's overwritten by tls.connect.
- NODE-518 connectTimeoutMS is doubled in 2.0.39.

1.2.8 2015-07-24
-----------------
- Minor fix to handle 2.4.x errors better by correctly return driver layer issues.

1.2.7 2015-07-16
-----------------
- Refactoring to allow to tap into find/getmore/killcursor in cursors for APM monitoring in driver.

1.2.6 2015-07-14
-----------------
- NODE-505 Query fails to find records that have a 'result' property with an array value.

1.2.5 2015-07-14
-----------------
- NODE-492 correctly handle hanging replicaset monitoring connections when server is unavailable due to network partitions or firewalls dropping packets, configureable using the connectionTimeoutMS setting.

1.2.4 2015-07-07
-----------------
- NODE-493 staggering the socket connections to avoid overwhelming the mongod process.

1.2.3 2015-06-26
-----------------
- Minor bug fixes.

1.2.2 2015-06-22
-----------------
- Fix issue with SCRAM authentication causing authentication to return true on failed authentication (Issue 26, https://github.com/cglass17).

1.2.1 2015-06-17
-----------------
- Ensure serializeFunctions passed down correctly to wire protocol.

1.2.0 2015-06-17
-----------------
- Switching to using the 0.4.x pure JS serializer, removing dependency on C++ parser.
- Refactoring wire protocol messages to avoid expensive size calculations of documents in favor of writing out an array of buffers to the sockets.
- NODE-486 fixed issue related to limit and skip when calling toArray in 2.0 driver.
- NODE-483 throw error if capabilities of topology is queries before topology has performed connection setup.
- NODE-487 fixed issue where killcursor command was not being sent correctly on limit and skip queries.

1.1.33 2015-05-31
-----------------
- NODE-478 Work around authentication race condition in mongos authentication due to multi step authentication methods like SCRAM.

1.1.32 2015-05-20
-----------------
- After reconnect, it updates the allowable reconnect retries to the option settings (Issue #23, https://github.com/owenallenaz)

1.1.31 2015-05-19
-----------------
- Minor fixes for issues with re-authentication of mongos.

1.1.30 2015-05-18
-----------------
- Correctly emit 'all' event when primary + all secondaries have connected.

1.1.29 2015-05-17
-----------------
- NODE-464 Only use a single socket against arbiters and hidden servers.
- Ensure we filter out hidden servers from any server queries.

1.1.28 2015-05-12
-----------------
- Fixed buffer compare for electionId for < node 12.0.2

1.1.27 2015-05-12
-----------------
- NODE-455 Update SDAM specification support to cover electionId and Mongos load balancing.

1.1.26 2015-05-06
-----------------
- NODE-456 Allow mongodb-core to pipeline commands (ex findAndModify+GLE) along the same connection and handle the returned results.
- Fixes to make mongodb-core work for node 0.8.x when using scram and setImmediate.

1.1.25 2015-04-24
-----------------
- Handle lack of callback in crud operations when returning error on application closed.

1.1.24 2015-04-22
-----------------
- Error out when topology has been destroyed either by connection retries being exhausted or destroy called on topology.

1.1.23 2015-04-15
-----------------
- Standardizing mongoErrors and its API (Issue #14)
- Creating a new connection is slow because of 100ms setTimeout() (Issue #17, https://github.com/vkarpov15)
- remove mkdirp and rimraf dependencies (Issue #12)
- Updated default value of param options.rejectUnauthorized to match documentation (Issue #16)
- ISSUE: NODE-417 Resolution. Improving behavior of thrown errors (Issue #14, https://github.com/owenallenaz)
- Fix cursor hanging when next() called on exhausted cursor (Issue #18, https://github.com/vkarpov15)

1.1.22 2015-04-10
-----------------
- Minor refactorings in cursor code to make extending the cursor simpler.
- NODE-417 Resolution. Improving behavior of thrown errors using Error.captureStackTrace.

1.1.21 2015-03-26
-----------------
- Updated bson module to 0.3.0 that extracted the c++ parser into bson-ext and made it an optional dependency.

1.1.20 2015-03-24
-----------------
- NODE-395 Socket Not Closing, db.close called before full set finished initalizing leading to server connections in progress not being closed properly.

1.1.19 2015-03-21
-----------------
- Made kerberos module ~0.0 to allow for quicker releases due to io.js of kerberos module.

1.1.18 2015-03-17
-----------------
- Added support for minHeartbeatFrequencyMS on server reconnect according to the SDAM specification.

1.1.17 2015-03-16
-----------------
- NODE-377, fixed issue where tags would correctly be checked on secondary and nearest to filter out eligible server candidates.

1.1.16 2015-03-06
-----------------
- rejectUnauthorized parameter is set to true for ssl certificates by default instead of false.

1.1.15 2015-03-04
-----------------
- Removed check for type in replset pickserver function.

1.1.14 2015-02-26
-----------------
- NODE-374 correctly adding passive secondaries to the list of eligable servers for reads

1.1.13 2015-02-24
-----------------
- NODE-365 mongoDB native node.js driver infinite reconnect attempts (fixed issue around handling of retry attempts)

1.1.12 2015-02-16
-----------------
- Fixed cursor transforms for buffered document reads from cursor.

1.1.11 2015-02-02
-----------------
- Remove the required setName for replicaset connections, if not set it will pick the first setName returned.

1.1.10 2015-31-01
-----------------
- Added tranforms.doc option to cursor to allow for pr. document transformations.

1.1.9 2015-21-01
----------------
- Updated BSON dependency to 0.2.18 to fix issues with io.js and node.
- Updated Kerberos dependency to 0.0.8 to fix issues with io.js and node.
- Don't treat findOne() as a command cursor.
- Refactored out state changes into methods to simplify read the next method.

1.1.8 2015-09-12
----------------
- Stripped out Object.defineProperty for performance reasons
- Applied more performance optimizations.
- properties cursorBatchSize, cursorSkip, cursorLimit are not methods setCursorBatchSize/cursorBatchSize, setCursorSkip/cursorSkip, setCursorLimit/cursorLimit

1.1.7 2014-18-12
----------------
- Use ns variable for getMore commands for command cursors to work properly with cursor version of listCollections and listIndexes.

1.1.6 2014-18-12
----------------
- Server manager fixed to support 2.2.X servers for travis test matrix.

1.1.5 2014-17-12
----------------
- Fall back to errmsg when creating MongoError for command errors

1.1.4 2014-17-12
----------------
- Added transform method support for cursor (initially just for initial query results) to support listCollections/listIndexes in 2.8.
- Fixed variable leak in scram.
- Fixed server manager to deal better with killing processes.
- Bumped bson to 0.2.16.

1.1.3 2014-01-12
----------------
- Fixed error handling issue with nonce generation in mongocr.
- Fixed issues with restarting servers when using ssl.
- Using strict for all classes.
- Cleaned up any escaping global variables.

1.1.2 2014-20-11
----------------
- Correctly encoding UTF8 collection names on wire protocol messages.
- Added emitClose parameter to topology destroy methods to allow users to specify that they wish the topology to emit the close event to any listeners.

1.1.1 2014-14-11
----------------
- Refactored code to use prototype instead of privileged methods.
- Fixed issue with auth where a runtime condition could leave replicaset members without proper authentication.
- Several deopt optimizations for v8 to improve performance and reduce GC pauses.

1.0.5 2014-29-10
----------------
- Fixed issue with wrong namespace being created for command cursors.

1.0.4 2014-24-10
----------------
- switched from using shift for the cursor due to bad slowdown on big batchSizes as shift causes entire array to be copied on each call.

1.0.3 2014-21-10
----------------
- fixed error issuing problem on cursor.next when iterating over a huge dataset with a very small batchSize.

1.0.2 2014-07-10
----------------
- fullsetup is now defined as a primary and secondary being available allowing for all read preferences to be satisfied.
- fixed issue with replset_state logging.

1.0.1 2014-07-10
----------------
- Dependency issue solved

1.0.0 2014-07-10
----------------
- Initial release of mongodb-core
