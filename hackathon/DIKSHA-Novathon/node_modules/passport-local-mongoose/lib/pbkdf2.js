const crypto = require('crypto');

module.exports = function pbkdf2(password, salt, options, callback) {
  crypto.pbkdf2(password, salt, options.iterations, options.keylen, options.digestAlgorithm, callback);
};
