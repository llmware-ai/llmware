/**
 * Cloudinary jQuery plugin
 * Depends on 'jquery', 'util', 'transformation', 'cloudinary'
 */
var webp;

import Cloudinary from './cloudinary';
import Transformation from './transformation'
import firstNotNull from './util/firstNotNull'

/**
 * Creates a new Cloudinary instance with jQuery support.
 * @class CloudinaryJQuery
 * @extends Cloudinary
 */
class CloudinaryJQuery extends Cloudinary {
  constructor(options) {
    super(options);
  }

  /**
   * @override
   */
  image(publicId, options = {}) {
    var client_hints, img;
    img = this.imageTag(publicId, options);
    client_hints = firstNotNull(options.client_hints, this.config('client_hints'), false);
    if (!((options.src != null) || client_hints)) {
      // generate a tag without the image src
      img.setAttr("src", '');
    }
    img = jQuery(img.toHtml());
    if (!client_hints) {
      // cache the image src
      // set image src taking responsiveness in account
      img.data('src-cache', this.url(publicId, options)).cloudinary_update(options);
    }
    return img;
  }

  /**
   * @override
   */
  responsive(options) {
    var responsiveClass, responsiveConfig, responsiveResizeInitialized, responsive_resize, timeout;
    responsiveConfig = jQuery.extend(responsiveConfig || {}, options);
    responsiveClass = this.responsiveConfig['responsive_class'] || this.config('responsive_class');
    jQuery(`img.${responsiveClass}, img.cld-hidpi`).cloudinary_update(responsiveConfig);
    responsive_resize = firstNotNull(responsiveConfig['responsive_resize'], this.config('responsive_resize'), true);
    if (responsive_resize && !responsiveResizeInitialized) {
      responsiveConfig.resizing = responsiveResizeInitialized = true;
      timeout = null;
      const makeResponsive = () => {
          const debounce = firstNotNull(responsiveConfig.responsive_debounce, this.config('responsive_debounce'), 100);
          let reset = function () {
            if (timeout) {
              clearTimeout(timeout);
              return timeout = null;
            }
          };
          let run = function () {
            return jQuery(`img.${responsiveClass}`).cloudinary_update(responsiveConfig);
          };
          let wait = function () {
            reset();
            return setTimeout((function () {
              reset();
              return run();
            }), debounce);
          };
          if (debounce) {
            return wait();
          } else {
            return run();
          }
        };
        jQuery(window).on('resize', makeResponsive);
        return ()=>jQuery(window).off('resize', makeResponsive);
    }
  }
}

/**
 * The following methods are provided through the jQuery class
 * @class jQuery
 */
/**
 * Convert all img tags in the collection to utilize Cloudinary.
 * @function jQuery#cloudinary
 * @param {Object} [options] - options for the tag and transformations
 * @returns {jQuery}
 */
jQuery.fn.cloudinary = function(options) {
  this.filter('img').each(function() {
    var img_options, public_id, url;
    img_options = jQuery.extend({
      width: jQuery(this).attr('width'),
      height: jQuery(this).attr('height'),
      src: jQuery(this).attr('src')
    }, jQuery(this).data(), options);
    public_id = img_options.source || img_options.src;
    delete img_options.source;
    delete img_options.src;
    url = jQuery.cloudinary.url(public_id, img_options);
    img_options = new Transformation(img_options).toHtmlAttributes();
    return jQuery(this).data('src-cache', url).attr({
      width: img_options.width,
      height: img_options.height
    });
  }).cloudinary_update(options);
  return this;
};

/**
 * Updates the dpr (for `dpr_auto`) and responsive (for `w_auto`) fields according to
  *  the current container size and the device pixel ratio.<br/>
  *  <b>Note</b>:`w_auto` is updated only for images marked with the `cld-responsive`
  *  (or other defined {@link Cloudinary#responsive|responsive}) class.
  * @function jQuery#cloudinary_update
  * @param {(Array|string|NodeList)} elements - The HTML image elements to modify.
  * @param {Object} options
  * @param {boolean|string} [options.responsive_use_breakpoints=true]
  * Possible values:<br/>
  *  - `true`: Always use breakpoints for width.<br/>
  *  - `resize`: Use exact width on first render and breakpoints on resize.<br/>
  *  - `false`: Always use exact width.
  * @param {boolean} [options.responsive] - If `true`, enable responsive on all specified elements.
  *  Alternatively, you can define specific HTML elements to modify by adding the `cld-responsive`
  *  (or other custom-defined {@link Cloudinary#responsive|responsive_class}) class to those elements.
  * @param {boolean} [options.responsive_preserve_height] - If `true`, original css height is preserved.
  *  Should be used only if the transformation supports different aspect ratios.
 */
jQuery.fn.cloudinary_update = function(options) {
  jQuery.cloudinary.cloudinary_update(this.filter('img').toArray(), options);
  return this;
};

webp = null;

/**
 * @function jQuery#webpify
 */
jQuery.fn.webpify = function(options = {}, webp_options) {
  var that, webp_canary;
  that = this;
  webp_options = webp_options != null ? webp_options : options;
  if (!webp) {
    webp = jQuery.Deferred();
    webp_canary = new Image;
    webp_canary.onerror = webp.reject;
    webp_canary.onload = webp.resolve;
    webp_canary.src = 'data:image/webp;base64,UklGRi4AAABXRUJQVlA4TCEAAAAvAUAAEB8wAiMwAgSSNtse/cXjxyCCmrYNWPwmHRH9jwMA';
  }
  jQuery(function() {
    return webp.done(function() {
      return jQuery(that).cloudinary(jQuery.extend({}, webp_options, {
        format: 'webp'
      }));
    }).fail(function() {
      return jQuery(that).cloudinary(options);
    });
  });
  return this;
};

jQuery.fn.fetchify = function(options) {
  return this.cloudinary(jQuery.extend(options, {
    'type': 'fetch'
  }));
};

jQuery.cloudinary = new CloudinaryJQuery();

jQuery.cloudinary.fromDocument();

export default CloudinaryJQuery;
