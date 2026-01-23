import Expression from './expression';

/**
 * Represents a transformation condition.
 * @param {string} conditionStr - a condition in string format
 * @class Condition
 * @example
 * // normally this class is not instantiated directly
 * var tr = cloudinary.Transformation.new()
 *    .if().width( ">", 1000).and().aspectRatio("<", "3:4").then()
 *      .width(1000)
 *      .crop("scale")
 *    .else()
 *      .width(500)
 *      .crop("scale")
 *
 * var tr = cloudinary.Transformation.new()
 *    .if("w > 1000 and aspectRatio < 3:4")
 *      .width(1000)
 *      .crop("scale")
 *    .else()
 *      .width(500)
 *      .crop("scale")
 *
 */
class Condition extends Expression {
  constructor(conditionStr) {
    super(conditionStr);
  }

  /**
   * @function Condition#height
   * @param {string} operator the comparison operator (e.g. "<", "lt")
   * @param {string|number} value the right hand side value
   * @return {Condition} this condition
   */
  height(operator, value) {
    return this.predicate("h", operator, value);
  }

  /**
   * @function Condition#width
   * @param {string} operator the comparison operator (e.g. "<", "lt")
   * @param {string|number} value the right hand side value
   * @return {Condition} this condition
   */
  width(operator, value) {
    return this.predicate("w", operator, value);
  }

  /**
   * @function Condition#aspectRatio
   * @param {string} operator the comparison operator (e.g. "<", "lt")
   * @param {string|number} value the right hand side value
   * @return {Condition} this condition
   */
  aspectRatio(operator, value) {
    return this.predicate("ar", operator, value);
  }

  /**
   * @function Condition#pages
   * @param {string} operator the comparison operator (e.g. "<", "lt")
   * @param {string|number} value the right hand side value
   * @return {Condition} this condition
   */
  pageCount(operator, value) {
    return this.predicate("pc", operator, value);
  }

  /**
   * @function Condition#faces
   * @param {string} operator the comparison operator (e.g. "<", "lt")
   * @param {string|number} value the right hand side value
   * @return {Condition} this condition
   */
  faceCount(operator, value) {
    return this.predicate("fc", operator, value);
  }

  /**
   * @function Condition#duration
   * @param {string} operator the comparison operator (e.g. "<", "lt")
   * @param {string|number} value the right hand side value
   * @return {Condition} this condition
   */
  duration(operator, value) {
    return this.predicate("du", operator, value);
  }

  /**
   * @function Condition#initialDuration
   * @param {string} operator the comparison operator (e.g. "<", "lt")
   * @param {string|number} value the right hand side value
   * @return {Condition} this condition
   */
  initialDuration(operator, value) {
    return this.predicate("idu", operator, value);
  }
}

export default Condition;
