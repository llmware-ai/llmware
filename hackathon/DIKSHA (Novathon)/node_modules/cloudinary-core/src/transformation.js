import Expression from './expression';
import Condition from './condition';
import Configuration from './configuration';
import {URL_KEYS} from './constants';

import {
  assign,
  camelCase,
  cloneDeep,
  compact,
  contains,
  difference,
  identity,
  isArray,
  isEmpty,
  isFunction,
  isPlainObject,
  isString,
  snakeCase
} from './util';

import {
  Param,
  ArrayParam,
  LayerParam,
  RangeParam,
  RawParam,
  TransformationParam
} from "./parameters";

/**
 * Assign key, value to target, when value is not null.<br>
 *   This function mutates the target!
 * @param {object} target the object to assign the values to
 * @param {object} sources one or more objects to get values from
 * @returns {object} the target after the assignment
 */
function assignNotNull(target, ...sources) {
  sources.forEach(source => {
    Object.keys(source).forEach(key => {
      if (source[key] != null) {
        target[key] = source[key];
      }
    });
  });
  return target;
}

/**
 * TransformationBase
 * Depends on 'configuration', 'parameters','util'
 * @internal
 */

class TransformationBase {
  /**
   * The base class for transformations.
   * Members of this class are documented as belonging to the {@link Transformation} class for convenience.
   * @class TransformationBase
   */
  constructor(options) {
    /** @private */
    /** @private */
    var parent, trans;
    parent = void 0;
    trans = {};
    /**
     * Return an options object that can be used to create an identical Transformation
     * @function Transformation#toOptions
     * @return {Object} Returns a plain object representing this transformation
     */
    this.toOptions = function (withChain) {
      let opt = {};
      if(withChain == null) {
        withChain = true;
      }
      Object.keys(trans).forEach(key => opt[key] = trans[key].origValue);
      assignNotNull(opt, this.otherOptions);
      if (withChain && !isEmpty(this.chained)) {
        let list = this.chained.map(tr => tr.toOptions());
        list.push(opt);
        opt = {};
        assignNotNull(opt, this.otherOptions);
        opt.transformation = list;
      }
      return opt;
    };
    /**
     * Set a parent for this object for chaining purposes.
     *
     * @function Transformation#setParent
     * @param {Object} object - the parent to be assigned to
     * @returns {Transformation} Returns this instance for chaining purposes.
     */
    this.setParent = function (object) {
      parent = object;
      if (object != null) {
        this.fromOptions(typeof object.toOptions === "function" ? object.toOptions() : void 0);
      }
      return this;
    };
    /**
     * Returns the parent of this object in the chain
     * @function Transformation#getParent
     * @protected
     * @return {Object} Returns the parent of this object if there is any
     */
    this.getParent = function () {
      return parent;
    };

    // Helper methods to create parameter methods
    // These methods are defined here because they access `trans` which is
    // a private member of `TransformationBase`

    /** @protected */
    this.param = function (value, name, abbr, defaultValue, process) {
      if (process == null) {
        if (isFunction(defaultValue)) {
          process = defaultValue;
        } else {
          process = identity;
        }
      }
      trans[name] = new Param(name, abbr, process).set(value);
      return this;
    };
    /** @protected */
    this.rawParam = function (value, name, abbr, defaultValue, process) {
      process = lastArgCallback(arguments);
      trans[name] = new RawParam(name, abbr, process).set(value);
      return this;
    };
    /** @protected */
    this.rangeParam = function (value, name, abbr, defaultValue, process) {
      process = lastArgCallback(arguments);
      trans[name] = new RangeParam(name, abbr, process).set(value);
      return this;
    };
    /** @protected */
    this.arrayParam = function (value, name, abbr, sep = ":", defaultValue = [], process = undefined) {
      process = lastArgCallback(arguments);
      trans[name] = new ArrayParam(name, abbr, sep, process).set(value);
      return this;
    };
    /** @protected */
    this.transformationParam = function (value, name, abbr, sep = ".", defaultValue = undefined, process = undefined) {
      process = lastArgCallback(arguments);
      trans[name] = new TransformationParam(name, abbr, sep, process).set(value);
      return this;
    };
    this.layerParam = function (value, name, abbr) {
      trans[name] = new LayerParam(name, abbr).set(value);
      return this;
    };

    // End Helper methods

    /**
     * Get the value associated with the given name.
     * @function Transformation#getValue
     * @param {string} name - the name of the parameter
     * @return {*} the processed value associated with the given name
     * @description Use {@link get}.origValue for the value originally provided for the parameter
     */
    this.getValue = function (name) {
      let value = trans[name] && trans[name].value();
      return value != null ? value : this.otherOptions[name];
    };
    /**
     * Get the parameter object for the given parameter name
     * @function Transformation#get
     * @param {string} name the name of the transformation parameter
     * @returns {Param} the param object for the given name, or undefined
     */
    this.get = function (name) {
      return trans[name];
    };
    /**
     * Remove a transformation option from the transformation.
     * @function Transformation#remove
     * @param {string} name - the name of the option to remove
     * @return {*} Returns the option that was removed or null if no option by that name was found. The type of the
     *              returned value depends on the value.
     */
    this.remove = function (name) {
      var temp;
      switch (false) {
        case trans[name] == null:
          temp = trans[name];
          delete trans[name];
          return temp.origValue;
        case this.otherOptions[name] == null:
          temp = this.otherOptions[name];
          delete this.otherOptions[name];
          return temp;
        default:
          return null;
      }
    };
    /**
     * Return an array of all the keys (option names) in the transformation.
     * @return {Array<string>} the keys in snakeCase format
     */
    this.keys = function () {
      var key;
      return ((function () {
        var results;
        results = [];
        for (key in trans) {
          if (key != null) {
            results.push(key.match(VAR_NAME_RE) ? key : snakeCase(key));
          }
        }
        return results;
      })()).sort();
    };
    /**
     * Returns a plain object representation of the transformation. Values are processed.
     * @function Transformation#toPlainObject
     * @return {Object} the transformation options as plain object
     */
    this.toPlainObject = function () {
      var hash, key, list;
      hash = {};
      for (key in trans) {
        hash[key] = trans[key].value();
        if (isPlainObject(hash[key])) {
          hash[key] = cloneDeep(hash[key]);
        }
      }
      if (!isEmpty(this.chained)) {
        list = this.chained.map(tr => tr.toPlainObject());
        list.push(hash);
        hash = {
          transformation: list
        };
      }
      return hash;
    };
    /**
     * Complete the current transformation and chain to a new one.
     * In the URL, transformations are chained together by slashes.
     * @function Transformation#chain
     * @return {Transformation} Returns this transformation for chaining
     * @example
     * var tr = cloudinary.Transformation.new();
     * tr.width(10).crop('fit').chain().angle(15).serialize()
     * // produces "c_fit,w_10/a_15"
     */
    this.chain = function () {
      var names, tr;
      names = Object.getOwnPropertyNames(trans);
      if (names.length !== 0) {
        tr = new this.constructor(this.toOptions(false));
        this.resetTransformations();
        this.chained.push(tr);
      }
      return this;
    };
    this.resetTransformations = function () {
      trans = {};
      return this;
    };
    this.otherOptions = {};
    this.chained = [];
    this.fromOptions(options);
  }

  /**
   * Merge the provided options with own's options
   * @param {Object} [options={}] key-value list of options
   * @returns {Transformation} Returns this instance for chaining
   */
  fromOptions(options = {}) {
    if (options instanceof TransformationBase) {
      this.fromTransformation(options);
    } else {
      if (isString(options) || isArray(options)) {
        options = {
          transformation: options
        };
      }
      options = cloneDeep(options, function (value) {
        if (value instanceof TransformationBase || value instanceof Layer) {
          return new value.clone();
        }
      });
      // Handling of "if" statements precedes other options as it creates a chained transformation
      if (options["if"]) {
        this.set("if", options["if"]);
        delete options["if"];
      }
      for (let key in options) {
        let opt = options[key];
        if(opt != null) {
          if (key.match(VAR_NAME_RE)) {
            if (key !== '$attr') {
              this.set('variable', key, opt);
            }
          } else {
            this.set(key, opt);
          }
        }
      }
    }
    return this;
  }

  fromTransformation(other) {
    if (other instanceof TransformationBase) {
      other.keys().forEach(key =>
        this.set(key, other.get(key).origValue)
      );
    }
    return this;
  }

  /**
   * Set a parameter.
   * The parameter name `key` is converted to
   * @param {string} key - the name of the parameter
   * @param {*} values - the value of the parameter
   * @returns {Transformation} Returns this instance for chaining
   */
  set(key, ...values) {
    var camelKey;
    camelKey = camelCase(key);
    if (contains(Transformation.methods, camelKey)) {
      this[camelKey].apply(this, values);
    } else {
      this.otherOptions[key] = values[0];
    }
    return this;
  }

  hasLayer() {
    return this.getValue("overlay") || this.getValue("underlay");
  }

  /**
   * Generate a string representation of the transformation.
   * @function Transformation#serialize
   * @return {string} Returns the transformation as a string
   */
  serialize() {
    var ifParam, j, len, paramList, ref, ref1, ref2, ref3, ref4, resultArray, t, transformationList,
      transformationString, transformations, value, variables, vars;
    resultArray = this.chained.map(tr => tr.serialize());
    paramList = this.keys();
    transformations = (ref = this.get("transformation")) != null ? ref.serialize() : void 0;
    ifParam = (ref1 = this.get("if")) != null ? ref1.serialize() : void 0;
    variables = processVar((ref2 = this.get("variables")) != null ? ref2.value() : void 0);
    paramList = difference(paramList, ["transformation", "if", "variables"]);
    vars = [];
    transformationList = [];
    for (j = 0, len = paramList.length; j < len; j++) {
      t = paramList[j];
      if (t.match(VAR_NAME_RE)) {
        vars.push(t + "_" + Expression.normalize((ref3 = this.get(t)) != null ? ref3.value() : void 0));
      } else {
        transformationList.push((ref4 = this.get(t)) != null ? ref4.serialize() : void 0);
      }
    }
    switch (false) {
      case !isString(transformations):
        transformationList.push(transformations);
        break;
      case !isArray(transformations):
        resultArray = resultArray.concat(transformations);
    }
    transformationList = (function () {
      var k, len1, results;
      results = [];
      for (k = 0, len1 = transformationList.length; k < len1; k++) {
        value = transformationList[k];
        if (isArray(value) && !isEmpty(value) || !isArray(value) && value) {
          results.push(value);
        }
      }
      return results;
    })();
    transformationList = vars.sort().concat(variables).concat(transformationList.sort());
    if (ifParam === "if_end") {
      transformationList.push(ifParam);
    } else if (!isEmpty(ifParam)) {
      transformationList.unshift(ifParam);
    }
    transformationString = compact(transformationList).join(this.param_separator);
    if (!isEmpty(transformationString)) {
      resultArray.push(transformationString);
    }
    return compact(resultArray).join(this.trans_separator);
  }

  /**
   * Provide a list of all the valid transformation option names
   * @function Transformation#listNames
   * @private
   * @return {Array<string>} a array of all the valid option names
   */
  static listNames() {
    return Transformation.methods;
  }

  /**
   * Returns the attributes for an HTML tag.
   * @function Cloudinary.toHtmlAttributes
   * @return PlainObject
   */
  toHtmlAttributes() {
    let attrName, height, options, ref2, ref3, value, width;
    options = {};
    let snakeCaseKey;
    Object.keys(this.otherOptions).forEach(key=>{
      value = this.otherOptions[key];
      snakeCaseKey = snakeCase(key);
      if (!contains(Transformation.PARAM_NAMES, snakeCaseKey) && !contains(URL_KEYS, snakeCaseKey)) {
        attrName = /^html_/.test(key) ? key.slice(5) : key;
        options[attrName] = value;
      }
    });
    // convert all "html_key" to "key" with the same value
    this.keys().forEach(key => {
      if (/^html_/.test(key)) {
        options[camelCase(key.slice(5))] = this.getValue(key);
      }
    });
    if (!(this.hasLayer() || this.getValue("angle") || contains(["fit", "limit", "lfill"], this.getValue("crop")))) {
      width = (ref2 = this.get("width")) != null ? ref2.origValue : void 0;
      height = (ref3 = this.get("height")) != null ? ref3.origValue : void 0;
      if (parseFloat(width) >= 1.0) {
        if (options.width == null) {
          options.width = width;
        }
      }
      if (parseFloat(height) >= 1.0) {
        if (options.height == null) {
          options.height = height;
        }
      }
    }
    return options;
  }

  static isValidParamName(name) {
    return Transformation.methods.indexOf(camelCase(name)) >= 0;
  }

  /**
   * Delegate to the parent (up the call chain) to produce HTML
   * @function Transformation#toHtml
   * @return {string} HTML representation of the parent if possible.
   * @example
   * tag = cloudinary.ImageTag.new("sample", {cloud_name: "demo"})
   * // ImageTag {name: "img", publicId: "sample"}
   * tag.toHtml()
   * // <img src="http://res.cloudinary.com/demo/image/upload/sample">
   * tag.transformation().crop("fit").width(300).toHtml()
   * // <img src="http://res.cloudinary.com/demo/image/upload/c_fit,w_300/sample">
   */
  toHtml() {
    var ref;
    return (ref = this.getParent()) != null ? typeof ref.toHtml === "function" ? ref.toHtml() : void 0 : void 0;
  }

  toString() {
    return this.serialize();
  }

  clone() {
    return new this.constructor(this.toOptions(true));
  }
}

const VAR_NAME_RE = /^\$[a-zA-Z0-9]+$/;

TransformationBase.prototype.trans_separator = '/';

TransformationBase.prototype.param_separator = ',';


function lastArgCallback(args) {
  var callback;
  callback = args != null ? args[args.length - 1] : void 0;
  if (isFunction(callback)) {
    return callback;
  } else {
    return void 0;
  }
}

function processVar(varArray) {
  var j, len, name, results, v;
  if (isArray(varArray)) {
    results = [];
    for (j = 0, len = varArray.length; j < len; j++) {
      [name, v] = varArray[j];
      results.push(`${name}_${Expression.normalize(v)}`);
    }
    return results;
  } else {
    return varArray;
  }
}

function processCustomFunction({function_type, source}) {
  if (function_type === 'remote') {
    return [function_type, btoa(source)].join(":");
  } else if (function_type === 'wasm') {
    return [function_type, source].join(":");
  }
}

/**
 * Transformation Class methods.
 * This is a list of the parameters defined in Transformation.
 * Values are camelCased.
 * @const Transformation.methods
 * @private
 * @ignore
 * @type {Array<string>}
 */
/**
 * Parameters that are filtered out before passing the options to an HTML tag.
 *
 * The list of parameters is a combination of `Transformation::methods` and `Configuration::CONFIG_PARAMS`
 * @const {Array<string>} Transformation.PARAM_NAMES
 * @private
 * @ignore
 * @see toHtmlAttributes
 */
class Transformation extends TransformationBase {
  /**
   * Represents a single transformation.
   * @class Transformation
   * @example
   * t = new cloudinary.Transformation();
   * t.angle(20).crop("scale").width("auto");
   *
   * // or
   *
   * t = new cloudinary.Transformation( {angle: 20, crop: "scale", width: "auto"});
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference"
   *  target="_blank">Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/video_transformation_reference"
   *  target="_blank">Available video transformations</a>
   */
  constructor(options) {
    super(options);
  }

  /**
   * Convenience constructor
   * @param {Object} options
   * @return {Transformation}
   * @example cl = cloudinary.Transformation.new( {angle: 20, crop: "scale", width: "auto"})
   */
  static new(options) {
    return new Transformation(options);
  }

  /*
    Transformation Parameters
  */
  angle(value) {
    return this.arrayParam(value, "angle", "a", ".", Expression.normalize);
  }

  audioCodec(value) {
    return this.param(value, "audio_codec", "ac");
  }

  audioFrequency(value) {
    return this.param(value, "audio_frequency", "af");
  }

  aspectRatio(value) {
    return this.param(value, "aspect_ratio", "ar", Expression.normalize);
  }

  background(value) {
    return this.param(value, "background", "b", Param.norm_color);
  }

  bitRate(value) {
    return this.param(value, "bit_rate", "br");
  }

  border(value) {
    return this.param(value, "border", "bo", function (border) {
      if (isPlainObject(border)) {
        border = assign({}, {
          color: "black",
          width: 2
        }, border);
        return `${border.width}px_solid_${Param.norm_color(border.color)}`;
      } else {
        return border;
      }
    });
  }

  color(value) {
    return this.param(value, "color", "co", Param.norm_color);
  }

  colorSpace(value) {
    return this.param(value, "color_space", "cs");
  }

  crop(value) {
    return this.param(value, "crop", "c");
  }

  customFunction(value) {
    return this.param(value, "custom_function", "fn", () => {
      return processCustomFunction(value);
    });
  }

  customPreFunction(value) {
    if (this.get('custom_function')) {
      return;
    }
    return this.rawParam(value, "custom_function", "", () => {
      value = processCustomFunction(value);
      return value ? `fn_pre:${value}` : value;
    });
  }

  defaultImage(value) {
    return this.param(value, "default_image", "d");
  }

  delay(value) {
    return this.param(value, "delay", "dl");
  }

  density(value) {
    return this.param(value, "density", "dn");
  }

  duration(value) {
    return this.rangeParam(value, "duration", "du");
  }

  dpr(value) {
    return this.param(value, "dpr", "dpr", (dpr) => {
      dpr = dpr.toString();
      if (dpr != null ? dpr.match(/^\d+$/) : void 0) {
        return dpr + ".0";
      } else {
        return Expression.normalize(dpr);
      }
    });
  }

  effect(value) {
    return this.arrayParam(value, "effect", "e", ":", Expression.normalize);
  }

  else() {
    return this.if('else');
  }

  endIf() {
    return this.if('end');
  }

  endOffset(value) {
    return this.rangeParam(value, "end_offset", "eo");
  }

  fallbackContent(value) {
    return this.param(value, "fallback_content");
  }

  fetchFormat(value) {
    return this.param(value, "fetch_format", "f");
  }

  format(value) {
    return this.param(value, "format");
  }

  flags(value) {
    return this.arrayParam(value, "flags", "fl", ".");
  }

  gravity(value) {
    return this.param(value, "gravity", "g");
  }

  fps(value) {
    return this.param(value, "fps", "fps", (fps) => {
      if (isString(fps)) {
        return fps;
      } else if (isArray(fps)) {
        return fps.join("-");
      } else {
        return fps;
      }
    });
  }

  height(value) {
    return this.param(value, "height", "h", () => {
      if (this.getValue("crop") || this.getValue("overlay") || this.getValue("underlay")) {
        return Expression.normalize(value);
      } else {
        return null;
      }
    });
  }

  htmlHeight(value) {
    return this.param(value, "html_height");
  }

  htmlWidth(value) {
    return this.param(value, "html_width");
  }

  if(value = "") {
    var i, ifVal, j, ref, trIf, trRest;
    switch (value) {
      case "else":
        this.chain();
        return this.param(value, "if", "if");
      case "end":
        this.chain();
        for (i = j = ref = this.chained.length - 1; j >= 0; i = j += -1) {
          ifVal = this.chained[i].getValue("if");
          if (ifVal === "end") {
            break;
          } else if (ifVal != null) {
            trIf = Transformation.new().if(ifVal);
            this.chained[i].remove("if");
            trRest = this.chained[i];
            this.chained[i] = Transformation.new().transformation([trIf, trRest]);
            if (ifVal !== "else") {
              break;
            }
          }
        }
        return this.param(value, "if", "if");
      case "":
        return Condition.new().setParent(this);
      default:
        return this.param(value, "if", "if", function (value) {
          return Condition.new(value).toString();
        });
    }
  }

  keyframeInterval(value) {
    return this.param(value, "keyframe_interval", "ki");
  }

  ocr(value) {
    return this.param(value, "ocr", "ocr");
  }

  offset(value) {
    var end_o, start_o;
    [start_o, end_o] = (isFunction(value != null ? value.split : void 0)) ? value.split('..') : isArray(value) ? value : [null, null];
    if (start_o != null) {
      this.startOffset(start_o);
    }
    if (end_o != null) {
      return this.endOffset(end_o);
    }
  }

  opacity(value) {
    return this.param(value, "opacity", "o", Expression.normalize);
  }

  overlay(value) {
    return this.layerParam(value, "overlay", "l");
  }

  page(value) {
    return this.param(value, "page", "pg");
  }

  poster(value) {
    return this.param(value, "poster");
  }

  prefix(value) {
    return this.param(value, "prefix", "p");
  }

  quality(value) {
    return this.param(value, "quality", "q", Expression.normalize);
  }

  radius(value) {
    return this.arrayParam(value, "radius", "r", ":", Expression.normalize);
  }

  rawTransformation(value) {
    return this.rawParam(value, "raw_transformation");
  }

  size(value) {
    var height, width;
    if (isFunction(value != null ? value.split : void 0)) {
      [width, height] = value.split('x');
      this.width(width);
      return this.height(height);
    }
  }

  sourceTypes(value) {
    return this.param(value, "source_types");
  }

  sourceTransformation(value) {
    return this.param(value, "source_transformation");
  }

  startOffset(value) {
    return this.rangeParam(value, "start_offset", "so");
  }

  streamingProfile(value) {
    return this.param(value, "streaming_profile", "sp");
  }

  transformation(value) {
    return this.transformationParam(value, "transformation", "t");
  }

  underlay(value) {
    return this.layerParam(value, "underlay", "u");
  }

  variable(name, value) {
    return this.param(value, name, name);
  }

  variables(values) {
    return this.arrayParam(values, "variables");
  }

  videoCodec(value) {
    return this.param(value, "video_codec", "vc", Param.process_video_params);
  }

  videoSampling(value) {
    return this.param(value, "video_sampling", "vs");
  }

  width(value) {
    return this.param(value, "width", "w", () => {
      if (this.getValue("crop") || this.getValue("overlay") || this.getValue("underlay")) {
        return Expression.normalize(value);
      } else {
        return null;
      }
    });
  }

  x(value) {
    return this.param(value, "x", "x", Expression.normalize);
  }

  y(value) {
    return this.param(value, "y", "y", Expression.normalize);
  }

  zoom(value) {
    return this.param(value, "zoom", "z", Expression.normalize);
  }

}

/**
 * Transformation Class methods.
 * This is a list of the parameters defined in Transformation.
 * Values are camelCased.
 */
Transformation.methods = [
  "angle",
  "audioCodec",
  "audioFrequency",
  "aspectRatio",
  "background",
  "bitRate",
  "border",
  "color",
  "colorSpace",
  "crop",
  "customFunction",
  "customPreFunction",
  "defaultImage",
  "delay",
  "density",
  "duration",
  "dpr",
  "effect",
  "else",
  "endIf",
  "endOffset",
  "fallbackContent",
  "fetchFormat",
  "format",
  "flags",
  "gravity",
  "fps",
  "height",
  "htmlHeight",
  "htmlWidth",
  "if",
  "keyframeInterval",
  "ocr",
  "offset",
  "opacity",
  "overlay",
  "page",
  "poster",
  "prefix",
  "quality",
  "radius",
  "rawTransformation",
  "size",
  "sourceTypes",
  "sourceTransformation",
  "startOffset",
  "streamingProfile",
  "transformation",
  "underlay",
  "variable",
  "variables",
  "videoCodec",
  "videoSampling",
  "width",
  "x",
  "y",
  "zoom"
];

/**
 * Parameters that are filtered out before passing the options to an HTML tag.
 *
 * The list of parameters is a combination of `Transformation::methods` and `Configuration::CONFIG_PARAMS`
 */
Transformation.PARAM_NAMES = Transformation.methods.map(snakeCase).concat(Configuration.CONFIG_PARAMS);

export default Transformation;
