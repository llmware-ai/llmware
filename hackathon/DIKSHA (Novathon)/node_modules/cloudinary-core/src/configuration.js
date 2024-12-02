/**
 * Class for defining account configuration options.
 * Depends on 'utils'
 */

import {
  defaults,
  assign,
  isString,
  isPlainObject,
  cloneDeep
} from './util';

/**
 * Class for defining account configuration options.
 * @constructor Configuration
 * @param {Object} options - The account configuration parameters to set.
 * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
 *  target="_new">Available configuration options</a>
 */
class Configuration {
  constructor(options) {
    this.configuration = options == null ? {} : cloneDeep(options);
    defaults(this.configuration, DEFAULT_CONFIGURATION_PARAMS);
  }

  /**
   * Initializes the configuration. This method is a convenience method that invokes both
   *  {@link Configuration#fromEnvironment|fromEnvironment()} (Node.js environment only)
   *  and {@link Configuration#fromDocument|fromDocument()}.
   *  It first tries to retrieve the configuration from the environment variable.
   *  If not available, it tries from the document meta tags.
   * @function Configuration#init
   * @return {Configuration} returns `this` for chaining
   * @see fromDocument
   * @see fromEnvironment
   */
  init() {
    this.fromEnvironment();
    this.fromDocument();
    return this;
  }

  /**
   * Set a new configuration item
   * @function Configuration#set
   * @param {string} name - the name of the item to set
   * @param {*} value - the value to be set
   * @return {Configuration}
   *
   */
  set(name, value) {
    this.configuration[name] = value;
    return this;
  }

  /**
   * Get the value of a configuration item
   * @function Configuration#get
   * @param {string} name - the name of the item to set
   * @return {*} the configuration item
   */
  get(name) {
    return this.configuration[name];
  }

  merge(config) {
    assign(this.configuration, cloneDeep(config));
    return this;
  }

  /**
   * Initialize Cloudinary from HTML meta tags.
   * @function Configuration#fromDocument
   * @return {Configuration}
   * @example <meta name="cloudinary_cloud_name" content="mycloud">
   *
   */
  fromDocument() {
    var el, i, len, meta_elements;
    meta_elements = typeof document !== "undefined" && document !== null ? document.querySelectorAll('meta[name^="cloudinary_"]') : void 0;
    if (meta_elements) {
      for (i = 0, len = meta_elements.length; i < len; i++) {
        el = meta_elements[i];
        this.configuration[el.getAttribute('name').replace('cloudinary_', '')] = el.getAttribute('content');
      }
    }
    return this;
  }

  /**
   * Initialize Cloudinary from the `CLOUDINARY_URL` environment variable.
   *
   * This function will only run under Node.js environment.
   * @function Configuration#fromEnvironment
   * @requires Node.js
   */
  fromEnvironment() {
    var cloudinary_url, query, uri, uriRegex;
    if(typeof process !== "undefined" && process !== null && process.env && process.env.CLOUDINARY_URL ){
      cloudinary_url = process.env.CLOUDINARY_URL;
      uriRegex = /cloudinary:\/\/(?:(\w+)(?:\:([\w-]+))?@)?([\w\.-]+)(?:\/([^?]*))?(?:\?(.+))?/;
      uri = uriRegex.exec(cloudinary_url);
      if (uri) {
        if (uri[3] != null) {
          this.configuration['cloud_name'] = uri[3];
        }
        if (uri[1] != null) {
          this.configuration['api_key'] = uri[1];
        }
        if (uri[2] != null) {
          this.configuration['api_secret'] = uri[2];
        }
        if (uri[4] != null) {
          this.configuration['private_cdn'] = uri[4] != null;
        }
        if (uri[4] != null) {
          this.configuration['secure_distribution'] = uri[4];
        }
        query = uri[5];
        if (query != null) {
          query.split('&').forEach(value=>{
            let [k, v] = value.split('=');
            if (v == null) {
              v = true;
            }
            this.configuration[k] = v;
          });
        }
      }
    }
    return this;
  }

  /**
   * Create or modify the Cloudinary client configuration
   *
   * Warning: `config()` returns the actual internal configuration object. modifying it will change the configuration.
   *
   * This is a backward compatibility method. For new code, use get(), merge() etc.
   * @function Configuration#config
   * @param {hash|string|boolean} new_config
   * @param {string} new_value
   * @returns {*} configuration, or value
   *
   * @see {@link fromEnvironment} for initialization using environment variables
   * @see {@link fromDocument} for initialization using HTML meta tags
   */
  config(new_config, new_value) {
    switch (false) {
      case new_value === void 0:
        this.set(new_config, new_value);
        return this.configuration;
      case !isString(new_config):
        return this.get(new_config);
      case !isPlainObject(new_config):
        this.merge(new_config);
        return this.configuration;
      default:
        // Backward compatibility - return the internal object
        return this.configuration;
    }
  }

  /**
   * Returns a copy of the configuration parameters
   * @function Configuration#toOptions
   * @returns {Object} a key:value collection of the configuration parameters
   */
  toOptions() {
    return cloneDeep(this.configuration);
  }

}

const DEFAULT_CONFIGURATION_PARAMS = {
  responsive_class: 'cld-responsive',
  responsive_use_breakpoints: true,
  round_dpr: true,
  secure: (typeof window !== "undefined" && window !== null ? window.location ? window.location.protocol : void 0 : void 0) === 'https:'
};

Configuration.CONFIG_PARAMS = [
  "api_key",
  "api_secret",
  "callback",
  "cdn_subdomain",
  "cloud_name",
  "cname",
  "private_cdn",
  "protocol",
  "resource_type",
  "responsive",
  "responsive_class",
  "responsive_use_breakpoints",
  "responsive_width",
  "round_dpr",
  "secure",
  "secure_cdn_subdomain",
  "secure_distribution",
  "shorten",
  "type",
  "upload_preset",
  "url_suffix",
  "use_root_path",
  "version",
  "externalLibraries",
  "max_timeout_ms"
];

export default Configuration;
