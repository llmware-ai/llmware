
const Transform = require("stream").Transform;

class UploadStream extends Transform {
  constructor(options) {
    super();
    this.boundary = options.boundary;
  }

  _transform(data, encoding, next) {
    let buffer = ((Buffer.isBuffer(data)) ? data : Buffer.from(data, encoding));
    this.push(buffer);
    next();
  }

  _flush(next) {
    this.push(Buffer.from("\r\n", 'ascii'));
    this.push(Buffer.from("--" + this.boundary + "--", 'ascii'));
    return next();
  }
}

module.exports = UploadStream;
