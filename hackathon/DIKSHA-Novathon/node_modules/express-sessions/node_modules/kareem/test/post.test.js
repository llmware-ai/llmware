var assert = require('assert');
var Kareem = require('../');

describe('execPost', function() {
  var hooks;

  beforeEach(function() {
    hooks = new Kareem();
  });

  it('handles errors', function(done) {
    hooks.post('cook', function(eggs, callback) {
      callback('error!');
    });

    hooks.execPost('cook', null, [4], function(error, eggs) {
      assert.equal('error!', error);
      assert.ok(!eggs);
      done();
    });
  });

  it('multiple posts', function(done) {
    hooks.post('cook', function(eggs, callback) {
      setTimeout(
        function() {
          callback();
        },
        5);
    });

    hooks.post('cook', function(eggs, callback) {
      setTimeout(
        function() {
          callback();
        },
        5);
    });

    hooks.execPost('cook', null, [4], function(error, eggs) {
      assert.ifError(error);
      assert.equal(4, eggs);
      done();
    });
  });

  it('error posts', function(done) {
    var called = {};
    hooks.post('cook', function(eggs, callback) {
      called.first = true;
      callback();
    });

    hooks.post('cook', function(eggs, callback) {
      called.second = true;
      callback(new Error('fail'));
    });

    hooks.post('cook', function(eggs, callback) {
      assert.ok(false);
    });

    hooks.post('cook', function(error, eggs, callback) {
      called.fourth = true;
      assert.equal(error.message, 'fail');
      callback(new Error('fourth'));
    });

    hooks.post('cook', function(error, eggs, callback) {
      called.fifth = true;
      assert.equal(error.message, 'fourth');
      callback(new Error('fifth'));
    });

    hooks.execPost('cook', null, [4], function(error, eggs) {
      assert.ok(error);
      assert.equal(error.message, 'fifth');
      assert.deepEqual(called, {
        first: true,
        second: true,
        fourth: true,
        fifth: true
      });
      done();
    });
  });

  it('error posts with initial error', function(done) {
    var called = {};

    hooks.post('cook', function(eggs, callback) {
      assert.ok(false);
    });

    hooks.post('cook', function(error, eggs, callback) {
      called.second = true;
      assert.equal(error.message, 'fail');
      callback(new Error('second'));
    });

    hooks.post('cook', function(error, eggs, callback) {
      called.third = true;
      assert.equal(error.message, 'second');
      callback(new Error('third'));
    });

    hooks.post('cook', function(error, eggs, callback) {
      called.fourth = true;
      assert.equal(error.message, 'third');
      callback();
    });

    var options = { error: new Error('fail') };
    hooks.execPost('cook', null, [4], options, function(error, eggs) {
      assert.ok(error);
      assert.equal(error.message, 'third');
      assert.deepEqual(called, {
        second: true,
        third: true,
        fourth: true
      });
      done();
    });
  });
});

describe('execPostSync', function() {
  var hooks;

  beforeEach(function() {
    hooks = new Kareem();
  });

  it('executes hooks synchronously', function() {
    var execed = {};

    hooks.post('cook', function() {
      execed.first = true;
    });

    hooks.post('cook', function() {
      execed.second = true;
    });

    hooks.execPostSync('cook', null);
    assert.ok(execed.first);
    assert.ok(execed.second);
  });

  it('works with no hooks specified', function() {
    assert.doesNotThrow(function() {
      hooks.execPostSync('cook', null);
    });
  });
});
