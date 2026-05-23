kruptein
========
crypto; from `kruptein` to hide or conceal.

[![npm](https://img.shields.io/npm/v/kruptein.svg)](https://npmjs.com/package/kruptein)
![Downloads](https://img.shields.io/npm/dm/kruptein.svg)
[![Known Vulnerabilities](https://snyk.io/test/github/jas-/kruptein/badge.svg)](https://snyk.io/test/github/jas-/kruptein)
![Build Status](https://github.com/jas-/kruptein/actions/workflows/node.js.yml/badge.svg)

Sandbox
-------
To test the module feel free to use the [sandbox](https://codesandbox.io/p/sandbox/kruptein-test-1z9zgd)

Install
-------
To install `npm install kruptein`

Methods
-------
*   `.set(secret, plaintext, [aad], callback)`
*   `.get(secret, ciphertext, [{at: auth_tag, aad: aad}], callback)`

Options
-------
Industry standards are used for the algorithm, hashing algorithm, key & IV sizes. The default key derivation
is pbkdf2, however use of the scrypt derivation function can be enabled.
*   `algorithm`: (Optional) Cipher algorithm from `crypto.getCiphers()`. Default: `aes-256-gcm`.
*   `hashing`: (Optional) Hash algorithm from `crypto.getHashes()`. Default: `sha384`.
*   `encodeas`: (Optional) Output encoding. Currently supports `binary`, `hex`, & `base64`. Default: `base64`.
*   `key_size`: (Optional) Key size bytes (should match block size of algorithm). Default: `32`
*   `iv_size`: (Optional) IV size bytes. Default: `16`.
*   `at_size`: (Optional) Authentication tag size. Applicable to `gcm` & `ocb` cipher modes. Default: `128`.
*   `use_scrypt`: (Optional) Use `.scrypt()` to derive a key. Requires node > v10. Default/Fallback: `.pbkdf2()`.
*   `use_asn1`: (Optional) Disable the default ASN.1 encoding. Default: true

Usage
-----
When selecting an algorithm from `crypto.getCiphers()` the
`iv` and `key_size` values are calculated auto-magically to make implementation
easy.

You can always define your own if the defaults per algorithm and mode
aren't what you would like; see the `options` section above.

Create ciphertext from plaintext
-----------------
To create a new ciphertext object. Run [example](https://codesandbox.io/p/devtool/task-log/cldvsajy7000hfqgja6e28q8c?project=1z9zgd) to encrypt plaintext.

```javascript
const kruptein = require("kruptein")(opts);
let secret = "squirrel";

kruptein.set(secret, "Operation mincemeat was an example of deception", (err, ct) => {
  if (err)
    throw err;

  console.log(ct);
});
```

Get plaintext from ciphertext
------------------
To retrieve plaintext from a ciphertext object. Run [example](https://codesandbox.io/p/devtool/task-log/cldvn1j3f0007fqgjgqzle28o?project=1z9zgd) to decrypt ciphertext.

```javascript
const kruptein = require("kruptein")(opts);
let ciphertext, secret = "squirrel";

kruptein.get(secret, ciphertext, (err, pt) => {
  if (err)
    throw err;

  console.log(pt);
});
```

Output
------
The `.set()` method output depends on three factors; the `encodeas`,
`algorithm` and `use_asn1`.

For any algorithm that supports authentication (AEAD), the object
structure includes the `Authentication Tag` and the `Additional
Authentication Data` attribute and value.

When the `use_asn1` option is enabled (default is true), the result is an [ASN.1](https://letsencrypt.org/docs/a-warm-welcome-to-asn1-and-der/)
value using the `encodeas` value. While this is a more complex
encoding option, it helps standardize & minimize the resulting
ciphertext output.


Test harness
------------
The included test harness, invoked with `npm test`, makes every
attempt to trap and handle errors. Some of which come from side
channel or possible malability of the resultant ciphertext.

This can be seen within the `test/index.js` CI test harness under
the HMAC, AT & AAD validation test cases.

An online playgound for experimenting with the module can also be
found [here](https://codesandbox.io/p/devtool/task-log/cldvmxl6k0003fqgj0dc2es4x?project=1z9zgd)

Cryptography References
-----------------------
This module conforms to industry recommendations regarding algorithm type,
mode, key size, iv size & implementation, digests, key derivation & management
etc. References used provided here:

**RFC:**
*   [RFC 2104](https://tools.ietf.org/html/rfc2104): HMAC: Keyed-Hashing for Message Authentication
*   [RFC 4086](https://tools.ietf.org/html/rfc4086): Randomness Requirements for Security
*   [RFC 5084](https://tools.ietf.org/html/rfc5084): Using AES-CCM and AES-GCM Authenticated Encryption
*   [RFC 7914](https://tools.ietf.org/html/rfc7914): The scrypt Password-Based Key Derivation Function
*   [RFC 8018](https://tools.ietf.org/html/rfc8018): Password-Based Cryptography Specification
*   [X.697](https://www.itu.int/rec/T-REC-X.697-201710-I/en): ASN.1 encoding rules: Specifications of JavaScript Object Notation Encoding Rules (JER)

**NIST:**
*   [SP 800-38A](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38a.pdf): Block cipher modes of operation
*   [SP 800-38B](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf): Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC
*   [SP 800-57P1](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r4.pdf): Recommendations for key management
*   [SP 800-107](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-107r1.pdf): Recommendation for Applications Using Approved Hash Algorithms
*   [SP 800-108](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-108.pdf): Recommendation for Key Derivation Using Pseudorandom Functions
*   [SP 800-131A](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-131Ar2.pdf): Transitioning the Use of Cryptographic Algorithms and Key Lengths
*   [SP 800-132](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-132.pdf): Recommendation for Password-Based Key Derivation
*   [SP 800-175B](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-175B.pdf): Guideline for Using Cryptographic Standards in the Federal Government

**FIPS:**
*   [FIPS 197](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf): Advanced Encryption Standard (AES)
*   [FIPS 198-1](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.198-1.pdf): The Keyed-Hash Message Authentication Code (HMAC)
*   [FIPS 180-4](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf): Secure Hash Standard (SHS)

Contributing
------------
Contributions are welcome & appreciated!

Refer to the [contributing document](https://github.com/jas-/kruptein/blob/master/CONTRIBUTING.md)
to help facilitate pull requests.

License
-------
This software is licensed under the [MIT License](https://github.com/jas-/kruptein/blob/master/LICENSE).

Copyright Jason Gerfen, 2019 to 2024.
