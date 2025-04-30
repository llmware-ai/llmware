/**
 * @description This function creates a new instanc eof seeThru (seeThru.create()) and returns a promise of the seeThru instance
 * @param {HTMLVideoElement} videoElement
 * @param {number} max_timeout_ms - Time to elapse before promise is rejected
 * @param {string} customClass - A classname to be added to the canvas element created by seeThru
 * @param {boolean} autoPlay
 * @return {Promise<any>} SeeThru instance or rejection error
 */
function instantiateSeeThru(videoElement, max_timeout_ms, customClass, autoPlay) {
  let {seeThru, setTimeout, clearTimeout} = window;

  return new Promise((resolve, reject) => {
    let timerID = setTimeout(() => {
      reject({status: 'error', message: 'Timeout instantiating seeThru instance'});
    }, max_timeout_ms);

    if (seeThru) {
      let seeThruInstance = seeThru.create(videoElement).ready(() => {
        // clear timeout reject error
        clearTimeout(timerID);

        // force container width, else the canvas can overflow out
        let canvasElement = seeThruInstance.getCanvas();
        canvasElement.style.width = '100%';
        canvasElement.className += ' ' + customClass;

        // start the video if autoplay is set
        if (autoPlay) {
          seeThruInstance.play();
        }

        resolve(seeThruInstance);
      });
    } else {
      reject({status: 'error', message: 'Error instantiating seeThru instance'});
    }
  });
}

export default instantiateSeeThru;
