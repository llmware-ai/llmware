function base64Encode(input) {
  if (!(input instanceof Buffer)) {
    input = Buffer.from(String(input), 'binary');
  }
  return input.toString('base64');
}

module.exports.base64Encode = base64Encode;
