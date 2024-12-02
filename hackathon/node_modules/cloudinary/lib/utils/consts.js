const DEFAULT_RESPONSIVE_WIDTH_TRANSFORMATION = {
  width: "auto",
  crop: "limit"
};

const DEFAULT_POSTER_OPTIONS = {
  format: 'jpg',
  resource_type: 'video'
};

const DEFAULT_VIDEO_SOURCE_TYPES = ['webm', 'mp4', 'ogv'];

const CONDITIONAL_OPERATORS = {
  "=": 'eq',
  "!=": 'ne',
  "<": 'lt',
  ">": 'gt',
  "<=": 'lte',
  ">=": 'gte',
  "&&": 'and',
  "||": 'or',
  "*": "mul",
  "/": "div",
  "+": "add",
  "-": "sub",
  "^": "pow"
};

let SIMPLE_PARAMS = [
  ["audio_codec", "ac"],
  ["audio_frequency", "af"],
  ["bit_rate", 'br'],
  ["color_space", "cs"],
  ["default_image", "d"],
  ["delay", "dl"],
  ["density", "dn"],
  ["duration", "du"],
  ["end_offset", "eo"],
  ["fetch_format", "f"],
  ["gravity", "g"],
  ["page", "pg"],
  ["prefix", "p"],
  ["start_offset", "so"],
  ["streaming_profile", "sp"],
  ["video_codec", "vc"],
  ["video_sampling", "vs"]
];

const PREDEFINED_VARS = {
  "aspect_ratio": "ar",
  "aspectRatio": "ar",
  "current_page": "cp",
  "currentPage": "cp",
  "duration": "du",
  "face_count": "fc",
  "faceCount": "fc",
  "height": "h",
  "initial_aspect_ratio": "iar",
  "initial_height": "ih",
  "initial_width": "iw",
  "initialAspectRatio": "iar",
  "initialHeight": "ih",
  "initialWidth": "iw",
  "initial_duration": "idu",
  "initialDuration": "idu",
  "page_count": "pc",
  "page_x": "px",
  "page_y": "py",
  "pageCount": "pc",
  "pageX": "px",
  "pageY": "py",
  "tags": "tags",
  "width": "w"
};

const TRANSFORMATION_PARAMS = [
  'angle',
  'aspect_ratio',
  'audio_codec',
  'audio_frequency',
  'background',
  'bit_rate',
  'border',
  'color',
  'color_space',
  'crop',
  'default_image',
  'delay',
  'density',
  'dpr',
  'duration',
  'effect',
  'end_offset',
  'fetch_format',
  'flags',
  'fps',
  'gravity',
  'height',
  'if',
  'keyframe_interval',
  'offset',
  'opacity',
  'overlay',
  'page',
  'prefix',
  'quality',
  'radius',
  'raw_transformation',
  'responsive_width',
  'size',
  'start_offset',
  'streaming_profile',
  'transformation',
  'underlay',
  'variables',
  'video_codec',
  'video_sampling',
  'width',
  'x',
  'y',
  'zoom' // + any key that starts with '$'
];

const LAYER_KEYWORD_PARAMS = {
  font_weight: "normal",
  font_style: "normal",
  text_decoration: "none",
  text_align: null,
  stroke: "none"
};

const UPLOAD_PREFIX = "https://api.cloudinary.com";

const SUPPORTED_SIGNATURE_ALGORITHMS = ["sha1", "sha256"];
const DEFAULT_SIGNATURE_ALGORITHM = "sha1";

module.exports = {
  DEFAULT_RESPONSIVE_WIDTH_TRANSFORMATION,
  DEFAULT_POSTER_OPTIONS,
  DEFAULT_VIDEO_SOURCE_TYPES,
  CONDITIONAL_OPERATORS,
  PREDEFINED_VARS,
  LAYER_KEYWORD_PARAMS,
  TRANSFORMATION_PARAMS,
  SIMPLE_PARAMS,
  UPLOAD_PREFIX,
  SUPPORTED_SIGNATURE_ALGORITHMS,
  DEFAULT_SIGNATURE_ALGORITHM
};
