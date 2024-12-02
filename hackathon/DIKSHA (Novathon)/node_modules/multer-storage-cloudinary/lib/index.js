"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createCloudinaryStorage = exports.CloudinaryStorage = void 0;
var CloudinaryStorage = /** @class */ (function () {
    function CloudinaryStorage(opts) {
        var _a;
        if (opts == null || opts.cloudinary == null) {
            throw new Error('`cloudinary` option required');
        }
        this.cloudinary = opts.cloudinary;
        this.params = (_a = opts.params) !== null && _a !== void 0 ? _a : {};
    }
    CloudinaryStorage.prototype._handleFile = function (req, file, callback) {
        return __awaiter(this, void 0, void 0, function () {
            var uploadOptions, _a, public_id, otherParams, _b, _c, _d, _i, untypedKey, key, getterOrValue, value, _e, resp, err_1;
            return __generator(this, function (_f) {
                switch (_f.label) {
                    case 0:
                        _f.trys.push([0, 11, , 12]);
                        uploadOptions = void 0;
                        if (!(typeof this.params === 'function')) return [3 /*break*/, 2];
                        return [4 /*yield*/, this.params(req, file)];
                    case 1:
                        uploadOptions = _f.sent();
                        return [3 /*break*/, 9];
                    case 2:
                        _a = this.params, public_id = _a.public_id, otherParams = __rest(_a, ["public_id"]);
                        _b = {};
                        return [4 /*yield*/, (public_id === null || public_id === void 0 ? void 0 : public_id(req, file))];
                    case 3:
                        uploadOptions = (_b.public_id = _f.sent(), _b);
                        _c = [];
                        for (_d in otherParams)
                            _c.push(_d);
                        _i = 0;
                        _f.label = 4;
                    case 4:
                        if (!(_i < _c.length)) return [3 /*break*/, 9];
                        untypedKey = _c[_i];
                        key = untypedKey;
                        getterOrValue = otherParams[key];
                        if (!(typeof getterOrValue === 'function')) return [3 /*break*/, 6];
                        return [4 /*yield*/, getterOrValue(req, file)];
                    case 5:
                        _e = _f.sent();
                        return [3 /*break*/, 7];
                    case 6:
                        _e = getterOrValue;
                        _f.label = 7;
                    case 7:
                        value = _e;
                        uploadOptions[key] = value;
                        _f.label = 8;
                    case 8:
                        _i++;
                        return [3 /*break*/, 4];
                    case 9: return [4 /*yield*/, this.upload(uploadOptions, file)];
                    case 10:
                        resp = _f.sent();
                        callback(undefined, {
                            path: resp.secure_url,
                            size: resp.bytes,
                            filename: resp.public_id,
                        });
                        return [3 /*break*/, 12];
                    case 11:
                        err_1 = _f.sent();
                        callback(err_1);
                        return [3 /*break*/, 12];
                    case 12: return [2 /*return*/];
                }
            });
        });
    };
    CloudinaryStorage.prototype._removeFile = function (req, file, callback) {
        this.cloudinary.uploader.destroy(file.filename, { invalidate: true }, callback);
    };
    CloudinaryStorage.prototype.upload = function (opts, file) {
        var _this = this;
        return new Promise(function (resolve, reject) {
            var stream = _this.cloudinary.uploader.upload_stream(opts, function (err, response) {
                if (err != null)
                    return reject(err);
                return resolve(response);
            });
            file.stream.pipe(stream);
        });
    };
    return CloudinaryStorage;
}());
exports.CloudinaryStorage = CloudinaryStorage;
function createCloudinaryStorage(opts) {
    return new CloudinaryStorage(opts);
}
exports.createCloudinaryStorage = createCloudinaryStorage;
exports.default = createCloudinaryStorage;
