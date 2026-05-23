3.0.0 / 2018-07-11
==================

  * Drop support for Node.js below 0.10
  * deps: debug@3.1.0
    - Add `DEBUG_HIDE_DATE` environment variable
    - Change timer to per-namespace instead of global
    - Change non-TTY date format
    - Remove `DEBUG_FD` environment variable support
    - Support 256 namespace colors

2.3.10 / 2017-09-27
===================

  * deps: debug@2.6.9
  * deps: parseurl@~1.3.2
    - perf: reduce overhead for full URLs
    - perf: unroll the "fast-path" `RegExp`
  * deps: vary@~1.1.2
    - perf: improve header token parsing speed
  * perf: skip unnecessary parsing of entire header

2.3.9 / 2017-05-19
==================

  * deps: debug@2.6.8
    - deps: ms@2.0.0
  * deps: vary@~1.1.1
    - perf: hoist regular expression

2.3.8 / 2017-03-24
==================

  * deps: debug@2.6.3
    - Allow colors in workers
    - Deprecated `DEBUG_FD` environment variable
    - Fix: `DEBUG_MAX_ARRAY_LENGTH`
    - Use same color for same namespace

2.3.7 / 2016-11-19
==================

  * deps: debug@2.3.3
    - Fix error when running under React Native
    - deps: ms@0.7.2
  * perf: remove argument reassignment

2.3.6 / 2016-05-20
==================

  * deps: methods@~1.1.2
    - perf: enable strict mode
  * deps: parseurl@~1.3.1
    - perf: enable strict mode
  * deps: vary@~1.1.0

2.3.5 / 2015-07-31
==================

  * perf: enable strict mode

2.3.4 / 2015-07-14
==================

  * deps: vary@~1.0.1

2.3.3 / 2015-05-12
==================

  * deps: debug@~2.2.0
    - deps: ms@0.7.1

2.3.2 / 2015-03-14
==================

  * deps: debug@~2.1.3
    - Fix high intensity foreground color for bold
    - deps: ms@0.7.0

2.3.1 / 2014-12-30
==================

  * deps: debug@~2.1.1
  * deps: methods@~1.1.1

2.3.0 / 2014-10-16
==================

  * deps: debug@~2.1.0
    - Implement `DEBUG_FD` env variable support

2.2.0 / 2014-09-02
==================

  * deps: debug@~2.0.0

2.1.3 / 2014-08-10
==================

  * deps: parseurl@~1.3.0
  * deps: vary@~1.0.0

2.1.2 / 2014-07-22
==================

  * deps: debug@1.0.4
  * deps: parseurl@~1.2.0
    - Cache URLs based on original value
    - Remove no-longer-needed URL mis-parse work-around
    - Simplify the "fast-path" `RegExp`

2.1.1 / 2014-07-11
==================

  * deps: debug@1.0.3
    - Add support for multiple wildcards in namespaces

2.1.0 / 2014-07-08
==================

  * add simple debug output
  * deps: methods@1.1.0
    - add `CONNECT`
  * deps: parseurl@~1.1.3
    - faster parsing of href-only URLs

2.0.2 / 2014-06-05
==================

  * use vary module for better `Vary` behavior

2.0.1 / 2014-06-02
==================

  * deps: methods@1.0.1

2.0.0 / 2014-06-01
==================

  * Default behavior only checks `X-HTTP-Method-Override` header
  * New interface, less magic
    - Can specify what header to look for override in, if wanted
    - Can specify custom function to get method from request
  * Only `POST` requests are examined by default
  * Remove `req.body` support for more standard query param support
    - Use custom `getter` function if `req.body` support is needed
  * Set `Vary` header when using built-in header checking

1.0.2 / 2014-05-22
==================

  * Handle `req.body` key referencing array or object
  * Handle multiple HTTP headers

1.0.1 / 2014-05-17
==================

  * deps: pin dependency versions

1.0.0 / 2014-03-03
==================

  * Genesis from `connect`
