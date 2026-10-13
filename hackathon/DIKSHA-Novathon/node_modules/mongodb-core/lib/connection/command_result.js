"use strict";

/**
 * Creates a new CommandResult instance
 * @class
 * @param {object} result CommandResult object
 * @param {Connection} connection A connection instance associated with this result
 * @return {CommandResult} A cursor instance
 */
var CommandResult = function(result, connection, message) {
  this.result = result;
  this.connection = connection;
  this.message = message;
}

/**
 * Convert CommandResult to JSON
 * @method
 * @return {object}
 */
CommandResult.prototype.toJSON = function() {
  return this.result;
}

/**
 * Convert CommandResult to String representation
 * @method
 * @return {string}
 */
CommandResult.prototype.toString = function() {
  return JSON.stringify(this.toJSON());
}

module.exports = CommandResult;
