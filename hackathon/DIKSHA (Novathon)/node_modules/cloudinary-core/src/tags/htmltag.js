/**
 * Generic HTML tag
 * Depends on 'transformation', 'util'
 */

import {
  isPlainObject,
  isFunction,
  getData,
  hasClass,
  merge,
  isString
} from '../util';

import Transformation from '../transformation';

/**
 * Represents an HTML (DOM) tag
 * @constructor HtmlTag
 * @param {string} name - the name of the tag
 * @param {string} [publicId]
 * @param {Object} options
 * @example tag = new HtmlTag( 'div', { 'width': 10})
 */
class HtmlTag {
  constructor(name, publicId, options) {
    var transformation;
    this.name = name;
    this.publicId = publicId;
    if (options == null) {
      if (isPlainObject(publicId)) {
        options = publicId;
        this.publicId = void 0;
      } else {
        options = {};
      }
    }
    transformation = new Transformation(options);
    transformation.setParent(this);
    this.transformation = function () {
      return transformation;
    };
  }

  /**
   * Convenience constructor
   * Creates a new instance of an HTML (DOM) tag
   * @function HtmlTag.new
   * @param {string} name - the name of the tag
   * @param {string} [publicId]
   * @param {Object} options
   * @return {HtmlTag}
   * @example tag = HtmlTag.new( 'div', { 'width': 10})
   */
  static new(name, publicId, options) {
    return new this(name, publicId, options);
  }

  /**
   * combine key and value from the `attr` to generate an HTML tag attributes string.
   * `Transformation::toHtmlTagOptions` is used to filter out transformation and configuration keys.
   * @protected
   * @param {Object} attrs
   * @return {string} the attributes in the format `'key1="value1" key2="value2"'`
   * @ignore
   */
  htmlAttrs(attrs) {
    var key, pairs, value;
    return pairs = ((function () {
      var results;
      results = [];
      for (key in attrs) {
        value = escapeQuotes(attrs[key]);
        if (value) {
          results.push(toAttribute(key, value));
        }
      }
      return results;
    })()).sort().join(' ');
  }

  /**
   * Get all options related to this tag.
   * @function HtmlTag#getOptions
   * @returns {Object} the options
   *
   */
  getOptions() {
    return this.transformation().toOptions();
  }

  /**
   * Get the value of option `name`
   * @function HtmlTag#getOption
   * @param {string} name - the name of the option
   * @returns {*} Returns the value of the option
   *
   */
  getOption(name) {
    return this.transformation().getValue(name);
  }

  /**
   * Get the attributes of the tag.
   * @function HtmlTag#attributes
   * @returns {Object} attributes
   */
  attributes() {
    // The attributes are be computed from the options every time this method is invoked.
    let htmlAttributes = this.transformation().toHtmlAttributes();
    Object.keys(htmlAttributes ).forEach(key => {
      if(isPlainObject(htmlAttributes[key])){
        delete htmlAttributes[key];
      }
    });
    if( htmlAttributes.attributes) {
      // Currently HTML attributes are defined both at the top level and under 'attributes'
      merge(htmlAttributes, htmlAttributes.attributes);
      delete htmlAttributes.attributes;
    }

    return htmlAttributes;
  }

  /**
   * Set a tag attribute named `name` to `value`
   * @function HtmlTag#setAttr
   * @param {string} name - the name of the attribute
   * @param {string} value - the value of the attribute
   */
  setAttr(name, value) {
    this.transformation().set(`html_${name}`, value);
    return this;
  }

  /**
   * Get the value of the tag attribute `name`
   * @function HtmlTag#getAttr
   * @param {string} name - the name of the attribute
   * @returns {*}
   */
  getAttr(name) {
    return this.attributes()[`html_${name}`] || this.attributes()[name];
  }

  /**
   * Remove the tag attributed named `name`
   * @function HtmlTag#removeAttr
   * @param {string} name - the name of the attribute
   * @returns {*}
   */
  removeAttr(name) {
    var ref;
    return (ref = this.transformation().remove(`html_${name}`)) != null ? ref : this.transformation().remove(name);
  }

  /**
   * @function HtmlTag#content
   * @protected
   * @ignore
   */
  content() {
    return "";
  }

  /**
   * @function HtmlTag#openTag
   * @protected
   * @ignore
   */
  openTag() {
    let tag = "<" + this.name;
    let htmlAttrs = this.htmlAttrs(this.attributes());
    if(htmlAttrs && htmlAttrs.length > 0) {
      tag += " " + htmlAttrs
    }
    return tag + ">";
  }

  /**
   * @function HtmlTag#closeTag
   * @protected
   * @ignore
   */
  closeTag() {
    return `</${this.name}>`;
  }

  /**
   * Generates an HTML representation of the tag.
   * @function HtmlTag#toHtml
   * @returns {string} Returns HTML in string format
   */
  toHtml() {
    return this.openTag() + this.content() + this.closeTag();
  }

  /**
   * Creates a DOM object representing the tag.
   * @function HtmlTag#toDOM
   * @returns {Element}
   */
  toDOM() {
    var element, name, ref, value;
    if (!isFunction(typeof document !== "undefined" && document !== null ? document.createElement : void 0)) {
      throw "Can't create DOM if document is not present!";
    }
    element = document.createElement(this.name);
    ref = this.attributes();
    for (name in ref) {
      value = ref[name];
      element.setAttribute(name, value);
    }
    return element;
  }

  static isResponsive(tag, responsiveClass) {
    var dataSrc;
    dataSrc = getData(tag, 'src-cache') || getData(tag, 'src');
    return hasClass(tag, responsiveClass) && /\bw_auto\b/.exec(dataSrc);
  }

};

/**
 * Represent the given key and value as an HTML attribute.
 * @function toAttribute
 * @protected
 * @param {string} key - attribute name
 * @param {*|boolean} value - the value of the attribute. If the value is boolean `true`, return the key only.
 * @returns {string} the attribute
 *
 */
function toAttribute(key, value) {
  if (!value) {
    return void 0;
  } else if (value === true) {
    return key;
  } else {
    return `${key}="${value}"`;
  }
}

/**
 * If given value is a string, replaces quotes with character entities (&#34;, &#39;)
 * @param value - value to change
 * @returns {*} changed value
 */
function escapeQuotes(value) {
  return isString(value) ? value.replace('"', '&#34;').replace("'", '&#39;') : value;
}

export default HtmlTag;
