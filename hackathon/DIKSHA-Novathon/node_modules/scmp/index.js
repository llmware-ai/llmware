'use strict'

const crypto = require('crypto')
const scmpCompare = require('./lib/scmpCompare')

/**
 * Does a constant-time Buffer comparison by not short-circuiting
 * on first sign of non-equivalency.
 *
 * @param {Buffer} a The first Buffer to be compared against the second
 * @param {Buffer} b The second Buffer to be compared against the first
 * @return {Boolean}
 */
module.exports = function scmp (a, b) {
  // check that both inputs are buffers
  if (!Buffer.isBuffer(a) || !Buffer.isBuffer(b)) {
    throw new Error('Both scmp args must be Buffers')
  }

  // return early here if buffer lengths are not equal since timingSafeEqual
  // will throw if buffer lengths are not equal
  if (a.length !== b.length) {
    return false
  }

  // use crypto.timingSafeEqual if available (since Node.js v6.6.0),
  // otherwise use our own scmp-internal function.
  if (crypto.timingSafeEqual) {
    return crypto.timingSafeEqual(a, b)
  }

  return scmpCompare(a, b)
}
