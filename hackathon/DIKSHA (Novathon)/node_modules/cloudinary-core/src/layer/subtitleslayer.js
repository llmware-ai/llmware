import TextLayer from './textlayer';

class SubtitlesLayer extends TextLayer {
  /**
   * Represent a subtitles layer
   * @constructor SubtitlesLayer
   * @param {Object} options - layer parameters
   */
  constructor(options) {
    super(options);
    this.options.resourceType = "subtitles";
  }

}
export default SubtitlesLayer;
