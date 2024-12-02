'use strict'

module.exports = function scmpCompare (a, b) {
  const len = a.length
  let result = 0
  for (let i = 0; i < len; ++i) {
    result |= a[i] ^ b[i]
  }
  return result === 0
}
