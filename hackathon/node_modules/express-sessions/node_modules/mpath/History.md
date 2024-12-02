0.5.1 / 2018-08-30
==================
 * fix: prevent writing to constructor and prototype as well as __proto__

0.5.0 / 2018-08-30
==================
 * BREAKING CHANGE: disallow setting/unsetting __proto__ properties
 * feat: re-add support for Node < 4 for this release

0.4.1 / 2018-04-08
==================
 * fix: allow opting out of weird `$` set behavior re: Automattic/mongoose#6273

0.4.0 / 2018-03-27
==================
 * feat: add support for ES6 maps
 * BREAKING CHANGE: drop support for Node < 4

0.3.0 / 2017-06-05
==================
 * feat: add has() and unset() functions

0.2.1 / 2013-03-22
==================

  * test; added for #5
  * fix typo that breaks set #5 [Contra](https://github.com/Contra)

0.2.0 / 2013-03-15
==================

  * added; adapter support for set
  * added; adapter support for get
  * add basic benchmarks
  * add support for using module as a component #2 [Contra](https://github.com/Contra)

0.1.1 / 2012-12-21
==================

  * added; map support

0.1.0 / 2012-12-13
==================

  * added; set('array.property', val, object) support
  * added; get('array.property', object) support

0.0.1 / 2012-11-03
==================

  * initial release
