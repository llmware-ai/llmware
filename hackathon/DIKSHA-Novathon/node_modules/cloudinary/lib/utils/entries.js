module.exports = Object.entries ? Object.entries : function (obj) {
  let ownProps = Object.keys(obj),
    i = ownProps.length,
    resArray = new Array(i); // preallocate the Array
  while (i--) {
    resArray[i] = [ownProps[i], obj[ownProps[i]]];
  }

  return resArray;
};
