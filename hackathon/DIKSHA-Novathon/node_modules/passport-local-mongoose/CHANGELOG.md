# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [8.0.0](https://github.com/saintedlama/passport-local-mongoose/compare/v7.1.2...v8.0.0) (2023-03-14)


### ⚠ BREAKING CHANGES

* Upgraded to mongoose 7 and removed node 12 support

### Features

* upgrade to mongoose 7 ([#370](https://github.com/saintedlama/passport-local-mongoose/issues/370)) ([a397c00](https://github.com/saintedlama/passport-local-mongoose/commit/a397c00330494563c8141bb6e1334b83d6aa16c7))

### [7.1.2](https://github.com/saintedlama/passport-local-mongoose/compare/v7.1.1...v7.1.2) (2022-05-21)

### [7.1.1](https://github.com/saintedlama/passport-local-mongoose/compare/v7.1.0...v7.1.1) (2022-05-17)


### Bug Fixes

* add usernameCaseInsensitive to the typings ([#355](https://github.com/saintedlama/passport-local-mongoose/issues/355)) ([26f4991](https://github.com/saintedlama/passport-local-mongoose/commit/26f49919220db8f489cfe7fd7f6534535ff0c544))

## [7.1.0](https://github.com/saintedlama/passport-local-mongoose/compare/v7.0.0...v7.1.0) (2022-05-17)


### Features

* add basic type definitions ([#354](https://github.com/saintedlama/passport-local-mongoose/issues/354)) ([92849db](https://github.com/saintedlama/passport-local-mongoose/commit/92849db3329efd1f10af52a16f8b020e657e1b98)), closes [#335](https://github.com/saintedlama/passport-local-mongoose/issues/335)

## [7.0.0](https://github.com/saintedlama/passport-local-mongoose/compare/v6.2.2...v7.0.0) (2022-03-13)


### Features

* reset maxAttempts after unlockInterval if activated ([#349](https://github.com/saintedlama/passport-local-mongoose/issues/349)) ([a752854](https://github.com/saintedlama/passport-local-mongoose/commit/a752854ce66220bff9e4c09f9b3713fafb9a0f2f))

## [6.3.0](https://github.com/saintedlama/passport-local-mongoose/compare/v6.2.2...v6.3.0) (2022-03-12)


### Features

* reset maxAttempts after unlockInterval if activated ([#349](https://github.com/saintedlama/passport-local-mongoose/issues/349)) ([a752854](https://github.com/saintedlama/passport-local-mongoose/commit/a752854ce66220bff9e4c09f9b3713fafb9a0f2f))

### [6.2.2](https://github.com/saintedlama/passport-local-mongoose/compare/v6.2.1...v6.2.2) (2022-03-12)

### [6.2.1](https://github.com/saintedlama/passport-local-mongoose/compare/v6.2.0...v6.2.1) (2022-03-12)

## [6.2.0](https://github.com/saintedlama/passport-local-mongoose/compare/v6.1.0...v6.2.0) (2022-03-12)


### Features

* escape username regex ([#296](https://github.com/saintedlama/passport-local-mongoose/issues/296)) ([6713c4e](https://github.com/saintedlama/passport-local-mongoose/commit/6713c4e02c9a2aabbe3cd4a9c2efc032e686eb3d))
* upgrade dependencies and drop support of legacy mongodb and node versions ([#344](https://github.com/saintedlama/passport-local-mongoose/issues/344)) ([2d88e70](https://github.com/saintedlama/passport-local-mongoose/commit/2d88e70c9afcbddd46076cde46e34111e6ab029d))

## [6.1.0](https://github.com/saintedlama/passport-local-mongoose/compare/v6.0.1...v6.1.0) (2021-01-09)


### Features

* remove babel and semver checks for crypto parameters ([857f93a](https://github.com/saintedlama/passport-local-mongoose/commit/857f93aabd3ee392aefe3dfb005ac4d88b1252d4))

### [6.0.1](https://github.com/saintedlama/passport-local-mongoose/compare/v6.0.0...v6.0.1) (2020-01-04)


### Bug Fixes

* remove superfluous files from package ([b1681a5](https://github.com/saintedlama/passport-local-mongoose/commit/b1681a5d47ef3dc0d50a60d795c925f6a03e0683))

## [6.0.0](https://github.com/saintedlama/passport-local-mongoose/compare/v5.0.1...v6.0.0) (2020-01-04)


### ⚠ BREAKING CHANGES

* mongodb driver update requires server port to be specified

### Bug Fixes

* make debug a dev dependency ([c9b0a78](https://github.com/saintedlama/passport-local-mongoose/commit/c9b0a78761c53edfde6850ed997662e001c430e7))
* update dependencies and specify server port in tests ([807d9cf](https://github.com/saintedlama/passport-local-mongoose/commit/807d9cf669f7a7c433eb0206c97574761c03b8e5))
* use Buffer.from instead of new Buffer ([37375b8](https://github.com/saintedlama/passport-local-mongoose/commit/37375b8b5555d82e6e6241fbd053f2f6b8d670d1))

<a name="5.0.1"></a>
## [5.0.1](https://github.com/saintedlama/passport-local-mongoose/compare/v5.0.0...v5.0.1) (2018-06-20)


### Bug Fixes

* require node engine >= 6.0.0 ([b18f083](https://github.com/saintedlama/passport-local-mongoose/commit/b18f083))
* update nyc dev dependency ([74854b1](https://github.com/saintedlama/passport-local-mongoose/commit/74854b1))



<a name="5.0.0"></a>
# [5.0.0](https://github.com/saintedlama/passport-local-mongoose/compare/v4.5.0...v5.0.0) (2018-03-01)


### Bug Fixes

* add back passwordValidatorPromisified ([4794266](https://github.com/saintedlama/passport-local-mongoose/commit/4794266))
* promise return signature ([0612b5b](https://github.com/saintedlama/passport-local-mongoose/commit/0612b5b))
* update build matrix ([788e0c9](https://github.com/saintedlama/passport-local-mongoose/commit/788e0c9))


### Features

* implement promises for authenticate and static authenticate including tests ([6752e0c](https://github.com/saintedlama/passport-local-mongoose/commit/6752e0c))
* promisify external functions not part of passport.js interface ([e687753](https://github.com/saintedlama/passport-local-mongoose/commit/e687753))


### BREAKING CHANGES

* drop support for node 4 and 5



4.4.0 / 2017-10-25
==================

  * 4.4.0
  * Merge pull request [#233](https://github.com/saintedlama/passport-local-mongoose/issues/233) from 4umfreak/master
    Issue [#79](https://github.com/saintedlama/passport-local-mongoose/issues/79) and Bug [#58](https://github.com/saintedlama/passport-local-mongoose/issues/58), handle save() asynchronously
  * Update changelog

4.3.0 / 2017-10-25
==================

  * 4.3.0
  * Merge pull request [#234](https://github.com/saintedlama/passport-local-mongoose/issues/234) from MeestorHok/master
    Fixed vulnerable dependency
  * Fixed vulnerable dependency
  * fixed up code tabbing style differences
  * added code and tests to handle mongoose errors and concurrency gracefully.

4.2.1 / 2017-08-26
==================

  * 4.2.1
  * Revert setting hash and salt to null in model since this is a breaking change with possibly the implication to loos credentials in a running system
  * Remove superfluous parameters and ;

4.2.0 / 2017-08-24
==================

  * 4.2.0
  * Remove methuselah aged node.js versions 0.10 and 0.12 from travis build matrix
  * Correct test to check that salt and hash are null
  * Merge branch 'master' of github.com:saintedlama/passport-local-mongoose
  * Implement findByUsername option. Fixes [#227](https://github.com/saintedlama/passport-local-mongoose/issues/227)
  * Move function setPasswordAndAuthenticate to end of file
  * Merge pull request [#226](https://github.com/saintedlama/passport-local-mongoose/issues/226) from guoyunhe/patch-1
    Hide hash and salt fields of user in register()
  * Change undefined to null
  * Hide hash and salt of user in authenticate callback
    After authentication, salt and hash are usually not used anymore. It is better to drop them to avoid exposing in `req.user`
  * Hide hash and salt fields of user in register()
    Usually, in `register()` callback, you do not need salt and hash anymore. They should be hidden to avoid exposing to API.

4.1.0 / 2017-08-08
==================

  * 4.1.0
  * Move to nyc for coverage
  * Adapt change password functionality and tests
  * Refactor authenticate function to its own module
  * Merge pull request [#128](https://github.com/saintedlama/passport-local-mongoose/issues/128) from Gentlee/change-password
    Implement changePassword method [#127](https://github.com/saintedlama/passport-local-mongoose/issues/127)
  * Merge pull request [#140](https://github.com/saintedlama/passport-local-mongoose/issues/140) from AshfordN/patch-2
    Update index.js
  * Add syntax highlighting to code examples
  * Modernize example code by using single line variable declarations and const
  * Refactor pbkdf2 adapter to a module of its own
  * Update dependencies
  * Update build matrix to test against node 7, 8 and mongodb 3.4
  * Compare fields and not object to avoid fields added by mongoose to break the build
  * Downgrade to cross-env ^2.0.0.0 to run tests on node 0.10 and 0.12
  * Update dependencies and adapt code to pass buffers to scmp 2
  * Set timeout to 5000ms for all tests
  * Use the ^ semver operator instead of 4.5.x operator
  * Update dependencies and add debug dependency
  * Minor code style fixes
  * Migrate from assert to chai.expect
  * Retry dropping mongodb collections
    Implementation works around a mongoose issue that background indexes are created while trying to drop a collection
  * Migrate to chai.expect
  * Migrate to chai.expect and cleanup code
  * Rename test "error" to "errors" to match tested file
  * Update index.js
    Corrected Grammatical error in the IncorrectUsernameError and IncorrectUsernameError messages
  * Simplify .travis.yml by moving dependencies required for coverage to dev dependencies
  * Adapt .travis.yml to new container based infrastructure
  * Fix output handling in shelljs 0.7
  * Use cross-env for cross platform tests
  * if user model doesn't include salt/hash, get them from db, change tests timeouts
  * optimize and add test for situation when passwords are the same
  * fix changePassword() test
  * implement changePassword method
  * Merge pull request [#123](https://github.com/saintedlama/passport-local-mongoose/issues/123) from Gentlee/optimize-lowercase
    optimize username lowercasing
  * Remove io.js from build matrix
  * Use travis container-based infrastructure
  * Simplify repository field
  * Use digestAlgorithm sha1 and sha1 generated hash for backward compatibility tests
  * optimize username lowercase
  * Add test to verify that authenticate/hashing is 3.0.0 compatible

4.0.0 / 2016-01-15
==================

  * 4.0.0
  * Revert "Revert "Use semver to do a version check instead of argument length checks""
    This reverts commit e17e720867eb283789d9461ec9b452fb513ee52e.

3.1.2 / 2016-01-15
==================

  * 3.1.2
  * Revert "Use semver to do a version check instead of argument length checks"
    This reverts commit 8732239272636272badcc7e88e0483fdd2be0366.

3.1.1 / 2016-01-15
==================

  * 3.1.1
  * Run tests against latest 4.x and latest 5.x versions
  * Use semver to do a version check instead of argument length checks
  * Update changelog

3.1.0 / 2015-10-05
==================

  * 3.1.0
  * Bring back customizable error messages

3.0.0 / 2015-09-21
==================

  * 3.0.0
  * Make the example depend on the latest npm version
  * Move main file to index.js to simplify the package
  * Refactor error generation and yielding
  * Rename variable Err to errors
  * Move mongotest module to helpers
  * Merge pull request [#105](https://github.com/saintedlama/passport-local-mongoose/issues/105) from opencharterhub/fix/error-handling
    Error handling: Always return instance of 'AuthenticationError'
  * Lint: Add some semicolons
  * Lint: Handle error case
  * Lint: Don't shadow variable names
  * Error handling: Always return instance of 'AuthenticationError'

2.0.0 / 2015-09-14
==================

  * 2.0.0
  * Update changelog
  * Add upgrade warning and document new default digest algorithm
  * Add node.js 4.0.0 as build target
  * Reformat code
  * Add editorconfig
  * Update dependencies

1.3.0 / 2015-09-14
==================

  * 1.3.0
  * Remove superfluous queryParameters declaration
  * Add missing semicolon
  * Merge pull request [#98](https://github.com/saintedlama/passport-local-mongoose/issues/98) from theanimal666/master
    Fix Issue [#96](https://github.com/saintedlama/passport-local-mongoose/issues/96)
  * Replace my tabs with spaces to macth project coding style
  * Support test MongoDB server other then localhost
    Implemented using MONGO_SERVER environment variable
  * Merge remote-tracking branch 'upstream/master'
  * Make authenticate work without salt/hash selected by default
  * Add a generated changelog

1.2.0 / 2015-08-28
==================

  * 1.2.0
