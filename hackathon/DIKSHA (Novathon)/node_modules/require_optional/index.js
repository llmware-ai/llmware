var path = require('path'),
  fs = require('fs'),
  f = require('util').format,
  resolveFrom = require('resolve-from'),
  semver = require('semver');

var exists = fs.existsSync || path.existsSync;

// Find the location of a package.json file near or above the given location
var find_package_json = function(location) {
  var found = false;

  while(!found) {
    if (exists(location + '/package.json')) {
      found = location;
    } else if (location !== '/') {
      location = path.dirname(location);
    } else {
      return false;
    }
  }

  return location;
}

// Find the package.json object of the module closest up the module call tree that contains name in that module's peerOptionalDependencies
var find_package_json_with_name = function(name) {
  // Walk up the module call tree until we find a module containing name in its peerOptionalDependencies
  var currentModule = module;
  var found = false;
  while (currentModule) {
    // Check currentModule has a package.json
    location = currentModule.filename;
    var location = find_package_json(location)
    if (!location) {
      currentModule = currentModule.parent;
      continue;
    }

    // Read the package.json file
    var object = JSON.parse(fs.readFileSync(f('%s/package.json', location)));
    // Is the name defined by interal file references
    var parts = name.split(/\//);

    // Check whether this package.json contains peerOptionalDependencies containing the name we're searching for
    if (!object.peerOptionalDependencies || (object.peerOptionalDependencies && !object.peerOptionalDependencies[parts[0]])) {
      currentModule = currentModule.parent;
      continue;
    }
    found = true;
    break;
  }

  // Check whether name has been found in currentModule's peerOptionalDependencies
  if (!found) {
    throw new Error(f('no optional dependency [%s] defined in peerOptionalDependencies in any package.json', parts[0]));
  }

  return {
    object: object,
    parts: parts
  }
}

var require_optional = function(name, options) {
  options = options || {};
  options.strict = typeof options.strict == 'boolean' ? options.strict : true;

  var res = find_package_json_with_name(name)
  var object = res.object;
  var parts = res.parts;

  // Unpack the expected version
  var expectedVersions = object.peerOptionalDependencies[parts[0]];
  // The resolved package
  var moduleEntry = undefined;
  // Module file
  var moduleEntryFile = name;

  try {
    // Validate if it's possible to read the module
    moduleEntry = require(moduleEntryFile);
  } catch(err) {
    // Attempt to resolve in top level package
    try {
      // Get the module entry file
      moduleEntryFile = resolveFrom(process.cwd(), name);
      if(moduleEntryFile == null) return undefined;
      // Attempt to resolve the module
      moduleEntry = require(moduleEntryFile);
    } catch(err) {
      if(err.code === 'MODULE_NOT_FOUND') return undefined;
    }
  }

  // Resolve the location of the module's package.json file
  var location = find_package_json(require.resolve(moduleEntryFile));
  if(!location) {
    throw new Error('package.json can not be located');
  }

  // Read the module file
  var dependentOnModule = JSON.parse(fs.readFileSync(f('%s/package.json', location)));
  // Get the version
  var version = dependentOnModule.version;
  // Validate if the found module satisfies the version id
  if(semver.satisfies(version, expectedVersions) == false
    && options.strict) {
      var error = new Error(f('optional dependency [%s] found but version [%s] did not satisfy constraint [%s]', parts[0], version, expectedVersions));
      error.code = 'OPTIONAL_MODULE_NOT_FOUND';
      throw error;
  }

  // Satifies the module requirement
  return moduleEntry;
}

require_optional.exists = function(name) {
  try {
    var m = require_optional(name);
    if(m === undefined) return false;
    return true;
  } catch(err) {
    return false;
  }
}

module.exports = require_optional;
