const crypto = require('crypto');
const LocalStrategy = require('passport-local').Strategy;

const pbkdf2 = require('./lib/pbkdf2');
const errors = require('./lib/errors');
const authenticate = require('./lib/authenticate');

module.exports = function (schema, options) {
  options = options || {};
  options.saltlen = options.saltlen || 32;
  options.iterations = options.iterations || 25000;
  options.keylen = options.keylen || 512;
  options.encoding = options.encoding || 'hex';
  options.digestAlgorithm = options.digestAlgorithm || 'sha256'; // To get a list of supported hashes use crypto.getHashes()

  function defaultPasswordValidator(password, cb) {
    cb(null);
  }

  function defaultPasswordValidatorAsync(password) {
    return new Promise((resolve, reject) => {
      options.passwordValidator(password, (err) => (err ? reject(err) : resolve()));
    });
  }

  options.passwordValidator = options.passwordValidator || defaultPasswordValidator;
  options.passwordValidatorAsync = options.passwordValidatorAsync || defaultPasswordValidatorAsync;

  // Populate field names with defaults if not set
  options.usernameField = options.usernameField || 'username';
  options.usernameUnique = options.usernameUnique === undefined ? true : options.usernameUnique;

  // Populate username query fields with defaults if not set,
  // otherwise add username field to query fields.
  if (options.usernameQueryFields) {
    options.usernameQueryFields.push(options.usernameField);
  } else {
    options.usernameQueryFields = [options.usernameField];
  }

  // option to find username case insensitively
  options.usernameCaseInsensitive = Boolean(options.usernameCaseInsensitive || false);

  // option to convert username to lowercase when finding
  options.usernameLowerCase = options.usernameLowerCase || false;

  options.hashField = options.hashField || 'hash';
  options.saltField = options.saltField || 'salt';

  if (options.limitAttempts) {
    options.lastLoginField = options.lastLoginField || 'last';
    options.attemptsField = options.attemptsField || 'attempts';
    options.interval = options.interval || 100; // 100 ms
    options.maxInterval = options.maxInterval || 300000; // 5 min
    options.maxAttempts = options.maxAttempts || Infinity;
  }

  options.findByUsername =
    options.findByUsername ||
    function (model, queryParameters) {
      return model.findOne(queryParameters);
    };

  options.errorMessages = options.errorMessages || {};
  options.errorMessages.MissingPasswordError = options.errorMessages.MissingPasswordError || 'No password was given';
  options.errorMessages.AttemptTooSoonError = options.errorMessages.AttemptTooSoonError || 'Account is currently locked. Try again later';
  options.errorMessages.TooManyAttemptsError =
    options.errorMessages.TooManyAttemptsError || 'Account locked due to too many failed login attempts';
  options.errorMessages.NoSaltValueStoredError =
    options.errorMessages.NoSaltValueStoredError || 'Authentication not possible. No salt value stored';
  options.errorMessages.IncorrectPasswordError = options.errorMessages.IncorrectPasswordError || 'Password or username is incorrect';
  options.errorMessages.IncorrectUsernameError = options.errorMessages.IncorrectUsernameError || 'Password or username is incorrect';
  options.errorMessages.MissingUsernameError = options.errorMessages.MissingUsernameError || 'No username was given';
  options.errorMessages.UserExistsError = options.errorMessages.UserExistsError || 'A user with the given username is already registered';

  const schemaFields = {};

  if (!schema.path(options.usernameField)) {
    schemaFields[options.usernameField] = { type: String, unique: options.usernameUnique };
  }
  schemaFields[options.hashField] = { type: String, select: false };
  schemaFields[options.saltField] = { type: String, select: false };

  if (options.limitAttempts) {
    schemaFields[options.attemptsField] = { type: Number, default: 0 };
    schemaFields[options.lastLoginField] = { type: Date, default: Date.now };
  }

  schema.add(schemaFields);

  schema.pre('save', function (next) {
    if (options.usernameLowerCase && this[options.usernameField]) {
      this[options.usernameField] = this[options.usernameField].toLowerCase();
    }

    next();
  });

  schema.methods.setPassword = function (password, cb) {
    const promise = Promise.resolve()
      .then(() => {
        if (!password) {
          throw new errors.MissingPasswordError(options.errorMessages.MissingPasswordError);
        }
      })
      .then(() => options.passwordValidatorAsync(password))
      .then(() => randomBytes(options.saltlen))
      .then((saltBuffer) => saltBuffer.toString(options.encoding))
      .then((salt) => {
        this.set(options.saltField, salt);

        return salt;
      })
      .then((salt) => pbkdf2Promisified(password, salt, options))
      .then((hashRaw) => {
        this.set(options.hashField, Buffer.from(hashRaw, 'binary').toString(options.encoding));
      })
      .then(() => this);

    if (!cb) {
      return promise;
    }

    promise.then((result) => cb(null, result)).catch((err) => cb(err));
  };

  schema.methods.changePassword = function (oldPassword, newPassword, cb) {
    const promise = Promise.resolve()
      .then(() => {
        if (!oldPassword || !newPassword) {
          throw new errors.MissingPasswordError(options.errorMessages.MissingPasswordError);
        }
      })
      .then(() => this.authenticate(oldPassword))
      .then(({ user, error }) => {
        if (!user) {
          throw error;
        }
      })
      .then(() => this.setPassword(newPassword))
      .then(() => this.save())
      .then(() => this);

    if (!cb) {
      return promise;
    }

    promise.then((result) => cb(null, result)).catch((err) => cb(err));
  };

  schema.methods.authenticate = function (password, cb) {
    const promise = Promise.resolve().then(() => {
      if (this.get(options.saltField)) {
        return authenticate(this, password, options);
      }

      return this.constructor.findByUsername(this.get(options.usernameField), true).then((user) => {
        if (user) {
          return authenticate(user, password, options);
        }

        return { user: false, error: new errors.IncorrectUsernameError(options.errorMessages.IncorrectUsernameError) };
      });
    });

    if (!cb) {
      return promise;
    }

    promise.then(({ user, error }) => cb(null, user, error)).catch((err) => cb(err));
  };

  if (options.limitAttempts) {
    schema.methods.resetAttempts = function (cb) {
      const promise = Promise.resolve().then(() => {
        this.set(options.attemptsField, 0);
        return this.save();
      });

      if (!cb) {
        return promise;
      }

      promise.then((result) => cb(null, result)).catch((err) => cb(err));
    };
  }

  // Passport Local Interface
  schema.statics.authenticate = function () {
    return (username, password, cb) => {
      const promise = Promise.resolve()
        .then(() => this.findByUsername(username, true))
        .then((user) => {
          if (user) {
            return user.authenticate(password);
          }

          return { user: false, error: new errors.IncorrectUsernameError(options.errorMessages.IncorrectUsernameError) };
        });

      if (!cb) {
        return promise;
      }

      promise.then(({ user, error }) => cb(null, user, error)).catch((err) => cb(err));
    };
  };

  // Passport Interface
  schema.statics.serializeUser = function () {
    return function (user, cb) {
      cb(null, user.get(options.usernameField));
    };
  };

  schema.statics.deserializeUser = function () {
    return (username, cb) => {
      this.findByUsername(username, cb);
    };
  };

  schema.statics.register = function (user, password, cb) {
    // Create an instance of this in case user isn't already an instance
    if (!(user instanceof this)) {
      user = new this(user);
    }

    const promise = Promise.resolve()
      .then(() => {
        if (!user.get(options.usernameField)) {
          throw new errors.MissingUsernameError(options.errorMessages.MissingUsernameError);
        }
      })
      .then(() => this.findByUsername(user.get(options.usernameField)))
      .then((existingUser) => {
        if (existingUser) {
          throw new errors.UserExistsError(options.errorMessages.UserExistsError);
        }
      })
      .then(() => user.setPassword(password))
      .then(() => user.save());

    if (!cb) {
      return promise;
    }

    promise.then((result) => cb(null, result)).catch((err) => cb(err));
  };

  schema.statics.findByUsername = function (username, opts, cb) {
    if (typeof opts === 'function') {
      cb = opts;
      opts = {};
    }

    if (typeof opts == 'boolean') {
      opts = {
        selectHashSaltFields: opts,
      };
    }

    opts = opts || {};
    opts.selectHashSaltFields = !!opts.selectHashSaltFields;

    // if specified, convert the username to lowercase
    if (username !== undefined && options.usernameLowerCase) {
      username = username.toLowerCase();
    }

    // escape regex tokens
    if (username !== undefined && options.usernameCaseInsensitive) {
      username = username.replace(/[!#$()*+\-./:<=>?[\\\]^{|}]/g, '\\$&');
    }

    // Add each username query field
    const queryOrParameters = [];
    for (let i = 0; i < options.usernameQueryFields.length; i++) {
      const parameter = {};
      parameter[options.usernameQueryFields[i]] = options.usernameCaseInsensitive ? new RegExp(`^${username}$`, 'i') : username;
      queryOrParameters.push(parameter);
    }

    const query = options.findByUsername(this, { $or: queryOrParameters });

    if (opts.selectHashSaltFields) {
      query.select('+' + options.hashField + ' +' + options.saltField);
    }

    if (options.selectFields) {
      query.select(options.selectFields);
    }

    if (options.populateFields) {
      query.populate(options.populateFields);
    }

    if (cb) {
      query
        .exec()
        .then((user) => cb(null, user))
        .catch(cb);
      return;
    }

    return query;
  };

  schema.statics.createStrategy = function () {
    return new LocalStrategy(options, this.authenticate());
  };
};

function pbkdf2Promisified(password, salt, options) {
  return new Promise((resolve, reject) => pbkdf2(password, salt, options, (err, hashRaw) => (err ? reject(err) : resolve(hashRaw))));
}

function randomBytes(saltlen) {
  return new Promise((resolve, reject) => crypto.randomBytes(saltlen, (err, saltBuffer) => (err ? reject(err) : resolve(saltBuffer))));
}

module.exports.errors = errors;
