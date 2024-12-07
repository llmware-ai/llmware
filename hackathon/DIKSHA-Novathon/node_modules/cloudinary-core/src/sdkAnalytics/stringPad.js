export default function stringPad(value, targetLength,padString) {
  targetLength = targetLength>>0; //truncate if number or convert non-number to 0;
  padString = String((typeof padString !== 'undefined' ? padString : ' '));
  if (value.length > targetLength) {
    return String(value);
  }
  else {
    targetLength = targetLength-value.length;
    if (targetLength > padString.length) {
      padString += repeatStringNumTimes(padString, targetLength/padString.length);
    }
    return padString.slice(0,targetLength) + String(value);
  }
}

function repeatStringNumTimes(string, times) {
  var repeatedString = "";
  while (times > 0) {
    repeatedString += string;
    times--;
  }
  return repeatedString;
}
