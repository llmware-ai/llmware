const fs = require('fs');
const path = require('path');
const rimraf = require('../utils/rimraf');

class FileKeyValueStorage {
  constructor({ baseFolder } = {}) {
    this.init(baseFolder);
  }

  init(baseFolder) {
    if (baseFolder) {
      try {
        fs.accessSync(baseFolder);
        this.baseFolder = baseFolder;
      } catch (err) {
        throw err;
      }
    } else {
      if (!fs.existsSync('test_cache')) {
        fs.mkdirSync('test_cache');
      }
      this.baseFolder = fs.mkdtempSync('test_cache/cloudinary_cache_');
      console.info("Created temporary cache folder at " + this.baseFolder);
    }
  }

  get(key) {
    let value = fs.readFileSync(this.getFilename(key));
    try {
      return JSON.parse(value);
    } catch (e) {
      throw "Cannot parse cache value";
    }
  }

  set(key, value) {
    fs.writeFileSync(this.getFilename(key), JSON.stringify(value));
  }

  clear() {
    let files = fs.readdirSync(this.baseFolder);
    files.forEach(file => fs.unlinkSync(path.join(this.baseFolder, file)));
  }

  deleteBaseFolder() {
    rimraf(this.baseFolder);
  }

  getFilename(key) {
    return path.format({ name: key, base: key, ext: '.json', dir: this.baseFolder });
  }
}

module.exports = FileKeyValueStorage;
