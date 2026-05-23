# History

## v2.1.0 (2019/12/26)
* code now uses `standard` as linter
* `var` has been replaced with `const` and `let`
* code now executed in strict mode

## v2.0.0 (2016/11/05)
* Buffers are now required to be passed as arguments. In 1.x,
  the arguments were assumed to be strings, and were always run through
  `String()`.
* Starting with Node.js v6.6.0, use `crypto.timingSafeEqual()` (if available).
