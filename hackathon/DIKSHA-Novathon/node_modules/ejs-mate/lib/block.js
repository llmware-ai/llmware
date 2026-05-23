'use strict';

class Block {
  constructor() {
    this.html = [];
  }

  toString() {
    return this.html.join('\n');
  }

  append(more) {
    this.html.push(more);
  }

  prepend(more) {
    this.html.unshift(more);
  }

  replace(instead) {
    this.html = [ instead ];
  }
}

module.exports = Block;
