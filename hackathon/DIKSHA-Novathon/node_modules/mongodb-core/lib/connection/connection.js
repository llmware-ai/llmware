"use strict";

var inherits = require('util').inherits
  , EventEmitter = require('events').EventEmitter
  , net = require('net')
  , tls = require('tls')
  , crypto = require('crypto')
  , f = require('util').format
  , debugOptions = require('./utils').debugOptions
  , Response = require('./commands').Response
  , MongoError = require('../error')
  , Logger = require('./logger');

var _id = 0;
var debugFields = ['host', 'port', 'size', 'keepAlive', 'keepAliveInitialDelay', 'noDelay'
  , 'connectionTimeout', 'socketTimeout', 'singleBufferSerializtion', 'ssl', 'ca', 'crl', 'cert'
  , 'rejectUnauthorized', 'promoteLongs', 'promoteValues', 'promoteBuffers', 'checkServerIdentity'];
var connectionAccounting = false;
var connections = {};

/**
 * Creates a new Connection instance
 * @class
 * @param {string} options.host The server host
 * @param {number} options.port The server port
 * @param {number} [options.family=null] IP version for DNS lookup, passed down to Node's [`dns.lookup()` function](https://nodejs.org/api/dns.html#dns_dns_lookup_hostname_options_callback). If set to `6`, will only look for ipv6 addresses.
 * @param {boolean} [options.keepAlive=true] TCP Connection keep alive enabled
 * @param {number} [options.keepAliveInitialDelay=300000] Initial delay before TCP keep alive enabled
 * @param {boolean} [options.noDelay=true] TCP Connection no delay
 * @param {number} [options.connectionTimeout=30000] TCP Connection timeout setting
 * @param {number} [options.socketTimeout=360000] TCP Socket timeout setting
 * @param {boolean} [options.singleBufferSerializtion=true] Serialize into single buffer, trade of peak memory for serialization speed
 * @param {boolean} [options.ssl=false] Use SSL for connection
 * @param {boolean|function} [options.checkServerIdentity=true] Ensure we check server identify during SSL, set to false to disable checking. Only works for Node 0.12.x or higher. You can pass in a boolean or your own checkServerIdentity override function.
 * @param {Buffer} [options.ca] SSL Certificate store binary buffer
 * @param {Buffer} [options.crl] SSL Certificate revocation store binary buffer
 * @param {Buffer} [options.cert] SSL Certificate binary buffer
 * @param {Buffer} [options.key] SSL Key file binary buffer
 * @param {string} [options.passphrase] SSL Certificate pass phrase
 * @param {boolean} [options.rejectUnauthorized=true] Reject unauthorized server certificates
 * @param {boolean} [options.promoteLongs=true] Convert Long values from the db into Numbers if they fit into 53 bits
 * @param {boolean} [options.promoteValues=true] Promotes BSON values to native types where possible, set to false to only receive wrapper types.
 * @param {boolean} [options.promoteBuffers=false] Promotes Binary BSON values to native Node Buffers.
 * @fires Connection#connect
 * @fires Connection#close
 * @fires Connection#error
 * @fires Connection#timeout
 * @fires Connection#parseError
 * @return {Connection} A cursor instance
 */
var Connection = function(messageHandler, options) {
  // Add event listener
  EventEmitter.call(this);
  // Set empty if no options passed
  this.options = options || {};
  // Identification information
  this.id = _id++;
  // Logger instance
  this.logger = Logger('Connection', options);
  // No bson parser passed in
  if(!options.bson) throw new Error("must pass in valid bson parser");
  // Get bson parser
  this.bson = options.bson;
  // Grouping tag used for debugging purposes
  this.tag = options.tag;
  // Message handler
  this.messageHandler = messageHandler;

  // Max BSON message size
  this.maxBsonMessageSize = options.maxBsonMessageSize || (1024 * 1024 * 16 * 4);
  // Debug information
  if(this.logger.isDebug()) this.logger.debug(f('creating connection %s with options [%s]', this.id, JSON.stringify(debugOptions(debugFields, options))));

  // Default options
  this.port = options.port || 27017;
  this.host = options.host || 'localhost';
  this.family = typeof options.family == 'number' ? options.family : void 0;
  this.keepAlive = typeof options.keepAlive == 'boolean' ? options.keepAlive : true;
  this.keepAliveInitialDelay = typeof options.keepAliveInitialDelay == 'number' 
    ? options.keepAliveInitialDelay : 300000;
  this.noDelay = typeof options.noDelay == 'boolean' ? options.noDelay : true;
  this.connectionTimeout = typeof options.connectionTimeout == 'number'
    ? options.connectionTimeout : 30000;
  this.socketTimeout = typeof options.socketTimeout == 'number'
    ? options.socketTimeout : 360000;

  // Is the keepAliveInitialDelay > socketTimeout set it to half of socketTimeout
  if(this.keepAliveInitialDelay > this.socketTimeout) {
    this.keepAliveInitialDelay = Math.round(this.socketTimeout/2);
  }

  // If connection was destroyed
  this.destroyed = false;

  // Check if we have a domain socket
  this.domainSocket = this.host.indexOf('\/') != -1;

  // Serialize commands using function
  this.singleBufferSerializtion = typeof options.singleBufferSerializtion == 'boolean' ? options.singleBufferSerializtion : true;
  this.serializationFunction = this.singleBufferSerializtion ? 'toBinUnified' : 'toBin';

  // SSL options
  this.ca = options.ca || null;
  this.crl = options.crl || null;
  this.cert = options.cert || null;
  this.key = options.key || null;
  this.passphrase = options.passphrase || null;
  this.ciphers = options.ciphers || null;
  this.ecdhCurve = options.ecdhCurve || null;
  this.ssl = typeof options.ssl == 'boolean' ? options.ssl : false;
  this.rejectUnauthorized = typeof options.rejectUnauthorized == 'boolean' ? options.rejectUnauthorized : true;
  this.checkServerIdentity = typeof options.checkServerIdentity == 'boolean'
    || typeof options.checkServerIdentity == 'function' ? options.checkServerIdentity : true;

  // If ssl not enabled
  if(!this.ssl) this.rejectUnauthorized = false;

  // Response options
  this.responseOptions = {
    promoteLongs: typeof options.promoteLongs == 'boolean' ?  options.promoteLongs : true,
    promoteValues: typeof options.promoteValues == 'boolean' ? options.promoteValues : true,
    promoteBuffers: typeof options.promoteBuffers == 'boolean' ? options.promoteBuffers: false
  }

  // Flushing
  this.flushing = false;
  this.queue = [];

  // Internal state
  this.connection = null;
  this.writeStream = null;

  // Create hash method
  var hash = crypto.createHash('sha1');
  hash.update(f('%s:%s', this.host, this.port));

  // Create a hash name
  this.hashedName = hash.digest('hex');

  // All operations in flight on the connection
  this.workItems = [];
}

inherits(Connection, EventEmitter);

Connection.prototype.setSocketTimeout = function(value) {
  if(this.connection) {
    this.connection.setTimeout(value);
  }
}

Connection.prototype.resetSocketTimeout = function() {
  if(this.connection) {
    this.connection.setTimeout(this.socketTimeout);
  }
}

Connection.enableConnectionAccounting = function() {
  connectionAccounting = true;
  connections = {};
}

Connection.disableConnectionAccounting = function() {
  connectionAccounting = false;
}

Connection.connections = function() {
  return connections;
}

function deleteConnection(id) {
  // console.log("=== deleted connection " + id + " :: " + (connections[id] ? connections[id].port : ''))
  delete connections[id];
}

function addConnection(id, connection) {
  // console.log("=== added connection " + id + " :: " + connection.port)
  connections[id] = connection;
}

//
// Connection handlers
var errorHandler = function(self) {
  return function(err) {
    if(connectionAccounting) deleteConnection(self.id);
    // Debug information
    if(self.logger.isDebug()) self.logger.debug(f('connection %s for [%s:%s] errored out with [%s]', self.id, self.host, self.port, JSON.stringify(err)));
    // Emit the error
    if(self.listeners('error').length > 0) self.emit("error", MongoError.create(err), self);
  }
}

var timeoutHandler = function(self) {
  return function() {
    if(connectionAccounting) deleteConnection(self.id);
    // Debug information
    if(self.logger.isDebug()) self.logger.debug(f('connection %s for [%s:%s] timed out', self.id, self.host, self.port));
    // Emit timeout error
    self.emit("timeout"
      , MongoError.create(f("connection %s to %s:%s timed out", self.id, self.host, self.port))
      , self);
  }
}

var closeHandler = function(self) {
  return function(hadError) {
    if(connectionAccounting) deleteConnection(self.id);
    // Debug information
    if(self.logger.isDebug()) self.logger.debug(f('connection %s with for [%s:%s] closed', self.id, self.host, self.port));

    // Emit close event
    if(!hadError) {
      self.emit("close"
        , MongoError.create(f("connection %s to %s:%s closed", self.id, self.host, self.port))
        , self);
    }
  }
}

var dataHandler = function(self) {
  return function(data) {
    // Parse until we are done with the data
    while(data.length > 0) {
      // If we still have bytes to read on the current message
      if(self.bytesRead > 0 && self.sizeOfMessage > 0) {
        // Calculate the amount of remaining bytes
        var remainingBytesToRead = self.sizeOfMessage - self.bytesRead;
        // Check if the current chunk contains the rest of the message
        if(remainingBytesToRead > data.length) {
          // Copy the new data into the exiting buffer (should have been allocated when we know the message size)
          data.copy(self.buffer, self.bytesRead);
          // Adjust the number of bytes read so it point to the correct index in the buffer
          self.bytesRead = self.bytesRead + data.length;

          // Reset state of buffer
          data = new Buffer(0);
        } else {
          // Copy the missing part of the data into our current buffer
          data.copy(self.buffer, self.bytesRead, 0, remainingBytesToRead);
          // Slice the overflow into a new buffer that we will then re-parse
          data = data.slice(remainingBytesToRead);

          // Emit current complete message
          try {
            var emitBuffer = self.buffer;
            // Reset state of buffer
            self.buffer = null;
            self.sizeOfMessage = 0;
            self.bytesRead = 0;
            self.stubBuffer = null;
            // Emit the buffer
            self.messageHandler(new Response(self.bson, emitBuffer, self.responseOptions), self);
          } catch(err) {
            var errorObject = {err:"socketHandler", trace:err, bin:self.buffer, parseState:{
              sizeOfMessage:self.sizeOfMessage,
              bytesRead:self.bytesRead,
              stubBuffer:self.stubBuffer}};
            // We got a parse Error fire it off then keep going
            self.emit("parseError", errorObject, self);
          }
        }
      } else {
        // Stub buffer is kept in case we don't get enough bytes to determine the
        // size of the message (< 4 bytes)
        if(self.stubBuffer != null && self.stubBuffer.length > 0) {
          // If we have enough bytes to determine the message size let's do it
          if(self.stubBuffer.length + data.length > 4) {
            // Prepad the data
            var newData = new Buffer(self.stubBuffer.length + data.length);
            self.stubBuffer.copy(newData, 0);
            data.copy(newData, self.stubBuffer.length);
            // Reassign for parsing
            data = newData;

            // Reset state of buffer
            self.buffer = null;
            self.sizeOfMessage = 0;
            self.bytesRead = 0;
            self.stubBuffer = null;

          } else {

            // Add the the bytes to the stub buffer
            var newStubBuffer = new Buffer(self.stubBuffer.length + data.length);
            // Copy existing stub buffer
            self.stubBuffer.copy(newStubBuffer, 0);
            // Copy missing part of the data
            data.copy(newStubBuffer, self.stubBuffer.length);
            // Exit parsing loop
            data = new Buffer(0);
          }
        } else {
          if(data.length > 4) {
            // Retrieve the message size
            // var sizeOfMessage = data.readUInt32LE(0);
            var sizeOfMessage = data[0] | data[1] << 8 | data[2] << 16 | data[3] << 24;
            // If we have a negative sizeOfMessage emit error and return
            if(sizeOfMessage < 0 || sizeOfMessage > self.maxBsonMessageSize) {
              errorObject = {err:"socketHandler", trace:'', bin:self.buffer, parseState:{
                sizeOfMessage: sizeOfMessage,
                bytesRead: self.bytesRead,
                stubBuffer: self.stubBuffer}};
              // We got a parse Error fire it off then keep going
              self.emit("parseError", errorObject, self);
              return;
            }

            // Ensure that the size of message is larger than 0 and less than the max allowed
            if(sizeOfMessage > 4 && sizeOfMessage < self.maxBsonMessageSize && sizeOfMessage > data.length) {
              self.buffer = new Buffer(sizeOfMessage);
              // Copy all the data into the buffer
              data.copy(self.buffer, 0);
              // Update bytes read
              self.bytesRead = data.length;
              // Update sizeOfMessage
              self.sizeOfMessage = sizeOfMessage;
              // Ensure stub buffer is null
              self.stubBuffer = null;
              // Exit parsing loop
              data = new Buffer(0);

            } else if(sizeOfMessage > 4 && sizeOfMessage < self.maxBsonMessageSize && sizeOfMessage == data.length) {
              try {
                emitBuffer = data;
                // Reset state of buffer
                self.buffer = null;
                self.sizeOfMessage = 0;
                self.bytesRead = 0;
                self.stubBuffer = null;
                // Exit parsing loop
                data = new Buffer(0);
                // Emit the message
                self.messageHandler(new Response(self.bson, emitBuffer, self.responseOptions), self);
              } catch (err) {
                self.emit("parseError", err, self);
              }
            } else if(sizeOfMessage <= 4 || sizeOfMessage > self.maxBsonMessageSize) {
              errorObject = {err:"socketHandler", trace:null, bin:data, parseState:{
                sizeOfMessage:sizeOfMessage,
                bytesRead:0,
                buffer:null,
                stubBuffer:null}};
              // We got a parse Error fire it off then keep going
              self.emit("parseError", errorObject, self);

              // Clear out the state of the parser
              self.buffer = null;
              self.sizeOfMessage = 0;
              self.bytesRead = 0;
              self.stubBuffer = null;
              // Exit parsing loop
              data = new Buffer(0);
            } else {
              emitBuffer = data.slice(0, sizeOfMessage);
              // Reset state of buffer
              self.buffer = null;
              self.sizeOfMessage = 0;
              self.bytesRead = 0;
              self.stubBuffer = null;
              // Copy rest of message
              data = data.slice(sizeOfMessage);
              // Emit the message
              self.messageHandler(new Response(self.bson, emitBuffer, self.responseOptions), self);
            }
          } else {
            // Create a buffer that contains the space for the non-complete message
            self.stubBuffer = new Buffer(data.length)
            // Copy the data to the stub buffer
            data.copy(self.stubBuffer, 0);
            // Exit parsing loop
            data = new Buffer(0);
          }
        }
      }
    }
  }
}

// List of socket level valid ssl options
var legalSslSocketOptions = ['pfx', 'key', 'passphrase', 'cert', 'ca', 'ciphers'
  , 'NPNProtocols', 'ALPNProtocols', 'servername', 'ecdhCurve'
  , 'secureProtocol', 'secureContext', 'session'
  , 'minDHSize'];

function merge(options1, options2) {
  // Merge in any allowed ssl options
  for(var name in options2) {
    if(options2[name] != null && legalSslSocketOptions.indexOf(name) != -1) {
      options1[name] = options2[name];
    }
  }
}

/**
 * Connect
 * @method
 */
Connection.prototype.connect = function(_options) {
  var self = this;
  _options = _options || {};
  // Set the connections
  if(connectionAccounting) addConnection(this.id, this);
  // Check if we are overriding the promoteLongs
  if(typeof _options.promoteLongs == 'boolean') {
    self.responseOptions.promoteLongs = _options.promoteLongs;
    self.responseOptions.promoteValues = _options.promoteValues;
    self.responseOptions.promoteBuffers = _options.promoteBuffers;
  }

  // Create new connection instance
  var connection_options;
  if (self.domainSocket) {
    connection_options = {path: self.host};
  } else {
    connection_options = {port: self.port, host: self.host};
    if (self.family !== void 0) {
      connection_options.family = self.family; 
    }
  }
  self.connection = net.createConnection(connection_options);

  // Set the options for the connection
  self.connection.setKeepAlive(self.keepAlive, self.keepAliveInitialDelay);
  self.connection.setTimeout(self.connectionTimeout);
  self.connection.setNoDelay(self.noDelay);

  // If we have ssl enabled
  if(self.ssl) {
    var sslOptions = {
        socket: self.connection
      , rejectUnauthorized: self.rejectUnauthorized
    }

    // Merge in options
    merge(sslOptions, this.options);
    merge(sslOptions, _options);

    // Set options for ssl
    if(self.ca) sslOptions.ca = self.ca;
    if(self.crl) sslOptions.crl = self.crl;
    if(self.cert) sslOptions.cert = self.cert;
    if(self.key) sslOptions.key = self.key;
    if(self.passphrase) sslOptions.passphrase = self.passphrase;

    // Override checkServerIdentity behavior
    if(self.checkServerIdentity == false) {
      // Skip the identiy check by retuning undefined as per node documents
      // https://nodejs.org/api/tls.html#tls_tls_connect_options_callback
      sslOptions.checkServerIdentity = function() {
        return undefined;
      }
    } else if(typeof self.checkServerIdentity == 'function') {
      sslOptions.checkServerIdentity = self.checkServerIdentity;
    }

    // Set default sni servername to be the same as host
    if(sslOptions.servername == null) {
      sslOptions.servername = self.host;
    }

    // Attempt SSL connection
    self.connection = tls.connect(self.port, self.host, sslOptions, function() {
      // Error on auth or skip
      if(self.connection.authorizationError && self.rejectUnauthorized) {
        return self.emit("error", self.connection.authorizationError, self, {ssl:true});
      }

      // Set socket timeout instead of connection timeout
      self.connection.setTimeout(self.socketTimeout);
      // We are done emit connect
      self.emit('connect', self);
    });
    self.connection.setTimeout(self.connectionTimeout);
  } else {
    self.connection.once('connect', function() {
      // Set socket timeout instead of connection timeout
      self.connection.setTimeout(self.socketTimeout);
      // Emit connect event
      self.emit('connect', self);
    });
  }

  // Add handlers for events
  self.connection.once('error', errorHandler(self));
  self.connection.once('timeout', timeoutHandler(self));
  self.connection.once('close', closeHandler(self));
  self.connection.on('data', dataHandler(self));
}

/**
 * Unref this connection
 * @method
 * @return {boolean}
 */
Connection.prototype.unref = function() {
  if (this.connection) this.connection.unref();
  else {
    var self = this;
    this.once('connect', function() {
      self.connection.unref();
    });
  }
}

/**
 * Destroy connection
 * @method
 */
Connection.prototype.destroy = function() {
  // Set the connections
  if(connectionAccounting) deleteConnection(this.id);
  if(this.connection) {
    // Catch posssible exception thrown by node 0.10.x
    try { this.connection.end(); } catch (err) {}
    // Destroy connection
    this.connection.destroy();
  }

  this.destroyed = true;
}

/**
 * Write to connection
 * @method
 * @param {Command} command Command to write out need to implement toBin and toBinUnified
 */
Connection.prototype.write = function(buffer) {
  var i;
  // Debug Log
  if(this.logger.isDebug()) {
    if(!Array.isArray(buffer)) {
      this.logger.debug(f('writing buffer [%s] to %s:%s', buffer.toString('hex'), this.host, this.port));
    } else {
      for(i = 0; i < buffer.length; i++)
        this.logger.debug(f('writing buffer [%s] to %s:%s', buffer[i].toString('hex'), this.host, this.port));
    }
  }

  // Double check that the connection is not destroyed
  if(this.connection.destroyed === false) {
    // Write out the command
    if(!Array.isArray(buffer)) {
      this.connection.write(buffer, 'binary');
      return true;
    }

    // Iterate over all buffers and write them in order to the socket
    for(i = 0; i < buffer.length; i++) this.connection.write(buffer[i], 'binary');
    return true;
  } 

  // Connection is destroyed return write failed
  return false;
}

/**
 * Return id of connection as a string
 * @method
 * @return {string}
 */
Connection.prototype.toString = function() {
  return "" + this.id;
}

/**
 * Return json object of connection
 * @method
 * @return {object}
 */
Connection.prototype.toJSON = function() {
  return {id: this.id, host: this.host, port: this.port};
}

/**
 * Is the connection connected
 * @method
 * @return {boolean}
 */
Connection.prototype.isConnected = function() {
  if(this.destroyed) return false;
  return !this.connection.destroyed && this.connection.writable;
}

/**
 * A server connect event, used to verify that the connection is up and running
 *
 * @event Connection#connect
 * @type {Connection}
 */

/**
 * The server connection closed, all pool connections closed
 *
 * @event Connection#close
 * @type {Connection}
 */

/**
 * The server connection caused an error, all pool connections closed
 *
 * @event Connection#error
 * @type {Connection}
 */

/**
 * The server connection timed out, all pool connections closed
 *
 * @event Connection#timeout
 * @type {Connection}
 */

/**
 * The driver experienced an invalid message, all pool connections closed
 *
 * @event Connection#parseError
 * @type {Connection}
 */

module.exports = Connection;
