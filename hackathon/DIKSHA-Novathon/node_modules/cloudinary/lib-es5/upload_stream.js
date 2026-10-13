"use strict";

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Transform = require("stream").Transform;

var UploadStream = function (_Transform) {
  _inherits(UploadStream, _Transform);

  function UploadStream(options) {
    _classCallCheck(this, UploadStream);

    var _this = _possibleConstructorReturn(this, (UploadStream.__proto__ || Object.getPrototypeOf(UploadStream)).call(this));

    _this.boundary = options.boundary;
    return _this;
  }

  _createClass(UploadStream, [{
    key: "_transform",
    value: function _transform(data, encoding, next) {
      var buffer = Buffer.isBuffer(data) ? data : Buffer.from(data, encoding);
      this.push(buffer);
      next();
    }
  }, {
    key: "_flush",
    value: function _flush(next) {
      this.push(Buffer.from("\r\n", 'ascii'));
      this.push(Buffer.from("--" + this.boundary + "--", 'ascii'));
      return next();
    }
  }]);

  return UploadStream;
}(Transform);

module.exports = UploadStream;