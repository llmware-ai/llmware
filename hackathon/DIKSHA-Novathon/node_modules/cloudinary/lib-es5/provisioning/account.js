'use strict';

var utils = require("../utils");
var call_account_api = require('../api_client/call_account_api');

var pickOnlyExistingValues = utils.pickOnlyExistingValues;

/**
 * @desc Lists sub-accounts.
 * @param [enabled] {boolean} - Whether to only return enabled sub-accounts (true) or disabled accounts (false).
 *                              Default: all accounts are returned (both enabled and disabled).
 * @param [ids] {number[]} - A list of up to 100 sub-account IDs. When provided, other parameters are ignored.
 * @param [prefix] {string} - Returns accounts where the name begins with the specified case-insensitive string.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */

function sub_accounts(enabled) {
  var ids = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
  var prefix = arguments[2];
  var options = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : {};
  var callback = arguments[4];

  var params = {
    enabled,
    ids,
    prefix
  };

  var uri = ['sub_accounts'];
  return call_account_api('GET', uri, params, callback, options);
}

/**
 * @desc Retrieves the details of the specified sub-account.
 * @param sub_account_id {string} - The ID of the sub-account.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function sub_account(sub_account_id) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var callback = arguments[2];

  var uri = ['sub_accounts', sub_account_id];
  return call_account_api('GET', uri, {}, callback, options);
}

/**
 * @desc Creates a new sub-account. Any users that have access to all sub-accounts will also automatically have access
 *       to the new sub-account.
 * @param name {string} The display name as shown in the management console.
 * @param cloud_name {string} A case-insensitive cloud name comprised of alphanumeric and underscore characters.
 *                            Generates an error if the specified cloud name is not unique across all Cloudinary
 *                            accounts. Note: Once created, the name can only be changed for accounts with fewer than
 *                            1000 assets.
 * @param custom_attributes {object} Any custom attributes you want to associate with the sub-account, as a map/hash of
 *                                   key/value pairs.
 * @param enabled {boolean} Whether the sub-account is enabled. Default: true
 * @param base_account {string} The ID of another sub-account, from which to copy all of the following settings:
 *                              Size limits, Timed limits, and Flags.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param callback
 */
function create_sub_account(name, cloud_name, custom_attributes, enabled, base_account) {
  var options = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : {};
  var callback = arguments[6];

  var params = {
    cloud_name: cloud_name,
    name,
    custom_attributes: custom_attributes,
    enabled,
    base_sub_account_id: base_account
  };

  options.content_type = "json";
  var uri = ['sub_accounts'];
  return call_account_api('POST', uri, params, callback, options);
}

/**
 * @desc Deletes the specified sub-account. Supported only for accounts with fewer than 1000 assets.
 * @param sub_account_id {string} - The ID of the sub-account to delete.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function delete_sub_account(sub_account_id) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var callback = arguments[2];

  var uri = ['sub_accounts', sub_account_id];
  return call_account_api('DELETE', uri, {}, callback, options);
}

/**
 * @desc Updates the specified details of the sub-account.
 * @param sub_account_id {string} - The ID of the sub-account.
 * @param [name] {string} - The display name as shown in the management console.
 * @param [cloud_name] {string} - A new cloud name for the account.
 *                                Notes:
 *                                  - Can only be changed for accounts with fewer than 1000 assets.
 *                                  - generates an error if the cloud name is not unique across all Cloudinary accounts.
 * @param [custom_attributes] {object} - Any custom attributes you want to associate with the sub-account, as a map/hash
 *                                       of key/value pairs.
 * @param [enabled] {boolean} - Whether the sub-account is enabled.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function update_sub_account(sub_account_id, name, cloud_name, custom_attributes, enabled) {
  var options = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : {};
  var callback = arguments[6];

  var params = {
    cloud_name: cloud_name,
    name,
    custom_attributes: custom_attributes,
    enabled
  };

  options.content_type = "json";
  var uri = ['sub_accounts', sub_account_id];
  return call_account_api('PUT', uri, params, callback, options);
}

/**
 * @desc Returns the user with the specified ID.
 * @param user_id {string} - The ID of the user.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function user(user_id) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var callback = arguments[2];

  var uri = ['users', user_id];
  return call_account_api('GET', uri, {}, callback, options);
}

/**
 * @desc Lists users in the account.
 * @param [pending] {boolean} - Limit results to pending users (true), users that are not pending (false), or all users (undefined, the default)
 * @param [user_ids] {string[]} - A list of up to 100 user IDs. When provided, other parameters are ignored.
 * @param [prefix] {string} - Returns users where the name or email address begins with the specified case-insensitive
 *                            string.
 * @param [sub_account_id[ {string} - Only returns users who have access to the specified account.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function users(pending, user_ids, prefix, sub_account_id) {
  var options = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : {};
  var callback = arguments[5];

  var uri = ['users'];
  var params = {
    ids: user_ids,
    pending,
    prefix,
    sub_account_id
  };
  return call_account_api('GET', uri, pickOnlyExistingValues(params, "ids", "pending", "prefix", "sub_account_id"), callback, options);
}

/**
 * @desc Creates a new user in the account.
 * @param name {string} - The name of the user.
 * @param email {string} - A unique email address, which serves as the login name and notification address.
 * @param role {string} - The role to assign. Possible values: master_admin, admin, billing, technical_admin, reports,
 *                                                             media_library_admin, media_library_user
 * @param [sub_account_ids] {string[]} - The list of sub-account IDs that this user can access.
 *                                       Note: This parameter is ignored if the role is specified as master_admin.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function create_user(name, email, role, sub_account_ids) {
  var options = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : {};
  var callback = arguments[5];

  var uri = ['users'];
  var params = {
    name,
    email,
    role,
    sub_account_ids: sub_account_ids
  };
  options.content_type = 'json';
  return call_account_api('POST', uri, params, callback, options);
}

/**
 * @desc Updates the details of the specified user.
 * @param user_id {string} - The ID of the user to update.
 * @param [name] {string} - The name of the user.
 * @param [email] {string} - A unique email address, which serves as the login name and notification address.
 * @param [role] {string} - The role to assign. Possible values: master_admin, admin, billing, technical_admin, reports,
 *                                              media_library_admin, media_library_user
 * @param [sub_account_ids] {string[]} - The list of sub-account IDs that this user can access.
 *                                       Note: This parameter is ignored if the role is specified as master_admin.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function update_user(user_id, name, email, role, sub_account_ids) {
  var options = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : {};
  var callback = arguments[6];

  var uri = ['users', user_id];
  var params = {
    name,
    email,
    role,
    sub_account_ids: sub_account_ids
  };
  options.content_type = 'json';
  return call_account_api('PUT', uri, params, callback, options);
}

/**
 * @desc Deletes an existing user.
 * @param user_id {string} - The ID of the user to delete.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function delete_user(user_id) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var callback = arguments[2];

  var uri = ['users', user_id];
  return call_account_api('DELETE', uri, {}, callback, options);
}

/**
 * @desc Creates a new user group.
 * @param name {string} - The name for the user group.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function create_user_group(name) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var callback = arguments[2];

  var uri = ['user_groups'];
  options.content_type = 'json';
  var params = {
    name
  };
  return call_account_api('POST', uri, params, callback, options);
}

/**
 * @desc Updates the specified user group.
 * @param group_id {string} The ID of the user group to update.
 * @param name {string} - The name for the user group.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function update_user_group(group_id, name) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
  var callback = arguments[3];

  var uri = ['user_groups', group_id];
  var params = {
    name
  };
  return call_account_api('PUT', uri, params, callback, options);
}

/**
 * @desc Deletes the user group with the specified ID.
 * @param group_id {string} The ID of the user group to delete.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function delete_user_group(group_id) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var callback = arguments[2];

  var uri = ['user_groups', group_id];
  return call_account_api('DELETE', uri, {}, callback, options);
}

/**
 * @desc Adds a user to a group with the specified ID.
 * @param group_id {string} - The ID of the user group.
 * @param user_id {string} - The ID of the user.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function add_user_to_group(group_id, user_id) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
  var callback = arguments[3];

  var uri = ['user_groups', group_id, 'users', user_id];
  return call_account_api('POST', uri, {}, callback, options);
}

/**
 * @desc Removes a user from a group with the specified ID.
 * @param group_id {string} - The ID of the user group.
 * @param user_id {string} - The ID of the user.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function remove_user_from_group(group_id, user_id) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
  var callback = arguments[3];

  var uri = ['user_groups', group_id, 'users', user_id];
  return call_account_api('DELETE', uri, {}, callback, options);
}

/**
 * @desc Retrieves the details of the specified user group.
 * @param group_id {string} - The ID of the user group to retrieve.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function user_group(group_id) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var callback = arguments[2];

  var uri = ['user_groups', group_id];
  return call_account_api('GET', uri, {}, callback, options);
}

/**
 * @desc Lists user groups in the account.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function user_groups() {
  var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
  var callback = arguments[1];

  var uri = ['user_groups'];
  return call_account_api('GET', uri, {}, callback, options);
}

/**
 * @desc Lists users in the specified user group.
 * @param group_id {string} - The ID of the user group.
 * @param [options] {object} - See {@link https://cloudinary.com/documentation/cloudinary_sdks#configuration_parameters|Configuration parameters} in the SDK documentation.
 * @param [callback] {function}
 */
function user_group_users(group_id) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var callback = arguments[2];

  var uri = ['user_groups', group_id, 'users'];
  return call_account_api('GET', uri, {}, callback, options);
}

module.exports = {
  sub_accounts,
  create_sub_account,
  delete_sub_account,
  sub_account,
  update_sub_account,
  user,
  users,
  user_group,
  user_groups,
  user_group_users,
  remove_user_from_group,
  delete_user,
  update_user_group,
  update_user,
  create_user,
  create_user_group,
  add_user_to_group,
  delete_user_group
};