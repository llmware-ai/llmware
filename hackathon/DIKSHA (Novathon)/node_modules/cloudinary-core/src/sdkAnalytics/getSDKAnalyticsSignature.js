import encodeVersion from "./encodeVersion.js";

/**
 * @description Gets the SDK signature by encoding the SDK version and tech version
 * @param {{
 *    [techVersion]:string,
 *    [sdkSemver]: string,
 *    [sdkCode]: string,
 *    [feature]: string
 * }} analyticsOptions
 * @return {string} sdkAnalyticsSignature
 */
export default function getSDKAnalyticsSignature(analyticsOptions={}) {
  try {
    let twoPartVersion = removePatchFromSemver(analyticsOptions.techVersion);
    let encodedSDKVersion = encodeVersion(analyticsOptions.sdkSemver);
    let encodedTechVersion = encodeVersion(twoPartVersion);
    let featureCode = analyticsOptions.feature;
    let SDKCode = analyticsOptions.sdkCode;
    let algoVersion = 'A'; // The algo version is determined here, it should not be an argument

    return `${algoVersion}${SDKCode}${encodedSDKVersion}${encodedTechVersion}${featureCode}`;
  } catch (e) {
    // Either SDK or Node versions were unparsable
    return 'E';
  }
}

/**
 * @description Removes patch version from the semver if it exists
 *              Turns x.y.z OR x.y into x.y
 * @param {'x.y.z' || 'x.y' || string} semVerStr
 */
function removePatchFromSemver(semVerStr) {
  let parts = semVerStr.split('.');

  return `${parts[0]}.${parts[1]}`;
}
