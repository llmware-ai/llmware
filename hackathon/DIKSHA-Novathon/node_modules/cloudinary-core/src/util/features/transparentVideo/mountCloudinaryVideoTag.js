/**
 * @param {HTMLElement} htmlElContainer
 * @param {object} clInstance cloudinary instance
 * @param {string} publicId
 * @param {object} options - TransformationOptions
 * @returns Promise<HTMLElement>
 */
function mountCloudinaryVideoTag(htmlElContainer, clInstance, publicId, options) {
  return new Promise((resolve, reject) => {
    htmlElContainer.innerHTML = clInstance.videoTag(publicId, options).toHtml();

    // All videos under the html container must have a width of 100%, or they might overflow from the container
    let cloudinaryVideoElement = htmlElContainer.querySelector('.cld-transparent-video');
    cloudinaryVideoElement.style.width = '100%';
    resolve(htmlElContainer);
  });
}

export default mountCloudinaryVideoTag;
