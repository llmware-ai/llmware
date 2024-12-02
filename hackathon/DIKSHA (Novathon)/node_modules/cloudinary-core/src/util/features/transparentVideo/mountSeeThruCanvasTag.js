import loadScript from "../../xhr/loadScript";
import getBlobFromURL from "../../xhr/getBlobFromURL";
import createHiddenVideoTag from "./createHiddenVideoTag";
import instantiateSeeThru from "./instantiateSeeThru";

/**
 *
 * @param {HTMLElement} htmlElContainer
 * @param {string} videoURL
 * @param {TransformationOptions} options
 * @return {Promise<any>}
 */
function mountSeeThruCanvasTag(htmlElContainer, videoURL, options) {
  let {poster, autoplay, playsinline, loop, muted} = options;
  videoURL = videoURL + '.mp4'; // seeThru always uses mp4
  return new Promise((resolve, reject) => {
    loadScript(options.externalLibraries.seeThru, options.max_timeout_ms, window.seeThru).then(() => {
      getBlobFromURL(videoURL, options.max_timeout_ms).then(({payload}) => {
        let videoElement = createHiddenVideoTag({
          blobURL: payload.blobURL,
          videoURL: videoURL, // for debugging/testing
          poster,
          autoplay,
          playsinline,
          loop,
          muted
        });

        htmlElContainer.appendChild(videoElement);

        instantiateSeeThru(videoElement, options.max_timeout_ms, options.class, options.autoplay)
          .then(() => {
            resolve(htmlElContainer);
          })
          .catch((err) => {
            reject(err);
          });

        // catch for getBlobFromURL()
      }).catch(({status, message}) => {
        reject({status, message});
      });
      // catch for loadScript()
    }).catch(({status, message}) => {
      reject({status, message});
    });
  });
}


export default mountSeeThruCanvasTag;
