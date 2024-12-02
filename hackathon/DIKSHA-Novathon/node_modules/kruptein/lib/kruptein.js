/*!
 * kruptein
 * Copyright(c) 2019 Jason Gerfen <jason.gerfen@gmail.com>
 * License: MIT
 */
"use strict";

class Kruptein {

  constructor(options) {
    options = options || {};

    this.crypto = require("crypto");

    // Set defaults if the user didn't supply any
    this._algorithm = options.algorithm || "aes-256-gcm";
    this._hashing = options.hashing || "sha384";
    this._encodeas = options.encodeas || "base64";
    this._use_asn1 = options.use_asn1 || true;

    // Are we using AEAD mode (authenticated ciphers)?
    this._aead_mode = this._algorithm.match(/ccm|gcm|ocb/) ? true : false;

    // Set some defaults based on the algorithm used
    let defaults = this._matrix(this._algorithm);
    this._at_size = options._at_size || defaults._at_size;
    this._iv_size = options._iv_size || defaults._iv_size;
    this._key_size = options._key_size || defaults._key_size;

    // Replace pbkdf2 with scrypt for key derivation?
    this._use_scrypt = options.use_scrypt || false;

    // Use asn.1 encoding?
    if (this._use_asn1) {
      this.asn1 = require("asn1.js");
      this.schema = this._schema();
    }
  }


  set(secret, plaintext, aad, cb) {
    // If non-aead cipher then expect 3 vs. 4 args
    cb = cb || aad;

    // Initialize some defaults
    let iv, ct, hmac, obj, key;

    // Bail if using weak cipher algorithm modes
    if (this._validator())
      return cb("Insecure cipher mode not supported!");

    // Bail if secret is not provided
    if (!secret)
      return cb("Must supply a secret!");

    // Derive a stronger key from secret;
    this._derive_key(secret, (err, secret) => {
      if (err)
        return cb("Unable to derive key!");

      key = secret;
    });

    // Generate a random IV based on the algorithms IV size
    iv = this._iv(this._iv_size);

    // Are we dealing with an object?
    let pt = plaintext;
    try {
      plaintext = Buffer.from(JSON.stringify(pt));
    } catch(err) {
      plaintext = Buffer.from(pt);
    }

    // If AEAD mode cipher used and an AAD not provided, create one
    if (this._aead_mode && typeof aad === "function") {
      this._digest(this._iv(128), plaintext, this._hashing, this._encodeas, (err, res) => {
        if (err)
          return cb("Unable to generate AAD!");

        aad = res;
      });
    }

    // Create ciphertext from plaintext with derived key
    this._encrypt(key.key, plaintext, this._algorithm, this._encodeas, iv, aad, (err, ciphertext) => {
      if (err)
        return cb("Unable to create ciphertext!");

      ct = ciphertext;
    });

    // Create an HMAC from the resulting ciphertext
    this._digest(key.key, ct.ct, this._hashing, this._encodeas, (err, digest) => {
      if (err)
        return cb("Unable to create digest!");

      hmac = digest;
    });

    // Create an object to pass back
    obj = {
      hmac: hmac,
      ct: ct.ct,
      iv: iv,
      salt: key.salt
    };

    // If AEAD mode include the AAD
    if (aad)
      obj.aad = aad;

    // If AEAD mode include the AT
    if (ct.at)
      obj.at = ct.at;

    // Make sure the retured object is encoded property
    return (this._use_asn1) ?
      cb(null, this.schema.encode(obj).toString(this._encodeas)) :
      cb(null, JSON.stringify(obj));
  }


  get(secret, ciphertext, opts, cb) {
    // If non-aead cipher then expect 3 vs. 4 args
    cb = cb || opts;

    // Initialize some defaults
    let ct, hmac, pt, key;

    // Bail if using weak cipher algorithm modes
    if (this._validator())
      return cb("Insecure cipher mode not supported!");

    // Bail if secret is not provided
    if (!secret)
      return cb("Must supply a secret!");

    // Parse the provided ciphertext object or bail
    try {
      if (this._use_asn1) {
        ct = this.schema.decode(Buffer.from(ciphertext, this._encodeas));

        if (ct.at)
          ct.ct = ct.ct.toString();

        if (ct.aad)
          ct.aad = ct.aad.toString();
      } else {
        ct = JSON.parse(ciphertext);
      }
    } catch (err) {
      return cb("Unable to parse ciphertext object!");
    }

    // Derive a stronger key from secret;
    this._derive_key(secret, ct.salt, (err, secret) => {
      if (err)
        return cb("Unable to derive key!");

      key = secret;
    });

    // Create an HMAC from the ciphertext HMAC value
    this._digest(key.key, ct.ct, this._hashing, this._encodeas, (err, res) => {
      if (err)
        cb("Unable to generate HMAC!");

      hmac = res;
    });


    // Compare computed from included & bail if not identical
    if (hmac !== ct.hmac.toString())
      return cb("Encrypted session was tampered with!");

    // If provided get the AAD &/or AT values
    if (opts) {
      ct.aad = (opts.aad) ? opts.aad :
        (ct.aad) ? ct.aad : false;

      ct.at = (opts.at && !ct.at) ?
        opts.at : (ct.at) ?
        ct.at : false;
    }

    // Convert the AT to a buffer
    if (ct.at)
      ct.at = Buffer.from(ct.at, this._encodeas);

    // Create plaintext from ciphertext with derived key
    this._decrypt(key.key, ct.ct, this._algorithm, this._encodeas, Buffer.from(ct.iv, this._encodeas), ct.at, ct.aad, (err, res) => {
      if (err)
        return cb("Unable to decrypt ciphertext!");

      pt = res;
    });

    return cb(null, pt);
  }

  _encrypt(key, pt, algo, encodeas, iv, aad, cb) {
    // If non-aead cipher then expect 6 vs. 7 args
    cb = cb || aad;

    // Initialize some defaults
    let cipher, ct, at;

    // Create a new cipher object using algorithm, derived key & iv
    cipher = this.crypto.createCipheriv(algo, key, iv, {
      authTagLength: this._at_size
    });

    // If an AEAD cipher is used & an AAD supplied, include it
    if (this._aead_mode && typeof aad !== "function") {
      try {
        cipher.setAAD(Buffer.from(aad, encodeas), {
          plaintextLength: Buffer.byteLength(pt)
        });
      } catch (err) {
        return cb("Unable to set AAD!");
      }
    }

    // Add our plaintext; encode & pad the resulting cipher text
    ct = cipher.update(Buffer.from(pt, encodeas), "utf8", encodeas);
    cipher.setAutoPadding(true);
    ct += cipher.final(encodeas);

    // If an AEAD cipher is used, retrieve the authentication tag
    if (this._aead_mode) {
      try {
        at = cipher.getAuthTag();
      } catch (err) {
        return cb("Unable to obtain authentication tag");
      }
    }

    // Return the object
    return cb(null, (at) ? { "ct": ct, "at": at } : { "ct": ct });
  }


  _decrypt(key, ct, algo, encodeas, iv, at, aad, cb) {
    // If non-aead cipher then expect 6 vs. 7 args
    cb = cb || aad;

    // Initialize some defaults
    let cipher, pt;

    // Create a new de-cipher object using algorithm, derived key & iv
    cipher = this.crypto.createDecipheriv(algo, key, iv, {
      authTagLength: this._at_size
    });

    // If an AEAD cipher is used & an AT supplied, include it
    if (this._aead_mode && at) {
      try {
        cipher.setAuthTag(Buffer.from(at, encodeas));
      } catch (err) {
        return cb("Unable to set authentication tag");
      }
    }

    // If an AEAD cipher is used & an AAD supplied, include it
    if (this._aead_mode && typeof aad !== "function") {
      try {
        cipher.setAAD(Buffer.from(aad, encodeas), {
          plaintextLength: ct.length
        });
      } catch (err) {
        return cb("Unable to set additional authentication data");
      }
    }

    // Add our ciphertext & encode
    try {
      pt = cipher.update(ct.toString(), encodeas, "utf8");
      pt += cipher.final("utf8");
    } catch(err) {
      return cb("Unable to decrypt ciphertext!");
    }

    // return the plaintext
    return cb(null, pt);
  }


  _derive_key(secret, salt, cb) {
    // If salt not supplied then expect 2 vs. 3 args
    cb = cb || salt;

    // Initialize some defaults
    let key, opts = {};

    // If secret is an object then extract the parts; test harness only
    if (typeof secret === "object") {
      opts = secret.opts;
      secret = secret.secret;
    }

    // If a salt was NOT supplied, create one
    salt = (typeof salt !== "function") ?
      Buffer.from(salt) : this.crypto.randomBytes(128);

    // PBKDF2 or scrypt key derivation logic
    try {
      if (!this._use_scrypt || typeof this.crypto.scryptSync !== "function") {
        key = this.crypto.pbkdf2Sync(secret, salt, 15000, this._key_size, this._hashing);
      } else {
        key = this.crypto.scryptSync(secret, salt, this._key_size, opts);
      }
    } catch (err) {
      return cb("Unable to derive key!");
    }

    // Return the derived key and salt
    return cb(null, {
      key: key,
      salt: salt
    });
  }


  _digest(key, obj, hashing, encodeas, cb) {

    // Initialize some defaults
    let hmac;

    // Create an HMAC from the supplied data
    try {
      hmac = this.crypto.createHmac(hashing, key);
      hmac.setEncoding(encodeas);
      hmac.write(obj);
      hmac.end();
    } catch (err) {
      return cb("Unable to generate digest!");
    }

    // Return digest
    return cb(null, hmac.read().toString(encodeas));
  }


  _iv(iv_size) {
    return this.crypto.randomBytes(iv_size);
  }


  _matrix(algo) {
    let obj = {
      _at_size: 16,
      _iv_size: 16,
      _key_size: 32
    };

    if (algo.match(/ccm|ocb|gcm/i))
      obj._iv_size = 12;

    if (algo.match(/aes/) && algo.match(/128/))
      obj._key_size = 16;

    if (algo.match(/aes/) && algo.match(/192/))
      obj._key_size = 24;

    if (algo.match(/aes/) && algo.match(/xts/))
      obj._key_size = 32;

    if (algo.match(/aes/) && algo.match(/xts/) && algo.match(/256/))
      obj._key_size = 64;

    return obj;
  }


  _validator() {
    return (this._algorithm.match(/ccm|ecb|ocb2/));
  }


  _schema() {
    let schema;
    if (!this._aead_mode) {

      schema = this.asn1.define('schema', function() {
        this.seq().obj(
          this.key("ct").octstr(),
          this.key("hmac").octstr(),
          this.key("iv").octstr(),
          this.key("salt").octstr()
        );
      });

    } else {

      schema = this.asn1.define('schema', function() {
        this.seq().obj(
          this.key("ct").octstr(),
          this.key("hmac").octstr(),
          this.key("iv").octstr(),
          this.key("salt").octstr(),
          this.key("at").octstr(),
          this.key("aad").octstr()
        );
      });
    }

    return schema;
  }
}


// Robot, do work
module.exports = function(options) {
  return new Kruptein(options || {});
};
