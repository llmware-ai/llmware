'use strict'

const Benchmark = require('benchmark')
const scmp = require('../')

// `safe-buffer` in case `Buffer.from` in newer versions of node aren't available
const Buffer = require('safe-buffer').Buffer

const HASH1 = Buffer.from('e727d1464ae12436e899a726da5b2f11d8381b26', 'hex')
const HASH2 = Buffer.from('f727d1464ae12436e899a726da5b2f11d8381b26', 'hex')

const suite = new Benchmark.Suite()
suite.add('short-circuit compares', function () {
  // eslint-disable-next-line no-unused-expressions
  HASH1 === HASH2
})
  .add('scmp compares', function () {
    scmp(HASH1, HASH2)
  })
  .on('cycle', function (event) {
    console.log(String(event.target))
  })
  .on('complete', function () {
    console.log('Fastest is ' + this.filter('fastest').map('name'))
  })
  .run()
