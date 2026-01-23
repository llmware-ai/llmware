"use strict";

const crypto = require('crypto');

let secret = "squirrel", kruptein,
    ciphers = [], hashes = [],
    encoding = ['binary', 'hex', 'base64'],
    phrases = [
      "Secret Squirrel",
      "écureuil secret",
      "गुप्त गिलहरी",
      "ਗੁਪਤ ਗਿੱਠੀ",
      "veverița secretă",
      "секретная белка",
      "leyndur íkorna",
      "السنجاب السري",
      "գաղտնի սկյուռ",
      "feòrag dìomhair",
      "গোপন কাঠবিড়ালি",
      "秘密のリス",
      "таемная вавёрка",
    ];


const options = {
  use_scrypt: true,
  use_asn1: true
};


// Filter getCiphers()
ciphers = crypto.getCiphers().filter(cipher => {
  if (cipher.match(/^aes/i) && cipher.match(/256/i)&& !cipher.match(/hmac|wrap|ccm|ecb/))
    return cipher;
});


// Filter getHashes()
hashes = crypto.getHashes().filter(hash => {
  if (hash.match(/^sha[2-5]/i) && !hash.match(/rsa/i))
    return hash;
});


for (let cipher in ciphers) {
  options.algorithm = ciphers[cipher];

  for (let hash in hashes) {
    options.hashing = hashes[hash];

    for (let enc in encoding) {
      options.encodeas = encoding[enc];

      kruptein = require("../index.js")(options);

      console.log('kruptein: { algorithm: "'+options.algorithm+'", hashing: "'+options.hashing+'", encodeas: "'+options.encodeas+'" }');
      let ct, pt;

      for (let phrase in phrases) {

        console.log(phrases[phrase])

        kruptein.set(secret, phrases[phrase], (err, res) => {
          if (err)
            console.log(err);

          ct = res;
        });

        console.log(ct);

        kruptein.get(secret, ct, (err, res) => {
          if (err)
            console.log(err);

          pt = res;
        });

        console.log(pt);
        console.log("");
      }
    }
  }
}
