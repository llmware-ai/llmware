var assert = require('assert');
var Kareem = require('../');

/* Much like [hooks](https://npmjs.org/package/hooks), kareem lets you define
 * pre and post hooks: pre hooks are called before a given function executes.
 * Unlike hooks, kareem stores hooks and other internal state in a separate
 * object, rather than relying on inheritance. Furthermore, kareem exposes
 * an `execPre()` function that allows you to execute your pre hooks when
 * appropriate, giving you more fine-grained control over your function hooks.
 */
describe('pre hooks', function() {
  var hooks;

  beforeEach(function() {
    hooks = new Kareem();
  });

  it('runs without any hooks specified', function(done) {
    hooks.execPre('cook', null, function() {
      done();
    });
  });

  /* pre hook functions take one parameter, a "done" function that you execute
   * when your pre hook is finished.
   */
  it('runs basic serial pre hooks', function(done) {
    var count = 0;

    hooks.pre('cook', function(done) {
      ++count;
      done();
    });

    hooks.execPre('cook', null, function() {
      assert.equal(1, count);
      done();
    });
  });

  it('can run multipe pre hooks', function(done) {
    var count1 = 0;
    var count2 = 0;

    hooks.pre('cook', function(done) {
      ++count1;
      done();
    });

    hooks.pre('cook', function(done) {
      ++count2;
      done();
    });

    hooks.execPre('cook', null, function() {
      assert.equal(1, count1);
      assert.equal(1, count2);
      done();
    });
  });

  /* If your pre hook function takes no parameters, its assumed to be
   * fully synchronous.
   */
  it('can run fully synchronous pre hooks', function(done) {
    var count1 = 0;
    var count2 = 0;

    hooks.pre('cook', function() {
      ++count1;
    });

    hooks.pre('cook', function() {
      ++count2;
    });

    hooks.execPre('cook', null, function(error) {
      assert.equal(null, error);
      assert.equal(1, count1);
      assert.equal(1, count2);
      done();
    });
  });

  /* Pre save hook functions are bound to the second parameter to `execPre()`
   */
  it('properly attaches context to pre hooks', function(done) {
    hooks.pre('cook', function(done) {
      this.bacon = 3;
      done();
    });

    hooks.pre('cook', function(done) {
      this.eggs = 4;
      done();
    });

    var obj = { bacon: 0, eggs: 0 };

    // In the pre hooks, `this` will refer to `obj`
    hooks.execPre('cook', obj, function(error) {
      assert.equal(null, error);
      assert.equal(3, obj.bacon);
      assert.equal(4, obj.eggs);
      done();
    });
  });

  /* Like the hooks module, you can declare "async" pre hooks - these take two
   * parameters, the functions `next()` and `done()`. `next()` passes control to
   * the next pre hook, but the underlying function won't be called until all
   * async pre hooks have called `done()`.
   */
  it('can execute parallel (async) pre hooks', function(done) {
    hooks.pre('cook', true, function(next, done) {
      this.bacon = 3;
      next();
      setTimeout(function() {
        done();
      }, 5);
    });

    hooks.pre('cook', true, function(next, done) {
      next();
      var _this = this;
      setTimeout(function() {
        _this.eggs = 4;
        done();
      }, 10);
    });

    hooks.pre('cook', function(next) {
      this.waffles = false;
      next();
    });

    var obj = { bacon: 0, eggs: 0 };

    hooks.execPre('cook', obj, function() {
      assert.equal(3, obj.bacon);
      assert.equal(4, obj.eggs);
      assert.equal(false, obj.waffles);
      done();
    });
  });
});

describe('post hooks', function() {
  var hooks;

  beforeEach(function() {
    hooks = new Kareem();
  });

  it('runs without any hooks specified', function(done) {
    hooks.execPost('cook', null, [1], function(error, eggs) {
      assert.ifError(error);
      assert.equal(1, eggs);
      done();
    });
  });

  it('executes with parameters passed in', function(done) {
    hooks.post('cook', function(eggs, bacon, callback) {
      assert.equal(1, eggs);
      assert.equal(2, bacon);
      callback();
    });

    hooks.execPost('cook', null, [1, 2], function(error, eggs, bacon) {
      assert.ifError(error);
      assert.equal(1, eggs);
      assert.equal(2, bacon);
      done();
    });
  });

  it('can use synchronous post hooks', function(done) {
    var execed = {};

    hooks.post('cook', function(eggs, bacon) {
      execed.first = true;
      assert.equal(1, eggs);
      assert.equal(2, bacon);
    });

    hooks.post('cook', function(eggs, bacon, callback) {
      execed.second = true;
      assert.equal(1, eggs);
      assert.equal(2, bacon);
      callback();
    });

    hooks.execPost('cook', null, [1, 2], function(error, eggs, bacon) {
      assert.ifError(error);
      assert.equal(2, Object.keys(execed).length);
      assert.ok(execed.first);
      assert.ok(execed.second);
      assert.equal(1, eggs);
      assert.equal(2, bacon);
      done();
    });
  });
});

describe('wrap()', function() {
  var hooks;

  beforeEach(function() {
    hooks = new Kareem();
  });

  it('wraps pre and post calls into one call', function(done) {
    hooks.pre('cook', true, function(next, done) {
      this.bacon = 3;
      next();
      setTimeout(function() {
        done();
      }, 5);
    });

    hooks.pre('cook', true, function(next, done) {
      next();
      var _this = this;
      setTimeout(function() {
        _this.eggs = 4;
        done();
      }, 10);
    });

    hooks.pre('cook', function(next) {
      this.waffles = false;
      next();
    });

    hooks.post('cook', function(obj) {
      obj.tofu = 'no';
    });

    var obj = { bacon: 0, eggs: 0 };

    var args = [obj];
    args.push(function(error, result) {
      assert.ifError(error);
      assert.equal(null, error);
      assert.equal(3, obj.bacon);
      assert.equal(4, obj.eggs);
      assert.equal(false, obj.waffles);
      assert.equal('no', obj.tofu);

      assert.equal(obj, result);
      done();
    });

    hooks.wrap(
      'cook',
      function(o, callback) {
        assert.equal(3, obj.bacon);
        assert.equal(4, obj.eggs);
        assert.equal(false, obj.waffles);
        assert.equal(undefined, obj.tofu);
        callback(null, o);
      },
      obj,
      args);
  });
});

describe('createWrapper()', function() {
  var hooks;

  beforeEach(function() {
    hooks = new Kareem();
  });

  it('wraps wrap() into a callable function', function(done) {
    hooks.pre('cook', true, function(next, done) {
      this.bacon = 3;
      next();
      setTimeout(function() {
        done();
      }, 5);
    });

    hooks.pre('cook', true, function(next, done) {
      next();
      var _this = this;
      setTimeout(function() {
        _this.eggs = 4;
        done();
      }, 10);
    });

    hooks.pre('cook', function(next) {
      this.waffles = false;
      next();
    });

    hooks.post('cook', function(obj) {
      obj.tofu = 'no';
    });

    var obj = { bacon: 0, eggs: 0 };

    var cook = hooks.createWrapper(
      'cook',
      function(o, callback) {
        assert.equal(3, obj.bacon);
        assert.equal(4, obj.eggs);
        assert.equal(false, obj.waffles);
        assert.equal(undefined, obj.tofu);
        callback(null, o);
      },
      obj);

    cook(obj, function(error, result) {
      assert.ifError(error);
      assert.equal(3, obj.bacon);
      assert.equal(4, obj.eggs);
      assert.equal(false, obj.waffles);
      assert.equal('no', obj.tofu);

      assert.equal(obj, result);
      done();
    });
  });
});

describe('clone()', function() {
  it('clones a Kareem object', function() {
    var k1 = new Kareem();
    k1.pre('cook', function() {});
    k1.post('cook', function() {});

    var k2 = k1.clone();
    assert.deepEqual(['cook'], Object.keys(k2._pres));
    assert.deepEqual(['cook'], Object.keys(k2._posts));
  });
});

describe('merge()', function() {
  it('pulls hooks from another Kareem object', function() {
    var k1 = new Kareem();
    var test1 = function() {};
    k1.pre('cook', test1);
    k1.post('cook', function() {});

    var k2 = new Kareem();
    var test2 = function() {};
    k2.pre('cook', test2);
    var k3 = k2.merge(k1);
    assert.equal(k3._pres['cook'].length, 2);
    assert.equal(k3._pres['cook'][0].fn, test2);
    assert.equal(k3._pres['cook'][1].fn, test1);
    assert.equal(k3._posts['cook'].length, 1);
  });
});
