/**
 * Based on video.js implementation:
 * https://github.com/videojs/video.js/blob/4238f5c1d88890547153e7e1de7bd0d1d8e0b236/src/js/utils/browser.js
 */

/**
* Retrieve from the navigator the user agent property.
* @returns user agent property.
*/
function getUserAgent(){
  return navigator && navigator.userAgent || '';
}

/**
 * Detect if current browser is any Android
 * @returns true if current browser is Android, false otherwise.
 */
export function isAndroid(){
  const userAgent = getUserAgent();
  return (/Android/i).test(userAgent);
}

/**
 * Detect if current browser is any Edge
 * @returns true if current browser is Edge, false otherwise.
 */
export function isEdge(){
  const userAgent = getUserAgent();
  return (/Edg/i).test(userAgent);
}

/**
 * Detect if current browser is chrome.
 * @returns true if current browser is Chrome, false otherwise.
 */
export function isChrome(){
  const userAgent = getUserAgent();
  return !isEdge() && ((/Chrome/i).test(userAgent) || (/CriOS/i).test(userAgent));
}

/**
 * Detect if current browser is Safari.
 * @returns true if current browser is Safari, false otherwise.
 */
export function isSafari(){
  // User agents for other browsers might include "Safari" so we must exclude them.
  // For example - this is the chrome user agent on windows 10:
  // Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36
  const userAgent = getUserAgent();
  return (/Safari/i).test(userAgent) && !isChrome() && !isAndroid() && !isEdge();
}
