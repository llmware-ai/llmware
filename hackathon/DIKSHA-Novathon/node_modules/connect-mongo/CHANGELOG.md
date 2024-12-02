# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [5.1.0] - 2023-10-14

### Changed

- Extend `mongodb` peer dependency allowed versions to `6.x`
- Upgrade dependency

## [5.0.0] - 2023-03-14

### **BREAKING CHANGES**

- Upgraded peer dependency `mongodb` to 5.0.0
- Change `engines` to require Node 12.9 or newer, matching the upgrade to `mongodb` that occurred in `v4.5.0`

### Fixed

- Declare `express-session` as a peer dependency.

## [4.6.0] - 2021-09-17

### Changed

- Moved `mongodb` to a peer dependency (and also as a dev dependency for `connect-mongo` developers).  `connect-mongo` is no longer pinned to a specific version of `mongodb`.  This allows end users to avoid errors due to Typescript definition changes when moving to new versions of `mongodb`.  Users can use any version of `mongodb` that provides a compatible (non-breaking) interface to `mongodb ^4.1.0`.  Tested on `mongodb` `4.1.0` and `4.1.1`.  Should fix: [#433](https://github.com/jdesboeufs/connect-mongo/issues/433) [#434](https://github.com/jdesboeufs/connect-mongo/issues/434) [#436](https://github.com/jdesboeufs/connect-mongo/issues/436)

### Fixed

- Fixed "Callback was already called" when some code throws immediately after calling the set function

## [4.5.0] - 2021-08-17

### **BREAKING CHANGES**

- Drop Node 10 support

### Changed

- Upgrade `mongodb` to V4 [#422] [#426]

### Fixed

- Move `writeConcern` away from top-level option to fix deprecation warning [#422](https://github.com/jdesboeufs/connect-mongo/issues/422)

## [4.4.1] - 2021-03-23

### Fixed

- `store.all()` method not working with encrypted store [#410](https://github.com/jdesboeufs/connect-mongo/issues/410) [#411](https://github.com/jdesboeufs/connect-mongo/issues/411)
- Update and unpin `mongodb` dependency due to upstream fix has been deployed [#409](https://github.com/jdesboeufs/connect-mongo/issues/409)

## [4.4.0] - 2021-03-11

### **BREAKING CHANGES**

- Use `export =` for better cjs require without `.default`

### Added

- Add typescript example

## [4.3.1] - 2021-03-09

### Fixed

- Fix incorrect assertion checking after adding `client` options

## [4.3.0] - 2021-03-08

### Added

- Add `client` option for non-promise client

## [4.2.2] - 2021-03-02

### Fixed

- Fix crypto parsing error by upgrading `kruptein` to `v3.0.0` and change encodeas to `base64`

## [4.2.0] - 2021-02-24

### Added

- Added mongoose example
- Revert `createAutoRemoveIdx` and add back `autoRemove` and `autoRemoveInterval`

### Fixed

- Use `matchedCount` instead of `modifiedCount` to avoid throwing exceptions when nothing to modify [#390](https://github.com/jdesboeufs/connect-mongo/issues/390)
- Fixed `Warning: Accessing non-existent property 'MongoError' of module exports inside circular dependency` by downgrade to `mongodb@3.6.3`
- Revert update session when touch #351
- Fix cannot read property `lastModified` of null
- Fix TS typing error

## [4.1.0] - 2021-02-22

### **BREAKING CHANGES**

- Support Node.Js 10.x, 12.x and 14.x and drop older support.
- Review method to connect to MongoDB and keep only `mongoUrl` and `clientPromise` options.
- Remove the "Remove expired sessions compatibility mode". Now library user can choose to create auto remove index on startup or not.
- Remove `fallbackMemory` options.
- Rewrite the library and test case using typescript.

> Checkout the complete [migration guide](MIGRATION_V4.md) for more details.

## [3.2.0] - 2019-11-29

### Added

- Add dbName option (#343)

### Fixed

- Add missing `secret` option to TS definition (#342)

## [3.1.2] - 2019-11-01

### Fixed

- Add @types/ dev dependencies for tsc. fixes #340 (#341)

## [3.1.1] - 2019-10-30

### Added

- Add TS type definition

## [3.1.0] - 2019-10-23

### Added

- Added `useUnifiedTopology=true` to mongo options

### Changed

- Refactor merge config logic
- chore: update depns (#326)

## [3.0.0] - 2019-06-17

### **BREAKING CHANGES**

- Drop Node.js 4 & 6 support
- Upgrade `mongoose` to v5 and `mongodb` to v3 and drop old version support
- Replace deprecated mongo operation
- MongoStore need to supply client/clientPromise instead of db/dbPromise due to depns upgrade

## Added

- Add Node.js 10 & 12 support
- Implement store.all function (#291)
- Add option `writeOperationOptions` (#295)
- Add Transparent crypto support (#314)

## Changed

* Change test framework from Mocha to Jest
* Change linter from `xo` to `eslint`

## [2.0.3] - 2018-12-03

## Fixed

- Fixed interval autoremove mode to use current date with every interval (#304, #305) (jlampise)

## [2.0.2] - 2018-11-20

## Fixed

- Fxi #300 DeprecationWarning: collection.remove is deprecated. Use deleteOne, deleteMany, or bulkWrite instead
- Fxi #297 DeprecationWarning: collection.update is deprecated. Use updateOne, updateMany, or bulkWrite instead

## [2.0.1] - 2018-01-04

## Fixed

- Fixed #271 TypeError: cb is not a function (brainthinks)

## [2.0.0] - 2017-10-09

### **BREAKING CHANGES**

* __Drop__ Node.js 0.12 and io.js support
* __Drop__ MongoDB 2.x support
* __Drop__ mongodb driver < 2.0.36 support
* __Drop__ mongoose < 4.1.2 support

## Changed

* __Fix__ `ensureIndex` deprecation warning ([#268](https://github.com/jdesboeufs/connect-mongo/issues/268), [#269](https://github.com/jdesboeufs/connect-mongo/pulls/269), [#270](https://github.com/jdesboeufs/connect-mongo/pulls/270))
* Improve `get()` ([#246](https://github.com/jdesboeufs/connect-mongo/pulls/246))
* Pass session in `touch` event
* Remove `bluebird` from dependencies

<!-- Legacy changelog format -->

1.3.2 / 2016-07-27
=================

* __Fix__ #228 Broken with mongodb@1.x

1.3.1 / 2016-07-23
=================

* Restrict `bluebird` accepted versions to 3.x

1.3.0 / 2016-07-23
=================

* __Add__ `create` and `update` events ([#215](https://github.com/jdesboeufs/connect-mongo/issues/215))
* Extend `mongodb` compatibility to `2.x`

1.2.1 / 2016-06-20
=================

* __Fix__ bluebird warning (Awk34)

1.2.0 / 2016-05-13
=================

* Accept `dbPromise` as connection param
* __Add__ `close()` method to close current connection

1.1.0 / 2015-12-24
=================

* Support mongodb `2.1.x`

1.0.2 / 2015-12-18
=================

* Enforce entry-points

1.0.1 / 2015-12-17
=================

* __Fix__ entry-point

1.0.0 (deprecated) / 2015-12-17
==================

__Breaking changes:__
* __For older Node.js version (`< 4.0`), the module must be loaded using `require('connect-mongo/es5')`__
* __Drop__ `hash` option (advanced)

__Others changes:__
* __Add__ `transformId` option to allow custom transformation on session id (advanced)
* __Rewrite in ES6__ (w/ fallback)
* Update dependencies
* Improve compatibility

0.8.2 / 2015-07-14
==================

* Bug fixes and improvements (whitef0x0, TimothyGu, behcet-li)


0.8.1 / 2015-04-21
==================

* __Fix__ initialization when a connecting `mongodb` `2.0.x` instance is given (1999)


0.8.0 / 2015-03-24
==================

* __Add__ `touchAfter` option to enable lazy update behavior on `touch()` method (rafaelcardoso)
* __Add__ `fallbackMemory` option to switch to `MemoryStore` in some case.


0.7.0 / 2015-01-24
==================

* __Add__ `touch()` method to be fully compliant with `express-session` `>= 1.10` (rafaelcardoso)


0.6.0 / 2015-01-12
==================

* __Add__ `ttl` option
* __Add__ `autoRemove` option
* __Deprecate__ `defaultExpirationTime` option. Use `ttl` instead (in seconds)


0.5.3 / 2014-12-30
==================

* Make callbacks optional


0.5.2 / 2014-12-29
==================

* Extend compatibility to `mongodb` `2.0.x`


0.5.1 / 2014-12-28
==================

* [bugfix] #143 Missing Sessions from DB should still make callback (brekkehj)


0.5.0 (deprecated) / 2014-12-25
==================

* Accept full-featured [MongoDB connection strings](http://docs.mongodb.org/manual/reference/connection-string/) as `url` + [advanced options](http://mongodb.github.io/node-mongodb-native/1.4/driver-articles/mongoclient.html)
* Re-use existing or upcoming mongoose connection
* [DEPRECATED] `mongoose_connection` is renamed `mongooseConnection`
* [DEPRECATED] `auto_reconnect` is renamed `autoReconnect`
* [BREAKING] `autoReconnect` option is now `true` by default
* [BREAKING] Insert `collection` option in `url` in not possible any more
* [BREAKING] Replace for-testing-purpose `callback` by `connected` event
* Add debug (use with `DEBUG=connect-mongo`)
* Improve error management
* Compatibility with `mongodb` `>= 1.2.0` and `< 2.0.0`
* Fix many bugs


0.4.2 / 2014-12-18
==================

  * Bumped mongodb version from 1.3.x to 1.4.x (B0k0)
  * Add `sid` hash capability (ZheFeng)
  * Add `serialize` and `unserialize` options (ksheedlo)


0.3.3 / 2013-07-04
==================

  * Merged a change which reduces data duplication


0.3.0 / 2013-01-20
==================

  * Merged several changes by Ken Pratt, including Write Concern support
  * Updated to `mongodb` version 1.2

0.2.0 / 2012-09-09
==================

  * Integrated pull request for `mongoose_connection` option
  * Move to mongodb 1.0.x

0.1.5 / 2010-07-07
==================

  * Made collection setup more robust to avoid race condition


0.1.4 / 2010-06-28
==================

  * Added session expiry


0.1.3 / 2010-06-27
==================

  * Added url support


0.1.2 / 2010-05-18
==================

  * Added auto_reconnect option


0.1.1 / 2010-03-18
==================

  * Fixed authentication


0.1.0 / 2010-03-08
==================

  * Initial release
