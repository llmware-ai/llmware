/**
 * @description Creates a hidden HTMLVideoElement with the specified videoOptions
 * @param {{autoplay, playsinline, loop, muted, poster, blobURL, videoURL }} videoOptions
 * @param {boolean} videoOptions.autoplay - autoplays the video if true
 * @param {string} videoOptions.blobURL - the blobURL to set as video.src
 * @param {string} videoOptions.videoURL - the original videoURL the user created (with transformations)
 * @return {HTMLVideoElement}
 */
function createHiddenVideoTag(videoOptions) {
  let { autoplay, playsinline, loop, muted, poster, blobURL, videoURL} = videoOptions;

  let el = document.createElement('video');
  el.style.visibility = 'hidden';
  el.position = 'absolute';
  el.x = 0;
  el.y = 0;
  el.src = blobURL;
  el.setAttribute('data-video-url', videoURL); // for debugging/testing

  autoplay && el.setAttribute('autoplay', autoplay);
  playsinline && el.setAttribute('playsinline', playsinline);
  loop && el.setAttribute('loop', loop);
  muted && el.setAttribute('muted', muted);
  muted && (el.muted = muted); // this is also needed for autoplay, on top of setAttribute
  poster && el.setAttribute('poster', poster);

  // Free memory at the end of the file loading.
  el.onload = () => {
    URL.revokeObjectURL(blobURL);
  };

  return el;
}

export default createHiddenVideoTag;
