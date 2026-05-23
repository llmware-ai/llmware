var shallowClone = require('./utils').shallowClone
  , handleCallback = require('./utils').handleCallback
  , MongoError = require('mongodb-core').MongoError
  , f = require('util').format;

var authenticate = function(self, username, password, options, callback) {
  // Did the user destroy the topology
  if(self.serverConfig && self.serverConfig.isDestroyed()) return callback(new MongoError('topology was destroyed'));

  // the default db to authenticate against is 'self'
  // if authenticate is called from a retry context, it may be another one, like admin
  var authdb = options.dbName ? options.dbName : self.databaseName;
  authdb = self.authSource ? self.authSource : authdb;
  authdb = options.authdb ? options.authdb : authdb;
  authdb = options.authSource ? options.authSource : authdb;

  // Callback
  var _callback = function(err, result) {
    if(self.listeners('authenticated').length > 0) {
      self.emit('authenticated', err, result);
    }

    // Return to caller
    handleCallback(callback, err, result);
  }

  // authMechanism
  var authMechanism = options.authMechanism || '';
  authMechanism = authMechanism.toUpperCase();

  // If classic auth delegate to auth command
  if(authMechanism == 'MONGODB-CR') {
    self.s.topology.auth('mongocr', authdb, username, password, function(err) {
      if(err) return handleCallback(callback, err, false);
      _callback(null, true);
    });
  } else if(authMechanism == 'PLAIN') {
    self.s.topology.auth('plain', authdb, username, password, function(err) {
      if(err) return handleCallback(callback, err, false);
      _callback(null, true);
    });
  } else if(authMechanism == 'MONGODB-X509') {
    self.s.topology.auth('x509', authdb, username, password, function(err) {
      if(err) return handleCallback(callback, err, false);
      _callback(null, true);
    });
  } else if(authMechanism == 'SCRAM-SHA-1') {
    self.s.topology.auth('scram-sha-1', authdb, username, password, function(err) {
      if(err) return handleCallback(callback, err, false);
      _callback(null, true);
    });
  } else if(authMechanism == 'GSSAPI') {
    if(process.platform == 'win32') {
      self.s.topology.auth('sspi', authdb, username, password, options, function(err) {
        if(err) return handleCallback(callback, err, false);
        _callback(null, true);
      });
    } else {
      self.s.topology.auth('gssapi', authdb, username, password, options, function(err) {
        if(err) return handleCallback(callback, err, false);
        _callback(null, true);
      });
    }
  } else if(authMechanism == 'DEFAULT') {
    self.s.topology.auth('default', authdb, username, password, function(err) {
      if(err) return handleCallback(callback, err, false);
      _callback(null, true);
    });
  } else {
    handleCallback(callback, MongoError.create({message: f("authentication mechanism %s not supported", options.authMechanism), driver:true}));
  }
}

module.exports = function(self, username, password, options, callback) {
  if(typeof options == 'function') callback = options, options = {};
  // Shallow copy the options
  options = shallowClone(options);

  // Set default mechanism
  if(!options.authMechanism) {
    options.authMechanism = 'DEFAULT';
  } else if(options.authMechanism != 'GSSAPI'
    && options.authMechanism != 'DEFAULT'
    && options.authMechanism != 'MONGODB-CR'
    && options.authMechanism != 'MONGODB-X509'
    && options.authMechanism != 'SCRAM-SHA-1'
    && options.authMechanism != 'PLAIN') {
      return handleCallback(callback, MongoError.create({message: "only DEFAULT, GSSAPI, PLAIN, MONGODB-X509, SCRAM-SHA-1 or MONGODB-CR is supported by authMechanism", driver:true}));
  }

  // If we have a callback fallback
  if(typeof callback == 'function') return authenticate(self, username, password, options, function(err, r) {
    // Support failed auth method
    if(err && err.message && err.message.indexOf('saslStart') != -1) err.code = 59;
    // Reject error
    if(err) return callback(err, r);
    callback(null, r);
  });

  // Return a promise
  return new self.s.promiseLibrary(function(resolve, reject) {
    authenticate(self, username, password, options, function(err, r) {
      // Support failed auth method
      if(err && err.message && err.message.indexOf('saslStart') != -1) err.code = 59;
      // Reject error
      if(err) return reject(err);
      resolve(r);
    });
  });
};
