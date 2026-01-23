/**
 * @return {Promise<boolean>} - Whether the browser supports transparent videos or not
 */
import {isSafari} from "./util";

function checkSupportForTransparency() {
  return new Promise((resolve, reject) => {
    // Resolve early for safari.
    // Currently (29 December 2021) Safari can play webm/vp9,
    // but it does not support transparent video in the format we're outputting
    if (isSafari()){
      resolve(false);
    }

    const video = document.createElement('video');
    const canPlay = video.canPlayType && video.canPlayType('video/webm; codecs="vp9"');
    resolve(canPlay === 'maybe' || canPlay === 'probably');
  });
}

export default checkSupportForTransparency;
