var stream = require('stream'),
  util = require('util');

module.exports = GridFSBucketReadStream;

/**
 * A readable stream that enables you to read buffers from GridFS.
 *
 * Do not instantiate this class directly. Use `openDownloadStream()` instead.
 *
 * @class
 * @param {Collection} chunks Handle for chunks collection
 * @param {Collection} files Handle for files collection
 * @param {Object} readPreference The read preference to use
 * @param {Object} filter The query to use to find the file document
 * @param {Object} [options=null] Optional settings.
 * @param {Number} [options.sort=null] Optional sort for the file find query
 * @param {Number} [options.skip=null] Optional skip for the file find query
 * @param {Number} [options.start=null] Optional 0-based offset in bytes to start streaming from
 * @param {Number} [options.end=null] Optional 0-based offset in bytes to stop streaming before
 * @fires GridFSBucketReadStream#error
 * @fires GridFSBucketReadStream#file
 * @return {GridFSBucketReadStream} a GridFSBucketReadStream instance.
 */

function GridFSBucketReadStream(chunks, files, readPreference, filter, options) {
  this.s = {
    bytesRead: 0,
    chunks: chunks,
    cursor: null,
    expected: 0,
    files: files,
    filter: filter,
    init: false,
    expectedEnd: 0,
    file: null,
    options: options,
    readPreference: readPreference
  };

  stream.Readable.call(this);
}

util.inherits(GridFSBucketReadStream, stream.Readable);

/**
 * An error occurred
 *
 * @event GridFSBucketReadStream#error
 * @type {Error}
 */

/**
 * Fires when the stream loaded the file document corresponding to the
 * provided id.
 *
 * @event GridFSBucketReadStream#file
 * @type {object}
 */

/**
 * Emitted when a chunk of data is available to be consumed.
 *
 * @event GridFSBucketReadStream#data
 * @type {object}
 */

/**
 * Fired when the stream is exhausted (no more data events).
 *
 * @event GridFSBucketReadStream#end
 * @type {object}
 */

/**
 * Fired when the stream is exhausted and the underlying cursor is killed
 *
 * @event GridFSBucketReadStream#close
 * @type {object}
 */

/**
 * Reads from the cursor and pushes to the stream.
 * @method
 */

GridFSBucketReadStream.prototype._read = function() {
  var _this = this;
  if (this.destroyed) {
    return;
  }

  waitForFile(_this, function() {
    doRead(_this);
  });
};

/**
 * Sets the 0-based offset in bytes to start streaming from. Throws
 * an error if this stream has entered flowing mode
 * (e.g. if you've already called `on('data')`)
 * @method
 * @param {Number} start Offset in bytes to start reading at
 * @return {GridFSBucketReadStream}
 */

GridFSBucketReadStream.prototype.start = function(start) {
  throwIfInitialized(this);
  this.s.options.start = start;
  return this;
};

/**
 * Sets the 0-based offset in bytes to start streaming from. Throws
 * an error if this stream has entered flowing mode
 * (e.g. if you've already called `on('data')`)
 * @method
 * @param {Number} end Offset in bytes to stop reading at
 * @return {GridFSBucketReadStream}
 */

GridFSBucketReadStream.prototype.end = function(end) {
  throwIfInitialized(this);
  this.s.options.end = end;
  return this;
};

/**
 * Marks this stream as aborted (will never push another `data` event)
 * and kills the underlying cursor. Will emit the 'end' event, and then
 * the 'close' event once the cursor is successfully killed.
 *
 * @method
 * @param {GridFSBucket~errorCallback} [callback] called when the cursor is successfully closed or an error occurred.
 * @fires GridFSBucketWriteStream#close
 * @fires GridFSBucketWriteStream#end
 */

GridFSBucketReadStream.prototype.abort = function(callback) {
  var _this = this;
  this.push(null);
  this.destroyed = true;
  if (this.s.cursor) {
    this.s.cursor.close(function(error) {
      _this.emit('close');
      callback && callback(error);
    });
  } else {
    if (!this.s.init) {
      // If not initialized, fire close event because we will never
      // get a cursor
      _this.emit('close');
    }
    callback && callback();
  }
};

/**
 * @ignore
 */

function throwIfInitialized(self) {
  if (self.s.init) {
    throw new Error('You cannot change options after the stream has entered' +
      'flowing mode!');
  }
}

/**
 * @ignore
 */

function doRead(_this) {
  if (_this.destroyed) {
    return;
  }

  _this.s.cursor.next(function(error, doc) {
    if (_this.destroyed) {
      return;
    }
    if (error) {
      return __handleError(_this, error);
    }
    if (!doc) {
      _this.push(null);
      return _this.s.cursor.close(function(error) {
        if (error) {
          return __handleError(_this, error);
        }
        _this.emit('close');
      });
    }

    var bytesRemaining = _this.s.file.length - _this.s.bytesRead;
    var expectedN = _this.s.expected++;
    var expectedLength = Math.min(_this.s.file.chunkSize,
      bytesRemaining);

    if (doc.n > expectedN) {
      var errmsg = 'ChunkIsMissing: Got unexpected n: ' + doc.n +
        ', expected: ' + expectedN;
      return __handleError(_this, new Error(errmsg));
    }

    if (doc.n < expectedN) {
      errmsg = 'ExtraChunk: Got unexpected n: ' + doc.n +
        ', expected: ' + expectedN;
      return __handleError(_this, new Error(errmsg));
    }

    var buf = Buffer.isBuffer(doc.data) ? doc.data : doc.data.buffer;

    if (buf.length !== expectedLength) {
      if (bytesRemaining <= 0) {
        errmsg = 'ExtraChunk: Got unexpected n: ' + doc.n;
        return __handleError(_this, new Error(errmsg));
      }

      errmsg = 'ChunkIsWrongSize: Got unexpected length: ' +
        buf.length + ', expected: ' + expectedLength;
      return __handleError(_this, new Error(errmsg));
    }

    _this.s.bytesRead += buf.length;

    if (buf.length === 0) {
      return _this.push(null);
    }

    var sliceStart = null;
    var sliceEnd = null;

    if (_this.s.bytesToSkip != null) {
      sliceStart = _this.s.bytesToSkip;
      _this.s.bytesToSkip = 0;
    }

    if (expectedN === _this.s.expectedEnd && _this.s.bytesToTrim != null) {
      sliceEnd = _this.s.bytesToTrim;
    }

    // If the remaining amount of data left is < chunkSize read the right amount of data
    if (_this.s.options.end && (
      (_this.s.options.end - _this.s.bytesToSkip) < buf.length
    )) {
      sliceEnd = (_this.s.options.end - _this.s.bytesToSkip);
    }

    if (sliceStart != null || sliceEnd != null) {
      buf = buf.slice(sliceStart || 0, sliceEnd || buf.length);
    }

    _this.push(buf);
  })
}

/**
 * @ignore
 */

function init(self) {
  var findOneOptions = {};
  if (self.s.readPreference) {
    findOneOptions.readPreference = self.s.readPreference;
  }
  if (self.s.options && self.s.options.sort) {
    findOneOptions.sort = self.s.options.sort;
  }
  if (self.s.options && self.s.options.skip) {
    findOneOptions.skip = self.s.options.skip;
  }

  self.s.files.findOne(self.s.filter, findOneOptions, function(error, doc) {
    if (error) {
      return __handleError(self, error);
    }
    if (!doc) {
      var identifier = self.s.filter._id ?
        self.s.filter._id.toString() : self.s.filter.filename;
      var errmsg = 'FileNotFound: file ' + identifier + ' was not found';
      var err = new Error(errmsg);
      err.code = 'ENOENT';
      return __handleError(self, err);
    }

    // If document is empty, kill the stream immediately and don't
    // execute any reads
    if (doc.length <= 0) {
      self.push(null);
      return;
    }

    if (self.destroyed) {
      // If user destroys the stream before we have a cursor, wait
      // until the query is done to say we're 'closed' because we can't
      // cancel a query.
      self.emit('close');
      return;
    }

    self.s.bytesToSkip = handleStartOption(self, doc, self.s.options);

    var filter = { files_id: doc._id };

    // Currently (MongoDB 3.4.4) skip function does not support the index,
    // it needs to retrieve all the documents first and then skip them. (CS-25811)
    // As work around we use $gte on the "n" field.
    if (self.s.options && self.s.options.start != null){
      var skip = Math.floor(self.s.options.start / doc.chunkSize);
      if (skip > 0){
        filter["n"] = {"$gte": skip};
      }
    }
    self.s.cursor = self.s.chunks.find(filter).sort({ n: 1 });

    if (self.s.readPreference) {
      self.s.cursor.setReadPreference(self.s.readPreference);
    }

    self.s.expectedEnd = Math.ceil(doc.length / doc.chunkSize);
    self.s.file = doc;
    self.s.bytesToTrim = handleEndOption(self, doc, self.s.cursor,
      self.s.options);
    self.emit('file', doc);
  });
}

/**
 * @ignore
 */

function waitForFile(_this, callback) {
  if (_this.s.file) {
    return callback();
  }

  if (!_this.s.init) {
    init(_this);
    _this.s.init = true;
  }

  _this.once('file', function() {
    callback();
  })
}

/**
 * @ignore
 */

function handleStartOption(stream, doc, options) {
  if (options && options.start != null) {
    if (options.start > doc.length) {
      throw new Error('Stream start (' + options.start + ') must not be ' +
        'more than the length of the file (' + doc.length +')');
    }
    if (options.start < 0) {
      throw new Error('Stream start (' + options.start + ') must not be ' +
        'negative');
    }
    if (options.end != null && options.end < options.start) {
      throw new Error('Stream start (' + options.start + ') must not be ' +
        'greater than stream end (' + options.end + ')');
    }

    stream.s.bytesRead = Math.floor(options.start / doc.chunkSize) *
      doc.chunkSize;
    stream.s.expected = Math.floor(options.start / doc.chunkSize);

    return options.start - stream.s.bytesRead;
  }
}

/**
 * @ignore
 */

function handleEndOption(stream, doc, cursor, options) {
  if (options && options.end != null) {
    if (options.end > doc.length) {
      throw new Error('Stream end (' + options.end + ') must not be ' +
        'more than the length of the file (' + doc.length +')')
    }
    if (options.start < 0) {
      throw new Error('Stream end (' + options.end + ') must not be ' +
        'negative');
    }

    var start = options.start != null ?
      Math.floor(options.start / doc.chunkSize) :
      0;

    cursor.limit(Math.ceil(options.end / doc.chunkSize) - start);

    stream.s.expectedEnd = Math.ceil(options.end / doc.chunkSize);

    return (Math.ceil(options.end / doc.chunkSize) * doc.chunkSize) -
      options.end;
  }
}

/**
 * @ignore
 */

function __handleError(_this, error) {
  _this.emit('error', error);
}
