var nodeContains;

import getSDKAnalyticsSignature from "../sdkAnalytics/getSDKAnalyticsSignature";
import getAnalyticsOptions from "../sdkAnalytics/getAnalyticsOptions";
export {getSDKAnalyticsSignature , getAnalyticsOptions};

export {
  default as assign
} from 'lodash/assign';

export {
  default as cloneDeep
} from 'lodash/cloneDeep';

export {
  default as compact
} from 'lodash/compact';

export {
  default as difference
} from 'lodash/difference';

export {
  default as functions
} from 'lodash/functions';

export {
  default as identity
} from 'lodash/identity';

export {
  default as includes
} from 'lodash/includes';

export {
  default as isArray
} from 'lodash/isArray';

export {
  default as isPlainObject
} from 'lodash/isPlainObject';

export {
  default as isString
} from 'lodash/isString';

export {
  default as merge
} from 'lodash/merge';

export {
  default as contains
} from 'lodash/includes';

import isElement from 'lodash/isElement';
import isFunction from 'lodash/isFunction';
import trim from 'lodash/trim';

export * from './lazyLoad';
export * from './baseutil';
export * from './browser';
export {
  isElement,
  isFunction,
  trim
};

/*
 * Includes utility methods and lodash / jQuery shims
 */
/**
 * Get data from the DOM element.
 *
 * This method will use jQuery's `data()` method if it is available, otherwise it will get the `data-` attribute
 * @param {Element} element - the element to get the data from
 * @param {string} name - the name of the data item
 * @returns the value associated with the `name`
 * @function Util.getData
 */
export var getData = function (element, name) {
  switch (false) {
    case !(element == null):
      return void 0;
    case !isFunction(element.getAttribute):
      return element.getAttribute(`data-${name}`);
    case !isFunction(element.getAttr):
      return element.getAttr(`data-${name}`);
    case !isFunction(element.data):
      return element.data(name);
    case !(isFunction(typeof jQuery !== "undefined" && jQuery.fn && jQuery.fn.data) && isElement(element)):
      return jQuery(element).data(name);
  }
};

/**
 * Set data in the DOM element.
 *
 * This method will use jQuery's `data()` method if it is available, otherwise it will set the `data-` attribute
 * @function Util.setData
 * @param {Element} element - the element to set the data in
 * @param {string} name - the name of the data item
 * @param {*} value - the value to be set
 *
 */
export var setData = function (element, name, value) {
  switch (false) {
    case !(element == null):
      return void 0;
    case !isFunction(element.setAttribute):
      return element.setAttribute(`data-${name}`, value);
    case !isFunction(element.setAttr):
      return element.setAttr(`data-${name}`, value);
    case !isFunction(element.data):
      return element.data(name, value);
    case !(isFunction(typeof jQuery !== "undefined" && jQuery.fn && jQuery.fn.data) && isElement(element)):
      return jQuery(element).data(name, value);
  }
};

/**
 * Get attribute from the DOM element.
 *
 * @function Util.getAttribute
 * @param {Element} element - the element to set the attribute for
 * @param {string} name - the name of the attribute
 * @returns {*} the value of the attribute
 *
 */
export var getAttribute = function (element, name) {
  switch (false) {
    case !(element == null):
      return void 0;
    case !isFunction(element.getAttribute):
      return element.getAttribute(name);
    case !isFunction(element.attr):
      return element.attr(name);
    case !isFunction(element.getAttr):
      return element.getAttr(name);
  }
};

/**
 * Set attribute in the DOM element.
 *
 * @function Util.setAttribute
 * @param {Element} element - the element to set the attribute for
 * @param {string} name - the name of the attribute
 * @param {*} value - the value to be set
 */
export var setAttribute = function (element, name, value) {
  switch (false) {
    case !(element == null):
      return void 0;
    case !isFunction(element.setAttribute):
      return element.setAttribute(name, value);
    case !isFunction(element.attr):
      return element.attr(name, value);
    case !isFunction(element.setAttr):
      return element.setAttr(name, value);
  }
};

/**
 * Remove an attribute in the DOM element.
 *
 * @function Util.removeAttribute
 * @param {Element} element - the element to set the attribute for
 * @param {string} name - the name of the attribute
 */
export var removeAttribute = function (element, name) {
  switch (false) {
    case !(element == null):
      return void 0;
    case !isFunction(element.removeAttribute):
      return element.removeAttribute(name);
    default:
      return setAttribute(element, void 0);
  }
};

/**
 * Set a group of attributes to the element
 * @function Util.setAttributes
 * @param {Element} element - the element to set the attributes for
 * @param {Object} attributes - a hash of attribute names and values
 */
export var setAttributes = function (element, attributes) {
  var name, results, value;
  results = [];
  for (name in attributes) {
    value = attributes[name];
    if (value != null) {
      results.push(setAttribute(element, name, value));
    } else {
      results.push(removeAttribute(element, name));
    }
  }
  return results;
};

/**
 * Checks if element has a css class
 * @function Util.hasClass
 * @param {Element} element - the element to check
 * @param {string} name - the class name
 @returns {boolean} true if the element has the class
 */
export var hasClass = function (element, name) {
  if (isElement(element)) {
    return element.className.match(new RegExp(`\\b${name}\\b`));
  }
};

/**
 * Add class to the element
 * @function Util.addClass
 * @param {Element} element - the element
 * @param {string} name - the class name to add
 */
export var addClass = function (element, name) {
  if (!element.className.match(new RegExp(`\\b${name}\\b`))) {
    return element.className = trim(`${element.className} ${name}`);
  }
};

// The following code is taken from jQuery
export var getStyles = function (elem) {
  // Support: IE<=11+, Firefox<=30+ (#15098, #14150)
  // IE throws on elements created in popups
  // FF meanwhile throws on frame elements through "defaultView.getComputedStyle"
  if (elem.ownerDocument.defaultView.opener) {
    return elem.ownerDocument.defaultView.getComputedStyle(elem, null);
  }
  return window.getComputedStyle(elem, null);
};

export var cssExpand = ["Top", "Right", "Bottom", "Left"];

nodeContains = function (a, b) {
  var adown, bup;
  adown = (a.nodeType === 9 ? a.documentElement : a);
  bup = b && b.parentNode;
  return a === bup || !!(bup && bup.nodeType === 1 && adown.contains(bup));
};

// Truncated version of jQuery.style(elem, name)
export var domStyle = function (elem, name) {
  if (!(!elem || elem.nodeType === 3 || elem.nodeType === 8 || !elem.style)) {
    return elem.style[name];
  }
};

export var curCSS = function (elem, name, computed) {
  var maxWidth, minWidth, ret, rmargin, style, width;
  rmargin = /^margin/;
  width = void 0;
  minWidth = void 0;
  maxWidth = void 0;
  ret = void 0;
  style = elem.style;
  computed = computed || getStyles(elem);
  if (computed) {
    // Support: IE9
    // getPropertyValue is only needed for .css('filter') (#12537)
    ret = computed.getPropertyValue(name) || computed[name];
  }
  if (computed) {
    if (ret === "" && !nodeContains(elem.ownerDocument, elem)) {
      ret = domStyle(elem, name);
    }
    // Support: iOS < 6
    // A tribute to the "awesome hack by Dean Edwards"
    // iOS < 6 (at least) returns percentage for a larger set of values, but width seems to be reliably pixels
    // this is against the CSSOM draft spec: http://dev.w3.org/csswg/cssom/#resolved-values
    if (rnumnonpx.test(ret) && rmargin.test(name)) {
      // Remember the original values
      width = style.width;
      minWidth = style.minWidth;
      maxWidth = style.maxWidth;
      // Put in the new values to get a computed value out
      style.minWidth = style.maxWidth = style.width = ret;
      ret = computed.width;
      // Revert the changed values
      style.width = width;
      style.minWidth = minWidth;
      style.maxWidth = maxWidth;
    }
  }
  // Support: IE
  // IE returns zIndex value as an integer.
  if (ret !== undefined) {
    return ret + "";
  } else {
    return ret;
  }
};

export var cssValue = function (elem, name, convert, styles) {
  var val;
  val = curCSS(elem, name, styles);
  if (convert) {
    return parseFloat(val);
  } else {
    return val;
  }
};

export var augmentWidthOrHeight = function (elem, name, extra, isBorderBox, styles) {
  var i, len, side, sides, val;
  // If we already have the right measurement, avoid augmentation
  // Otherwise initialize for horizontal or vertical properties
  if (extra === (isBorderBox ? "border" : "content")) {
    return 0;
  } else {
    sides = name === "width" ? ["Right", "Left"] : ["Top", "Bottom"];
    val = 0;
    for (i = 0, len = sides.length; i < len; i++) {
      side = sides[i];
      if (extra === "margin") {
        // Both box models exclude margin, so add it if we want it
        val += cssValue(elem, extra + side, true, styles);
      }
      if (isBorderBox) {
        if (extra === "content") {
          // border-box includes padding, so remove it if we want content
          val -= cssValue(elem, `padding${side}`, true, styles);
        }
        if (extra !== "margin") {
          // At this point, extra isn't border nor margin, so remove border
          val -= cssValue(elem, `border${side}Width`, true, styles);
        }
      } else {
        // At this point, extra isn't content, so add padding
        val += cssValue(elem, `padding${side}`, true, styles);
        if (extra !== "padding") {
          // At this point, extra isn't content nor padding, so add border
          val += cssValue(elem, `border${side}Width`, true, styles);
        }
      }
    }
    return val;
  }
};

var pnum = /[+-]?(?:\d*\.|)\d+(?:[eE][+-]?\d+|)/.source;

var rnumnonpx = new RegExp("^(" + pnum + ")(?!px)[a-z%]+$", "i");

export var getWidthOrHeight = function (elem, name, extra) {
  var isBorderBox, styles, val, valueIsBorderBox;
  // Start with offset property, which is equivalent to the border-box value
  valueIsBorderBox = true;
  val = (name === "width" ? elem.offsetWidth : elem.offsetHeight);
  styles = getStyles(elem);
  isBorderBox = cssValue(elem, "boxSizing", false, styles) === "border-box";
  // Some non-html elements return undefined for offsetWidth, so check for null/undefined
  // svg - https://bugzilla.mozilla.org/show_bug.cgi?id=649285
  // MathML - https://bugzilla.mozilla.org/show_bug.cgi?id=491668
  if (val <= 0 || (val == null)) {
    // Fall back to computed then uncomputed css if necessary
    val = curCSS(elem, name, styles);
    if (val < 0 || (val == null)) {
      val = elem.style[name];
    }
    if (rnumnonpx.test(val)) {
      // Computed unit is not pixels. Stop here and return.
      return val;
    }
    // Check for style in case a browser which returns unreliable values
    // for getComputedStyle silently falls back to the reliable elem.style
    //    valueIsBorderBox = isBorderBox and (support.boxSizingReliable() or val is elem.style[name])
    valueIsBorderBox = isBorderBox && (val === elem.style[name]);
    // Normalize "", auto, and prepare for extra
    val = parseFloat(val) || 0;
  }
  // Use the active box-sizing model to add/subtract irrelevant styles
  return val + augmentWidthOrHeight(elem, name, extra || (isBorderBox ? "border" : "content"), valueIsBorderBox, styles);
};

export var width = function (element) {
  return getWidthOrHeight(element, "width", "content");
};


/**
 * @class Util
 */
/**
 * Returns true if item is a string
 * @function Util.isString
 * @param item
 * @returns {boolean} true if item is a string
 */
/**
 * Returns true if item is empty:
 * <ul>
 *   <li>item is null or undefined</li>
 *   <li>item is an array or string of length 0</li>
 *   <li>item is an object with no keys</li>
 * </ul>
 * @function Util.isEmpty
 * @param item
 * @returns {boolean} true if item is empty
 */
/**
 * Assign source properties to destination.
 * If the property is an object it is assigned as a whole, overriding the destination object.
 * @function Util.assign
 * @param {Object} destination - the object to assign to
 */
/**
 * Recursively assign source properties to destination
 * @function Util.merge
 * @param {Object} destination - the object to assign to
 * @param {...Object} [sources] The source objects.
 */
/**
 * Create a new copy of the given object, including all internal objects.
 * @function Util.cloneDeep
 * @param {Object} value - the object to clone
 * @return {Object} a new deep copy of the object
 */
/**
 * Creates a new array from the parameter with "falsey" values removed
 * @function Util.compact
 * @param {Array} array - the array to remove values from
 * @return {Array} a new array without falsey values
 */
/**
 * Check if a given item is included in the given array
 * @function Util.contains
 * @param {Array} array - the array to search in
 * @param {*} item - the item to search for
 * @return {boolean} true if the item is included in the array
 */
/**
 * Returns values in the given array that are not included in the other array
 * @function Util.difference
 * @param {Array} arr - the array to select from
 * @param {Array} values - values to filter from arr
 * @return {Array} the filtered values
 */
/**
 * Returns a list of all the function names in obj
 * @function Util.functions
 * @param {Object} object - the object to inspect
 * @return {Array} a list of functions of object
 */
/**
 * Returns the provided value. This functions is used as a default predicate function.
 * @function Util.identity
 * @param {*} value
 * @return {*} the provided value
 */
/**
 * Remove leading or trailing spaces from text
 * @function Util.trim
 * @param {string} text
 * @return {string} the `text` without leading or trailing spaces
 */
