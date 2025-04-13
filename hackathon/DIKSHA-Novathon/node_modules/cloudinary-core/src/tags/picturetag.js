import HtmlTag from './htmltag';
import ImageTag from './imagetag';
import Transformation from '../transformation';
import SourceTag from './sourcetag';
import {extractUrlParams} from "../util";

class PictureTag extends HtmlTag {
  constructor(publicId, options = {}, sources = []) {
    super('picture', publicId, options);
    this.widthList = sources;
  }

  /** @override */
  content() {
    return this.widthList.map(({min_width, max_width, transformation}) => {
      let options = this.getOptions();
      let sourceTransformation = new Transformation(options);
      sourceTransformation.chain().fromOptions(typeof transformation === 'string' ? {
        raw_transformation: transformation
      } : transformation);
      options = extractUrlParams(options);
      options.media = {min_width, max_width};
      options.transformation = sourceTransformation;
      return new SourceTag(this.publicId, options).toHtml();
    }).join('') +
      new ImageTag(this.publicId, this.getOptions()).toHtml();
  }

  /** @override */
  attributes() {

    let attr = super.attributes();
    delete attr.width;
    delete attr.height;
    return attr;
  }

  /** @override */
  closeTag() {
    return "</" + this.name + ">";
  }

};

export default PictureTag;
