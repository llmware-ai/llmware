/**
 * Creates the namespace for Cloudinary
 */
import utf8_encode from '../utf8_encode';
import crc32 from '../crc32';
import * as Util from '../util';
import Transformation from '../transformation';
import Condition from '../condition';
import Configuration from '../configuration';
import Expression from "../expression";
import HtmlTag from '../tags/htmltag';
import ImageTag from '../tags/imagetag';
import PictureTag from '../tags/picturetag';
import VideoTag from '../tags/videotag';
import ClientHintsMetaTag from '../tags/clienthintsmetatag';
import Layer from '../layer/layer';
import FetchLayer from '../layer/fetchlayer';
import TextLayer from '../layer/textlayer';
import SubtitlesLayer from '../layer/subtitleslayer';
import Cloudinary from '../cloudinary';

export default {
  ClientHintsMetaTag,
  Cloudinary,
  Condition,
  Configuration,
  crc32,
  Expression,
  FetchLayer,
  HtmlTag,
  ImageTag,
  Layer,
  PictureTag,
  SubtitlesLayer,
  TextLayer,
  Transformation,
  utf8_encode,
  Util,
  VideoTag
};

export {
  ClientHintsMetaTag,
  Cloudinary,
  Condition,
  Configuration,
  crc32,
  Expression,
  FetchLayer,
  HtmlTag,
  ImageTag,
  Layer,
  PictureTag,
  SubtitlesLayer,
  TextLayer,
  Transformation,
  utf8_encode,
  Util,
  VideoTag
};
