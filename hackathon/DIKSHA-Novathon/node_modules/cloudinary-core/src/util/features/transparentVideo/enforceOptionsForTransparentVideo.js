import addFlagToOptions from "../../transformations/addFlag";
import {DEFAULT_EXTERNAL_LIBRARIES, DEFAULT_TIMEOUT_MS} from "../../../constants";

/**
 * @description - Enforce option structure, sets defaults and ensures alpha flag exists
 * @param options {TransformationOptions}
 */
function enforceOptionsForTransparentVideo(options) {
  options.autoplay = true;
  options.muted = true;
  options.controls = false;
  options.max_timeout_ms = options.max_timeout_ms || DEFAULT_TIMEOUT_MS;
  options.class = options.class || '';
  options.class += ' cld-transparent-video';
  options.externalLibraries = options.externalLibraries || {};

  if (!options.externalLibraries.seeThru) {
    options.externalLibraries.seeThru = DEFAULT_EXTERNAL_LIBRARIES.seeThru;
  }

  // ensure there's an alpha transformation present
  // this is a non documented internal flag
  addFlagToOptions(options, 'alpha');
}

export default enforceOptionsForTransparentVideo;
