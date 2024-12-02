import stringPad from "./stringPad";
let chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
let num = 0;
let map = {};

[...chars].forEach((char) => {
  let key = num.toString(2);
  key = stringPad(key, 6, '0');
  map[key] = char;
  num++;
});


/**
 * Map of six-bit binary codes to Base64 characters
 */
export default map;
