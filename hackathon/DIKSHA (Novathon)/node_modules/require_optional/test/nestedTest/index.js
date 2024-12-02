var require_optional = require('../../')

function findPackage(packageName) {
  var pkg = require_optional(packageName);
  return pkg;
}

module.exports.findPackage = findPackage
