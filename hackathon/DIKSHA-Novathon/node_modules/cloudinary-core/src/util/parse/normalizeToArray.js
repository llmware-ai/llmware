import {isArray, isString} from "./util";


/**
 * @desc normalize elements, support a single element, array or nodelist, always outputs array
 * @param elements<HTMLElement[]>
 * @returns {[]}
 */
export function normalizeToArray(elements) {
  if (isArray(elements)) {
    return elements;
  } else if (elements.constructor.name === "NodeList") {
    return [...elements]; // ensure an array is always returned, even if nodelist
  } else if (isString(elements)) {
    return Array.prototype.slice.call(document.querySelectorAll(elements), 0);
  } else {
    return [elements];
  }
}

