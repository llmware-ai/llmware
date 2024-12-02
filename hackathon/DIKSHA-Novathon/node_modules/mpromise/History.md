0.5.5 / 2014-09-19
==================

 * change `end()` semantics
 * add `catch()` as in ES6

0.5.1 / 2014-01-20
==================

 * fixed; `end` is much more consistent (especially for `then` chains)

0.4.4 / 2014-01-20
==================

 * fixed; `end` is much more consistent (especially for `then` chains)

0.4.3 / 2013-12-17
==================

 * fixed; non-A+ behavior on fulfill and reject [lbeschastny](https://github.com/lbeschastny)
 * tests; simplified harness + compatible with travis + compatible with windows

0.5.0 / 2013-12-14
==================

 * fixed; non-A+ behavior on fulfill and reject [lbeschastny](https://github.com/lbeschastny)
 * tests; simplified harness + compatible with travis + compatible with windows

0.4.2 / 2013-11-26
==================

 * fixed; enter the domain only if not the present domain
 * added; `end` returns the promise

0.4.1 / 2013-10-26
==================

 * Add `all`
 * Longjohn for easier debugging
 * can end a promise chain with an error handler
 * Add ```chain```

0.4.0 / 2013-10-24
==================

 * fixed; now plays nice with domains #3 [refack](https://github.com/refack)
 * updated; compatibility for Promises A+ 2.0.0 [refack](https://github.com/refack)
 * updated; guard against invalid arguments [refack](https://github.com/refack)

0.3.0 / 2013-07-25
==================

  * updated; sliced to 0.0.5
  * fixed; then is passed all fulfillment values
  * use setImmediate if available
  * conform to Promises A+ 1.1

0.2.1 / 2013-02-09
==================

  * fixed; conformancy with A+ 1.2

0.2.0 / 2013-01-09
==================

  * added; .end()
  * fixed; only catch handler executions

0.1.0 / 2013-01-08
==================

  * cleaned up API
  * customizable event names
  * docs

0.0.1 / 2013-01-07
==================

  * original release

