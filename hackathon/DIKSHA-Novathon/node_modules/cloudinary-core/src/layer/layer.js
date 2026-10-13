import {
  snakeCase,
  compact
} from '../util';

class Layer {
  /**
   * Layer
   * @constructor Layer
   * @param {Object} options - layer parameters
   */
  constructor(options) {
    this.options = {};
    if (options != null) {
      ["resourceType", "type", "publicId", "format"].forEach((key) => {
        var ref;
        return this.options[key] = (ref = options[key]) != null ? ref : options[snakeCase(key)];
      });
    }
  }

  resourceType(value) {
    this.options.resourceType = value;
    return this;
  }

  type(value) {
    this.options.type = value;
    return this;
  }

  publicId(value) {
    this.options.publicId = value;
    return this;
  }

  /**
   * Get the public ID, formatted for layer parameter
   * @function Layer#getPublicId
   * @return {String} public ID
   */
  getPublicId() {
    var ref;
    return (ref = this.options.publicId) != null ? ref.replace(/\//g, ":") : void 0;
  }

  /**
   * Get the public ID, with format if present
   * @function Layer#getFullPublicId
   * @return {String} public ID
   */
  getFullPublicId() {
    if (this.options.format != null) {
      return this.getPublicId() + "." + this.options.format;
    } else {
      return this.getPublicId();
    }
  }

  format(value) {
    this.options.format = value;
    return this;
  }

  /**
   * generate the string representation of the layer
   * @function Layer#toString
   */
  toString() {
    var components;
    components = [];
    if (this.options.publicId == null) {
      throw "Must supply publicId";
    }
    if (!(this.options.resourceType === "image")) {
      components.push(this.options.resourceType);
    }
    if (!(this.options.type === "upload")) {
      components.push(this.options.type);
    }
    components.push(this.getFullPublicId());
    return compact(components).join(":");
  }

  clone() {
    return new this.constructor(this.options);
  }

}

export default Layer;
