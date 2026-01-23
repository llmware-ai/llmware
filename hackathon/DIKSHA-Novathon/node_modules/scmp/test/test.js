/* eslint-env mocha */
'use strict'

const assert = require('assert')
const scmp = require('../')

// use safe-buffer in case Buffer.from in newer versions of node aren't
// available
const Buffer = require('safe-buffer').Buffer

describe('scmp', function () {
  it('should return true for identical strings', function () {
    assert(scmp(Buffer.from('a', 'utf8'), Buffer.from('a', 'utf8')))
    assert(scmp(Buffer.from('abc', 'utf8'), Buffer.from('abc', 'utf8')))
    assert(scmp(Buffer.from('e727d1464ae12436e899a726da5b2f11d8381b26', 'hex'), Buffer.from('e727d1464ae12436e899a726da5b2f11d8381b26', 'hex')))
  })

  it('should return false for non-identical strings', function () {
    assert(!scmp(Buffer.from('a', 'utf8'), Buffer.from('b', 'utf8')))
    assert(!scmp(Buffer.from('abc', 'utf8'), Buffer.from('b', 'utf8')))
    assert(!scmp(Buffer.from('e727d1464ae12436e899a726da5b2f11d8381b26', 'hex'), Buffer.from('e727e1b80e448a213b392049888111e1779a52db', 'hex')))
  })

  it('should throw errors for non-Buffers', function () {
    assert.throws(scmp.bind(null, 'a', {}))
    assert.throws(scmp.bind(null, {}, 'b'))
    assert.throws(scmp.bind(null, 1, 2))
    assert.throws(scmp.bind(null, undefined, 2))
    assert.throws(scmp.bind(null, null, 2))
  })
})
