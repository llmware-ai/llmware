/**
 * @description - Given a string URL, this function will load the script and resolve the promise.
 *                The function doesn't resolve any value,
 *                this is not a UMD loader where you can get your library name back.
 * @param scriptURL {string}
 * @param {number} max_timeout_ms - Time to elapse before promise is rejected
 * @param isAlreadyLoaded {boolean} if true, the loadScript resolves immediately
 *                                  this is used for multiple invocations - prevents the script from being loaded multiple times
 * @return {Promise<any | {status:string, message:string}>}
 */
function loadScript(scriptURL, max_timeout_ms, isAlreadyLoaded) {
  return new Promise((resolve, reject) => {
    if (isAlreadyLoaded) {
      resolve();
    } else {
      let scriptTag = document.createElement('script');
      scriptTag.src = scriptURL;

      let timerID = setTimeout(() => {
        reject({
          status: 'error',
          message: `Timeout loading script ${scriptURL}`
        });
      }, max_timeout_ms); // 10 seconds for timeout

      scriptTag.onerror = () => {
        clearTimeout(timerID); // clear timeout reject error
        reject({
          status: 'error',
          message: `Error loading ${scriptURL}`
        });
      };

      scriptTag.onload = () => {
        clearTimeout(timerID); // clear timeout reject error
        resolve();
      };
      document.head.appendChild(scriptTag);
    }
  });
}

export default loadScript;
