'use strict';

var fs = require('fs');
var path = require('path');
var sdkCode = 'M'; // Constant per SDK

/**
 * @description Gets the relevant versions of the SDK(package version, node version and sdkCode)
 * @param {'default' | 'x.y.z' | 'x.y' | string} useSDKVersion Default uses package.json version
 * @param {'default' | 'x.y.z' | 'x.y' | string} useNodeVersion Default uses process.versions.node
 * @return {{sdkSemver:string, techVersion:string, sdkCode:string}} A map of relevant versions and codes
 */
function getSDKVersions() {
  var useSDKVersion = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 'default';
  var useNodeVersion = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 'default';

  var pkgJSONFile = fs.readFileSync(path.join(__dirname, '../../../../package.json'), 'utf-8');

  // allow to pass a custom SDKVersion
  var sdkSemver = useSDKVersion === 'default' ? JSON.parse(pkgJSONFile).version : useSDKVersion;

  // allow to pass a custom techVersion (Node version)
  var techVersion = useNodeVersion === 'default' ? process.versions.node : useNodeVersion;

  return {
    sdkSemver,
    techVersion,
    sdkCode
  };
}

module.exports = getSDKVersions;