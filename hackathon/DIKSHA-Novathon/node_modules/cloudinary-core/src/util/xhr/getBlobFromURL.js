/**
 * Reject on timeout
 * @param maxTimeoutMS
 * @param reject
 * @returns {number} timerID
 */
function rejectOnTimeout(maxTimeoutMS, reject) {
  return setTimeout(() => {
    reject({
      status: 'error',
      message: 'Timeout loading Blob URL'
    });
  }, maxTimeoutMS);
}

/**
 * @description Converts a URL to a BLOB URL
 * @param {string} urlToLoad
 * @param {number} max_timeout_ms - Time to elapse before promise is rejected
 * @return {Promise<{
 *   status: 'success' | 'error'
 *   message?: string,
 *    payload: {
 *      url: string
 *    }
 * }>}
 */
function getBlobFromURL(urlToLoad, maxTimeoutMS) {
  return new Promise((resolve, reject) => {
    const timerID = rejectOnTimeout(maxTimeoutMS, reject);

    // If fetch exists, use it to fetch blob, otherwise use XHR.
    // XHR causes issues on safari 14.1 so we prefer fetch
    const fetchBlob = (typeof fetch !== 'undefined' && fetch) ? loadUrlUsingFetch : loadUrlUsingXhr;

    fetchBlob(urlToLoad).then((blob) => {
      resolve({
        status: 'success',
        payload: {
          blobURL: URL.createObjectURL(blob)
        }
      });
    }).catch(() => {
      reject({
        status: 'error',
        message: 'Error loading Blob URL'
      });
    }).finally(() => {
      // Clear the timeout timer on fail or success.
      clearTimeout(timerID);
    });
  });
}

/**
 * Use fetch function to fetch file
 * @param urlToLoad
 * @returns {Promise<unknown>}
 */
function loadUrlUsingFetch(urlToLoad) {
  return new Promise((resolve, reject) => {
    fetch(urlToLoad).then((response) => {
      response.blob().then((blob) => {
        resolve(blob);
      });
    }).catch(() => {
      reject('error');
    });
  });
}

/**
 * Use XHR to fetch file
 * @param urlToLoad
 * @returns {Promise<unknown>}
 */
function loadUrlUsingXhr(urlToLoad) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.responseType = 'blob';
    xhr.onload = function (response) {
      resolve(xhr.response);
    };

    xhr.onerror = function () {
      reject('error');
    };

    xhr.open('GET', urlToLoad, true);
    xhr.send();
  });
}

export default getBlobFromURL;
