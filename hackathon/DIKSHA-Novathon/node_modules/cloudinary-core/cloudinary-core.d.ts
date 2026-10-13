export as namespace cloudinary;

/****************************** Constants *************************************/
type CropMode = string | "scale" | "fit" | "limit" | "mfit" | "fill" | "lfill" | "pad" | "lpad" | "mpad" | "crop" | "thumb" | "imagga_crop" | "imagga_scale";
type CustomFunctionType = "wasm" | "remote";
interface CustomFunction {
    function_type: CustomFunctionType;
    source: string;
}
type Gravity = string | "north_west" | "north" | "north_east" | "west" | "center" | "east" | "south_west" | "south" | "south_east" | "xy_center" |
    "face" | "face:center" | "face:auto" | "faces" | "faces:center" | "faces:auto" | "body" | "body:face" | "adv_face" | "adv_faces" | "adv_eyes" |
    "custom" | "custom:face" | "custom:faces" | "custom:adv_face" | "custom:adv_faces" |
    "auto" | "auto:adv_face" | "auto:adv_faces" | "auto:adv_eyes" | "auto:body" | "auto:face" | "auto:faces" | "auto:custom_no_override" | "auto:none";
type ImageFileExtension = string | "jpg" | "jpe" | "jpeg" | "jpc" | "jp2" | "j2k" | "wdp" | "jxr" | "hdp" | "png" | "gif" | "webp" | "bmp" | "tif" | "tiff" |
    "ico" | "pdf" | "ps" | "ept" | "eps" | "eps3" | "psd" | "svg" | "ai" | "djvu" | "flif";
type VideoFileExtension = string | "webm" | "mp4" | "ogv" | "flv" | "m3u8";
type Angle = number | string | Array<number | string> | "auto_right" | "auto_left" | "ignore" | "vflip" | "hflip";
type ColorSpace = string | "srgb" | "no_cmyk";
type ImageFlags = string | Array<string> | "any_format" | "attachment" | "awebp" | "clip" | "cutter" | "force_strip" | "ignore_aspect_ratio" | "keep_iptc" | "layer_apply" |
    "lossy" | "preserve_transparency" | "png8" | "progressive" | "rasterize" | "region_relative" | "relative" | "strip_profile" | "text_no_trim" | "no_overflow" | "tiled";
type VideoFlags = string | Array<string> | "splice" | "layer_apply" | "no_stream" | "truncate_ts" | "waveform";
type AudioCodec = string | "none" | "aac" | "vorbis" | "mp3";
type AudioFrequency = number | 8000 | 11025 | 16000 | 22050 | 32000 | 37800 | 44056 | 44100 | 47250 | 48000 | 88200 | 96000 | 176400 | 192000;
type StreamingProfiles = string | "4k" | "full_hd" | "hd" | "sd" | "full_hd_wifi" | "full_hd_lean" | "hd_lean";
type UrlOptions = (Transformation | Transformation.Options) & { placeholder?: string, accessibility?: string };

export function crc32(str: string): any;
export function utf8_encode(argString: string): any;

type AnalyticsOptions = {
    sdkSemver: string;
    techVersion: string;
    sdkCode: string;
    feature: string;
}

type AnalyticsOptionsParameters = {
    sdkSemver: string;
    techVersion: string;
    sdkCode: string;
    urlAnalytics?: boolean;
    accessibility?: boolean;
    loading?: string;
    responsive?: boolean;
    placeholder?: boolean;
}

export class Util {
    static allStrings(list: Array<any>): boolean;
    static camelCase(text: string): string;
    static convertKeys(source: Object, converter?: (value: any) => any): Object;
    static defaults(target: Object, object1?: any, ...objectN: any[]): Object;
    static snakeCase(source: string): string;
    static without(array: Array<any>, item: any): Array<any>;
    static isNumberLike(value: any): boolean;
    static withCamelCaseKeys(source: Object): Object;
    static smartEscape(text: string, unsafe: string | RegExp): string;
    static withSnakeCaseKeys(source: Object): Object;
    static hasClass(element: Element, name: string): boolean;
    static addClass(element: Element, name: string): void;
    static getAttribute(element: Element, name: string): string;
    static setAttribute(element: Element, name: string, value: any): void;
    static removeAttribute(element: Element, name: string): void;
    static setAttributes(element: Element, attributes: Array<any>): any;
    static getData(element: Element, name: string): any;
    static setData(element: Element, name: string, value: any): void;
    static width(element: Element): number;
    static isString(value: any): boolean;
    static isArray(obj: any): boolean;
    static isEmpty(value: any): boolean;
    static assign(target: Object, object1?: any, ...objectN: any[]): any;
    static merge(target: Object, object1?: any, ...objectN: any[]): any;
    static cloneDeep(value: any): any;
    static compact(array: Array<any>): Array<any>;
    static contains(collection: Array<any>, item: any): boolean;
    static difference(array: Array<any>, values: Array<any>): Array<any>;
    static isFunction(value: any): boolean;
    static functions(object: any): Array<any>;
    static identity(value: any): any;
    static isPlainObject(value: any): boolean;
    static trim(text: string): string;
    static detectIntersection(element: Element, onIntersect: Function): void

    static getAnalyticsOptions(options: AnalyticsOptionsParameters) : AnalyticsOptions;
    static getSDKAnalyticsSignature(options: AnalyticsOptions):string;
}


/**
 *  Represents a single transformation.
 *  @class Transformation
 *  @example
 *  t = new cloudinary.Transformation();
 * t.angle(20).crop("scale").width("auto");
 *
 * // or
 *
 * t = new cloudinary.Transformation( {angle: 20, crop: "scale", width: "auto"});
 */
export class Transformation {

    constructor(options?: Transformation.Options);

    static "new"(options?: Transformation.Options): Transformation;

    /**
     * Return an options object that can be used to create an identical Transformation
     * @function Transformation#toOptions
     * @return {Object} Returns a plain object representing this transformation
     */
    toOptions(): Object;

    /**
     * Get the value associated with the given name.
     * @function Transformation#getValue
     * @param {string} name - the name of the parameter
     * @return {*} the processed value associated with the given name
     * @description Use {@link get}.origValue for the value originally provided for the parameter
     */
    getValue(name: string): any;

    /**
     * Get the parameter object for the given parameter name
     * @function Transformation#get
     * @param {string} name the name of the transformation parameter
     * @returns {Param} the param object for the given name, or undefined
     */
    get(name: string): any;

    /**
     * Remove a transformation option from the transformation.
     * @function Transformation#remove
     * @param {string} name - the name of the option to remove
     * @return {*} Returns the option that was removed or null if no option by that name was found. The type of the
     *              returned value depends on the value.
     */
    remove(name: string): any;

    /**
     * Return an array of all the keys (option names) in the transformation.
     * @return {Array<string>} the keys in snakeCase format
     */
    keys(): Array<string>;

    /**
     * Returns a plain object representation of the transformation. Values are processed.
     * @function Transformation#toPlainObject
     * @return {Object} the transformation options as plain object
     */
    toPlainObject(): Object;

    /**
     * Returns the value of "overlay" if it exists, otherwise returns the value of "underlay"
     */
    hasLayer(): any;

    /**
     * Generate a string representation of the transformation.
     * @return {string } Returns the transformation as a string
     */
    serialize(): string;

    /**
     * Combines all propoerties from source transformation into this one
     * @param source transformation to copy
     * @return this transforamtion
     */
    fromTransformation(source: Transformation): Transformation;

    /**
     * Returns attributes for an HTML tag.
     * @return PlainObject
     */
    toHtmlAttributes(): Object;


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
    chain(): Transformation;

    /**
     * Resets this transformation to an empty one
     */
    resetTransformations(): Transformation;

    "if"(): Condition; // Create a condition
    "if"(condition?: string): Transformation; // Create a condition
    "else"(): Transformation; // Separator for setting the desired transformation for an "if" branch in case of falsy condition
    endIf(): Transformation; // End condition

    /**
     * Transformation methods
     */
    angle(value: Angle): Transformation; // degrees or mode
    audioCodec(value: AudioCodec): Transformation;
    audioFrequency(value: AudioFrequency): Transformation;
    aspectRatio(value: string | number): Transformation; // ratio or percent, e.g. 1.5 or 16:9
    background(value: string): Transformation; // color, e.g. "blue" or "rgb:9090ff"
    border(value: string): Transformation; // style, e.g. "6px_solid_rgb:00390b60"
    color(value: string): Transformation; // e.g. "red" or "rgb:20a020"
    colorSpace(value: ColorSpace): Transformation;
    crop(value: CropMode): Transformation;
    customFunction(value: CustomFunction): Transformation;
    customPreFunction(value: CustomFunction): Transformation;
    defaultImage(value: string): Transformation; // public id of an uploaded image
    delay(value: string): Transformation;
    density(value: number): Transformation; // Control the density to use while converting a PDF document to images. (range: 50-300, default: 150)
    dpr(value: "auto" | number): Transformation; // Deliver the image in the specified device pixel ratio. The parameter accepts any positive float value
    effect(value: string | Array<string | number>): Transformation; // name and value, e.g. hue:40
    fetchFormat(value: "auto" | ImageFileExtension): Transformation;
    format(value: ImageFileExtension): Transformation;
    flags(value: ImageFlags | string): Transformation; // Set one or more flags that alter the default transformation behavior. Separate multiple flags with a dot (`.`).
    gravity(value: Gravity): Transformation; // The last any covers auto:50 which is cropping algorithm aggresiveness and future proofing
    height(value: number): Transformation; // Number of pixels or height %
    htmlHeight(value: string): Transformation;
    htmlWidth(value: string): Transformation;
    opacity(value: number): Transformation; // percent, 0-100
    overlay(value: string): Transformation; // Identifier, e.g. "text:Arial_50:Smile!", or public id of a different resource
    page(value: number): Transformation; // Given a multi-page file (PDF, animated GIF, TIFF), generate an image of a single page using the given index.
    prefix(value: string): Transformation;
    quality(value: string | number): Transformation; // percent or percent[:chroma_subsampling] or auto[:quality_level]
    radius(value: "max" | number): Transformation; // pixels or max
    rawTransformation(value: any): Transformation;
    size(value: string): Transformation;
    sourceTypes(value: VideoFileExtension | Array<VideoFileExtension>): Transformation;
    sources?: Array<object>;
    sourceTransformation(value: Object): Transformation; // Set the transformation to apply on each source by an object with pairs of source type and source transformations to apply
    startOffset(value: number | string): Transformation;
    streamingProfile(value: string): Transformation;
    transformation(value: string | Array<Transformation.Options>): Transformation; // Apply a pre-defined named transformation of the given name. When using Cloudinary's client integration libraries, the 'transformation' parameter accepts an array of transformation parameters to be chained together.
    underlay(value: string): Transformation; // public id of an uploaded image
    variable(name: string, value: any): Transformation;
    variables(value: Array<[string, any]>): Transformation;
    videoCodec(value: string | Object): Transformation; // Select the video codec and control the video content of the profile used. Can be provided in the form <codec>[:<profile>:[<level>:[<:b_frames>]]] to specify specific values to apply for video codec, profile, level and b_frames, e.g. "h264:baseline:3.1:bframes_no". Also accepts a hash of values such as { codec: 'h264', profile: 'basic', level: '3.1', b_frames: false }
    videoSampling(value: number | string): Transformation; // Integer - The total number of frames to sample from the original video. String - The number of seconds between each frame to sample from the original video. e.g. 2.3s takes one frame every 2.3 seconds.
    width(value: string | number): Transformation; // Number of pixels, width % or "auto" with rounding step
    x(value: number): Transformation; // pixels or percent
    y(value: number): Transformation; // pixels or percent
    zoom(value: number): Transformation; // percent
    toHtml(): string; // Returns the string representation of this transformation

    // Video options
    bitRate(value: number | string): Transformation; // Advanced control of video bitrate in bits per second. By default the video uses a variable bitrate (VBR), with this value indicating the maximum bitrate. If constant is specified, the video plays with a constant bitrate (CBR).
    // Supported codecs: h264, h265(MPEG - 4); vp8, vp9(WebM).
    duration(value :number | string): Transformation; // Float or string
    endOffset(value: number | string): Transformation; // Float or string
    fallbackContent(value: string): Transformation;
    fps(value: string | Array<string|number>): Transformation;
    keyframeInterval(value: number): Transformation;
    offset(value: string): Transformation; // [float, float] or [string, string] or a range. Shortcut to set video cutting using a combination of start_offset and end_offset values
    poster(value: string | Object): Transformation;
    sourceTypes(value: string): Transformation;
}

export class Condition {
    /**
     * Represents a transformation condition
     * @param {string} conditionStr - a condition in string format
     * @class Condition
     * @example
     * // normally this class is not instantiated directly */
    constructor(conditionStr: string);

    static "new"(conditionStr: string): Condition;

    "and"(): Condition; // Add terms to the condition
    "or"(): Condition; // Add terms to the condition
    "then"(): Transformation; // Separator for setting the desired transformation for an "if" branch in case of truthy condition

    /**
     * @function Condition#height
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Condition} this condition
     */
    height(operator: string, value: string | number): Condition;
    /**
     * @function Condition#width
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Condition} this condition
     */
    width(operator: string, value: string | number): Condition;
    /**
     * @function Condition#aspectRatio
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Condition} this condition
     */
    aspectRatio(operator: string, value: string | number): Condition;
    /**
     * @function Condition#pageCount
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Condition} this condition
     */
    pageCount(operator: string, value: string | number): Condition;
    /**
     * @function Condition#faceCount
     * @param {string} operator the comparison operator (e.g. "<", "lt")
     * @param {string|number} value the right hand side value
     * @return {Condition} this condition
     */
    faceCount(operator: string, value: string | number): Condition;
}
export namespace Transformation {
    export interface Options extends Configuration.Options {
        angle?: Angle; // degrees or mode
        aspectRatio?: string | number; // ratio or percent, e.g. 1.5 or 16:9
        background?: string; // color, e.g. "blue" or "rgb:9090ff"
        border?: string; // style, e.g. "6px_solid_rgb:00390b60"
        color?: string; // e.g. "red" or "rgb:20a020"
        colorSpace?: ColorSpace;
        crop?: CropMode,
        customFunction?: CustomFunction,
        customPreFunction?: CustomFunction,
        defaultImage?: string; // public id of an uploaded image
        delay?: string;
        density?: number | string; // Control the density to use while converting a PDF document to images. (range: 50-300, default: 150)
        dpr?: number | string; // Deliver the image in the specified device pixel ratio. The parameter accepts any positive float value
        effect?: string | Array<string | number>; // name and value, e.g. hue:40
        fetchFormat?: ImageFileExtension;
        format?: ImageFileExtension;
        flags?: ImageFlags | string; // Set one or more flags that alter the default transformation behavior. Separate multiple flags with a dot (`.`).
        gravity?: Gravity; // The last any covers auto:50 which is cropping algorithm aggresiveness and future proofing
        height?: number | string; // Number of pixels or height %
        htmlHeight?: string;
        htmlWidth?: string;
        "if"?: string; // Apply a transformation only if a specified condition is met (see the conditional transformations documentation).
        "else"?: string;
        endIf?: string;
        opacity?: number | string; // percent, 0-100
        overlay?: string; // Identifier, e.g. "text:Arial_50:Smile!", or public id of a different resource
        page?: number | string; // Given a multi-page file (PDF, animated GIF, TIFF), generate an image of a single page using the given index.
        prefix?: string;
        quality?: string | number; // percent or percent[:chroma_subsampling] or auto[:quality_level]
        radius?: number | string; // pixels or max
        rawTransformation?: any;
        size?: string;
        transformation?: string | Array<Transformation.Options>; // Apply a pre-defined named transformation of the given name. When using Cloudinary's client integration libraries, the 'transformation' parameter accepts an array of transformation parameters to be chained together.
        underlay?: string; // public id of an uploaded image
        variable?: [string, any];
        variables?: Array<[string, any]>;
        width?: string | number; // Number of pixels, width % or "auto" with rounding step
        x?: number | string; // pixels or percent
        y?: number | string; // pixels or percent
        zoom?: number | string; // percent
        [futureKey: string]: any;
    }

    interface VideoOptions extends Transformation.Options {
        audioCodec?: AudioCodec;
        audioFrequency?: AudioFrequency;
        bitRate?: number | string; // Advanced control of video bitrate in bits per second. By default the video uses a variable bitrate (VBR), with this value indicating the maximum bitrate. If constant is specified, the video plays with a constant bitrate (CBR).
        // Supported codecs: h264, h265(MPEG - 4); vp8, vp9(WebM).
        duration?: number | string; // Float or string
        endOffset?: number | string; // Float or string
        fallbackContent?: string;
        flags?: VideoFlags;
        fps?: string | Array<string|number>;
        keyframeInterval?: number;
        offset?: string, // [float, float] or [string, string] or a range. Shortcut to set video cutting using a combination of start_offset and end_offset values
        poster?: string | Object,
        sourceTypes?: string;
        sourceTransformation?: string;
        startOffset?: number | string; // Float or string
        streamingProfile?: StreamingProfiles
        videoCodec?: string | Object; // Select the video codec and control the video content of the profile used. Can be provided in the form <codec>[:<profile>:[<level>:[<:b_frames>]]] to specify specific values to apply for video codec, profile, level and b_frames, e.g. "h264:baseline:3.1:bframes_no". Also accepts a hash of values such as { codec: 'h264', profile: 'basic', level: '3.1', b_frames: false }
        videoSampling?: number | string; // Integer - The total number of frames to sample from the original video. The frames are spread out over the length of the video, e.g. 20 takes one frame every 5% -- OR -- String - The number of seconds between each frame to sample from the original video. e.g. 2.3s takes one frame every 2.3 seconds.
    }
}

/**
 * Cloudinary configuration class
 * @constructor Configuration
 * @param {Object} options - configuration parameters
 */
export class Configuration {
    constructor(options?: Configuration.Options);

    init(): Configuration;
    set(name: string, value?: any): Configuration;
    get(name: string): any;
    merge(config?: Object): Configuration;

    /**
     * Initialize Cloudinary from HTML meta tags.
     * @function Configuration#fromDocument
     * @return {Configuration}
     * @example <meta name="cloudinary_cloud_name" content="mycloud">
     *
     */
    fromDocument(): Configuration;

    fromEnvironment(): Configuration;

    toOptions(): Object;
}


/**
 * Represents an HTML (DOM) tag
 * @constructor HtmlTag
 * @param {string} name - the name of the tag
 * @param {string} [publicId]
 * @param {Object} options
 * @example tag = new HtmlTag( 'div', { 'width': 10})
 */
export class HtmlTag {
    constructor(name: string, publicId?: string, options?: Transformation.Options);
    constructor(name: string, options?: Transformation.Options);
    static "new"(name: string, publicId?: string, options?: Transformation.Options): HtmlTag;
    static "new"(name: string, options?: Transformation.Options): HtmlTag;
    getOptions(): Object;
    getOption(name: string): any;
    attributes(): Object;
    setAttr(name: string, value: string): void;
    getAttr(name: string): string;
    removeAttr(name: string): string;
    content(): string;
    openTag(): string;
    closeTag(): string;
    toHtml(): string;
    toDOM(): Element;
    isResponsive(): boolean;
    transformation(): Transformation;
}
/**
 * Creates an HTML (DOM) Image tag using Cloudinary as the source.
 * @constructor ImageTag
 * @extends HtmlTag
 * @param {string} [publicId]
 * @param {Object} [options]
 */
export class ImageTag extends HtmlTag {
    static "new"(publicId: string, options?: Transformation.Options): ImageTag;
    static "new"(name: string, publicId: string, options?: Transformation.Options): ImageTag;
}

/**
 * Creates an HTML (DOM) Picture tag using Cloudinary as the source.
 * @constructor PictureTag
 * @extends HtmlTag
 * @param {string} [publicId]
 * @param {Object} [options]
 * @param {Array<Object>} [widthList]
 */
export class PictureTag extends HtmlTag {
    static "new"(publicId: string, options?: Transformation.Options, widthList?: Array<Object>): PictureTag;
    static "new"(name: string, publicId: string, options?: Transformation.Options): PictureTag;
}

/**
 * Creates an HTML (DOM) Source tag using Cloudinary as the source.
 * @constructor SourceTag
 * @extends HtmlTag
 * @param {string} [publicId]
 * @param {Object} [options]
 */
export class SourceTag extends HtmlTag {
    static "new"(publicId: string, options?: Transformation.Options): SourceTag;
    static "new"(name: string, publicId: string, options?: Transformation.Options): SourceTag;
}

/**
 * Creates an HTML (DOM) Video tag using Cloudinary as the source.
 * @constructor VideoTag
 * @extends HtmlTag
 * @param {string} [publicId]
 * @param {Object} [options]
 */
export class VideoTag extends HtmlTag {
    static "new"(publicId: string, options?: Transformation.VideoOptions): VideoTag;
    static "new"(name: string, publicId: string, options?: Transformation.Options): VideoTag;
    /**
     * Set the transformation to apply on each source
     * @function VideoTag#setSourceTransformation
     * @param {Object} value an object with pairs of source type and source transformation
     * @returns {VideoTag} Returns this instance for chaining purposes.
     */
    setSourceTransformation(value: Object): VideoTag;

    /**
     * Set the source types to include in the video tag
     * @function VideoTag#setSourceTypes
     * @param {Array<string>} sourceTypes an array of source types
     * @returns {VideoTag} Returns this instance for chaining purposes.
     */
    setSourceTypes(sourceTypes: VideoFileExtension | Array<VideoFileExtension>): VideoTag;

    /**
     * Set the poster to be used in the video tag
     * @function VideoTag#setPoster
     * @param {string|Object} poster
     * - string: a URL to use for the poster
     * - Object: transformation parameters to apply to the poster. May optionally include a public_id to use instead of the video public_id.
     * @returns {VideoTag} Returns this instance for chaining purposes.
     */
    setPoster(poster: string | Object): VideoTag;

    /**
     * Set the content to use as fallback in the video tag
     * @function VideoTag#setFallbackContent
     * @param {string} fallbackContent - the content to use, in HTML format
     * @returns {VideoTag} Returns this instance for chaining purposes.
     */
    setFallbackContent(fallbackContent: string): VideoTag;

    /**
     * Returns the HTML for the child <source> elements of this video
     */
    content(): string;
}

/**
 * Creates an HTML (DOM) Meta tag that enables client-hints.
 * @constructor ClientHintsMetaTag
 * @extends HtmlTag
 */
export class ClientHintsMetaTag extends HtmlTag {
    constructor (options?: Transformation.Options);
}

/**************************************** Layers section ************************************/

export class Layer {
    /**
     * Layer
     * @constructor Layer
     * @param {Object} options - layer parameters
     */
    constructor(options?: Layer.Options);

    /** Setters */
    resourceType(value: string): Layer;
    type(value: string): Layer;
    publicId(value: string): Layer;
    format(value: string): Layer;
    /** Getters */
    getPublicId(): string;
    getFullPublicId(): string;
    toString(): string;
}

export namespace Layer {
    export interface Options {
        resourceType?: string;
        type?: string;
        publicId?: string;
        format?: string;
    }
}

export class FetchLayer extends Layer {
    constructor(options?: FetchLayer.Options);

    /** setters */
    url(url: string): FetchLayer;
    toString(): string;
}

export namespace FetchLayer {
    export interface Options {
        url?: string
    }
}

/**
 * @constructor TextLayer
 * @param {Object} options - layer parameters
 */
export class TextLayer extends Layer {
    constructor (options?: TextLayer.Options);

    /** Setters */
    fontFamily(value: string): TextLayer;
    fontSize(value: number): TextLayer;
    fontWeight(value: string): TextLayer;
    fontStyle(value: string): TextLayer;
    fontHinting(value: string): TextLayer;
    fontAntialiasing(value: string): TextLayer;
    textDecoration(value: string): TextLayer;
    textAlign(value: string): TextLayer;
    stroke(value: string): TextLayer;
    letterSpacing(value: number): TextLayer;
    lineSpacing(value: number): TextLayer;
    text(value: string): TextLayer;
    textStyle(value: string): TextLayer;
    /** Getters */
    toString(): string;
    textStyleIdentifier(): Array<string>;
}

export namespace TextLayer {
    export interface Options {
        resourceType?: string;
        fontFamily?: string;
        fontSize?: number;
        fontWeight?: string;
        fontStyle?: string;
        fontHinting?: string;
        fontAntialiasing?: string;
        textDecoration?: string;
        textAlign?: string;
        stroke?: string;
        letterSpacing?: number;
        lineSpacing?: number;
        text?: string;
        textStyle?: string;
    }
}

/**
 * Represent a subtitles layer
 * @constructor SubtitlesLayer
 * @param {Object} options - layer parameters
 */
export class SubtitlesLayer extends TextLayer {
    constructor (options: TextLayer.Options);
}

export class Param {
    constructor (name: string, shortName?: string, process?: (value: any) => any);

    /**
     * Set a (unprocessed) value for this parameter
     * @function Param#set
     * @param {*} origValue - the value of the parameter
     * @return {Param} self for chaining
     */
    set(origValue: any): Param;

    /**
     * Generate the serialized form of the parameter
     * @function Param#serialize
     * @return {string} the serialized form of the parameter
     */
    serialize(): string;

    /**
     * Return the processed value of the parameter
     * @function Param#value
     */
    value(): any;

    /**
     * Replaces '#' symbols with 'rgb:'
     */
    norm_color(): string;

    /**
     * Wraps this param in an array if it isn't already an array
     */
    build_array(): Array<any>
}

/**
 * Main Cloudinary class
 * @class Cloudinary
 * @param {Object} options - options to configure Cloudinary
 * @see Configuration for more details
 * @example
 *    // Include cloudinary_js in a <script> tag, then:
 *    var cl = new cloudinary.Cloudinary( { cloud_name: "mycloud"});
 *    // Or import it from the npm package:
 *    import { Cloudinary } from 'cloudinary-core';
 *    var cl = new Cloudinary( { cloud_name: "mycloud"});
 *    var imgTag = cl.image("myPicID");
 */
export class Cloudinary {
    constructor(options: Configuration.Options);

    static "new"(options: Configuration.Options): Cloudinary;
    /**
     * Generate an resource URL.
     * @function Cloudinary#url
     * @param {string} publicId - the public ID of the resource
     * @param {Object} [options] - options for the tag and transformations, possible values include all {@link Transformation} parameters
     *                          and {@link Configuration} parameters with addition of 'placeholder' and 'accessibility'
     * @param {string} [options.type='upload'] - the classification of the resource
     * @param {Object} [options.resource_type='image'] - the type of the resource
     * @return {string} The resource URL
     */
    url(publicId: string, options?: UrlOptions ): string;

    /**
     * Generate an video resource URL.
     * @function Cloudinary#video_url
     * @param {string} publicId - the public ID of the resource
     * @param {Object} [options] - options for the tag and transformations, possible values include all {@link Transformation} parameters
     *                          and {@link Configuration} parameters
     * @param {string} [options.type='upload'] - the classification of the resource
     * @return {string} The video URL
     */
    video_url(publicId: string, options?: Transformation | Transformation.VideoOptions): string;

    /**
     * Generate an image tag.
     * @function Cloudinary#image
     * @param {string} publicId - the public ID of the image
     * @param {Object} [options] - options for the tag and transformations
     * @return {HTMLImageElement} an image tag element
     */
    image(publicId: string, options?: Transformation | Transformation.Options): HTMLImageElement;

    /**
     * Generate an video thumbnail URL.
     * @function Cloudinary#video_thumbnail_url
     * @param {string} publicId - the public ID of the resource
     * @param {Object} [options] - options for the tag and transformations, possible values include all {@link Transformation} parameters
     *                          and {@link Configuration} parameters
     * @param {string} [options.type='upload'] - the classification of the resource
     * @return {string} The video thumbnail URL
     */
    video_thumbnail_url(publicId: string, options?: Transformation | Transformation.VideoOptions): string;

    /**
     * Generate a string representation of the provided transformation options.
     * @function Cloudinary#transformation_string
     * @param {Object} options - the transformation options
     * @returns {string} The transformation string
     */
    transformation_string(options: Transformation | Transformation.Options): string;

    /**
     * Generate an image tag.
     * @function Cloudinary#image
     * @param {string} publicId - the public ID of the image
     * @param {Object} [options] - options for the tag and transformations
     * @return {HTMLImageElement} an image tag element
     */
    image(publicId: string, options?: Transformation | Transformation.Options): HTMLImageElement;

    /**
     * Creates a new ImageTag instance, configured using this own's configuration.
     * @function Cloudinary#imageTag
     * @param {string} publicId - the public ID of the resource
     * @param {Object} options - additional options to pass to the new ImageTag instance
     * @return {ImageTag} An ImageTag that is attached (chained) to this Cloudinary instance
     */
    imageTag(publicId: string, options?: Transformation | Transformation.Options): ImageTag;

    /**
     * Creates a new PictureTag instance, configured using this own's configuration.
     * @function Cloudinary#pictureTag
     * @param {string} publicId - the public ID of the resource
     * @param {Object} options - additional options to pass to the new PictureTag instance
     * @param {Array<Object>} sources - the sources definitions
     * @return {PictureTag} An PictureTag that is attached (chained) to this Cloudinary instance
     */
    pictureTag(publicId: string, options?: Transformation | Transformation.Options, sources?: Array<object>): PictureTag;

    /**
     * Creates a new SourceTag instance, configured using this own's configuration.
     * @function Cloudinary#sourceTag
     * @param {string} publicId - the public ID of the resource
     * @param {Object} options - additional options to pass to the new SourceTag instance
     * @return {SourceTag} An SourceTag that is attached (chained) to this Cloudinary instance
     */
    sourceTag(publicId: string, options?: Transformation | Transformation.Options): SourceTag;

    /**
     * Generate an image tag for the video thumbnail.
     * @function Cloudinary#video_thumbnail
     * @param {string} publicId - the public ID of the video
     * @param {Object} [options] - options for the tag and transformations
     * @return {HTMLImageElement} An image tag element
     */
    video_thumbnail(publicId: string, options?: Transformation | Transformation.Options): HTMLImageElement;

    /**
     * @function Cloudinary#facebook_profile_image
     * @param {string} publicId - the public ID of the image
     * @param {Object} [options] - options for the tag and transformations
     * @return {HTMLImageElement} an image tag element
     */
    facebook_profile_image(publicId: string, options?: Transformation | Transformation.Options): HTMLImageElement;

    /**
     * @function Cloudinary#twitter_profile_image
     * @param {string} publicId - the public ID of the image
     * @param {Object} [options] - options for the tag and transformations
     * @return {HTMLImageElement} an image tag element
     */
    twitter_profile_image(publicId: string, options?: Transformation | Transformation.Options): HTMLImageElement;

    /**
     * @function Cloudinary#twitter_name_profile_image
     * @param {string} publicId - the public ID of the image
     * @param {Object} [options] - options for the tag and transformations
     * @return {HTMLImageElement} an image tag element
     */
    twitter_name_profile_image(publicId: string, options?: Transformation | Transformation.Options): HTMLImageElement;

    /**
     * @function Cloudinary#gravatar_image
     * @param {string} publicId - the public ID of the image
     * @param {Object} [options] - options for the tag and transformations
     * @return {HTMLImageElement} an image tag element
     */
    gravatar_image(publicId: string, options?: Transformation | Transformation.Options): HTMLImageElement;

    /**
     * @function Cloudinary#fetch_image
     * @param {string} publicId - the public ID of the image
     * @param {Object} [options] - options for the tag and transformations
     * @return {HTMLImageElement} an image tag element
     */
    fetch_image(publicId: string, options?: Transformation | Transformation.Options): HTMLImageElement;

    /**
     * @function Cloudinary#video
     * @param {string} publicId - the public ID of the video
     * @param {Object} [options] - options for the tag and transformations
     * @return {string} The generated <video> tag and its descendants
     */
    video(publicId: string, options?: Transformation | Transformation.VideoOptions): string;

    /**
     * Creates a new VideoTag instance, configured using this own's configuration.
     * @function Cloudinary#videoTag
     * @param {string} publicId - the public ID of the resource
     * @param {Object} options - additional options to pass to the new VideoTag instance
     * @return {VideoTag} A VideoTag that is attached (chained) to this Cloudinary instance
     */
    videoTag(publicId: string, options?: Transformation | Transformation.VideoOptions): VideoTag;

    /**
     * Generate the URL of the sprite image
     * @function Cloudinary#sprite_css
     * @param {string} publicId - the public ID of the resource
     * @param {Object} [options] - options for the tag and transformations
     * @see {@link http://cloudinary.com/documentation/sprite_generation Sprite generation}
     */
    sprite_css(publicId: string, options?: Transformation | Transformation.Options): string;

    /**
     * Initialize the responsive behaviour.<br>
     * Calls {@link Cloudinary#cloudinary_update} to modify image tags.
     * @function Cloudinary#responsive
     * @param {Object} options
     * @param {String} [options.responsive_class='cld-responsive'] - provide an alternative class used to locate img tags
     * @param {number} [options.responsive_debounce=100] - the debounce interval in milliseconds.
     * @param {boolean} [bootstrap=true] if true processes the img tags by calling cloudinary_update. When false the tags will be processed only after a resize event.
     * @see {@link Cloudinary#cloudinary_update} for additional configuration parameters
     */
    responsive(options?: Transformation | Transformation.Options, bootstrap?: boolean): void;

    /**
     * Update hidpi (dpr_auto) and responsive (w_auto) fields according to the current container size and the device pixel ratio.
     * Only images marked with the cld-responsive class have w_auto updated.
     * @function Cloudinary#cloudinary_update
     * @param {(Array|string|NodeList)} elements - the elements to modify
     * @param {Object} options
     * @param {boolean|string} [options.responsive_use_breakpoints=true]
     *  - when `true`, always use breakpoints for width
     * - when `"resize"` use exact width on first render and breakpoints on resize
     * - when `false` always use exact width
     * @param {boolean} [options.responsive] - if `true`, enable responsive on this element. Can be done by adding cld-responsive.
     * @param {boolean} [options.responsive_preserve_height] - if set to true, original css height is preserved.
     *   Should only be used if the transformation supports different aspect ratios.
     */
    cloudinary_update(elements: Array<string> | NodeList, options?: Transformation | Transformation.Options): Cloudinary;

    /**
     * Provide a transformation object, initialized with own's options, for chaining purposes.
     * @function Cloudinary#transformation
     * @param {Object} options
     * @return {Transformation}
     */
    transformation(options?: Transformation | Transformation.Options): Transformation;

    injectTransparentVideoElement(container: HTMLElement, publicId: string, options: TransparentVideoOptions): Promise<HTMLElement | {status: string, message: string}>
}


interface TransparentVideoOptions extends Transformation.Options {
    externalLibraries?: {
        [future:string]:string
    } & {
        seeThru?: string,
    }
    loop?: boolean,
    autoplay?: true,
    playsinline?: boolean,
    muted?: true,
    controls?: false,
    max_timeout_ms?: number,
    class?: string,
    poster?: string
}

declare let _default: {
    ClientHintsMetaTag: ClientHintsMetaTag,
    Cloudinary: Cloudinary,
    Condition: Condition,
    Configuration: Configuration,
    FetchLayer: FetchLayer,
    HtmlTag: HtmlTag,
    ImageTag: ImageTag,
    Layer: Layer,
    Param: Param,
    PictureTag: PictureTag,
    SourceTag: SourceTag,
    SubtitlesLayer: SubtitlesLayer,
    TextLayer: TextLayer,
    Transformation: Transformation,
    Util: Util,
    VideoTag: VideoTag
}

export default _default;

export const VERSION: string;
export namespace Configuration {
    export interface Options {
        responsive_class?: string;
        responsive_use_breakpoints?: boolean;
        responsive_debounce?: number; // The debounce interval in milliseconds, default is 100
        round_dpr?: boolean;
        secure?: boolean; // Default value is based on window.location.protocol

        api_key?: string;
        api_secret?: string;
        cdn_subdomain?: boolean;
        cloud_name?: string;
        cname?: string | null;
        private_cdn?: boolean;
        protocol?: string;
        resource_type?: string;
        responsive?: boolean;
        responsive_width?: string;
        secure_cdn_subdomain?: boolean;
        secure_distribution?: string | null;
        shorten?: string;
        type?: string;
        url_suffix?: string;
        use_root_path?: boolean;
        version?: string;

        static_image_support?: string;
        enhance_image_tag?: boolean;
        [futureKey: string]: any;
    }
}

