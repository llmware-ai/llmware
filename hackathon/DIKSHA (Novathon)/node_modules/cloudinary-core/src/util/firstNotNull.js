/**
 * Return the first argument whose value is not null
 * @param args
 * @returns {*}
 */
let firstNotNull = function firstNotNull(...args) {
  while(args && args.length > 0) {
    let next = args.shift();
    if( next != null){
      return next;
    }
  }
  return null;
};

export default firstNotNull;
