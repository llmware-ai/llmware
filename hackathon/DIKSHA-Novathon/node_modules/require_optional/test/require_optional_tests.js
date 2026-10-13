var assert = require('assert'),
  require_optional = require('../'),
  nestedTest = require('./nestedTest');

describe('Require Optional', function() {
  describe('top level require', function() {
    it('should correctly require co library', function() {
      var promise = require_optional('es6-promise');
      assert.ok(promise);
    });

    it('should fail to require es6-promise library', function() {
      try {
        require_optional('co');
      } catch(e) {
        assert.equal('OPTIONAL_MODULE_NOT_FOUND', e.code);
        return;
      }

      assert.ok(false);
    });

    it('should ignore optional library not defined', function() {
      assert.equal(undefined, require_optional('es6-promise2'));
    });
  });

  describe('internal module file require', function() {
    it('should correctly require co library', function() {
      var Long = require_optional('bson/lib/bson/long.js');
      assert.ok(Long);
    });
  });

  describe('top level resolve', function() {
    it('should correctly use exists method', function() {
      assert.equal(false, require_optional.exists('co'));
      assert.equal(true, require_optional.exists('es6-promise'));
      assert.equal(true, require_optional.exists('bson/lib/bson/long.js'));
      assert.equal(false, require_optional.exists('es6-promise2'));
    });
  });

  describe('require_optional inside dependencies', function() {
    it('should correctly walk up module call stack searching for peerOptionalDependencies', function() {
      assert.ok(nestedTest.findPackage('bson'))
    });
    it('should return null when a package is defined in top-level package.json but not installed', function() {
      assert.equal(null, nestedTest.findPackage('es6-promise2'))
    });
    it('should error when searching for an optional dependency that is not defined in any ancestor package.json', function() {
      try {
        nestedTest.findPackage('bison')
      } catch (err) {
        assert.equal(err.message, 'no optional dependency [bison] defined in peerOptionalDependencies in any package.json')
      }
    })
  });
});
