let fs = require('fs');
let path = require('path');
let sdkCode = 'M'; // Constant per SDK

/**
 * @description Gets the relevant versions of the SDK(package version, node version and sdkCode)
 * @param {'default' | 'x.y.z' | 'x.y' | string} useSDKVersion Default uses package.json version
 * @param {'default' | 'x.y.z' | 'x.y' | string} useNodeVersion Default uses process.versions.node
 * @return {{sdkSemver:string, techVersion:string, sdkCode:string}} A map of relevant versions and codes
 */
function getSDKVersions(useSDKVersion = 'default', useNodeVersion = 'default') {
  let pkgJSONFile = fs.readFileSync(path.join(__dirname, '../../../../package.json'), 'utf-8');

  // allow to pass a custom SDKVersion
  let sdkSemver = useSDKVersion === 'default' ? JSON.parse(pkgJSONFile).version : useSDKVersion;

  // allow to pass a custom techVersion (Node version)
  let techVersion = useNodeVersion === 'default' ? process.versions.node : useNodeVersion;

  return {
    sdkSemver,
    techVersion,
    sdkCode
  };
}

module.exports = getSDKVersions;
