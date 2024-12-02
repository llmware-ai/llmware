# scmp
[![travis][travis-image]][travis-url]
[![npm][npm-image]][npm-url]
[![downloads][downloads-image]][downloads-url]

[travis-image]: https://travis-ci.org/freewil/scmp.svg?branch=master
[travis-url]: https://travis-ci.org/freewil/scmp

[npm-image]: https://img.shields.io/npm/v/scmp.svg?style=flat
[npm-url]: https://npmjs.org/package/scmp

[downloads-image]: https://img.shields.io/npm/dm/scmp.svg?style=flat
[downloads-url]: https://npmjs.org/package/scmp

Safe, constant-time comparison of Buffers.

## Install

```
npm install scmp
```

## Why?

To minimize vulnerability against [timing attacks](http://codahale.com/a-lesson-in-timing-attacks/).

## Example

```js
const scmp = require('scmp');
const Buffer = require('safe-buffer').Buffer;

const hash      = Buffer.from('e727d1464ae12436e899a726da5b2f11d8381b26', 'hex');
const givenHash = Buffer.from('e727e1b80e448a213b392049888111e1779a52db', 'hex');

if (scmp(hash, givenHash)) {
  console.log('good hash');
} else {
  console.log('bad hash');
}

```
