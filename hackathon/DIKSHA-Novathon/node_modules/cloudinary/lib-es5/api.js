"use strict";

var utils = require("./utils");
var call_api = require("./api_client/call_api");

var extend = utils.extend,
    pickOnlyExistingValues = utils.pickOnlyExistingValues;


var TRANSFORMATIONS_URI = "transformations";

function deleteResourcesParams(options) {
  var params = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return extend(params, pickOnlyExistingValues(options, "keep_original", "invalidate", "next_cursor", "transformations"));
}

function getResourceParams(options) {
  return pickOnlyExistingValues(options, "exif", "cinemagraph_analysis", "colors", "derived_next_cursor", "faces", "image_metadata", "media_metadata", "pages", "phash", "coordinates", "max_results", "versions", "accessibility_analysis", 'related', 'related_next_cursor');
}

exports.ping = function ping(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return call_api("get", ["ping"], {}, callback, options);
};

exports.usage = function usage(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var uri = ["usage"];

  if (options.date) {
    uri.push(options.date);
  }

  return call_api("get", uri, {}, callback, options);
};

exports.resource_types = function resource_types(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return call_api("get", ["resources"], {}, callback, options);
};

exports.resources = function resources(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var resource_type = void 0,
      type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  type = options.type;
  uri = ["resources", resource_type];
  if (type != null) {
    uri.push(type);
  }
  if (options.start_at != null && Object.prototype.toString.call(options.start_at) === '[object Date]') {
    options.start_at = options.start_at.toUTCString();
  }
  return call_api("get", uri, pickOnlyExistingValues(options, "next_cursor", "max_results", "prefix", "tags", "context", "direction", "moderations", "start_at", "metadata"), callback, options);
};

exports.resources_by_tag = function resources_by_tag(tag, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var resource_type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  uri = ["resources", resource_type, "tags", tag];
  return call_api("get", uri, pickOnlyExistingValues(options, "next_cursor", "max_results", "tags", "context", "direction", "moderations", "metadata"), callback, options);
};

exports.resources_by_context = function resources_by_context(key, value, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var params = void 0,
      resource_type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  uri = ["resources", resource_type, "context"];
  params = pickOnlyExistingValues(options, "next_cursor", "max_results", "tags", "context", "direction", "moderations", "metadata");
  params.key = key;
  if (value != null) {
    params.value = value;
  }
  return call_api("get", uri, params, callback, options);
};

exports.resources_by_moderation = function resources_by_moderation(kind, status, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var resource_type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  uri = ["resources", resource_type, "moderations", kind, status];
  return call_api("get", uri, pickOnlyExistingValues(options, "next_cursor", "max_results", "tags", "context", "direction", "moderations", "metadata"), callback, options);
};

exports.resource_by_asset_id = function resource_by_asset_id(asset_id, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var uri = ["resources", asset_id];
  return call_api("get", uri, getResourceParams(options), callback, options);
};

exports.resources_by_asset_folder = function resources_by_asset_folder(asset_folder, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = void 0,
      uri = void 0;
  uri = ["resources", 'by_asset_folder'];
  params = pickOnlyExistingValues(options, "next_cursor", "max_results", "tags", "context", "moderations");
  params.asset_folder = asset_folder;
  return call_api("get", uri, params, callback, options);
};

exports.resources_by_asset_ids = function resources_by_asset_ids(asset_ids, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = void 0,
      uri = void 0;
  uri = ["resources", "by_asset_ids"];
  params = pickOnlyExistingValues(options, "tags", "context", "moderations");
  params["asset_ids[]"] = asset_ids;
  return call_api("get", uri, params, callback, options);
};

exports.resources_by_ids = function resources_by_ids(public_ids, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = void 0,
      resource_type = void 0,
      type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  type = options.type || "upload";
  uri = ["resources", resource_type, type];
  params = pickOnlyExistingValues(options, "tags", "context", "moderations");
  params["public_ids[]"] = public_ids;
  return call_api("get", uri, params, callback, options);
};

exports.resource = function resource(public_id, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var resource_type = void 0,
      type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  type = options.type || "upload";
  uri = ["resources", resource_type, type, public_id];
  return call_api("get", uri, getResourceParams(options), callback, options);
};

exports.restore = function restore(public_ids, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  options.content_type = 'json';
  var resource_type = void 0,
      type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  type = options.type || "upload";
  uri = ["resources", resource_type, type, "restore"];
  return call_api("post", uri, {
    public_ids: public_ids,
    versions: options.versions
  }, callback, options);
};

exports.update = function update(public_id, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = void 0,
      resource_type = void 0,
      type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  type = options.type || "upload";
  uri = ["resources", resource_type, type, public_id];
  params = utils.updateable_resource_params(options);
  if (options.moderation_status != null) {
    params.moderation_status = options.moderation_status;
  }
  if (options.clear_invalid != null) {
    params.clear_invalid = options.clear_invalid;
  }
  return call_api("post", uri, params, callback, options);
};

exports.delete_resources = function delete_resources(public_ids, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var resource_type = void 0,
      type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  type = options.type || "upload";
  uri = ["resources", resource_type, type];
  return call_api("delete", uri, deleteResourcesParams(options, {
    "public_ids[]": public_ids
  }), callback, options);
};

exports.delete_resources_by_prefix = function delete_resources_by_prefix(prefix, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var resource_type = void 0,
      type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  type = options.type || "upload";
  uri = ["resources", resource_type, type];
  return call_api("delete", uri, deleteResourcesParams(options, {
    prefix: prefix
  }), callback, options);
};

exports.delete_resources_by_tag = function delete_resources_by_tag(tag, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var resource_type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  uri = ["resources", resource_type, "tags", tag];
  return call_api("delete", uri, deleteResourcesParams(options), callback, options);
};

exports.delete_all_resources = function delete_all_resources(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var resource_type = void 0,
      type = void 0,
      uri = void 0;

  resource_type = options.resource_type || "image";
  type = options.type || "upload";
  uri = ["resources", resource_type, type];
  return call_api("delete", uri, deleteResourcesParams(options, {
    all: true
  }), callback, options);
};

var createRelationParams = function createRelationParams() {
  var publicIds = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];

  return {
    assets_to_relate: Array.isArray(publicIds) ? publicIds : [publicIds]
  };
};

var deleteRelationParams = function deleteRelationParams() {
  var publicIds = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];

  return {
    assets_to_unrelate: Array.isArray(publicIds) ? publicIds : [publicIds]
  };
};

exports.add_related_assets = function (publicId, assetsToRelate, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var params = createRelationParams(assetsToRelate);
  return call_api('post', ['resources', 'related_assets', options.resource_type, options.type, publicId], params, callback, options);
};

exports.add_related_assets_by_asset_id = function (assetId, assetsToRelate, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var params = createRelationParams(assetsToRelate);
  return call_api('post', ['resources', 'related_assets', assetId], params, callback, options);
};

exports.delete_related_assets = function (publicId, assetsToUnrelate, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var params = deleteRelationParams(assetsToUnrelate);
  return call_api('delete', ['resources', 'related_assets', options.resource_type, options.type, publicId], params, callback, options);
};

exports.delete_related_assets_by_asset_id = function (assetId, assetsToUnrelate, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var params = deleteRelationParams(assetsToUnrelate);
  return call_api('delete', ['resources', 'related_assets', assetId], params, callback, options);
};

exports.delete_derived_resources = function delete_derived_resources(derived_resource_ids, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var uri = void 0;
  uri = ["derived_resources"];
  return call_api("delete", uri, {
    "derived_resource_ids[]": derived_resource_ids
  }, callback, options);
};

exports.delete_derived_by_transformation = function delete_derived_by_transformation(public_ids, transformations, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var params = void 0,
      resource_type = void 0,
      type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  type = options.type || "upload";
  uri = "resources/" + resource_type + "/" + type;
  params = extend({
    "public_ids[]": public_ids
  }, pickOnlyExistingValues(options, "invalidate"));
  params.keep_original = true;
  params.transformations = utils.build_eager(transformations);
  return call_api("delete", uri, params, callback, options);
};

exports.tags = function tags(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var resource_type = void 0,
      uri = void 0;
  resource_type = options.resource_type || "image";
  uri = ["tags", resource_type];
  return call_api("get", uri, pickOnlyExistingValues(options, "next_cursor", "max_results", "prefix"), callback, options);
};

exports.transformations = function transformations(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var params = pickOnlyExistingValues(options, "next_cursor", "max_results", "named");
  return call_api("get", TRANSFORMATIONS_URI, params, callback, options);
};

exports.transformation = function transformation(transformationName, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = pickOnlyExistingValues(options, "next_cursor", "max_results");
  params.transformation = utils.build_eager(transformationName);
  return call_api("get", TRANSFORMATIONS_URI, params, callback, options);
};

exports.delete_transformation = function delete_transformation(transformationName, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = {};
  params.transformation = utils.build_eager(transformationName);
  return call_api("delete", TRANSFORMATIONS_URI, params, callback, options);
};

exports.update_transformation = function update_transformation(transformationName, updates, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var params = pickOnlyExistingValues(updates, "allowed_for_strict");
  params.transformation = utils.build_eager(transformationName);
  if (updates.unsafe_update != null) {
    params.unsafe_update = utils.build_eager(updates.unsafe_update);
  }
  return call_api("put", TRANSFORMATIONS_URI, params, callback, options);
};

exports.create_transformation = function create_transformation(name, definition, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var params = { name };
  params.transformation = utils.build_eager(definition);
  return call_api("post", TRANSFORMATIONS_URI, params, callback, options);
};

exports.upload_presets = function upload_presets(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return call_api("get", ["upload_presets"], pickOnlyExistingValues(options, "next_cursor", "max_results"), callback, options);
};

exports.upload_preset = function upload_preset(name, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var uri = void 0;
  uri = ["upload_presets", name];
  return call_api("get", uri, {}, callback, options);
};

exports.delete_upload_preset = function delete_upload_preset(name, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var uri = void 0;
  uri = ["upload_presets", name];
  return call_api("delete", uri, {}, callback, options);
};

exports.update_upload_preset = function update_upload_preset(name, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = void 0,
      uri = void 0;
  uri = ["upload_presets", name];
  params = utils.merge(utils.clear_blank(utils.build_upload_params(options)), pickOnlyExistingValues(options, "unsigned", "disallow_public_id", "live"));
  return call_api("put", uri, params, callback, options);
};

exports.create_upload_preset = function create_upload_preset(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var params = void 0,
      uri = void 0;
  uri = ["upload_presets"];
  params = utils.merge(utils.clear_blank(utils.build_upload_params(options)), pickOnlyExistingValues(options, "name", "unsigned", "disallow_public_id", "live"));
  return call_api("post", uri, params, callback, options);
};

exports.root_folders = function root_folders(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var uri = void 0,
      params = void 0;
  uri = ["folders"];
  params = pickOnlyExistingValues(options, "next_cursor", "max_results");
  return call_api("get", uri, params, callback, options);
};

exports.sub_folders = function sub_folders(path, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var uri = void 0,
      params = void 0;
  uri = ["folders", path];
  params = pickOnlyExistingValues(options, "next_cursor", "max_results");
  return call_api("get", uri, params, callback, options);
};

/**
 * Creates an empty folder
 *
 * @param {string}    path      The folder path to create
 * @param {function}  callback  Callback function
 * @param {object}    options   Configuration options
 * @returns {*}
 */
exports.create_folder = function create_folder(path, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var uri = void 0;
  uri = ["folders", path];
  return call_api("post", uri, {}, callback, options);
};

exports.delete_folder = function delete_folder(path, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var uri = void 0;
  uri = ["folders", path];
  return call_api("delete", uri, {}, callback, options);
};

exports.upload_mappings = function upload_mappings(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var params = void 0;
  params = pickOnlyExistingValues(options, "next_cursor", "max_results");
  return call_api("get", "upload_mappings", params, callback, options);
};

exports.upload_mapping = function upload_mapping(name, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  if (name == null) {
    name = null;
  }
  return call_api("get", 'upload_mappings', {
    folder: name
  }, callback, options);
};

exports.delete_upload_mapping = function delete_upload_mapping(name, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("delete", 'upload_mappings', {
    folder: name
  }, callback, options);
};

exports.update_upload_mapping = function update_upload_mapping(name, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = void 0;
  params = pickOnlyExistingValues(options, "template");
  params.folder = name;
  return call_api("put", 'upload_mappings', params, callback, options);
};

exports.create_upload_mapping = function create_upload_mapping(name, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = void 0;
  params = pickOnlyExistingValues(options, "template");
  params.folder = name;
  return call_api("post", 'upload_mappings', params, callback, options);
};

function publishResource(byKey, value, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var params = void 0,
      resource_type = void 0,
      uri = void 0;
  params = pickOnlyExistingValues(options, "type", "invalidate", "overwrite");
  params[byKey] = value;
  resource_type = options.resource_type || "image";
  uri = ["resources", resource_type, "publish_resources"];
  options = extend({
    resource_type: resource_type
  }, options);
  return call_api("post", uri, params, callback, options);
}

exports.publish_by_prefix = function publish_by_prefix(prefix, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return publishResource("prefix", prefix, callback, options);
};

exports.publish_by_tag = function publish_by_tag(tag, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return publishResource("tag", tag, callback, options);
};

exports.publish_by_ids = function publish_by_ids(public_ids, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return publishResource("public_ids", public_ids, callback, options);
};

exports.list_streaming_profiles = function list_streaming_profiles(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return call_api("get", "streaming_profiles", {}, callback, options);
};

exports.get_streaming_profile = function get_streaming_profile(name, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("get", "streaming_profiles/" + name, {}, callback, options);
};

exports.delete_streaming_profile = function delete_streaming_profile(name, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("delete", "streaming_profiles/" + name, {}, callback, options);
};

exports.update_streaming_profile = function update_streaming_profile(name, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = void 0;
  params = utils.build_streaming_profiles_param(options);
  return call_api("put", "streaming_profiles/" + name, params, callback, options);
};

exports.create_streaming_profile = function create_streaming_profile(name, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = void 0;
  params = utils.build_streaming_profiles_param(options);
  params.name = name;
  return call_api("post", 'streaming_profiles', params, callback, options);
};

function updateResourcesAccessMode(access_mode, by_key, value, callback) {
  var options = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : {};

  var params = void 0,
      resource_type = void 0,
      type = void 0;
  resource_type = options.resource_type || "image";
  type = options.type || "upload";
  params = {
    access_mode: access_mode
  };
  params[by_key] = value;
  return call_api("post", "resources/" + resource_type + "/" + type + "/update_access_mode", params, callback, options);
}

exports.search = function search(params, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  options.content_type = 'json';
  return call_api("post", "resources/search", params, callback, options);
};

exports.visual_search = function visual_search(params, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var allowedParams = pickOnlyExistingValues(params, 'image_url', 'image_asset_id', 'text');
  return call_api('get', ['resources', 'visual_search'], allowedParams, callback, options);
};

exports.search_folders = function search_folders(params, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  options.content_type = 'json';
  return call_api("post", "folders/search", params, callback, options);
};

exports.update_resources_access_mode_by_prefix = function update_resources_access_mode_by_prefix(access_mode, prefix, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  return updateResourcesAccessMode(access_mode, "prefix", prefix, callback, options);
};

exports.update_resources_access_mode_by_tag = function update_resources_access_mode_by_tag(access_mode, tag, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  return updateResourcesAccessMode(access_mode, "tag", tag, callback, options);
};

exports.update_resources_access_mode_by_ids = function update_resources_access_mode_by_ids(access_mode, ids, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  return updateResourcesAccessMode(access_mode, "public_ids[]", ids, callback, options);
};

/**
 * Creates a new metadata field definition
 *
 * @see https://cloudinary.com/documentation/admin_api#create_a_metadata_field
 *
 * @param {Object}   field    The field to add
 * @param {Function} callback Callback function
 * @param {Object}   options  Configuration options
 *
 * @return {Object}
 */
exports.add_metadata_field = function add_metadata_field(field, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  var params = pickOnlyExistingValues(field, "external_id", "type", "label", "mandatory", "default_value", "validation", "datasource", "restrictions");
  options.content_type = "json";
  return call_api("post", ["metadata_fields"], params, callback, options);
};

/**
 * Returns a list of all metadata field definitions
 *
 * @see https://cloudinary.com/documentation/admin_api#get_metadata_fields
 *
 * @param {Function} callback Callback function
 * @param {Object}   options  Configuration options
 *
 * @return {Object}
 */
exports.list_metadata_fields = function list_metadata_fields(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return call_api("get", ["metadata_fields"], {}, callback, options);
};

/**
 * Deletes a metadata field definition.
 *
 * The field should no longer be considered a valid candidate for all other endpoints
 *
 * @see https://cloudinary.com/documentation/admin_api#delete_a_metadata_field_by_external_id
 *
 * @param {String}   field_external_id  The external id of the field to delete
 * @param {Function} callback           Callback function
 * @param {Object}   options            Configuration options
 *
 * @return {Object}
 */
exports.delete_metadata_field = function delete_metadata_field(field_external_id, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("delete", ["metadata_fields", field_external_id], {}, callback, options);
};

/**
 * Get a metadata field by external id
 *
 * @see https://cloudinary.com/documentation/admin_api#get_a_metadata_field_by_external_id
 *
 * @param {String}   external_id  The ID of the metadata field to retrieve
 * @param {Function} callback     Callback function
 * @param {Object}   options      Configuration options
 *
 * @return {Object}
 */
exports.metadata_field_by_field_id = function metadata_field_by_field_id(external_id, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api("get", ["metadata_fields", external_id], {}, callback, options);
};

/**
 * Updates a metadata field by external id
 *
 * Updates a metadata field definition (partially, no need to pass the entire object) passed as JSON data.
 * See {@link https://cloudinary.com/documentation/admin_api#generic_structure_of_a_metadata_field Generic structure of a metadata field} for details.
 *
 * @see https://cloudinary.com/documentation/admin_api#update_a_metadata_field_by_external_id
 *
 * @param {String}   external_id  The ID of the metadata field to update
 * @param {Object}   field        Updated values of metadata field
 * @param {Function} callback     Callback function
 * @param {Object}   options      Configuration options
 *
 * @return {Object}
 */
exports.update_metadata_field = function update_metadata_field(external_id, field, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var params = pickOnlyExistingValues(field, "external_id", "type", "label", "mandatory", "default_value", "validation", "datasource", "restrictions");
  options.content_type = "json";
  return call_api("put", ["metadata_fields", external_id], params, callback, options);
};

/**
 * Updates a metadata field datasource
 *
 * Updates the datasource of a supported field type (currently only enum and set), passed as JSON data. The
 * update is partial: datasource entries with an existing external_id will be updated and entries with new
 * external_id’s (or without external_id’s) will be appended.
 *
 * @see https://cloudinary.com/documentation/admin_api#update_a_metadata_field_datasource
 *
 * @param {String}   field_external_id    The ID of the field to update
 * @param {Object}   entries_external_id  Updated values for datasource
 * @param {Function} callback             Callback function
 * @param {Object}   options              Configuration options
 *
 * @return {Object}
 */
exports.update_metadata_field_datasource = function update_metadata_field_datasource(field_external_id, entries_external_id, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  var params = pickOnlyExistingValues(entries_external_id, "values");
  options.content_type = "json";
  return call_api("put", ["metadata_fields", field_external_id, "datasource"], params, callback, options);
};

/**
 * Deletes entries in a metadata field datasource
 *
 * Deletes (blocks) the datasource entries for a specified metadata field definition. Sets the state of the
 * entries to inactive. This is a soft delete, the entries still exist under the hood and can be activated again
 * with the restore datasource entries method.
 *
 * @see https://cloudinary.com/documentation/admin_api#delete_entries_in_a_metadata_field_datasource
 *
 * @param {String}   field_external_id    The ID of the metadata field
 * @param {Array}    entries_external_id  An array of IDs of datasource entries to delete
 * @param {Function} callback             Callback function
 * @param {Object}   options              Configuration options
 *
 * @return {Object}
 */
exports.delete_datasource_entries = function delete_datasource_entries(field_external_id, entries_external_id, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  options.content_type = "json";
  var params = { external_ids: entries_external_id };
  return call_api("delete", ["metadata_fields", field_external_id, "datasource"], params, callback, options);
};

/**
 * Restores entries in a metadata field datasource
 *
 * Restores (unblocks) any previously deleted datasource entries for a specified metadata field definition.
 * Sets the state of the entries to active.
 *
 * @see https://cloudinary.com/documentation/admin_api#restore_entries_in_a_metadata_field_datasource
 *
 * @param {String}   field_external_id    The ID of the metadata field
 * @param {Array}    entries_external_id  An array of IDs of datasource entries to delete
 * @param {Function} callback             Callback function
 * @param {Object}   options              Configuration options
 *
 * @return {Object}
 */
exports.restore_metadata_field_datasource = function restore_metadata_field_datasource(field_external_id, entries_external_id, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  options.content_type = "json";
  var params = { external_ids: entries_external_id };
  return call_api("post", ["metadata_fields", field_external_id, "datasource_restore"], params, callback, options);
};

/**
 * Sorts metadata field datasource. Currently supports only value
 * @param {String}   field_external_id    The ID of the metadata field
 * @param {String}   sort_by              Criteria for the sort. Currently supports only value
 * @param {String}   direction            Optional (gets either asc or desc)
 * @param {Function} callback             Callback function
 * @param {Object}   options              Configuration options
 *
 * @return {Object}
 */
exports.order_metadata_field_datasource = function order_metadata_field_datasource(field_external_id, sort_by, direction, callback) {
  var options = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : {};

  options.content_type = "json";
  var params = {
    order_by: sort_by,
    direction: direction
  };
  return call_api("post", ["metadata_fields", field_external_id, "datasource", "order"], params, callback, options);
};

/**
 * Reorders metadata fields.
 *
 * @param {String}   order_by  Criteria for the order (one of the fields 'label', 'external_id', 'created_at').
 * @param {String}   direction Optional (gets either asc or desc).
 * @param {Function} callback  Callback function.
 * @param {Object}   options   Configuration options.
 *
 * @return {Object}
 */
exports.reorder_metadata_fields = function reorder_metadata_fields(order_by, direction, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  options.content_type = "json";
  var params = {
    order_by,
    direction
  };
  return call_api("put", ["metadata_fields", "order"], params, callback, options);
};

exports.list_metadata_rules = function list_metadata_rules(callback) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  return call_api('get', ['metadata_rules'], {}, callback, options);
};

exports.add_metadata_rule = function add_metadata_rule(metadata_rule, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  options.content_type = 'json';
  var params = pickOnlyExistingValues(metadata_rule, 'metadata_field_id', 'condition', 'result', 'name');
  return call_api('post', ['metadata_rules'], params, callback, options);
};

exports.update_metadata_rule = function update_metadata_rule(field_external_id, updated_metadata_rule, callback) {
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};

  options.content_type = 'json';
  var params = pickOnlyExistingValues(updated_metadata_rule, 'metadata_field_id', 'condition', 'result', 'name', 'state');
  return call_api('put', ['metadata_rules', field_external_id], params, callback, options);
};

exports.delete_metadata_rule = function delete_metadata_rule(field_external_id, callback) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

  return call_api('delete', ['metadata_rules', field_external_id], {}, callback, options);
};