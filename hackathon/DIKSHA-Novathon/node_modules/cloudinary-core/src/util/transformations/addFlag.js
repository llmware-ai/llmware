/**
 * @description - Function will push a flag to incoming options
 * @param {{transformation} | {...transformation}} options - These options are the same options provided to all our SDK methods
 *                           We expect options to either be the transformation itself, or an object containing
 *                           an array of transformations
 *
 * @param {string} flag
 * @returns the mutated options object
 */

function addFlagToOptions(options, flag) {
  // Do we have transformation
  if (options.transformation) {
    options.transformation.push({
      flags: [flag]
    });
  } else {
    // no transformation
    // ensure the flags are extended
    if (!options.flags) {
      options.flags = [];
    }

    if (typeof options.flags === 'string') {
      options.flags = [options.flags];
    }

    options.flags.push(flag);
  }
}

export default addFlagToOptions;
