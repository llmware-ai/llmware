# kareem

  [![Build Status](https://travis-ci.org/vkarpov15/kareem.svg?branch=master)](https://travis-ci.org/vkarpov15/kareem)
  [![Coverage Status](https://img.shields.io/coveralls/vkarpov15/kareem.svg)](https://coveralls.io/r/vkarpov15/kareem)

Re-imagined take on the [hooks](http://npmjs.org/package/hooks) module, meant to offer additional flexibility in allowing you to execute hooks whenever necessary, as opposed to simply wrapping a single function.

Named for the NBA's all-time leading scorer Kareem Abdul-Jabbar, known for his mastery of the [hook shot](http://en.wikipedia.org/wiki/Kareem_Abdul-Jabbar#Skyhook)

<img src="http://upload.wikimedia.org/wikipedia/commons/0/00/Kareem-Abdul-Jabbar_Lipofsky.jpg" width="220">

# API

## pre hooks

Much like [hooks](https://npmjs.org/package/hooks), kareem lets you define
pre and post hooks: pre hooks are called before a given function executes.
Unlike hooks, kareem stores hooks and other internal state in a separate
object, rather than relying on inheritance. Furthermore, kareem exposes
an `execPre()` function that allows you to execute your pre hooks when
appropriate, giving you more fine-grained control over your function hooks.


#### It runs without any hooks specified

```javascript
    
    hooks.execPre('cook', null, function() {
      done();
    });
  
```

#### It runs basic serial pre hooks

pre hook functions take one parameter, a "done" function that you execute
when your pre hook is finished.


```javascript
    
    var count = 0;

    hooks.pre('cook', function(done) {
      ++count;
      done();
    });

    hooks.execPre('cook', null, function() {
      assert.equal(1, count);
      done();
    });
  
```

#### It can run multipe pre hooks

```javascript
    
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
  
```

#### It can run fully synchronous pre hooks

If your pre hook function takes no parameters, its assumed to be
fully synchronous.


```javascript
    
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
  
```

#### It properly attaches context to pre hooks

Pre save hook functions are bound to the second parameter to `execPre()`


```javascript
    
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
  
```

#### It can execute parallel (async) pre hooks

Like the hooks module, you can declare "async" pre hooks - these take two
parameters, the functions `next()` and `done()`. `next()` passes control to
the next pre hook, but the underlying function won't be called until all
async pre hooks have called `done()`.


```javascript
    
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
  
```

## post hooks

#### It runs without any hooks specified

```javascript
    
    hooks.execPost('cook', null, [1], function(error, eggs) {
      assert.ifError(error);
      assert.equal(1, eggs);
      done();
    });
  
```

#### It executes with parameters passed in

```javascript
    
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
  
```

#### It can use synchronous post hooks

```javascript
    
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
  
```

## wrap()

#### It wraps pre and post calls into one call

```javascript
    
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
  
```

## createWrapper()

#### It wraps wrap() into a callable function

```javascript
    
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
  
```

## clone()

#### It clones a Kareem object

```javascript
    
    var k1 = new Kareem();
    k1.pre('cook', function() {});
    k1.post('cook', function() {});

    var k2 = k1.clone();
    assert.deepEqual(['cook'], Object.keys(k2._pres));
    assert.deepEqual(['cook'], Object.keys(k2._posts));
  
```

