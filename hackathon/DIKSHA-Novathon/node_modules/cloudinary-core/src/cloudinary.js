import {normalizeToArray} from "./util/parse/normalizeToArray";

var applyBreakpoints, closestAbove, defaultBreakpoints, findContainerWidth, maxWidth, updateDpr;

import Configuration from './configuration';
import HtmlTag from './tags/htmltag';
import ImageTag from './tags/imagetag';
import PictureTag from './tags/picturetag';
import SourceTag from './tags/sourcetag';
import Transformation from './transformation';
import url from './url';
import VideoTag from './tags/videotag';
import * as constants from './constants';

import {
  addClass,
  assign,
  defaults,
  getData,
  isEmpty,
  isFunction,
  isString,
  merge,
  removeAttribute,
  setAttribute,
  setData,
  width
} from './util';
//

import mountCloudinaryVideoTag from "./util/features/transparentVideo/mountCloudinaryVideoTag";
import enforceOptionsForTransparentVideo from "./util/features/transparentVideo/enforceOptionsForTransparentVideo";
import mountSeeThruCanvasTag from "./util/features/transparentVideo/mountSeeThruCanvasTag";
import checkSupportForTransparency from "./util/features/transparentVideo/checkSupportForTransparency";

defaultBreakpoints = function(width, steps = 100) {
  return steps * Math.ceil(width / steps);
};

closestAbove = function(list, value) {
  var i;
  i = list.length - 2;
  while (i >= 0 && list[i] >= value) {
    i--;
  }
  return list[i + 1];
};

applyBreakpoints = function(tag, width, steps, options) {
  var ref, ref1, ref2, responsive_use_breakpoints;
  responsive_use_breakpoints = (ref = (ref1 = (ref2 = options['responsive_use_breakpoints']) != null ? ref2 : options['responsive_use_stoppoints']) != null ? ref1 : this.config('responsive_use_breakpoints')) != null ? ref : this.config('responsive_use_stoppoints');
  if ((!responsive_use_breakpoints) || (responsive_use_breakpoints === 'resize' && !options.resizing)) {
    return width;
  } else {
    return this.calc_breakpoint(tag, width, steps);
  }
};

findContainerWidth = function(element) {
  var containerWidth, style;
  containerWidth = 0;
  while (((element = element != null ? element.parentNode : void 0) instanceof Element) && !containerWidth) {
    style = window.getComputedStyle(element);
    if (!/^inline/.test(style.display)) {
      containerWidth = width(element);
    }
  }
  return containerWidth;
};

updateDpr = function(dataSrc, roundDpr) {
  return dataSrc.replace(/\bdpr_(1\.0|auto)\b/g, 'dpr_' + this.device_pixel_ratio(roundDpr));
};

maxWidth = function(requiredWidth, tag) {
  var imageWidth;
  imageWidth = getData(tag, 'width') || 0;
  if (requiredWidth > imageWidth) {
    imageWidth = requiredWidth;
    setData(tag, 'width', requiredWidth);
  }
  return imageWidth;
};

class Cloudinary {
  /**
   * Creates a new Cloudinary instance.
   * @class Cloudinary
   * @classdesc Main class for accessing Cloudinary functionality.
   * @param {Object} options - A {@link Configuration} object for globally configuring Cloudinary account settings.
   * @example<br/>
   *  var cl = new cloudinary.Cloudinary( { cloud_name: "mycloud"});<br/>
   *  var imgTag = cl.image("myPicID");
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters" target="_blank">
   *  Available configuration options</a>
   */
  constructor(options) {
    var configuration;
    this.devicePixelRatioCache = {};
    this.responsiveConfig = {};
    this.responsiveResizeInitialized = false;
    configuration = new Configuration(options);
    // Provided for backward compatibility
    this.config = function(newConfig, newValue) {
      return configuration.config(newConfig, newValue);
    };
    /**
     * Use \<meta\> tags in the document to configure this `cloudinary` instance.
     * @return This {Cloudinary} instance for chaining.
     */
    this.fromDocument = function() {
      configuration.fromDocument();
      return this;
    };
    /**
     * Use environment variables to configure this `cloudinary` instance.
     * @return This {Cloudinary} instance for chaining.
     */
    this.fromEnvironment = function() {
      configuration.fromEnvironment();
      return this;
    };
    /**
     * Initializes the configuration of this `cloudinary` instance.
     *  This is a convenience method that invokes both {@link Configuration#fromEnvironment|fromEnvironment()}
     *  (Node.js environment only) and {@link Configuration#fromDocument|fromDocument()}.
     *  It first tries to retrieve the configuration from the environment variable.
     *  If not available, it tries from the document meta tags.
     * @function Cloudinary#init
     * @see Configuration#init
     * @return This {Cloudinary} instance for chaining.
     */
    this.init = function() {
      configuration.init();
      return this;
    };
  }

  /**
   * Convenience constructor
   * @param {Object} options
   * @return {Cloudinary}
   * @example cl = cloudinary.Cloudinary.new( { cloud_name: "mycloud"})
   */
  static new(options) {
    return new this(options);
  }

  /**
   * Generates a URL for any asset in your Media library.
   * @function Cloudinary#url
   * @param {string} publicId - The public ID of the media asset.
   * @param {Object} [options] - The {@link Transformation} parameters to include in the URL.
   * @param {type} [options.type='upload'] - The asset's storage type.
   *  For details on all fetch types, see
   * <a href="https://cloudinary.com/documentation/image_transformations#fetching_images_from_remote_locations"
   *  target="_blank">Fetch types</a>.
   * @param {resourceType} [options.resource_type='image'] - The type of asset. Possible values:<br/>
   *  - `image`<br/>
   *  - `video`<br/>
   *  - `raw`
   * @return {string} The media asset URL.
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
   *  Available video transformations</a>
   */
  url(publicId, options = {}) {
    return url(publicId, options, this.config());
  }

  /**
   * Generates a video asset URL.
   * @function Cloudinary#video_url
   * @param {string} publicId - The public ID of the video.
   * @param {Object} [options] - The {@link Transformation} parameters to include in the URL.
   * @param {type} [options.type='upload'] - The asset's storage type.
   *  For details on all fetch types, see
   *  <a href="https://cloudinary.com/documentation/image_transformations#fetching_images_from_remote_locations"
   *  target="_blank">Fetch types</a>.
   * @return {string} The video URL.
   * @see <a href="https://cloudinary.com/documentation/video_transformation_reference"
   *  target="_blank">Available video transformations</a>
   */
  video_url(publicId, options) {
    options = assign({
      resource_type: 'video'
    }, options);
    return this.url(publicId, options);
  }

  /**
   * Generates a URL for an image intended to be used as a thumbnail for the specified video.
   *  Identical to {@link Cloudinary#url|url}, except that the `resource_type` is `video`
   *  and the default `format` is `jpg`.
   * @function Cloudinary#video_thumbnail_url
   * @param {string} publicId -  The unique identifier of the video from which you want to generate a thumbnail image.
   * @param {Object} [options] - The image {@link Transformation} parameters to apply to the thumbnail.
   * In addition to standard image transformations, you can also use the `start_offset` transformation parameter
   * to instruct Cloudinary to generate the thumbnail from a frame other than the middle frame of the video.
   * For details, see
   * <a href="https://cloudinary.com/documentation/video_manipulation_and_delivery#generating_video_thumbnails"
   * target="_blank">Generating video thumbnails</a> in the Cloudinary documentation.
   * @param {type} [options.type='upload'] - The asset's storage type.
   * @return {string} The URL of the video thumbnail image.
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   */
  video_thumbnail_url(publicId, options) {
    options = assign({}, constants.DEFAULT_POSTER_OPTIONS, options);
    return this.url(publicId, options);
  }

  /**
   * Generates a string representation of the specified transformation options.
   * @function Cloudinary#transformation_string
   * @param {Object} options - The {@link Transformation} options.
   * @returns {string} The transformation string.
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
   *  Available video transformations</a>
   */
  transformation_string(options) {
    return new Transformation(options).serialize();
  }

  /**
   * Generates an image tag.
   * @function Cloudinary#image
   * @param {string} publicId - The public ID of the image.
   * @param {Object} options - The {@link Transformation} parameters, {@link Configuration} parameters,
   *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
   * @return {HTMLImageElement} An image tag DOM element.
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
   *  target="_blank">Available configuration options</a>
   */
  image(publicId, options = {}) {
    var client_hints, img, ref;
    img = this.imageTag(publicId, options);
    client_hints = (ref = options.client_hints != null ? options.client_hints : this.config('client_hints')) != null ? ref : false;
    if (options.src == null && !client_hints) {
      // src must be removed before creating the DOM element to avoid loading the image
      img.setAttr("src", '');
    }
    img = img.toDOM();
    if (!client_hints) {
      // cache the image src
      setData(img, 'src-cache', this.url(publicId, options));
      // set image src taking responsiveness in account
      this.cloudinary_update(img, options);
    }
    return img;
  }

  /**
   * Creates a new ImageTag instance using the configuration defined for this `cloudinary` instance.
   * @function Cloudinary#imageTag
   * @param {string} publicId - The public ID of the image.
   * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
   *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
   * @return {ImageTag} An ImageTag instance that is attached (chained) to this Cloudinary instance.
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
   *  target="_blank">Available configuration options</a>
   */
  imageTag(publicId, options) {
    var tag;
    tag = new ImageTag(publicId, this.config());
    tag.transformation().fromOptions(options);
    return tag;
  }

  /**
   * Creates a new PictureTag instance, configured using this `cloudinary` instance.
   * @function Cloudinary#PictureTag
   * @param {string} publicId - the public ID of the resource
   * @param {Object} options - additional options to pass to the new ImageTag instance
   * @param {Array<Object>} sources - the sources definitions
   * @return {PictureTag} A PictureTag that is attached (chained) to this Cloudinary instance
   */
  pictureTag(publicId, options, sources) {
    var tag;
    tag = new PictureTag(publicId, this.config(), sources);
    tag.transformation().fromOptions(options);
    return tag;
  }

  /**
   * Creates a new SourceTag instance, configured using this `cloudinary` instance.
   * @function Cloudinary#SourceTag
   * @param {string} publicId - the public ID of the resource.
   * @param {Object} options - additional options to pass to the new instance.
   * @return {SourceTag} A SourceTag that is attached (chained) to this Cloudinary instance
   */
  sourceTag(publicId, options) {
    var tag;
    tag = new SourceTag(publicId, this.config());
    tag.transformation().fromOptions(options);
    return tag;
  }

  /**
   * Generates a video thumbnail URL from the specified remote video and includes it in an image tag.
   * @function Cloudinary#video_thumbnail
   * @param {string} publicId - The unique identifier of the video from the relevant video site.
   *  Additionally, either append the image extension type to the identifier value or set
   *  the image delivery format in the 'options' parameter using the 'format' transformation option.
   *  For example, a YouTube video might have the identifier: 'o-urnlaJpOA.jpg'.
   * @param {Object} [options] - The {@link Transformation} parameters to apply.
   * @return {HTMLImageElement} An HTML image tag element
   * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
   *  Available video transformations</a>
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
   *  target="_blank">Available configuration options</a>
   */
  video_thumbnail(publicId, options) {
    return this.image(publicId, merge({}, constants.DEFAULT_POSTER_OPTIONS, options));
  }

  /**
   * Fetches a facebook profile image and delivers it in an image tag element.
   * @function Cloudinary#facebook_profile_image
   * @param {string} publicId - The Facebook numeric ID. Additionally, either append the image extension type
   *  to the ID or set the image delivery format in the 'options' parameter using the 'format' transformation option.
   * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
   *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
   * @return {HTMLImageElement} An image tag element.
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
   *  target="_blank">Available configuration options</a>
   */
  facebook_profile_image(publicId, options) {
    return this.image(publicId, assign({
      type: 'facebook'
    }, options));
  }

  /**
   * Fetches a Twitter profile image by ID and delivers it in an image tag element.
   * @function Cloudinary#twitter_profile_image
   * @param {string} publicId - The Twitter numeric ID. Additionally, either append the image extension type
   *  to the ID or set the image delivery format in the 'options' parameter using the 'format' transformation option.
   * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
   *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
   * @return {HTMLImageElement} An image tag element.
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
   *  target="_blank">Available configuration options</a>
   */
  twitter_profile_image(publicId, options) {
    return this.image(publicId, assign({
      type: 'twitter'
    }, options));
  }

  /**
   * Fetches a Twitter profile image by name and delivers it in an image tag element.
   * @function Cloudinary#twitter_name_profile_image
   * @param {string} publicId - The Twitter screen name. Additionally, either append the image extension type
   *  to the screen name or set the image delivery format in the 'options' parameter using the 'format' transformation option.
   * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
   *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
   * @return {HTMLImageElement} An image tag element.
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
   *  target="_blank">Available configuration options</a>
   */
  twitter_name_profile_image(publicId, options) {
    return this.image(publicId, assign({
      type: 'twitter_name'
    }, options));
  }

  /**
   * Fetches a Gravatar profile image and delivers it in an image tag element.
   * @function Cloudinary#gravatar_image
   * @param {string} publicId - The calculated hash for the Gravatar email address.
   *  Additionally, either append the image extension type to the screen name or set the image delivery format
   *  in the 'options' parameter using the 'format' transformation option.
   * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
   *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
   * @return {HTMLImageElement} An image tag element.
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
   *  target="_blank">Available configuration options</a>
   */
  gravatar_image(publicId, options) {
    return this.image(publicId, assign({
      type: 'gravatar'
    }, options));
  }

  /**
   * Fetches an image from a remote URL and delivers it in an image tag element.
   * @function Cloudinary#fetch_image
   * @param {string} publicId - The full URL of the image to fetch, including the extension.
   * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
   *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
   * @return {HTMLImageElement} An image tag element.
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
   *  target="_blank">Available configuration options</a>
   */
  fetch_image(publicId, options) {
    return this.image(publicId, assign({
      type: 'fetch'
    }, options));
  }

  /**
   * Generates a video tag.
   * @function Cloudinary#video
   * @param {string} publicId - The public ID of the video.
   * @param {Object} [options] - The {@link Transformation} parameters, {@link Configuration} parameters,
   *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
   * @return {HTMLVideoElement} A video tag DOM element.
   * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
   *  Available video transformations</a>
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
   *  target="_blank">Available configuration options</a>
   */
  video(publicId, options = {}) {
    return this.videoTag(publicId, options).toHtml();
  }

  /**
   * Creates a new VideoTag instance using the configuration defined for this `cloudinary` instance.
   * @function Cloudinary#videoTag
   * @param {string} publicId - The public ID of the video.
   * @param {Object} options - The {@link Transformation} parameters, {@link Configuration} parameters,
   *  and standard HTML &lt;img&gt; tag attributes to apply to the image tag.
   * @return {VideoTag} A VideoTag that is attached (chained) to this `cloudinary` instance.
   * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
   *  Available video transformations</a>
   * @see <a href="https://cloudinary.com/documentation/solution_overview#configuration_parameters"
   *  target="_blank">Available configuration options</a>
   */
  videoTag(publicId, options) {
    options = defaults({}, options, this.config());
    return new VideoTag(publicId, options);
  }

  /**
   * Generates a sprite PNG image that contains all images with the specified tag and the corresponding css file.
   * @function Cloudinary#sprite_css
   * @param {string} publicId - The tag on which to base the sprite image.
   * @param {Object} [options] - The {@link Transformation} parameters to include in the URL.
   * @return {string} The URL of the generated CSS file. The sprite image has the same URL, but with a PNG extension.
   * @see <a href="https://cloudinary.com/documentation/sprite_generation" target="_blank">
   *  Sprite generation</a>
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   */
  sprite_css(publicId, options) {
    options = assign({
      type: 'sprite'
    }, options);
    if (!publicId.match(/.css$/)) {
      options.format = 'css';
    }
    return this.url(publicId, options);
  }

  /**
   * Initializes responsive image behavior for all image tags with the 'cld-responsive'
   *  (or other defined {@link Cloudinary#responsive|responsive} class).<br/>
   *  This method should be invoked after the page has loaded.<br/>
   *  <b>Note</b>: Calls {@link Cloudinary#cloudinary_update|cloudinary_update} to modify image tags.
   * @function Cloudinary#responsive
   * @param {Object} options
   * @param {String} [options.responsive_class='cld-responsive'] - An alternative class
   *  to locate the relevant &lt;img&gt; tags.
   * @param {number} [options.responsive_debounce=100] - The debounce interval in milliseconds.
   * @param {boolean} [bootstrap=true] If true, processes the &lt;img&gt; tags by calling
   *  {@link Cloudinary#cloudinary_update|cloudinary_update}. When false, the tags are processed
   *  only after a resize event.
   * @see {@link Cloudinary#cloudinary_update|cloudinary_update} for additional configuration parameters
   * @see <a href="https://cloudinary.com/documentation/responsive_images#automating_responsive_images_with_javascript"
   *  target="_blank">Automating responsive images with JavaScript</a>
   * @return {function} that when called, removes the resize EventListener added by this function
   */
  responsive(options, bootstrap = true) {
    var ref, ref1, ref2, responsiveClass, responsiveResize, timeout;
    this.responsiveConfig = merge(this.responsiveConfig || {}, options);
    responsiveClass = (ref = this.responsiveConfig.responsive_class) != null ? ref : this.config('responsive_class');
    if (bootstrap) {
      this.cloudinary_update(`img.${responsiveClass}, img.cld-hidpi`, this.responsiveConfig);
    }
    responsiveResize = (ref1 = (ref2 = this.responsiveConfig.responsive_resize) != null ? ref2 : this.config('responsive_resize')) != null ? ref1 : true;
    if (responsiveResize && !this.responsiveResizeInitialized) {
      this.responsiveConfig.resizing = this.responsiveResizeInitialized = true;
      timeout = null;
      const makeResponsive = () => {
        var debounce, ref3, ref4, reset, run, wait, waitFunc;
        debounce = (ref3 = (ref4 = this.responsiveConfig.responsive_debounce) != null ? ref4 : this.config('responsive_debounce')) != null ? ref3 : 100;
        reset = function() {
          if (timeout) {
            clearTimeout(timeout);
            timeout = null;
          }
        };
        run = () => {
          return this.cloudinary_update(`img.${responsiveClass}`, this.responsiveConfig);
        };
        waitFunc = function() {
          reset();
          return run();
        };
        wait = function() {
          reset();
          timeout = setTimeout(waitFunc, debounce);
        };
        if (debounce) {
          return wait();
        } else {
          return run();
        }
      };
      window.addEventListener('resize', makeResponsive);
      return ()=>window.removeEventListener('resize', makeResponsive);
    }
  }

  /**
   * @function Cloudinary#calc_breakpoint
   * @private
   * @ignore
   */
  calc_breakpoint(element, width, steps) {
    let breakpoints = getData(element, 'breakpoints') || getData(element, 'stoppoints') || this.config('breakpoints') || this.config('stoppoints') || defaultBreakpoints;
    if (isFunction(breakpoints)) {
      return breakpoints(width, steps);
    } else {
      if (isString(breakpoints)) {
        breakpoints = breakpoints.split(',').map(point=>parseInt(point)).sort((a, b) => a - b);
      }
      return closestAbove(breakpoints, width);
    }
  }

  /**
   * @function Cloudinary#calc_stoppoint
   * @deprecated Use {@link calc_breakpoint} instead.
   * @private
   * @ignore
   */
  calc_stoppoint(element, width, steps) {
    return this.calc_breakpoint(element, width, steps);
  }

  /**
   * @function Cloudinary#device_pixel_ratio
   * @private
   */
  device_pixel_ratio(roundDpr) {
    roundDpr = roundDpr == null ? true : roundDpr;
    let dpr = (typeof window !== "undefined" && window !== null ? window.devicePixelRatio : void 0) || 1;
    if (roundDpr) {
      dpr = Math.ceil(dpr);
    }
    if (dpr <= 0 || dpr === (0/0)) {
      dpr = 1;
    }
    let dprString = dpr.toString();
    if (dprString.match(/^\d+$/)) {
      dprString += '.0';
    }
    return dprString;
  }

  /**
  * Applies responsiveness to all <code>&lt;img&gt;</code> tags under each relevant node
  *  (regardless of whether the tag contains the {@link Cloudinary#responsive|responsive} class).
  * @param {Element[]} nodes The parent nodes where you want to search for &lt;img&gt; tags.
  * @param {Object} [options] The {@link Cloudinary#cloudinary_update|cloudinary_update} options to apply.
  * @see <a href="https://cloudinary.com/documentation/image_transformation_reference"
  *  target="_blank">Available image transformations</a>
  * @function Cloudinary#processImageTags
  */
  processImageTags(nodes, options) {
    if (isEmpty(nodes)) {
      // similar to `$.fn.cloudinary`
      return this;
    }

    options = defaults({}, options || {}, this.config());
    let images = nodes
      .filter(node=>/^img$/i.test(node.tagName))
      .map(function(node){
          let imgOptions = assign({
            width: node.getAttribute('width'),
            height: node.getAttribute('height'),
            src: node.getAttribute('src')
          }, options);
          let publicId = imgOptions['source'] || imgOptions['src'];
          delete imgOptions['source'];
          delete imgOptions['src'];
          let attr = new Transformation(imgOptions).toHtmlAttributes();
          setData(node, 'src-cache', url(publicId, imgOptions));
          node.setAttribute('width', attr.width);
          node.setAttribute('height', attr.height);
          return node;
      });
    this.cloudinary_update(images, options);
    return this;
  }

  /**
  * Updates the dpr (for `dpr_auto`) and responsive (for `w_auto`) fields according to
  *  the current container size and the device pixel ratio.<br/>
  *  <b>Note</b>:`w_auto` is updated only for images marked with the `cld-responsive`
  *  (or other defined {@link Cloudinary#responsive|responsive}) class.
  * @function Cloudinary#cloudinary_update
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
  cloudinary_update(elements, options) {
    var containerWidth, dataSrc, match, ref4, requiredWidth;
    if (elements === null) {
      return this;
    }
    if(options == null) {
      options = {};
    }
    const responsive = options.responsive != null ? options.responsive : this.config('responsive');

    elements = normalizeToArray(elements);

    let responsiveClass;
    if (this.responsiveConfig && this.responsiveConfig.responsive_class != null) {
      responsiveClass = this.responsiveConfig.responsive_class;
    } else if (options.responsive_class != null) {
      responsiveClass = options.responsive_class;
    } else {
      responsiveClass = this.config('responsive_class');
    }

    let roundDpr = options.round_dpr != null ? options.round_dpr : this.config('round_dpr');
    elements.forEach(tag => {
      if (/img/i.test(tag.tagName)) {
        let setUrl = true;
        if (responsive) {
          addClass(tag, responsiveClass);
        }
        dataSrc = getData(tag, 'src-cache') || getData(tag, 'src');
        if (!isEmpty(dataSrc)) {
          // Update dpr according to the device's devicePixelRatio
          dataSrc = updateDpr.call(this, dataSrc, roundDpr);
          if (HtmlTag.isResponsive(tag, responsiveClass)) {
            containerWidth = findContainerWidth(tag);
            if (containerWidth !== 0) {
              if (/w_auto:breakpoints/.test(dataSrc)) {
                requiredWidth = maxWidth(containerWidth, tag);
                if (requiredWidth) {
                  dataSrc = dataSrc.replace(/w_auto:breakpoints([_0-9]*)(:[0-9]+)?/, `w_auto:breakpoints$1:${requiredWidth}`);
                } else {
                  setUrl = false;
                }
              } else {
                match = /w_auto(:(\d+))?/.exec(dataSrc);
                if (match) {
                  requiredWidth = applyBreakpoints.call(this, tag, containerWidth, match[2], options);
                  requiredWidth = maxWidth(requiredWidth, tag)
                  if (requiredWidth) {
                    dataSrc = dataSrc.replace(/w_auto[^,\/]*/g, `w_${requiredWidth}`);
                  } else {
                    setUrl = false;
                  }
                }
              }
              removeAttribute(tag, 'width');
              if (!options.responsive_preserve_height) {
                removeAttribute(tag, 'height');
              }
            } else {
              // Container doesn't know the size yet - usually because the image is hidden or outside the DOM.
              setUrl = false;
            }
          }
          const isLazyLoading = (options.loading === 'lazy' && !this.isNativeLazyLoadSupported() && this.isLazyLoadSupported() && !elements[0].getAttribute('src'));
          if (setUrl || isLazyLoading){
            // If data-width exists, set width to be data-width
            this.setAttributeIfExists(elements[0], 'width', 'data-width');
          }

          if (setUrl && !isLazyLoading) {
            setAttribute(tag, 'src', dataSrc);
          }
        }
      }
    });
    return this;
  }

  /**
   * Sets element[toAttribute] = element[fromAttribute] if element[fromAttribute] is set
   * @param element
   * @param toAttribute
   * @param fromAttribute
   */
  setAttributeIfExists(element, toAttribute, fromAttribute){
    const attributeValue = element.getAttribute(fromAttribute);
    if (attributeValue != null) {
      setAttribute(element, toAttribute, attributeValue);
    }
  }

  /**
   * Returns true if Intersection Observer API is supported
   * @returns {boolean}
   */
  isLazyLoadSupported() {
    return window && 'IntersectionObserver' in window;
  }

  /**
   * Returns true if using Chrome
   * @returns {boolean}
   */
  isNativeLazyLoadSupported() {
    return 'loading' in HTMLImageElement.prototype;
  }

  /**
   * Returns a {@link Transformation} object, initialized with the specified options, for chaining purposes.
   * @function Cloudinary#transformation
   * @param {Object} options The {@link Transformation} options to apply.
   * @return {Transformation}
   * @see Transformation
   * @see <a href="https://cloudinary.com/documentation/image_transformation_reference" target="_blank">
   *  Available image transformations</a>
   * @see <a href="https://cloudinary.com/documentation/video_transformation_reference" target="_blank">
   *  Available video transformations</a>
   */
  transformation(options) {
    return Transformation.new(this.config()).fromOptions(options).setParent(this);
  }


  /**
   * @description This function will append a TransparentVideo element to the htmlElContainer passed to it.
   *              TransparentVideo can either be an HTML Video tag, or an HTML Canvas Tag.
   * @param {HTMLElement} htmlElContainer
   * @param {string} publicId
   * @param {object} options The {@link TransparentVideoOptions} options to apply - Extends TransformationOptions
   *                 options.playsinline    - HTML Video Tag's native playsinline - passed to video element.
   *                 options.poster         - HTML Video Tag's native poster - passed to video element.
   *                 options.loop           - HTML Video Tag's native loop - passed to video element.
   *                 options?.externalLibraries = { [key: string]: string} - map of external libraries to be loaded
   * @return {Promise<HTMLElement | {status:string, message:string}>}
   */
  injectTransparentVideoElement(htmlElContainer, publicId, options = {}) {
    return new Promise((resolve, reject) => {
      if (!htmlElContainer) {
        reject({status: 'error', message: 'Expecting htmlElContainer to be HTMLElement'});
      }

      enforceOptionsForTransparentVideo(options);

      let videoURL = this.video_url(publicId, options);

      checkSupportForTransparency().then((isNativelyTransparent) => {
        let mountPromise;

        if (isNativelyTransparent) {
          mountPromise = mountCloudinaryVideoTag(htmlElContainer, this, publicId, options);
          resolve(htmlElContainer);
        } else {
          mountPromise = mountSeeThruCanvasTag(htmlElContainer, videoURL, options);
        }

        mountPromise
          .then(() => {
          resolve(htmlElContainer);
        }).catch(({status, message}) => { reject({status, message});});

        // catch for checkSupportForTransparency()
      }).catch(({status, message}) => { reject({status, message});});
    });
  }
}

assign(Cloudinary, constants);
export default Cloudinary;
