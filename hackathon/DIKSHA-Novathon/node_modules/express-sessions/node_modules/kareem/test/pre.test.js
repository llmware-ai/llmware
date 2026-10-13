var assert = require('assert');
var Kareem = require('../');

describe('execPre', function() {
  var hooks;

  beforeEach(function() {
    hooks = new Kareem();
  });

  it('handles errors with multiple pres', function(done) {
    var execed = {};

    hooks.pre('cook', function(done) {
      execed.first = true;
      done();
    });

    hooks.pre('cook', function(done) {
      execed.second = true;
      done('error!');
    });

    hooks.pre('cook', function(done) {
      execed.third = true;
      done();
    });

    hooks.execPre('cook', null, function(err) {
      assert.equal('error!', err);
      assert.equal(2, Object.keys(execed).length);
      assert.ok(execed.first);
      assert.ok(execed.second);
      done();
    });
  });

  it('handles async errors', function(done) {
    var execed = {};

    hooks.pre('cook', true, function(next, done) {
      execed.first = true;
      setTimeout(
        function() {
          done('error!');
        },
        5);

      next();
    });

    hooks.pre('cook', true, function(next, done) {
      execed.second = true;
      setTimeout(
        function() {
          done('other error!');
        },
        10);

      next();
    });

    hooks.execPre('cook', null, function(err) {
      assert.equal('error!', err);
      assert.equal(2, Object.keys(execed).length);
      assert.ok(execed.first);
      assert.ok(execed.second);
      done();
    });
  });

  it('handles async errors in next()', function(done) {
    var execed = {};

    hooks.pre('cook', true, function(next, done) {
      execed.first = true;
      setTimeout(
        function() {
          done('other error!');
        },
        15);

      next();
    });

    hooks.pre('cook', true, function(next, done) {
      execed.second = true;
      setTimeout(
        function() {
          next('error!');
          done('another error!');
        },
        5);
    });

    hooks.execPre('cook', null, function(err) {
      assert.equal('error!', err);
      assert.equal(2, Object.keys(execed).length);
      assert.ok(execed.first);
      assert.ok(execed.second);
      done();
    });
  });

  it('handles async errors in next() when already done', function(done) {
    var execed = {};

    hooks.pre('cook', true, function(next, done) {
      execed.first = true;
      setTimeout(
        function() {
          done('other error!');
        },
        5);

      next();
    });

    hooks.pre('cook', true, function(next, done) {
      execed.second = true;
      setTimeout(
        function() {
          next('error!');
          done('another error!');
        },
        25);
    });

    hooks.execPre('cook', null, function(err) {
      assert.equal('other error!', err);
      assert.equal(2, Object.keys(execed).length);
      assert.ok(execed.first);
      assert.ok(execed.second);
      done();
    });
  });

  it('async pres with clone()', function(done) {
    var execed = false;

    hooks.pre('cook', true, function(next, done) {
      execed = true;
      setTimeout(
        function() {
          done();
        },
        5);

      next();
    });

    hooks.clone().execPre('cook', null, function(err) {
      assert.ifError(err);
      assert.ok(execed);
      done();
    });
  });

  it('returns correct error when async pre errors', function(done) {
    var execed = {};

    hooks.pre('cook', true, function(next, done) {
      execed.first = true;
      setTimeout(
        function() {
          done('other error!');
        },
        5);

      next();
    });

    hooks.pre('cook', function(next) {
      execed.second = true;
      setTimeout(
        function() {
          next('error!');
        },
        15);
    });

    hooks.execPre('cook', null, function(err) {
      assert.equal('other error!', err);
      assert.equal(2, Object.keys(execed).length);
      assert.ok(execed.first);
      assert.ok(execed.second);
      done();
    });
  });

  it('lets async pres run when fully sync pres are done', function(done) {
    var execed = {};

    hooks.pre('cook', true, function(next, done) {
      execed.first = true;
      setTimeout(
        function() {
          done();
        },
        5);

      next();
    });

    hooks.pre('cook', function() {
      execed.second = true;
    });

    hooks.execPre('cook', null, function(err) {
      assert.ifError(err);
      assert.equal(2, Object.keys(execed).length);
      assert.ok(execed.first);
      assert.ok(execed.second);
      done();
    });
  });

  it('allows passing arguments to the next pre', function(done) {
    var execed = {};

    hooks.pre('cook', function(next) {
      execed.first = true;
      next(null, 'test');
    });

    hooks.pre('cook', function(next, p) {
      execed.second = true;
      assert.equal(p, 'test');
      next();
    });

    hooks.pre('cook', function(next, p) {
      execed.third = true;
      assert.ok(!p);
      next();
    });

    hooks.execPre('cook', null, function(err) {
      assert.ifError(err);
      assert.equal(3, Object.keys(execed).length);
      assert.ok(execed.first);
      assert.ok(execed.second);
      assert.ok(execed.third);
      done();
    });
  });
});

describe('execPreSync', function() {
  var hooks;

  beforeEach(function() {
    hooks = new Kareem();
  });

  it('executes hooks synchronously', function() {
    var execed = {};

    hooks.pre('cook', function() {
      execed.first = true;
    });

    hooks.pre('cook', function() {
      execed.second = true;
    });

    hooks.execPreSync('cook', null);
    assert.ok(execed.first);
    assert.ok(execed.second);
  });

  it('works with no hooks specified', function() {
    assert.doesNotThrow(function() {
      hooks.execPreSync('cook', null);
    });
  });
});
