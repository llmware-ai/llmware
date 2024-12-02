1.41.3 / 2024-01-18
==================



1.41.2 / 2024-01-08
==================



1.41.1 / 2023-12-18
==================

 * fix: sending restrictions when creating or updating metadata fields

1.41.0 / 2023-09-26
==================

* fix: improved calculation of the signature in url
* fix: improved ResourceApiResponse interface
* fix: fetch overlay video creates correct transformation
* feat: added support for on_success script for uploader_spec.js

1.40.0 / 2023-07-31
==================

* feat: visual search api
* fix: adding clear_invalid only when not null

1.39.0 / 2023-07-24
==================

* feat: basic asset relations api

1.38.0 / 2023-07-20
==================

  * feat: new method to_url added to support cached search feature

1.37.3 / 2023-06-26
==================

* fix: native http agent used instead of an external dependency

1.37.2 / 2023-06-19
==================

* chore: bumped npm override for vm2 to latest

1.37.1 / 2023-06-09
==================

  * chore: removing ts installed with dtslint to prevent fails on older node.js
  * fix: only explicit require used
  * fix: upgrade core-js from 3.30.1 to 3.30.2

1.37.0 / 2023-05-16
==================

* feat: exposing structured metadata rules api

1.36.4 / 2023-05-02
==================

fix: isRemoteUrl check improved to reduce false positives

1.36.3 / 2023-05-02
==================

  * fix: smd number field allows both numbers and string when uploading
  * fix: isRemoteUrl not working on big files sometimes

1.36.2 / 2023-04-24
==================

fix: bumped vm2 override to latest

1.36.1 / 2023-04-13
==================

chore: overriding vulnerable transitive dependency

1.36.0 / 2023-04-13
==================

* feat: add support for `media_metadata` param for `upload` and `explicit`
* feat: passing context and metadata when using rename

1.35.0 / 2023-03-03
==================

  * fix: removing nested nulls from options passed to api, closes #581
  * feat: add option to configure tracked analytics

1.34.0 / 2023-02-13
==================

  * fix: resource_type is not optional
  * feat: search for folders
  * feat: support for extra_headers in upload request

1.33.0 / 2022-12-15
==================

  * feat: start and end offset normalized in a transformation string
  * feat: new config option for hiding sensitive data when logging errors
  * feat: multiple ACLs for generate_auth_token
  * fix: improved TS typing

1.32.0 / 2022-09-14
==================

* Add dynamic folder feature (#559)


1.31.0 / 2022-08-28
==================

  * Update core-js package (#558)
  * Add download_backedup_asset typings (#557)


1.30.1 / 2022-07-21
==================

* Bump lodash version to 4.17.21 (#551)
* Add types for verifyNotificationSignature (#555)


1.30.0 / 2022-05-15
==================

  * Add filename_override option to types (#548)


1.29.1 / 2022-04-17
==================

  * Fix support of the lowercase response headers (#545)
  * Fix tags function type definition (#544)


1.29.0 / 2022-03-24
==================

New functionality
-----------------
* Add support for `resources_by_asset_ids` Admin API (#529)
* Add support for `reorder_metadata_fields` Admin API (#526)

Other changes
-----------------
  * bump bson version (#541)
  * bumbed ejs version in photo_album (#540)
  * Add Travis configuration for node 16 (#535)
  * Stabilize OCR tests (#533)
  * update README (#528)
  * Stabilize metadata tests (#530)
 

1.28.1 / 2022-01-06
==================

* Bump proxy-agent version to ^5.0.0 due to vulnerability 

1.28.0 / 2022-01-02
==================

New functionality
-----------------
  * Add support for folder decoupling (#523)
  * Add support for `resource_by_asset_id` Admin API (#522)
  * Add proxy support (#518)

Other changes
-----------------
  * Add tests for expression normalization (#521)

1.27.1 / 2021-10-11
==================

  * Add node version to user agent (#519)


1.27.0 / 2021-09-12
==================

* Fix: `verifyNotificationSignature` timestamps are in seconds (#515)
 * Allow multi and sprite with urls, add download_generated_sprite and download_multi methods (#493)
 * Prevent preview:duration from being normalized (#513)
 * Prevent duplicate search fields in search api (#510)
 * Add support for create_slideshow Upload API (#508)
 * Add support for variables in text style (#507)


1.26.3 / 2021-08-01
==================

  * Add update_metada type to upload api (#500)
  * Return structured metadata in resources APIs (#503)

1.26.2 / 2021-07-04
==================

  * fixed font_family encoding (#498)


1.26.1 / 2021-06-22
==================

  * updated sent upload params (#497)
  * Improve the return type of cloudinary.v2.config() in TypeScript (#494)


1.26.0 / 2021-06-06
==================

Add support for oauth authorization (#489)


1.25.2 / 2021-05-30
==================

Other Changes
  * Fix - Remove file extensions from require statements (#490)
  * Fix - Add support for complex variable names (aheight) (#488)
  * Fix - #486 - upload_prefix configuration retrieval (#487)



1.25.1 / 2021-03-22
==================

  * Fix/unhandled promise rejection call api (#481)
  * Fix return type of api_url function(return String instead of Promise) (#483)
  * Add SHA-256 support for auth signatures (#479)

1.25.0 / 2021-02-22
==================

New functionality
-----------------
* Add sort by metadata field (#474)
* Add filename override param (#471)

Other changes
-------------
* Add safe base64 to all url generation (#477)
* Fix config backup in sign requests test (#476)
* Add missing types to create/delete_folder and private_download_url (#473)
* Add validation to genreate_auth_token to enforce url or acl (#472)



 1.24.0 / 2021-01-31
=============

New functionality and features
------------------------------
  * Add `accessibility_analysis` parameter support (#463)
  * Add support for date parameter in usage API (#467)

Other Changes
-------------
  * Change test for `eval` upload parameter (#468)
  * Update docstring for normalize_expression (#461)
  * Fix secure_distribution has type (#462)
  * Remove unused parameter from archive_params (#454)
  * Fix type of generate_auth_token options (#448)
  * Set the provisioning API config as optional (#451)
  * Encode all URI components when building a URL in base_api_url() (#447)
  * Generate url-safe base64 strings in remote custom functions (#446)

1.23.0 / 2020-08-26
===================
New functionality and features
------------------------------
* Add support for pending, prefix, and sub_account_id to users method (#417)
* Add support for metadata array value (#433)
* Detect data URLs with suffix in mime type (#418)
* Add support for download backedup asset function (#415)
* Add support `max_results` and `next_cursor` in `root_folders` and `sub_folders` (#411)
* Add download_folder method (#404)

Other Changes
-------------
* Added linter rules (#423)
* Fix docstring for pending parameter of the users method (#436)
* Fix invalid detection failing test (#439)
* Test: Ignore URL in AuthToken generation if ACL is provided (#431)
* Add pull_request_template.md (#435)
* Fix and improve docstring for download_folder() (#434)
* Refactor `pickOnlyExistingValues()` function (#432)
* Add tests for new OCR features (#385)

 
1.22.0 / 2020-06-08
==================


New functionality and features
------------------------------ 
  * Feature encode sdk version (#371)
  * Add support for cinemagraph_analysis parameter in upload, explicit, and resource (#391)
  * Support for creating folders using Admin API (#370)
  * Add support for pow operator in expressions (#386)
  * Feature/support download backup version api (#380)
  * Fix normalize_expression when variable is named like a keyword (e.g., ) (#367)
  * Add support for 32 char SHA-256 signatures (#368)

  Other Changes
  -------------
  * Add missing types for sign-request (#398)
  * Add deprecation warning for node 6, add tests for node 14 (#389)
  * Add linter (#388)
  * Fix incorrect text implementation for list resources(#382)
  * Update issue templates (#365)






1.21.0 / 2020-03-29
==================

New functionality and features
------------------------------ 
  * Add types for Structured Metadata functions (#359)
  * Added types for upload response callback (#360)
  * Updated promise types for resources methods (#358)

Other Changes
-------------
 * Add  back to responses sent from Admin API (#361)
 * Align all structured metadata tests with reference implementation (#351)
 * Improve provisioning api tests (#354)
 * Refactor in a wait period for eager uploads (#355)


1.20.0 / 2020-03-11
==================

New functionality and features
------------------------------ 
  * Add support for sources in video tag (#265)
  * Add support multiple resource_types in ZIP generation (#348)
  * Add API support for account/provisioning (#343)
  * Add filename options (#273)
  * Add use_filename option (#274)
  * Support quality_override param for update and explicit api (#242)
  
  Other Changes
  -------------
  * Refactor out a duplicate test (#353)
  * Refactor the order of the assertions in account_spec (#352)
  * Fix type defs for stream upload methods (#336)
  * Remove typings spec and config from npm package
  * Add automation to delete the es5-lib dir when npm run compile is run
  * Move typescript to devDependencies and update version
  * Refactor out utils functions

1.19.0 / 2020-01-20
==================

New functionality and features
------------------------------ 
 * Add structured metadata support
 * Add verifyNotificationSignature()

Other Changes
-------------
  * Fix isRemoteUrl to correctly detect docx files
  * Fix named transformations with spaces
  * Fix/fixed type def for upload stream
  * Add name to errors in uploader.js

1.18.1 / 2019-12-11
==================

* Fix acl and url escaping in auth_token generation

1.18.0 / 2019-12-09
===================

 New functionality
 -----------------
  * Add live parameter to create_upload_preset and update_upload_preset

 Other changes
 -------------
  * Fixed tests on Utils and Cloudinary_spec and removed a duplicate one


1.17.0 / 2019-11-11
===================

  * Update ejs dependency in photo album
  * Add Type Script declaration file

1.16.0 / 2019-10-15
===================

  * Support different radius for each corner (containing images and overlays) (#260)
  * Add feature to allow override on timestamp and signature (#295)
  * remove package-lock (#303)
  * Fixed open linting issues (#279)
  * Feature/publish script (#289)
  * Fix parameters sent when creating a text image (#298)
  * Add custom pre function support (#302)
  * Escape quotes in HTML attributes (#259)

1.15.0 / 2019-09-08
===================

New functionality
-----------------

* Add 'derived_next_resource' to api.resource method
* Add support for 'delete folder' API
* Add support for remote/local function invocation (fn:remote and fn:wasm) (#261)
* Add antialiasing and hinting
* Add `force_version` transformation parameterAdd automatic JavaScript linting and fix existing code conflicts (#262)
* Add automatic JavaScript linting and fix existing code conflicts (#262)

Other changes
-------------
  * Mock upload preset listing test
  * Feature/duration to condition video
  * Update test for change moderation status
  * Simplified error assertions in a few test specs
  * Fix base64 URL validation
  * Rearrange util tests
  * Test support of `async` option in explicit api
  * Remove unnecessary return statements and options from tests
  * Remove unnecessary use of options and API in access_control_spec.js
  * Merge pull request #239 from tornqvist/remove-coffeescript-transform
  * Remove coffee script deps and transform

1.14.0 / 2019-03-26
===================

New functionality
-----------------

  * Support format in transformation API
  * Add support for `start_offset` value `auto`
  * Add support for gs:// urls in uploader
  * Add support for the `quality_analysis` upload parameter. Fixes #171
  * Add `fps` transformation parameter (#230)

Other changes
-------------

  * Update code samples in the README file. Fixes #135
  * Reject deferred on request error. Fixes #136
  * Refactor test code after conversion from CoffeeScript
  * Convert test code from CoffeeScript to JavaScript
  * Merge pull request #208 from cloudinary/fix_update_samples_readme
  * Fix the "upload large" test for node 4
  * Remove bower from the sample code
  * Add timeout to search integration tests
  * Fix detection test
  * Fix broken links in node sample project readme

1.13.2 / 2018-11-14
===================

  * Use a new timestamp for each chunk in `upload_large` API

1.13.1 / 2018-11-13
===================

  * Filter files in the npm package
  * Add polyfill for `Object.entries`
  * Add `update_version` script

1.13.0 / 2018-11-13
===================

  * Support listing of named transformations using the `named` parameter
  * Fix Node version check. Fixes #217

1.12.0 / 2018-11-08
===================

New functionality
-----------------

  * Add Responsive Breakpoints cache
  * Add `picture` and `source` tags
  * Add fetch support to overlay/underlay (#189)
  * Add async param to uploader (#193)
 
Other changes
-------------

  * Convert CoffeeScript source to JavaScript
  * Refactor compiled coffee to proper JS
  * Remove old lib files
  * Move all sources from `src` to `lib`
  * Move `cloudinary.js` inside the src folder
  * Setup library and tests to run with either es6 or es5
  * Apply babel to support older Node versions
  * Refactor tests to use promises
  * Fix Tests
  * Refactor utils
  * Move utils.js to utils folder
  * Add `ensurePresenceOf` and `rimraf` utility functions
  * Add `nyc` for coverage and update sinon
  * Add "Join the Community" (#201)
  * Use upload params in explicit API
  * Fix raw convert test

1.11.0 / 2018-03-19
===================

New functionality
-----------------

  * Add `access_control` parameter to `upload` and `update`
 
Other changes
-------------

  * Mock `delete_all_resources` test
  * Add `compileTests` script to `package.json`
  * Add http/https handling to spec helper
  * Mock moderation tests
  * Fix `categorization` test
  * Remove `similiarity_search` test
  * Add test helper functions
  * Add utility functions to `utils`
  * Replace lodash's `_` with explicitly requiring methods

1.10.0 / 2018-02-13
===================

New functionality
-----------------

  * Support url suffix for shared CDN
  * Add Node 8 to Travis CI tests and remove secure variables
  * Fix breakpoints format parameter
  * Extend support of url_suffix for different resource types
  * Add support for URLs in upload_large
  * Add support for transformations parameter in delete_resources api
  * Add support for delete_derived_by_transformation
  * Add format parameter support to responsive-breakpoints encoder
  * Add expires_at parameter to archive_params
  * Add `faces` parameter to the `explicit` API

Other changes
-------------

  * Fix typos
  * Test transformations api with next_cursor
  * add test cases of ocr for upload and url generation
  * add test case of conditional tags
  * Update dependencies
  * Fix tests
  * Remove tests for `auto_tagging`

1.9.1 / 2017-10-24
==================

  * Decode string to sign before creating the signature (#167)
  * Update Readme to point to HTTPS URLs of cloudinary.com
  * Update lib files
  * Ignore error when `.env` file is missing.
  * Remove CoffeeScript header
  * Add `lib\v2\search.js` to git.

1.9.0 / 2017-04-30
==================

New functionality
-----------------

  * Add Search API
  * Add support for `type` parameter in publish-resources api
  * Add support for `keyframe-interval` (ki) video manipulation parameter
  * Added parameters `allow_missing` and `skip_transformation_name` to generate-archive api
  * Add support for `notification-url` parameter to update API
  * Support = and | characters within context values using escaping + test (#143)

Other changes
-------------

  * Test/upgrade mocha (#142)
  * fix bad escaping of special characters in certain scenarios + tests (#140) Fixes #138
  * Don't normalize negative numbers.
  * Fix typo: rename `min` to `sub`

1.8.0 / 2017-03-09
==================

  * Add User Defined Variables

1.7.1 / 2017-02-23
==================

  * Refactor `generate_auth_token`
  * Update utils documentation.
  * Add URL authorization token. 
  * Rename token function.
  * Support nested keys in CLOUDINARY_URL
  * Allow tests to run concurrently

1.7.0 / 2017-02-08
==================

New functionality
-----------------

  * Add access mode API

Other changes
-------------

  * Rework tests cleanup
  * Use TRAVIS_JOB_ID to make test tags unique

1.6.0 / 2017-01-30
==================

New functionality
-----------------

  * Add Akamai token generator
  * Add Search resource by context

Other changes
-------------

  * Use http library when api protocol is set to http patch 
  * Added timeouts to spec in order to force consistency
  * Fix publish API test cleanup
  * Use random suffix in api tests
  * Use binary encoding for signature
  * Add coffee watch
  * Fixed async issues with before queue
  * Add missing options to explicit api call

1.5.0 / 2016-12-29
==================

New functionality
-----------------

  * `add_context` & `remove_all_context` API
  * Add `data-max-chunk-size` to input created by `image_upload_tag`
  * Add `moderation` and `phash` parameters to explicit API
  
    
Other changes
-------------

  * Modify Travis configuration to test NodeJS v4 and v6 only.
  * Modify `TEST_TAG`
  * Use Sinon spy in `start_at` test
  * Support context as hash argument in context API
  * Delete streaming profiles after tests
  * Fix signing URL tests, Fixes #89
  * Add timeout to delete streaming profile test
  * add tests for add_context & remove_all_context
  * add add_context & remove_all_context methods
  * fix test description
  * add test to phash in an explicit call
  * add test to moderation parameter in an explicit call
  * Add test to accepts {effect: art:incognito}
  * support phash in explicit call
  * Fix missing moderation parameter in an explicit call
  * Fix `nil` to `null`. Call `config()` with parameter name.

1.4.6 / 2016-11-25
==================

  * Merge pull request #118 from cloudinary/explicit-eager-transformations
    * Support multiple eager transformations with explicit api

1.4.5 / 2016-11-25
==================

New functionality
-----------------

  * Add `remove_all_tags` API
  * Add `streaming_profile` transformation parameter.

Other changes
-------------

  * Fix face coordinates test
  * Sort parameters
  * Support `http` mode for tests.
  * Add tests for gravity modes

1.4.4 / 2016-10-27
==================

New functionality
-----------------

  * Add streaming profiles API

Other changes
-------------

  * Change email address in sample project's bower.json
  * Add files to `.npmignore`

1.4.3 / 2016-10-27
==================

1.4.2 / 2016-09-14
==================

New functionality
-----------------

  * Add publish API: `publish_by_prefix`, `publish_by_public_ids`, `publish_by_tag`.
  * Add `to_type` to `rename`.

Other changes
-------------

  * Get version in `utils` from `package.json`
  * Fix tests.

1.4.1 / 2016-06-22
==================

Other changes
-------------

  * Fix #105 #106 - url generation broken width numeric width parameter

1.4.0 / 2016-06-22
==================

New functionality
-----------------

  * New configuration parameter `:client_hints`
  * Enhanced auto `width` values
  * Enhanced `quality` values
  * Add `next_cursor` to `transformation`

Other changes
-------------

  * Remove redundant `max_results` from `upload_preset`
  * Add tests for `max_results` and `next_cursor`
  * Refactor explicit with invalidate test
  * Fix double slash replacement
  * Fix "should allow listing resources by start date" test

1.3.1 / 2016-04-04
==================

New functionality
-----------------

  * Conditional transformations

Other changes
-------------

  * Add error handling to test
  * Fix categorization test
  * Update sample project to use the new cloudinary_js library.
  * Change explicit test to simple eager instead of twitter
  * Add `*.js` and `*.map` to gitignore.
  * Merge pull request #87 from bompus/util-speedup-2
    * optimized speed of generate_transformation_string, removed js/map files.
    * optimized speed of generate_transformation_string
  * Replace `_.include` with `_.includes` - It was removed in lodash 4.0. PR #83
  * Merge pull request #1 from cloudinary/master
  * Merge pull request #76 from joneslee85/renaming-tests
    * Use snakecase naming for spec files
  * Fix dependency of sample projects on cloudinary. Fixes #80.
  * Remove `promised-jugglingdb` - it has been deprecated. Fixes #81.

1.3.0 / 2016-01-08
==================

New functionality
-----------------

  * Add Archive functionality
  * Add responsive breakpoints.
  * Add structured text layers
  * Add upload mapping API
  * Add Restore API
  * Add new USER_AGENT format - CloudinaryNodeJS/ver
  * Add Support for `aspect_ratio` transformation parameter
  * Add invalidate to explicit. Encode public_ids array with `[]` in URL. Replace cleanup code with TEST_TAG.
  * Add "invalidate" flag to rename
  * Add support invalidate=>true in explicit for social resources
  * Support uploading large files using the new Content-Range based upload API.

Other changes
-------------
  * Use `target_tags` instead of `tags` in tests.
  * Utilize spechelper
  * Add license to package, add Sinon.JS, update mocha
  * Increase timeout in tests.
  * Merge pull request #77 from joneslee85/consolidate-test-runner
  * get rid of Cakefile

1.2.6 / 2015-11-19
==================

  * Fix API timeout from 60ms to 60000ms

1.2.5 / 2015-10-14
==================

  * Add timeout to test. Compiled CoffeeScript and whitespace changes
  * Add dev dependency on `coffee-script`
  * Updated upload_large_stream tols return a stream and let the caller control the piping to it, similar to upload_stream.
  * fixes #65 - upload_large using chunk_size is corrupting data - also adds the very useful upload_large_stream function. upload_large tests now verify data integrity.
  * Add bower to the photo_album sample project.
  * Add CHANGELOG.md

1.2.4 / 2015-08-09
==================

  * Fix npmignore entries

1.2.3 / 2015-08-09
==================

  * Adding samples and test to .npmignore

1.2.2 / 2015-07-19
==================

  * Fix upload_large, change api signature to v2, update dependencies
  * Fix typo
  * Add tests to see if options are mutated
  * Update cloudinary.js to copy over options instead of mutating

1.2.1 / 2015-04-16
==================

  * Add and arrange `var` keywords. Edit video() documentation.
  * Better error handling of read stream errors

1.2.0 / 2015-04-07
==================

  * return delete token on direct upload in sample project
  * Reapply node 0.12 compatibility fix. Test minor cleanup
  * Correct use of _.extend
  * Support video tag generation. Support html5 attributes
  * Video support, underscore -> lodash, tests, zoom parameter, eager
  * Spelling, Tag fixes
  * Add video support
  * Fix issue with admin api on node >= 0.12
  * Override lodash's _.first to maintain compatibility with underscore version.
  * Change underscore to lodash
  * added lodash to package.json
  * compile changes after migrating from underscore to lodash
  * remove underscore from pacakge.json
  * update from underscore to lodash

1.1.2 / 2015-02-26
==================

  * Test fixes - resilient to test order change. Cleanup
  * Update coffeescript configuration
  * remove duplicate object key
  * remove duplicate object key
  * Support root path for shared CDN
  * added failed http.Agent test
  * override https agent
  * Allow request agent to be customized
  * fixed issue #42 Bug in samples/basic , api fully supports node.js stream api
  * Add method to generate a webhook signature.

1.1.1 / 2014-12-22
==================

  * invalidate in bulk deltes
  * after code review
  * precompiling coffeescript
  * all tests pass
  * fixed default type and public_id
  * utils cloudinary_url supports new signature & dns sharding
  * upload supports tags

1.1.0 / 2014-12-02
==================

  * Update README.md
  * Update README.md
  * fix #34 Upload stream does not support pipe

1.0.13 / 2014-11-09
===================

  * fixed #32 Reject promise for error codes https://github.com/cloudinary/cloudinary_npm/issues/32
  * bug fix
  * fixed #27 cloudinary.utils.sign_request doesn't read config properly

1.0.12 / 2014-08-28
===================

  * Skipping folder listing test in default
  * - support unsigned upload - redirect to upload form when no image was provided
  * comments
  * set explicit format (jpg)
  * moved image_upload_tag & cloudinary_js_config to view (ejs)
  * case fix
  * using Cloudinary gem to generate images and urls
  * - added cloudinary to response locals - added cloudinary configuration logging
  * ignoring bin directories (support node_monules .bin symlinks)
  * fixed v2 missing methods
  * - added root_folders & sub_folders management api + tests - fixed v2 module (requiring v2 would override v1) - fixed api promises reject a result with error attribute - added dotenv for test environment
  * ignoring bin folder
  * updated demo
  * node photo album
  * fix: changed to public api cloudinary.url
  * Fix mis-spell of deferred
  * added promise support
  * 2space indent
  * package description
  * basic samples + fix to v2 api
  * git ignore

1.0.11 / 2014-07-17
===================

  * Support custom_coordinates in upload, explicit and update, coordinates flag in resource details
  * Support return_delete_token flag in upload
  * Encode utf-8 when signing requests. Issue #20
  * Correctly encode parameters as utf8 in uploader API
  * Support node style callbacks and parameter order in cloudinary.v2.uploader and cloudinary.v2.api - issue #18
  * Support browserify via coffeeify.
