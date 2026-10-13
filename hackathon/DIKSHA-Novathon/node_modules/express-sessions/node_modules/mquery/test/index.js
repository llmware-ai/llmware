var mquery = require('../');
var assert = require('assert');

describe('mquery', function(){
  var col;

  before(function(done){
    // get the env specific collection interface
    require('./env').getCollection(function (err, collection) {
      assert.ifError(err);
      col = collection;
      done();
    });
  })

  after(function(done){
    require('./env').dropCollection(done);
  })

  describe('mquery', function(){
    it('is a function', function(){
      assert.equal('function', typeof mquery);
    })
    it('creates instances with the `new` keyword', function(){
      assert.ok(mquery() instanceof mquery);
    })
    describe('defaults', function(){
      it('are set', function(){
        var m = mquery();
        assert.strictEqual(undefined, m.op);
        assert.deepEqual({}, m.options);
      })
    })
    describe('criteria', function(){
      it('if collection-like is used as collection', function(){
        var m = mquery(col);
        assert.equal(col, m._collection.collection);
      })
      it('non-collection-like is used as criteria', function(){
        var m = mquery({ works: true });
        assert.ok(!m._collection);
        assert.deepEqual({ works: true }, m._conditions);
      })
    })
    describe('options', function(){
      it('are merged when passed', function(){
        var m = mquery(col, { safe: true });
        assert.deepEqual({ safe: true }, m.options);
        var m = mquery({ name: 'mquery' }, { safe: true });
        assert.deepEqual({ safe: true }, m.options);
      })
    })
  })

  describe('toConstructor', function(){
    it('creates subclasses of mquery', function(){
      var opts = { safe: { w: 'majority' }, readPreference: 'p' };
      var match = { name: 'test', count: { $gt: 101 }};
      var select = { name: 1, count: 0 }
      var update = { $set: { x: true }};
      var path = 'street';

      var q = mquery().setOptions(opts);
      q.where(match);
      q.select(select);
      q.update(update);
      q.where(path);
      q.find();

      var M = q.toConstructor();
      var m = M();

      assert.ok(m instanceof mquery);
      assert.deepEqual(opts, m.options);
      assert.deepEqual(match, m._conditions);
      assert.deepEqual(select, m._fields);
      assert.deepEqual(update, m._update);
      assert.equal(path, m._path);
      assert.equal('find', m.op);
    })
  })

  describe('setOptions', function(){
    it('calls associated methods', function(){
      var m = mquery();
      assert.equal(m._collection, null);
      m.setOptions({ collection: col });
      assert.equal(m._collection.collection, col);
    })
    it('directly sets option when no method exists', function(){
      var m = mquery();
      assert.equal(m.options.woot, null);
      m.setOptions({ woot: 'yay' });
      assert.equal(m.options.woot, 'yay');
    })
    it('is chainable', function(){
      var m = mquery();
      var n = m.setOptions();
      assert.equal(m, n);
      var n = m.setOptions({ x: 1 });
      assert.equal(m, n);
    })
  })

  describe('collection', function(){
    it('sets the _collection', function(){
      var m = mquery();
      m.collection(col);
      assert.equal(m._collection.collection, col);
    })
    it('is chainable', function(){
      var m = mquery();
      var n = m.collection(col);
      assert.equal(m, n);
    })
  })

  describe('$where', function(){
    it('sets the $where condition', function(){
      var m = mquery();
      function go () {}
      m.$where(go);
      assert.ok(go === m._conditions.$where);
    })
    it('is chainable', function(){
      var m = mquery();
      var n = m.$where('x');
      assert.equal(m, n);
    })
  })

  describe('where', function(){
    it('without arguments', function(){
      var m = mquery();
      m.where();
      assert.deepEqual({}, m._conditions);
    })
    it('with non-string/object argument', function(){
      var m = mquery();

      assert.throws(function(){
        m.where([]);
      }, /path must be a string or object/);
    })
    describe('with one argument', function(){
      it('that is an object', function(){
        var m = mquery();
        m.where({ name: 'flawed' });
        assert.strictEqual(m._conditions.name, 'flawed');
      })
      it('that is a query', function(){
        var m = mquery({ name: 'first' });
        var n = mquery({ name: 'changed' });
        m.where(n);
        assert.strictEqual(m._conditions.name, 'changed');
      })
      it('that is a string', function(){
        var m = mquery();
        m.where('name');
        assert.equal('name', m._path);
        assert.strictEqual(m._conditions.name, undefined);
      })
    })
    it('with two arguments', function(){
      var m = mquery();
      m.where('name', 'The Great Pumpkin');
      assert.equal('name', m._path);
      assert.strictEqual(m._conditions.name, 'The Great Pumpkin');
    })
    it('is chainable', function(){
      var m = mquery();
      var n = m.where('x', 'y');
      assert.equal(m, n);
      var n = m.where()
      assert.equal(m, n);
    })
  })
  describe('equals', function(){
    it('must be called after where()', function(){
      var m = mquery();
      assert.throws(function () {
        m.equals();
      }, /must be used after where/)
    })
    it('sets value of path set with where()', function(){
      var m = mquery();
      m.where('age').equals(1000);
      assert.deepEqual({ age: 1000 }, m._conditions);
    })
    it('is chainable', function(){
      var m = mquery();
      var n = m.where('x').equals(3);
      assert.equal(m, n);
    })
  })
  describe('eq', function(){
    it('is alias of equals', function(){
      var m = mquery();
      m.where('age').eq(1000);
      assert.deepEqual({ age: 1000 }, m._conditions);
    })
  })
  describe('or', function(){
    it('pushes onto the internal $or condition', function(){
      var m = mquery();
      m.or({ 'Nightmare Before Christmas': true });
      assert.deepEqual([{'Nightmare Before Christmas': true }], m._conditions.$or)
    })
    it('allows passing arrays', function(){
      var m = mquery();
      var arg = [{ 'Nightmare Before Christmas': true }, { x: 1 }];
      m.or(arg);
      assert.deepEqual(arg, m._conditions.$or)
    })
    it('allows calling multiple times', function(){
      var m = mquery();
      var arg = [{ looper: true }, { x: 1 }];
      m.or(arg);
      m.or({ y: 1 })
      m.or([{ w: 'oo' }, { z: 'oo'} ])
      assert.deepEqual([{looper:true},{x:1},{y:1},{w:'oo'},{z:'oo'}], m._conditions.$or)
    })
    it('is chainable', function(){
      var m = mquery();
      m.or({ o: "k"}).where('name', 'table');
      assert.deepEqual({ name: 'table', $or: [{ o: 'k' }] }, m._conditions)
    })
  })

  describe('nor', function(){
    it('pushes onto the internal $nor condition', function(){
      var m = mquery();
      m.nor({ 'Nightmare Before Christmas': true });
      assert.deepEqual([{'Nightmare Before Christmas': true }], m._conditions.$nor)
    })
    it('allows passing arrays', function(){
      var m = mquery();
      var arg = [{ 'Nightmare Before Christmas': true }, { x: 1 }];
      m.nor(arg);
      assert.deepEqual(arg, m._conditions.$nor)
    })
    it('allows calling multiple times', function(){
      var m = mquery();
      var arg = [{ looper: true }, { x: 1 }];
      m.nor(arg);
      m.nor({ y: 1 })
      m.nor([{ w: 'oo' }, { z: 'oo'} ])
      assert.deepEqual([{looper:true},{x:1},{y:1},{w:'oo'},{z:'oo'}], m._conditions.$nor)
    })
    it('is chainable', function(){
      var m = mquery();
      m.nor({ o: "k"}).where('name', 'table');
      assert.deepEqual({ name: 'table', $nor: [{ o: 'k' }] }, m._conditions)
    })
  })

  describe('and', function(){
    it('pushes onto the internal $and condition', function(){
      var m = mquery();
      m.and({ 'Nightmare Before Christmas': true });
      assert.deepEqual([{'Nightmare Before Christmas': true }], m._conditions.$and)
    })
    it('allows passing arrays', function(){
      var m = mquery();
      var arg = [{ 'Nightmare Before Christmas': true }, { x: 1 }];
      m.and(arg);
      assert.deepEqual(arg, m._conditions.$and)
    })
    it('allows calling multiple times', function(){
      var m = mquery();
      var arg = [{ looper: true }, { x: 1 }];
      m.and(arg);
      m.and({ y: 1 })
      m.and([{ w: 'oo' }, { z: 'oo'} ])
      assert.deepEqual([{looper:true},{x:1},{y:1},{w:'oo'},{z:'oo'}], m._conditions.$and)
    })
    it('is chainable', function(){
      var m = mquery();
      m.and({ o: "k"}).where('name', 'table');
      assert.deepEqual({ name: 'table', $and: [{ o: 'k' }] }, m._conditions)
    })
  })

  function generalCondition (type) {
    return function () {
      it('accepts 2 args', function(){
        var m = mquery()[type]('count', 3);
        var check = {};
        check['$' + type] = 3;
        assert.deepEqual(m._conditions.count, check);
      })
      it('uses previously set `where` path if 1 arg passed', function(){
        var m = mquery().where('count')[type](3);
        var check = {};
        check['$' + type] = 3;
        assert.deepEqual(m._conditions.count, check);
      })
      it('throws if 1 arg was passed but no previous `where` was used', function(){
        assert.throws(function(){
          mquery()[type](3);
        }, /must be used after where/);
      })
      it('is chainable', function(){
        var m = mquery().where('count')[type](3).where('x', 8);
        var check = {x: 8, count: {}};
        check.count['$' + type] = 3;
        assert.deepEqual(m._conditions, check);
      })
      it('overwrites previous value', function(){
        var m = mquery().where('count')[type](3)[type](8);
        var check = {};
        check['$' + type] = 8;
        assert.deepEqual(m._conditions.count, check);
      })
    }
  }

  'gt gte lt lte ne in nin regex size maxDistance minDistance'.split(' ').forEach(function (type) {
    describe(type, generalCondition(type))
  })

  describe('mod', function () {
    describe('with 1 argument', function(){
      it('requires a previous where()', function(){
        assert.throws(function () {
          mquery().mod([30, 10])
        }, /must be used after where/);
      })
      it('works', function(){
        var m = mquery().where('madmen').mod([10,20]);
        assert.deepEqual(m._conditions, { madmen: { $mod: [10,20] }})
      })
    })

    describe('with 2 arguments and second is non-Array', function(){
      it('requires a previous where()', function(){
        assert.throws(function () {
          mquery().mod('x', 10)
        }, /must be used after where/);
      })
      it('works', function(){
        var m = mquery().where('madmen').mod(10, 20);
        assert.deepEqual(m._conditions, { madmen: { $mod: [10,20] }})
      })
    })

    it('with 2 arguments and second is an array', function(){
      var m = mquery().mod('madmen', [10,20]);
      assert.deepEqual(m._conditions, { madmen: { $mod: [10,20] }})
    })

    it('with 3 arguments', function(){
      var m = mquery().mod('madmen', 10, 20);
      assert.deepEqual(m._conditions, { madmen: { $mod: [10,20] }})
    })

    it('is chainable', function(){
      var m = mquery().mod('madmen', 10, 20).where('x', 8);
      var check = { madmen: { $mod: [10,20] }, x: 8};
      assert.deepEqual(m._conditions, check);
    })
  })

  describe('exists', function(){
    it('with 0 args', function(){
      it('throws if not used after where()', function(){
        assert.throws(function () {
          mquery().exists()
        }, /must be used after where/);
      })
      it('works', function(){
        var m = mquery().where('name').exists();
        var check = { name: { $exists: true }};
        assert.deepEqual(m._conditions, check);
      })
    })

    describe('with 1 arg', function(){
      describe('that is boolean', function(){
        it('throws if not used after where()', function(){
          assert.throws(function () {
            mquery().exists()
          }, /must be used after where/);
        })
        it('works', function(){
          var m = mquery().exists('name', false);
          var check = { name: { $exists: false }};
          assert.deepEqual(m._conditions, check);
        })
      })
      describe('that is not boolean', function(){
        it('sets the value to `true`', function(){
          var m = mquery().where('name').exists('yummy');
          var check = { yummy: { $exists: true }};
          assert.deepEqual(m._conditions, check);
        })
      })
    })

    describe('with 2 args', function(){
      it('works', function(){
        var m = mquery().exists('yummy', false);
        var check = { yummy: { $exists: false }};
        assert.deepEqual(m._conditions, check);
      })
    })

    it('is chainable', function(){
      var m = mquery().where('name').exists().find({ x: 1 });
      var check = { name: { $exists: true }, x: 1};
      assert.deepEqual(m._conditions, check);
    })
  })

  describe('elemMatch', function(){
    describe('with null/undefined first argument', function(){
      assert.throws(function () {
        mquery().elemMatch();
      }, /Invalid argument/);
      assert.throws(function () {
        mquery().elemMatch(null);
      }, /Invalid argument/);
      assert.doesNotThrow(function () {
        mquery().elemMatch('', {});
      });
    })

    describe('with 1 argument', function(){
      it('throws if not a function or object', function(){
        assert.throws(function () {
          mquery().elemMatch([]);
        }, /Invalid argument/);
      })

      describe('that is an object', function(){
        it('throws if no previous `where` was used', function(){
          assert.throws(function () {
            mquery().elemMatch({});
          }, /must be used after where/);
        })
        it('works', function(){
          var m = mquery().where('comment').elemMatch({ author: 'joe', votes: {$gte: 3 }});
          assert.deepEqual({ comment: { $elemMatch: { author: 'joe', votes: {$gte: 3}}}}, m._conditions);
        })
      })
      describe('that is a function', function(){
        it('throws if no previous `where` was used', function(){
          assert.throws(function () {
            mquery().elemMatch(function(){});
          }, /must be used after where/);
        })
        it('works', function(){
          var m = mquery().where('comment').elemMatch(function (query) {
            query.where({ author: 'joe', votes: {$gte: 3 }})
          });
          assert.deepEqual({ comment: { $elemMatch: { author: 'joe', votes: {$gte: 3}}}}, m._conditions);
        })
      })
    })

    describe('with 2 arguments', function(){
      describe('and the 2nd is an object', function(){
        it('works', function(){
          var m = mquery().elemMatch('comment', { author: 'joe', votes: {$gte: 3 }});
          assert.deepEqual({ comment: { $elemMatch: { author: 'joe', votes: {$gte: 3}}}}, m._conditions);
        })
      })
      describe('and the 2nd is a function', function(){
        it('works', function(){
          var m = mquery().elemMatch('comment', function (query) {
            query.where({ author: 'joe', votes: {$gte: 3 }})
          });
          assert.deepEqual({ comment: { $elemMatch: { author: 'joe', votes: {$gte: 3}}}}, m._conditions);
        })
      })
      it('and the 2nd is not a function or object', function(){
        assert.throws(function () {
          mquery().elemMatch('comment', []);
        }, /Invalid argument/);
      })
    })
  })

  describe('within', function(){
    it('is chainable', function(){
      var m = mquery();
      assert.equal(m.where('a').within(), m);
    })
    describe('when called with arguments', function(){
      it('must follow where()', function(){
        assert.throws(function () {
          mquery().within([]);
        }, /must be used after where/);
      })

      describe('of length 1', function(){
        it('throws if not a recognized shape', function(){
          assert.throws(function () {
            mquery().where('loc').within({});
          }, /Invalid argument/)
          assert.throws(function () {
            mquery().where('loc').within(null);
          }, /Invalid argument/)
        })
        it('delegates to circle when center exists', function(){
          var m = mquery().where('loc').within({ center: [10,10], radius: 3 });
          assert.deepEqual({ $geoWithin: {$center:[[10,10], 3]}}, m._conditions.loc);
        })
        it('delegates to box when exists', function(){
          var m = mquery().where('loc').within({ box: [[10,10], [11,14]] });
          assert.deepEqual({ $geoWithin: {$box:[[10,10], [11,14]]}}, m._conditions.loc);
        })
        it('delegates to polygon when exists', function(){
          var m = mquery().where('loc').within({ polygon: [[10,10], [11,14],[10,9]] });
          assert.deepEqual({ $geoWithin: {$polygon:[[10,10], [11,14],[10,9]]}}, m._conditions.loc);
        })
        it('delegates to geometry when exists', function(){
          var m = mquery().where('loc').within({ type: 'Polygon', coordinates: [[10,10], [11,14],[10,9]] });
          assert.deepEqual({ $geoWithin: {$geometry: {type:'Polygon', coordinates: [[10,10], [11,14],[10,9]]}}}, m._conditions.loc);
        })
      })

      describe('of length 2', function(){
        it('delegates to box()', function(){
          var m = mquery().where('loc').within([1,2],[2,5]);
          assert.deepEqual(m._conditions.loc, { $geoWithin: { $box: [[1,2],[2,5]]}});
        })
      })

      describe('of length > 2', function(){
        it('delegates to polygon()', function(){
          var m = mquery().where('loc').within([1,2],[2,5],[2,4],[1,3]);
          assert.deepEqual(m._conditions.loc, { $geoWithin: { $polygon: [[1,2],[2,5],[2,4],[1,3]]}});
        })
      })
    })
  })

  describe('geoWithin', function(){
    before(function(){
      mquery.use$geoWithin = false;
    })
    after(function(){
      mquery.use$geoWithin = true;
    })
    describe('when called with arguments', function(){
      describe('of length 1', function(){
        it('delegates to circle when center exists', function(){
          var m = mquery().where('loc').within({ center: [10,10], radius: 3 });
          assert.deepEqual({ $within: {$center:[[10,10], 3]}}, m._conditions.loc);
        })
        it('delegates to box when exists', function(){
          var m = mquery().where('loc').within({ box: [[10,10], [11,14]] });
          assert.deepEqual({ $within: {$box:[[10,10], [11,14]]}}, m._conditions.loc);
        })
        it('delegates to polygon when exists', function(){
          var m = mquery().where('loc').within({ polygon: [[10,10], [11,14],[10,9]] });
          assert.deepEqual({ $within: {$polygon:[[10,10], [11,14],[10,9]]}}, m._conditions.loc);
        })
        it('delegates to geometry when exists', function(){
          var m = mquery().where('loc').within({ type: 'Polygon', coordinates: [[10,10], [11,14],[10,9]] });
          assert.deepEqual({ $within: {$geometry: {type:'Polygon', coordinates: [[10,10], [11,14],[10,9]]}}}, m._conditions.loc);
        })
      })

      describe('of length 2', function(){
        it('delegates to box()', function(){
          var m = mquery().where('loc').within([1,2],[2,5]);
          assert.deepEqual(m._conditions.loc, { $within: { $box: [[1,2],[2,5]]}});
        })
      })

      describe('of length > 2', function(){
        it('delegates to polygon()', function(){
          var m = mquery().where('loc').within([1,2],[2,5],[2,4],[1,3]);
          assert.deepEqual(m._conditions.loc, { $within: { $polygon: [[1,2],[2,5],[2,4],[1,3]]}});
        })
      })
    })
  })

  describe('box', function(){
    describe('with 1 argument', function(){
      it('throws', function(){
        assert.throws(function () {
          mquery().box('sometihng');
        }, /Invalid argument/);
      })
    })
    describe('with > 3 arguments', function(){
      it('throws', function(){
        assert.throws(function () {
          mquery().box(1,2,3,4);
        }, /Invalid argument/);
      })
    })

    describe('with 2 arguments', function(){
      it('throws if not used after where()', function(){
        assert.throws(function () {
          mquery().box([],[]);
        }, /must be used after where/);
      })
      it('works', function(){
        var m = mquery().where('loc').box([1,2],[3,4]);
        assert.deepEqual(m._conditions.loc, { $geoWithin: { $box: [[1,2],[3,4]] }});
      })
    })

    describe('with 3 arguments', function(){
      it('works', function(){
        var m = mquery().box('loc', [1,2],[3,4]);
        assert.deepEqual(m._conditions.loc, { $geoWithin: { $box: [[1,2],[3,4]] }});
      })
    })
  })

  describe('polygon', function(){
    describe('when first argument is not a string', function(){
      it('throws if not used after where()', function(){
        assert.throws(function () {
          mquery().polygon({});
        }, /must be used after where/);

        assert.doesNotThrow(function () {
          mquery().where('loc').polygon([1,2], [2,3], [3,6]);
        });
      })

      it('assigns arguments to within polygon condition', function(){
        var m = mquery().where('loc').polygon([1,2], [2,3], [3,6]);
        assert.deepEqual(m._conditions, { loc: {$geoWithin: {$polygon: [[1,2],[2,3],[3,6]]}} });
      })
    })

    describe('when first arg is a string', function(){
      it('assigns remaining arguments to within polygon condition', function(){
        var m = mquery().polygon('loc', [1,2], [2,3], [3,6]);
        assert.deepEqual(m._conditions, { loc: {$geoWithin: {$polygon: [[1,2],[2,3],[3,6]]}} });
      })
    })
  })

  describe('circle', function(){
    describe('with one arg', function(){
      it('must follow where()', function(){
        assert.throws(function () {
          mquery().circle('x');
        }, /must be used after where/);
        assert.doesNotThrow(function () {
          mquery().where('loc').circle({center:[0,0], radius: 3 });
        });
      })
      it('works', function(){
        var m = mquery().where('loc').circle({center:[0,0], radius: 3 });
        assert.deepEqual(m._conditions, { loc: { $geoWithin: {$center: [[0,0],3] }}});
      })
    })
    describe('with 3 args', function(){
      it('throws', function(){
        assert.throws(function () {
          mquery().where('loc').circle(1,2,3);
        }, /Invalid argument/);
      })
    })
    describe('requires radius and center', function(){
      assert.throws(function () {
        mquery().circle('loc', { center: 1 });
      }, /center and radius are required/);
      assert.throws(function () {
        mquery().circle('loc', { radius: 1 });
      }, /center and radius are required/);
      assert.doesNotThrow(function () {
        mquery().circle('loc', { center: [1,2], radius: 1 });
      });
    })
  })

  describe('geometry', function(){
    // within + intersects
    var point = { type: 'Point', coordinates: [[0,0],[1,1]] };

    it('must be called after within or intersects', function(done){
      assert.throws(function () {
        mquery().where('a').geometry(point);
      }, /must come after/);

      assert.doesNotThrow(function () {
        mquery().where('a').within().geometry(point);
      });

      assert.doesNotThrow(function () {
        mquery().where('a').intersects().geometry(point);
      });

      done();
    })

    describe('when called with one argument', function(){
      describe('after within()', function(){
        it('and arg quacks like geoJSON', function(done){
          var m = mquery().where('a').within().geometry(point);
          assert.deepEqual({ a: { $geoWithin: { $geometry: point }}}, m._conditions);
          done();
        })
      })

      describe('after intersects()', function(){
        it('and arg quacks like geoJSON', function(done){
          var m = mquery().where('a').intersects().geometry(point);
          assert.deepEqual({ a: { $geoIntersects: { $geometry: point }}}, m._conditions);
          done();
        })
      })

      it('and arg does not quack like geoJSON', function(done){
        assert.throws(function () {
          mquery().where('b').within().geometry({type:1, coordinates:2});
        }, /Invalid argument/);
        done();
      })
    })

    describe('when called with zero arguments', function(){
      it('throws', function(done){
        assert.throws(function () {
          mquery().where('a').within().geometry();
        }, /Invalid argument/);

        done();
      })
    })

    describe('when called with more than one arguments', function(){
      it('throws', function(done){
        assert.throws(function () {
          mquery().where('a').within().geometry({type:'a',coordinates:[]}, 2);
        }, /Invalid argument/);
        done();
      })
    })
  })

  describe('intersects', function(){
    it('must be used after where()', function(done){
      var m = mquery();
      assert.throws(function () {
        m.intersects();
      }, /must be used after where/)
      done();
    })

    it('sets geo comparison to "$intersects"', function(done){
      var n = mquery().where('a').intersects();
      assert.equal('$geoIntersects', n._geoComparison);
      done();
    })

    it('is chainable', function(){
      var m = mquery();
      assert.equal(m.where('a').intersects(), m);
    })

    it('calls geometry if argument quacks like geojson', function(done){
      var m = mquery();
      var o = { type: 'LineString', coordinates: [[0,1],[3,40]] };
      var ran = false;

      m.geometry = function (arg) {
        ran = true;
        assert.deepEqual(o, arg);
      }

      m.where('a').intersects(o);
      assert.ok(ran);

      done();
    })

    it('throws if argument is not geometry-like', function(done){
      var m = mquery().where('a');

      assert.throws(function () {
        m.intersects(null);
      }, /Invalid argument/);

      assert.throws(function () {
        m.intersects(undefined);
      }, /Invalid argument/);

      assert.throws(function () {
        m.intersects(false);
      }, /Invalid argument/);

      assert.throws(function () {
        m.intersects({});
      }, /Invalid argument/);

      assert.throws(function () {
        m.intersects([]);
      }, /Invalid argument/);

      assert.throws(function () {
        m.intersects(function(){});
      }, /Invalid argument/);

      assert.throws(function () {
        m.intersects(NaN);
      }, /Invalid argument/);

      done();
    })
  })

  describe('near', function(){
    // near nearSphere
    describe('with 0 args', function(){
      it('is compatible with geometry()', function(done){
        var q = mquery().where('x').near().geometry({ type: 'Point', coordinates: [180, 11] });
        assert.deepEqual({ $near: {$geometry: {type:'Point', coordinates: [180,11]}}}, q._conditions.x);
        done();
      })
    })

    describe('with 1 arg', function(){
      it('throws if not used after where()', function(){
        assert.throws(function () {
          mquery().near(1);
        }, /must be used after where/)
      })
      it('does not throw if used after where()', function(){
        assert.doesNotThrow(function () {
          mquery().where('loc').near({center:[1,1]});
        })
      })
    })
    describe('with > 2 args', function(){
      it('throws', function(){
        assert.throws(function () {
          mquery().near(1,2,3);
        }, /Invalid argument/)
      })
    })

    it('creates $geometry args for GeoJSON', function(){
      var m = mquery().where('loc').near({ center: { type: 'Point', coordinates: [10,10] }});
      assert.deepEqual({ $near: {$geometry: {type:'Point', coordinates: [10,10]}}}, m._conditions.loc);
    })

    it('expects `center`', function(){
      assert.throws(function () {
        mquery().near('loc', { maxDistance: 3 });
      }, /center is required/)
      assert.doesNotThrow(function () {
        mquery().near('loc', { center: [3,4] });
      })
    })

    it('accepts spherical conditions', function(){
      var m = mquery().where('loc').near({ center: [1,2], spherical: true });
      assert.deepEqual(m._conditions, { loc: { $nearSphere: [1,2]}});
    })

    it('is non-spherical by default', function(){
      var m = mquery().where('loc').near({ center: [1,2] });
      assert.deepEqual(m._conditions, { loc: { $near: [1,2]}});
    })

    it('supports maxDistance', function(){
      var m = mquery().where('loc').near({ center: [1,2], maxDistance:4 });
      assert.deepEqual(m._conditions, { loc: { $near: [1,2], $maxDistance: 4}});
    })

    it('supports minDistance', function(){
      var m = mquery().where('loc').near({ center: [1,2], minDistance:4 });
      assert.deepEqual(m._conditions, { loc: { $near: [1,2], $minDistance: 4}});
    })

    it('is chainable', function(){
      var m = mquery().where('loc').near({ center: [1,2], maxDistance:4 }).find({ x: 1 });
      assert.deepEqual(m._conditions, { loc: { $near: [1,2], $maxDistance: 4}, x: 1});
    })

    describe('supports passing GeoJSON, gh-13', function(){
      it('with center', function(){
        var m = mquery().where('loc').near({
            center: { type: 'Point', coordinates: [1,1] }
          , maxDistance: 2
        });

        var expect = {
            loc: {
                $near: {
                    $geometry: {
                        type: 'Point'
                      , coordinates : [1,1]
                    }
                  , $maxDistance : 2
                }
            }
        }

        assert.deepEqual(m._conditions, expect);
      })
    })
  })

  // fields

  describe('select', function(){
    describe('with 0 args', function(){
      it('is chainable', function(){
        var m = mquery()
        assert.equal(m, m.select());
      })
    })

    it('accepts an object', function(){
      var o = { x: 1, y: 1 }
      var m = mquery().select(o);
      assert.deepEqual(m._fields, o);
    })

    it('accepts a string', function(){
      var o = 'x -y';
      var m = mquery().select(o);
      assert.deepEqual(m._fields, { x: 1, y: 0 });
    })

    it('does accept an array', function(){
      var o = ['x', '-y'];
      var m = mquery().select(o);
      assert.deepEqual(m._fields, { x: 1, y: 0 });
    })

    it('merges previous arguments', function(){
      var o = { x: 1, y: 0, a: 1 }
      var m = mquery().select(o);
      m.select('z -u w').select({ x: 0 })
      assert.deepEqual(m._fields, {
          x: 0
        , y: 0
        , z: 1
        , u: 0
        , w: 1
        , a: 1
      });
    })

    it('rejects non-string, object, arrays', function(){
      assert.throws(function () {
        mquery().select(function(){});
      }, /Invalid select\(\) argument/);
    })

    it('accepts arguments objects', function(){
      var m = mquery();
      function t () {
        m.select(arguments);
        assert.deepEqual(m._fields, { x: 1, y: 0 });
      }
      t('x', '-y');
    })

    noDistinct('select');
  })

  describe('selected', function() {
    it('returns true when fields have been selected', function(done) {
      var m = mquery().select({ name: 1 });
      assert.ok(m.selected());

      var m = mquery().select('name');
      assert.ok(m.selected());

      done();
    });

    it('returns false when no fields have been selected', function(done) {
      var m = mquery();
      assert.strictEqual(false, m.selected());
      done();
    });
  });

  describe('selectedInclusively', function() {
    describe('returns false', function(){
      it('when no fields have been selected', function(done) {
        assert.strictEqual(false, mquery().selectedInclusively());
        assert.equal(false, mquery().select({}).selectedInclusively());
        done();
      });
      it('when any fields have been excluded', function(done) {
        assert.strictEqual(false, mquery().select('-name').selectedInclusively());
        assert.strictEqual(false, mquery().select({ name: 0 }).selectedInclusively());
        assert.strictEqual(false, mquery().select('name bio -_id').selectedInclusively());
        assert.strictEqual(false, mquery().select({ name: 1, _id: 0 }).selectedInclusively());
        done();
      });
      it('when using $meta', function(done) {
        assert.strictEqual(false, mquery().select({ name: { $meta: 'textScore' } }).selectedInclusively());
        done();
      });
    });

    describe('returns true', function() {
      it('when fields have been included', function(done) {
        assert.equal(true, mquery().select('name').selectedInclusively());
        assert.equal(true, mquery().select({ name:1 }).selectedInclusively());
        done();
      });
    });
  });

  describe('selectedExclusively', function() {
    describe('returns false', function(){
      it('when no fields have been selected', function(done) {
        assert.equal(false, mquery().selectedExclusively());
        assert.equal(false, mquery().select({}).selectedExclusively());
        done();
      });
      it('when fields have only been included', function(done) {
        assert.equal(false, mquery().select('name').selectedExclusively());
        assert.equal(false, mquery().select({ name: 1 }).selectedExclusively());
        done();
      });
    });

    describe('returns true', function() {
      it('when any field has been excluded', function(done) {
        assert.equal(true, mquery().select('-name').selectedExclusively());
        assert.equal(true, mquery().select({ name:0 }).selectedExclusively());
        assert.equal(true, mquery().select('-_id').selectedExclusively());
        assert.strictEqual(true, mquery().select('name bio -_id').selectedExclusively());
        assert.strictEqual(true, mquery().select({ name: 1, _id: 0 }).selectedExclusively());
        done();
      });
    });
  });

  describe('slice', function(){
    describe('with 0 args', function(){
      it('is chainable', function(){
        var m = mquery()
        assert.equal(m, m.slice());
      })
      it('is a noop', function(){
        var m = mquery().slice();
        assert.deepEqual(m._fields, undefined);
      })
    })

    describe('with 1 arg', function(){
      it('throws if not called after where()', function(){
        assert.throws(function () {
          mquery().slice(1);
        }, /must be used after where/);
        assert.doesNotThrow(function () {
          mquery().where('a').slice(1);
        });
      })
      it('that is a number', function(){
        var query = mquery();
        query.where('collection').slice(5);
        assert.deepEqual(query._fields, {collection: {$slice: 5}});
      })
      it('that is an array', function(){
        var query = mquery();
        query.where('collection').slice([5,10]);
        assert.deepEqual(query._fields, {collection: {$slice: [5,10]}});
      })
      it('that is an object', function() {
        var query = mquery();
        query.slice({ collection: [5, 10] });
        assert.deepEqual(query._fields, {collection: {$slice: [5,10]}});
      })
    })

    describe('with 2 args', function(){
      describe('and first is a number', function(){
        it('throws if not called after where', function(){
          assert.throws(function () {
            mquery().slice(2,3);
          }, /must be used after where/);
        })
        it('does not throw if used after where', function(){
          var query = mquery();
          query.where('collection').slice(2,3);
          assert.deepEqual(query._fields, {collection: {$slice: [2,3]}});
        })
      })
      it('and first is not a number', function(){
        var query = mquery().slice('collection', [-5, 2]);
        assert.deepEqual(query._fields, {collection: {$slice: [-5,2]}});
      })
    })

    describe('with 3 args', function(){
      it('works', function(){
        var query = mquery();
        query.slice('collection', 14, 10);
        assert.deepEqual(query._fields, {collection: {$slice: [14, 10]}});
      })
    })

    noDistinct('slice');
    no('count', 'slice');
  })

  // options

  describe('sort', function(){
    describe('with 0 args', function(){
      it('chains', function(){
        var m = mquery();
        assert.equal(m, m.sort());
      })
      it('has no affect', function(){
        var m = mquery();
        assert.equal(m.options.sort, undefined);
      })
    });

    it('works', function(){
      var query = mquery();
      query.sort('a -c b');
      assert.deepEqual(query.options.sort, { a : 1, b: 1, c : -1});

      query = mquery();
      query.sort({'a': 1, 'c': -1, 'b': 'asc', e: 'descending', f: 'ascending'});
      assert.deepEqual(query.options.sort, {'a': 1, 'c': -1, 'b': 1, 'e': -1, 'f': 1});

      query = mquery();
      var e= undefined;

      e= undefined;
      try {
        query.sort('a', 1, 'c', -1, 'b', 1);
      } catch (err) {
        e= err;
      }
      assert.ok(e, 'uh oh. no error was thrown');
      assert.equal(e.message, 'Invalid sort() argument. Must be a string, object, or array.');
    });

    it('handles $meta sort options', function(){
      var query = mquery();
      query.sort({ score: { $meta : "textScore" } });
      assert.deepEqual(query.options.sort, { score : { $meta : "textScore" } });
    });

    it('array syntax', function(){
      var query = mquery();
      query.sort([['field', 1], ['test', -1]]);
      assert.deepEqual(query.options.sort, [['field', 1], ['test', -1]]);
    });

    it('throws with mixed array/object syntax', function(){
      var query = mquery();
      assert.throws(function() {
        query.sort({ field: 1 }).sort([['test', -1]]);
      }, /Can't mix sort syntaxes/);
      assert.throws(function() {
        query.sort([['field', 1]]).sort({ test: 1 });
      }, /Can't mix sort syntaxes/);
    });

    it('works with maps', function() {
      if (typeof Map === 'undefined') {
        return this.skip();
      }
      var query = mquery();
      query.sort(new Map().set('field', 1).set('test', -1));
      assert.deepEqual(query.options.sort, new Map().set('field', 1).set('test', -1));
    });
  })

  function simpleOption (type, options) {
    describe(type, function(){
      it('sets the ' + type + ' option', function(){
        var m = mquery()[type](2);
        var optionName = options.name || type;
        assert.equal(2, m.options[optionName]);
      })
      it('is chainable', function(){
        var m = mquery();
        assert.equal(m[type](3), m);
      })

      if (!options.distinct) noDistinct(type);
      if (!options.count) no('count', type);
    })
  }

  var negated = {
      limit: {distinct: false, count: true}
    , skip: {distinct: false, count: true}
    , maxScan: {distinct: false, count: false}
    , batchSize: {distinct: false, count: false}
    , maxTime: {distinct: true, count: true, name: 'maxTimeMS' }
    , comment: {distinct: false, count: false}
  };
  Object.keys(negated).forEach(function (key) {
    simpleOption(key, negated[key]);
  })

  describe('snapshot', function(){
    it('works', function(){
      var query = mquery();
      query.snapshot();
      assert.equal(true, query.options.snapshot);

      var query = mquery()
      query.snapshot(true);
      assert.equal(true, query.options.snapshot);

      var query = mquery()
      query.snapshot(false);
      assert.equal(false, query.options.snapshot);
    })
    noDistinct('snapshot');
    no('count', 'snapshot');
  })

  describe('hint', function(){
    it('accepts an object', function(){
      var query2 = mquery();
      query2.hint({'a': 1, 'b': -1});
      assert.deepEqual(query2.options.hint, {'a': 1, 'b': -1});
    })

    it('accepts a string', function(){
      var query2 = mquery();
      query2.hint('a');
      assert.deepEqual(query2.options.hint, 'a');
    })

    it('rejects everything else', function(){
      assert.throws(function(){
        mquery().hint(['c']);
      }, /Invalid hint./);
      assert.throws(function(){
        mquery().hint(1);
      }, /Invalid hint./);
    })

    describe('does not have side affects', function(){
      it('on invalid arg', function(){
        var m = mquery();
        try {
          m.hint(1);
        } catch (err) {
          // ignore
        }
        assert.equal(undefined, m.options.hint);
      })
      it('on missing arg', function(){
        var m = mquery().hint();
        assert.equal(undefined, m.options.hint);
      })
    })

    noDistinct('hint');
  })

  describe('slaveOk', function(){
    it('works', function(){
      var query = mquery();
      query.slaveOk();
      assert.equal(true, query.options.slaveOk);

      var query = mquery()
      query.slaveOk(true);
      assert.equal(true, query.options.slaveOk);

      var query = mquery()
      query.slaveOk(false);
      assert.equal(false, query.options.slaveOk);
    })
  })

  describe('read', function(){
    it('sets associated readPreference option', function(){
      var m = mquery();
      m.read('p');
      assert.equal('primary', m.options.readPreference);
    })
    it('is chainable', function(){
      var m = mquery();
      assert.equal(m, m.read('sp'));
    })
  })

  describe('tailable', function(){
    it('works', function(){
      var query = mquery();
      query.tailable();
      assert.equal(true, query.options.tailable);

      var query = mquery()
      query.tailable(true);
      assert.equal(true, query.options.tailable);

      var query = mquery()
      query.tailable(false);
      assert.equal(false, query.options.tailable);
    })
    it('is chainable', function(){
      var m = mquery();
      assert.equal(m, m.tailable());
    })
    noDistinct('tailable');
    no('count', 'tailable');
  })

  // query utilities

  describe('merge', function(){
    describe('with falsy arg', function(){
      it('returns itself', function(){
        var m = mquery();
        assert.equal(m, m.merge());
        assert.equal(m, m.merge(null));
        assert.equal(m, m.merge(0));
      })
    })
    describe('with an argument', function(){
      describe('that is not a query or plain object', function(){
        it('throws', function(){
          assert.throws(function () {
            mquery().merge([]);
          }, /Invalid argument/);
          assert.throws(function () {
            mquery().merge('merge');
          }, /Invalid argument/);
          assert.doesNotThrow(function () {
            mquery().merge({});
          }, /Invalid argument/);
        })
      })

      describe('that is a query', function(){
        it('merges conditions, field selection, and options', function(){
          var m = mquery({ x: 'hi' }, { select: 'x y', another: true })
          var n = mquery().merge(m);
          assert.deepEqual(n._conditions, m._conditions);
          assert.deepEqual(n._fields, m._fields);
          assert.deepEqual(n.options, m.options);
        })
        it('clones update arguments', function(done){
          var original = { $set: { iTerm: true }}
          var m = mquery().update(original);
          var n = mquery().merge(m);
          m.update({ $set: { x: 2 }})
          assert.notDeepEqual(m._update, n._update);
          done();
        })
        it('is chainable', function(){
          var m = mquery({ x: 'hi' });
          var n = mquery();
          assert.equal(n, n.merge(m));
        })
      })

      describe('that is an object', function(){
        it('merges', function(){
          var m = { x: 'hi' };
          var n = mquery().merge(m);
          assert.deepEqual(n._conditions, { x: 'hi' });
        })
        it('clones update arguments', function(done){
          var original = { $set: { iTerm: true }}
          var m = mquery().update(original);
          var n = mquery().merge(original);
          m.update({ $set: { x: 2 }})
          assert.notDeepEqual(m._update, n._update);
          done();
        })
        it('is chainable', function(){
          var m = { x: 'hi' };
          var n = mquery();
          assert.equal(n, n.merge(m));
        })
      })
    })
  })

  // queries

  describe('find', function(){
    describe('with no callback', function(){
      it('does not execute', function(){
        var m = mquery();
        assert.doesNotThrow(function () {
          m.find()
        })
        assert.doesNotThrow(function () {
          m.find({ x: 1 })
        })
      })
    })

    it('is chainable', function(){
      var m = mquery().find({ x: 1 }).find().find({ y: 2 });
      assert.deepEqual(m._conditions, {x:1,y:2});
    })

    it('merges other queries', function(){
      var m = mquery({ name: 'mquery' });
      m.tailable();
      m.select('_id');
      var a = mquery().find(m);
      assert.deepEqual(a._conditions, m._conditions);
      assert.deepEqual(a.options, m.options);
      assert.deepEqual(a._fields, m._fields);
    })

    describe('executes', function(){
      before(function (done) {
        col.insert({ name: 'mquery' }, { safe: true }, done);
      });

      after(function(done){
        col.remove({ name: 'mquery' }, done);
      })

      it('when criteria is passed with a callback', function(done){
        mquery(col).find({ name: 'mquery' }, function (err, docs) {
          assert.ifError(err);
          assert.equal(1, docs.length);
          done();
        })
      })
      it('when Query is passed with a callback', function(done){
        var m = mquery({ name: 'mquery' });
        mquery(col).find(m, function (err, docs) {
          assert.ifError(err);
          assert.equal(1, docs.length);
          done();
        })
      })
      it('when just a callback is passed', function(done){
        mquery({ name: 'mquery' }).collection(col).find(function (err, docs) {
          assert.ifError(err);
          assert.equal(1, docs.length);
          done();
        });
      })
    })
  })

  describe('findOne', function(){
    describe('with no callback', function(){
      it('does not execute', function(){
        var m = mquery();
        assert.doesNotThrow(function () {
          m.findOne()
        })
        assert.doesNotThrow(function () {
          m.findOne({ x: 1 })
        })
      })
    })

    it('is chainable', function(){
      var m = mquery();
      var n = m.findOne({ x: 1 }).findOne().findOne({ y: 2 });
      assert.equal(m, n);
      assert.deepEqual(m._conditions, {x:1,y:2});
      assert.equal('findOne', m.op);
    })

    it('merges other queries', function(){
      var m = mquery({ name: 'mquery' });
      m.read('nearest');
      m.select('_id');
      var a = mquery().findOne(m);
      assert.deepEqual(a._conditions, m._conditions);
      assert.deepEqual(a.options, m.options);
      assert.deepEqual(a._fields, m._fields);
    })

    describe('executes', function(){
      before(function (done) {
        col.insert({ name: 'mquery findone' }, { safe: true }, done);
      });

      after(function(done){
        col.remove({ name: 'mquery findone' }, done);
      })

      it('when criteria is passed with a callback', function(done){
        mquery(col).findOne({ name: 'mquery findone' }, function (err, doc) {
          assert.ifError(err);
          assert.ok(doc);
          assert.equal('mquery findone', doc.name);
          done();
        })
      })
      it('when Query is passed with a callback', function(done){
        var m = mquery(col).where({ name: 'mquery findone' });
        mquery(col).findOne(m, function (err, doc) {
          assert.ifError(err);
          assert.ok(doc);
          assert.equal('mquery findone', doc.name);
          done();
        })
      })
      it('when just a callback is passed', function(done){
        mquery({ name: 'mquery findone' }).collection(col).findOne(function (err, doc) {
          assert.ifError(err);
          assert.ok(doc);
          assert.equal('mquery findone', doc.name);
          done();
        });
      })
    })
  })

  describe('count', function(){
    describe('with no callback', function(){
      it('does not execute', function(){
        var m = mquery();
        assert.doesNotThrow(function () {
          m.count()
        })
        assert.doesNotThrow(function () {
          m.count({ x: 1 })
        })
      })
    })

    it('is chainable', function(){
      var m = mquery();
      var n = m.count({ x: 1 }).count().count({ y: 2 });
      assert.equal(m, n);
      assert.deepEqual(m._conditions, {x:1,y:2});
      assert.equal('count', m.op);
    })

    it('merges other queries', function(){
      var m = mquery({ name: 'mquery' });
      m.read('nearest');
      m.select('_id');
      var a = mquery().count(m);
      assert.deepEqual(a._conditions, m._conditions);
      assert.deepEqual(a.options, m.options);
      assert.deepEqual(a._fields, m._fields);
    })

    describe('executes', function(){
      before(function (done) {
        col.insert({ name: 'mquery count' }, { safe: true }, done);
      });

      after(function(done){
        col.remove({ name: 'mquery count' }, done);
      })

      it('when criteria is passed with a callback', function(done){
        mquery(col).count({ name: 'mquery count' }, function (err, count) {
          assert.ifError(err);
          assert.ok(count);
          assert.ok(1 === count);
          done();
        })
      })
      it('when Query is passed with a callback', function(done){
        var m = mquery({ name: 'mquery count' });
        mquery(col).count(m, function (err, count) {
          assert.ifError(err);
          assert.ok(count);
          assert.ok(1 === count);
          done();
        })
      })
      it('when just a callback is passed', function(done){
        mquery({ name: 'mquery count' }).collection(col).count(function (err, count) {
          assert.ifError(err);
          assert.ok(1 === count);
          done();
        });
      })
    })

    describe('validates its option', function(){
      it('sort', function(done){
        assert.doesNotThrow(function(){
          var m = mquery().sort('x').count();
        });
        done();
      })

      it('select', function(done){
        assert.throws(function(){
          var m = mquery().select('x').count();
        }, /field selection and slice cannot be used with count/);
        done();
      })

      it('slice', function(done){
        assert.throws(function(){
          var m = mquery().where('x').slice(-3).count();
        }, /field selection and slice cannot be used with count/);
        done();
      })

      it('limit', function(done){
        assert.doesNotThrow(function(){
          var m = mquery().limit(3).count();
        })
        done();
      })

      it('skip', function(done){
        assert.doesNotThrow(function(){
          var m = mquery().skip(3).count();
        })
        done();
      })

      it('batchSize', function(done){
        assert.throws(function(){
          var m = mquery({}, { batchSize: 3 }).count();
        }, /batchSize cannot be used with count/);
        done();
      })

      it('comment', function(done){
        assert.throws(function(){
          var m = mquery().comment('mquery').count();
        }, /comment cannot be used with count/);
        done();
      })

      it('maxScan', function(done){
        assert.throws(function(){
          var m = mquery().maxScan(300).count();
        }, /maxScan cannot be used with count/);
        done();
      })

      it('snapshot', function(done){
        assert.throws(function(){
          var m = mquery().snapshot().count();
        }, /snapshot cannot be used with count/);
        done();
      })

      it('tailable', function(done){
        assert.throws(function(){
          var m = mquery().tailable().count();
        }, /tailable cannot be used with count/);
        done();
      })
    })
  })

  describe('distinct', function(){
    describe('with no callback', function(){
      it('does not execute', function(){
        var m = mquery();
        assert.doesNotThrow(function () {
          m.distinct()
        })
        assert.doesNotThrow(function () {
          m.distinct('name')
        })
        assert.doesNotThrow(function () {
          m.distinct({ name: 'mquery distinct' })
        })
        assert.doesNotThrow(function () {
          m.distinct({ name: 'mquery distinct' }, 'name')
        })
      })
    })

    it('is chainable', function(){
      var m = mquery({x:1}).distinct('name');
      var n = m.distinct({y:2});
      assert.equal(m, n);
      assert.deepEqual(n._conditions, {x:1, y:2});
      assert.equal('name', n._distinct);
      assert.equal('distinct', n.op);
    });

    it('overwrites field', function(){
      var m = mquery({ name: 'mquery' }).distinct('name');
      m.distinct('rename');
      assert.equal(m._distinct, 'rename');
      m.distinct({x:1}, 'renamed');
      assert.equal(m._distinct, 'renamed');
    })

    it('merges other queries', function(){
      var m = mquery().distinct({ name: 'mquery' }, 'age')
      m.read('nearest');
      var a = mquery().distinct(m);
      assert.deepEqual(a._conditions, m._conditions);
      assert.deepEqual(a.options, m.options);
      assert.deepEqual(a._fields, m._fields);
      assert.deepEqual(a._distinct, m._distinct);
    })

    describe('executes', function(){
      before(function (done) {
        col.insert({ name: 'mquery distinct', age: 1 }, { safe: true }, done);
      });

      after(function(done){
        col.remove({ name: 'mquery distinct' }, done);
      })

      it('when distinct arg is passed with a callback', function(done){
        mquery(col).distinct('distinct', function (err, doc) {
          assert.ifError(err);
          assert.ok(doc);
          done();
        })
      })
      describe('when criteria is passed with a callback', function(){
        it('if distinct arg was declared', function(done){
          mquery(col).distinct('age').distinct({ name: 'mquery distinct' }, function (err, doc) {
            assert.ifError(err);
            assert.ok(doc);
            done();
          })
        })
        it('but not if distinct arg was not declared', function(){
          assert.throws(function(){
            mquery(col).distinct({ name: 'mquery distinct' }, function(){})
          }, /No value for `distinct`/)
        })
      })
      describe('when Query is passed with a callback', function(){
        var m = mquery({ name: 'mquery distinct' });
        it('if distinct arg was declared', function(done){
          mquery(col).distinct('age').distinct(m, function (err, doc) {
            assert.ifError(err);
            assert.ok(doc);
            done();
          })
        })
        it('but not if distinct arg was not declared', function(){
          assert.throws(function(){
            mquery(col).distinct(m, function(){})
          }, /No value for `distinct`/)
        })
      })
      describe('when just a callback is passed', function(done){
        it('if distinct arg was declared', function(done){
          var m = mquery({ name: 'mquery distinct' });
          m.collection(col);
          m.distinct('age');
          m.distinct(function (err, doc) {
            assert.ifError(err);
            assert.ok(doc);
            done();
          });
        })
        it('but not if no distinct arg was declared', function(){
          var m = mquery();
          m.collection(col);
          assert.throws(function () {
            m.distinct(function(){});
          }, /No value for `distinct`/);
        })
      })
    })

    describe('validates its option', function(){
      it('sort', function(done){
        assert.throws(function(){
          var m = mquery().sort('x').distinct();
        }, /sort cannot be used with distinct/);
        done();
      })

      it('select', function(done){
        assert.throws(function(){
          var m = mquery().select('x').distinct();
        }, /field selection and slice cannot be used with distinct/);
        done();
      })

      it('slice', function(done){
        assert.throws(function(){
          var m = mquery().where('x').slice(-3).distinct();
        }, /field selection and slice cannot be used with distinct/);
        done();
      })

      it('limit', function(done){
        assert.throws(function(){
          var m = mquery().limit(3).distinct();
        }, /limit cannot be used with distinct/);
        done();
      })

      it('skip', function(done){
        assert.throws(function(){
          var m = mquery().skip(3).distinct();
        }, /skip cannot be used with distinct/);
        done();
      })

      it('batchSize', function(done){
        assert.throws(function(){
          var m = mquery({}, { batchSize: 3 }).distinct();
        }, /batchSize cannot be used with distinct/);
        done();
      })

      it('comment', function(done){
        assert.throws(function(){
          var m = mquery().comment('mquery').distinct();
        }, /comment cannot be used with distinct/);
        done();
      })

      it('maxScan', function(done){
        assert.throws(function(){
          var m = mquery().maxScan(300).distinct();
        }, /maxScan cannot be used with distinct/);
        done();
      })

      it('snapshot', function(done){
        assert.throws(function(){
          var m = mquery().snapshot().distinct();
        }, /snapshot cannot be used with distinct/);
        done();
      })

      it('hint', function(done){
        assert.throws(function(){
          var m = mquery().hint({ x: 1 }).distinct();
        }, /hint cannot be used with distinct/);
        done();
      })

      it('tailable', function(done){
        assert.throws(function(){
          var m = mquery().tailable().distinct();
        }, /tailable cannot be used with distinct/);
        done();
      })
    })
  })

  describe('update', function(){
    describe('with no callback', function(){
      it('does not execute', function(){
        var m = mquery();
        assert.doesNotThrow(function () {
          m.update({ name: 'old' }, { name: 'updated' }, { multi: true })
        })
        assert.doesNotThrow(function () {
          m.update({ name: 'old' }, { name: 'updated' })
        })
        assert.doesNotThrow(function () {
          m.update({ name: 'updated' })
        })
        assert.doesNotThrow(function () {
          m.update()
        })
      })
    })

    it('is chainable', function(){
      var m = mquery({x:1}).update({ y: 2 });
      var n = m.where({y:2});
      assert.equal(m, n);
      assert.deepEqual(n._conditions, {x:1, y:2});
      assert.deepEqual({ y: 2 }, n._update);
      assert.equal('update', n.op);
    });

    it('merges update doc arg', function(){
      var a = [1,2];
      var m = mquery().where({ name: 'mquery' }).update({ x: 'stuff', a: a });
      m.update({ z: 'stuff' });
      assert.deepEqual(m._update, { z: 'stuff', x: 'stuff', a: a });
      assert.deepEqual(m._conditions, { name: 'mquery' });
      assert.ok(!m.options.overwrite);
      m.update({}, { z: 'renamed' }, { overwrite: true });
      assert.ok(m.options.overwrite === true);
      assert.deepEqual(m._conditions, { name: 'mquery' });
      assert.deepEqual(m._update, { z: 'renamed', x: 'stuff', a: a });
      a.push(3);
      assert.notDeepEqual(m._update, { z: 'renamed', x: 'stuff', a: a });
    })

    it('merges other options', function(){
      var m = mquery();
      m.setOptions({ overwrite: true });
      m.update({ age: 77 }, { name: 'pagemill' }, { multi: true })
      assert.deepEqual({ age: 77 }, m._conditions);
      assert.deepEqual({ name: 'pagemill' }, m._update);
      assert.deepEqual({ overwrite: true, multi: true }, m.options);
    })

    describe('executes', function(){
      var id;
      before(function (done) {
        col.insert({ name: 'mquery update', age: 1 }, { safe: true }, function (err, res) {
          id = res.insertedIds[0];
          done();
        });
      });

      after(function(done){
        col.remove({ _id: id }, done);
      })

      describe('when conds + doc + opts + callback passed', function(){
        it('works', function(done){
          var m = mquery(col).where({ _id: id })
          m.update({}, { name: 'Sparky' }, { safe: true }, function (err, res) {
            assert.ifError(err);
            assert.equal(res.result.n, 1);
            m.findOne(function (err, doc) {
              assert.ifError(err);
              assert.equal(doc.name, 'Sparky');
              done();
            })
          })
        })
      })

      describe('when conds + doc + callback passed', function(){
        it('works', function (done) {
          var m = mquery(col).update({ _id: id }, { name: 'fairgrounds' }, function (err, num, doc) {
            assert.ifError(err);
            assert.ok(1, num);
            m.findOne(function (err, doc) {
              assert.ifError(err);
              assert.equal(doc.name, 'fairgrounds');
              done();
            })
          })
        })
      })

      describe('when doc + callback passed', function(){
        it('works', function (done) {
          var m = mquery(col).where({ _id: id }).update({ name: 'changed' }, function (err, num, doc) {
            assert.ifError(err);
            assert.ok(1, num);
            m.findOne(function (err, doc) {
              assert.ifError(err);
              assert.equal(doc.name, 'changed');
              done();
            })
          })
        })
      })

      describe('when just callback passed', function(){
        it('works', function (done) {
          var m = mquery(col).where({ _id: id });
          m.setOptions({ safe: true });
          m.update({ name: 'Frankenweenie' });
          m.update(function (err, res) {
            assert.ifError(err);
            assert.equal(res.result.n, 1);
            m.findOne(function (err, doc) {
              assert.ifError(err);
              assert.equal(doc.name, 'Frankenweenie');
              done();
            })
          })
        })
      })

      describe('without a callback', function(){
        it('when forced by exec()', function(done){
          var m = mquery(col).where({ _id: id });
          m.setOptions({ safe: true, multi: true });
          m.update({ name: 'forced' });

          var update = m._collection.update;
          m._collection.update = function (conds, doc, opts, cb) {
            m._collection.update = update;

            assert.ok(opts.safe);
            assert.ok(true === opts.multi);
            assert.equal('forced', doc.$set.name);
            done();
          }

          m.exec()
        })
      })

      describe('except when update doc is empty and missing overwrite flag', function(){
        it('works', function (done) {
          var m = mquery(col).where({ _id: id });
          m.setOptions({ safe: true });
          m.update({ }, function (err, num) {
            assert.ifError(err);
            assert.ok(0 === num);
            setTimeout(function(){
              m.findOne(function (err, doc) {
                assert.ifError(err);
                assert.equal(3, mquery.utils.keys(doc).length);
                assert.equal(id, doc._id.toString());
                assert.equal('Frankenweenie', doc.name);
                done();
              })
            }, 300);
          })
        })
      });

      describe('when update doc is set with overwrite flag', function(){
        it('works', function (done) {
          var m = mquery(col).where({ _id: id });
          m.setOptions({ safe: true, overwrite: true });
          m.update({ all: 'yep', two: 2 }, function (err, res) {
            assert.ifError(err);
            assert.equal(res.result.n, 1);
            m.findOne(function (err, doc) {
              assert.ifError(err);
              assert.equal(3, mquery.utils.keys(doc).length);
              assert.equal('yep', doc.all);
              assert.equal(2, doc.two);
              assert.equal(id, doc._id.toString());
              done();
            })
          })
        })
      })

      describe('when update doc is empty with overwrite flag', function(){
        it('works', function (done) {
          var m = mquery(col).where({ _id: id });
          m.setOptions({ safe: true, overwrite: true });
          m.update({ }, function (err, res) {
            assert.ifError(err);
            assert.equal(res.result.n, 1);
            m.findOne(function (err, doc) {
              assert.ifError(err);
              assert.equal(1, mquery.utils.keys(doc).length);
              assert.equal(id, doc._id.toString());
              done();
            })
          })
        })
      })

      describe('when boolean (true) - exec()', function(){
        it('works', function(done){
          var m = mquery(col).where({ _id: id });
          m.update({ name: 'bool' }).update(true);
          setTimeout(function () {
            m.findOne(function (err, doc) {
              assert.ifError(err);
              assert.ok(doc);
              assert.equal('bool', doc.name);
              done();
            })
          }, 300)
        })
      })
    })
  })

  describe('remove', function(){
    describe('with 0 args', function(){
      var name = 'remove: no args test'
      before(function(done){
        col.insert({ name: name }, { safe: true }, done)
      })
      after(function(done){
        col.remove({ name: name }, { safe: true }, done)
      })

      it('does not execute', function(done){
        var remove = col.remove;
        col.remove = function () {
          col.remove = remove;
          done(new Error('remove executed!'));
        }

        var m = mquery(col).where({ name: name }).remove()
        setTimeout(function () {
          col.remove = remove;
          done();
        }, 10);
      })

      it('chains', function(){
        var m = mquery();
        assert.equal(m, m.remove());
      })
    })

    describe('with 1 argument', function(){
      var name = 'remove: 1 arg test'
      before(function(done){
        col.insert({ name: name }, { safe: true }, done)
      })
      after(function(done){
        col.remove({ name: name }, { safe: true }, done)
      })

      describe('that is a', function(){
        it('plain object', function(){
          var m = mquery(col).remove({ name: 'Whiskers' });
          m.remove({ color: '#fff' })
          assert.deepEqual({ name: 'Whiskers', color: '#fff' }, m._conditions);
        })

        it('query', function(){
          var q = mquery({ color: '#fff' });
          var m = mquery(col).remove({ name: 'Whiskers' });
          m.remove(q)
          assert.deepEqual({ name: 'Whiskers', color: '#fff' }, m._conditions);
        })

        it('function', function(done){
          mquery(col, { safe: true }).where({name: name}).remove(function (err) {
            assert.ifError(err);
            mquery(col).findOne({ name: name }, function (err, doc) {
              assert.ifError(err);
              assert.equal(null, doc);
              done();
            })
          });
        })

        it('boolean (true) - execute', function(done){
          col.insert({ name: name }, { safe: true }, function (err) {
            assert.ifError(err);
            mquery(col).findOne({ name: name }, function (err, doc) {
              assert.ifError(err);
              assert.ok(doc);
              mquery(col).remove(true);
              setTimeout(function () {
                mquery(col).find(function (err, docs) {
                  assert.ifError(err);
                  assert.ok(docs);
                  assert.equal(0, docs.length);
                  done();
                })
              }, 300)
            })
          })
        })
      })
    })

    describe('with 2 arguments', function(){
      var name = 'remove: 2 arg test'
      beforeEach(function(done){
        col.remove({}, { safe: true }, function (err) {
          assert.ifError(err);
          col.insert([{ name: 'shelly' }, { name: name }], { safe: true }, function (err) {
            assert.ifError(err);
            mquery(col).find(function (err, docs) {
              assert.ifError(err);
              assert.equal(2, docs.length);
              done();
            })
          })
        })
      })

      describe('plain object + callback', function(){
        it('works', function(done){
          mquery(col).remove({ name: name }, function (err) {
            assert.ifError(err);
            mquery(col).find(function (err, docs) {
              assert.ifError(err);
              assert.ok(docs);
              assert.equal(1, docs.length);
              assert.equal('shelly', docs[0].name);
              done();
            })
          });
        })
      })

      describe('mquery + callback', function(){
        it('works', function(done){
          var m = mquery({ name: name });
          mquery(col).remove(m, function (err) {
            assert.ifError(err);
            mquery(col).find(function (err, docs) {
              assert.ifError(err);
              assert.ok(docs);
              assert.equal(1, docs.length);
              assert.equal('shelly', docs[0].name);
              done();
            })
          });
        })
      })
    })
  })

  function validateFindAndModifyOptions (method) {
    describe('validates its option', function(){
      it('sort', function(done){
        assert.doesNotThrow(function(){
          var m = mquery().sort('x')[method]();
        })
        done();
      })

      it('select', function(done){
        assert.doesNotThrow(function(){
          var m = mquery().select('x')[method]();
        })
        done();
      })

      it('limit', function(done){
        assert.throws(function(){
          var m = mquery().limit(3)[method]();
        }, new RegExp('limit cannot be used with ' + method));
        done();
      })

      it('skip', function(done){
        assert.throws(function(){
          var m = mquery().skip(3)[method]();
        }, new RegExp('skip cannot be used with ' + method));
        done();
      })

      it('batchSize', function(done){
        assert.throws(function(){
          var m = mquery({}, { batchSize: 3 })[method]();
        }, new RegExp('batchSize cannot be used with ' + method));
        done();
      })

      it('maxScan', function(done){
        assert.throws(function(){
          var m = mquery().maxScan(300)[method]();
        }, new RegExp('maxScan cannot be used with ' + method));
        done();
      })

      it('snapshot', function(done){
        assert.throws(function(){
          var m = mquery().snapshot()[method]();
        }, new RegExp('snapshot cannot be used with ' + method));
        done();
      })

      it('hint', function(done){
        assert.throws(function(){
          var m = mquery().hint({ x: 1 })[method]();
        }, new RegExp('hint cannot be used with ' + method));
        done();
      })

      it('tailable', function(done){
        assert.throws(function(){
          var m = mquery().tailable()[method]();
        }, new RegExp('tailable cannot be used with ' + method));
        done();
      })

      it('comment', function(done){
        assert.throws(function(){
          var m = mquery().comment('mquery')[method]();
        }, new RegExp('comment cannot be used with ' + method));
        done();
      })
    })
  }

  describe('findOneAndUpdate', function(){
    var name = 'findOneAndUpdate + fn'

    validateFindAndModifyOptions('findOneAndUpdate');

    describe('with 0 args', function(){
      it('makes no changes', function(){
        var m = mquery();
        var n = m.findOneAndUpdate();
        assert.deepEqual(m, n);
      })
    })
    describe('with 1 arg', function(){
      describe('that is an object', function(){
        it('updates the doc', function(){
          var m = mquery();
          var n = m.findOneAndUpdate({ $set: { name: '1 arg' }});
          assert.deepEqual(n._update, { $set: { name: '1 arg' }});
        })
      })
      describe('that is a query', function(){
        it('updates the doc', function(){
          var m = mquery({ name: name }).update({ x: 1 });
          var n = mquery().findOneAndUpdate(m);
          assert.deepEqual(n._update, { x: 1 });
        })
      })
      it('that is a function', function(done){
        col.insert({ name: name }, { safe: true }, function (err) {
          assert.ifError(err);
          var m = mquery({ name: name }).collection(col);
          name = '1 arg';
          var n = m.update({ $set: { name: name }});
          n.findOneAndUpdate(function (err, res) {
            assert.ifError(err);
            assert.ok(res.value);
            assert.equal(name, res.value.name);
            done();
          });
        })
      })
    })
    describe('with 2 args', function(){
      it('conditions + update', function(){
        var m = mquery(col);
        m.findOneAndUpdate({ name: name }, { age: 100 });
        assert.deepEqual({ name: name }, m._conditions);
        assert.deepEqual({ age: 100 }, m._update);
      })
      it('query + update', function(){
        var n = mquery({ name: name });
        var m = mquery(col);
        m.findOneAndUpdate(n, { age: 100 });
        assert.deepEqual({ name: name }, m._conditions);
        assert.deepEqual({ age: 100 }, m._update);
      })
      it('update + callback', function(done){
        var m = mquery(col).where({ name: name });
        m.findOneAndUpdate({}, { $inc: { age: 10 }}, { new: true }, function (err, res) {
          assert.ifError(err);
          assert.equal(10, res.value.age);
          done();
        });
      })
    })
    describe('with 3 args', function(){
      it('conditions + update + options', function(){
        var m = mquery();
        var n = m.findOneAndUpdate({ name: name }, { works: true }, { new: false });
        assert.deepEqual({ name: name}, n._conditions);
        assert.deepEqual({ works: true }, n._update);
        assert.deepEqual({ new: false }, n.options);
      })
      it('conditions + update + callback', function(done){
        var m = mquery(col);
        m.findOneAndUpdate({ name: name }, { works: true }, { new: true }, function (err, res) {
          assert.ifError(err);
          assert.ok(res.value);
          assert.equal(name, res.value.name);
          assert.ok(true === res.value.works);
          done();
        });
      })
    })
    describe('with 4 args', function(){
      it('conditions + update + options + callback', function(done){
        var m = mquery(col);
        m.findOneAndUpdate({ name: name }, { works: false }, { new: false },  function (err, res) {
          assert.ifError(err);
          assert.ok(res.value);
          assert.equal(name, res.value.name);
          assert.ok(true === res.value.works);
          done();
        });
      })
    })
  })

  describe('findOneAndRemove', function(){
    var name = 'findOneAndRemove'

    validateFindAndModifyOptions('findOneAndRemove');

    describe('with 0 args', function(){
      it('makes no changes', function(){
        var m = mquery();
        var n = m.findOneAndRemove();
        assert.deepEqual(m, n);
      })
    })
    describe('with 1 arg', function(){
      describe('that is an object', function(){
        it('updates the doc', function(){
          var m = mquery();
          var n = m.findOneAndRemove({ name: '1 arg' });
          assert.deepEqual(n._conditions, { name: '1 arg' });
        })
      })
      describe('that is a query', function(){
        it('updates the doc', function(){
          var m = mquery({ name: name });
          var n = m.findOneAndRemove(m);
          assert.deepEqual(n._conditions, { name: name });
        })
      })
      it('that is a function', function(done){
        col.insert({ name: name }, { safe: true }, function (err) {
          assert.ifError(err);
          var m = mquery({ name: name }).collection(col);
          m.findOneAndRemove(function (err, res) {
            assert.ifError(err);
            assert.ok(res.value);
            assert.equal(name, res.value.name);
            done();
          });
        })
      })
    })
    describe('with 2 args', function(){
      it('conditions + options', function(){
        var m = mquery(col);
        m.findOneAndRemove({ name: name }, { new: false });
        assert.deepEqual({ name: name }, m._conditions);
        assert.deepEqual({ new: false }, m.options);
      })
      it('query + options', function(){
        var n = mquery({ name: name });
        var m = mquery(col);
        m.findOneAndRemove(n, { sort: { x: 1 }});
        assert.deepEqual({ name: name }, m._conditions);
        assert.deepEqual({ sort: { 'x': 1 }}, m.options);
      })
      it('conditions + callback', function(done){
        col.insert({ name: name }, { safe: true }, function (err) {
          assert.ifError(err);
          var m = mquery(col);
          m.findOneAndRemove({ name: name }, function (err, res) {
            assert.ifError(err);
            assert.equal(name, res.value.name);
            done();
          });
        });
      })
      it('query + callback', function(done){
        col.insert({ name: name }, { safe: true }, function (err) {
          assert.ifError(err);
          var n = mquery({ name: name })
          var m = mquery(col);
          m.findOneAndRemove(n, function (err, res) {
            assert.ifError(err);
            assert.equal(name, res.value.name);
            done();
          });
        });
      })
    })
    describe('with 3 args', function(){
      it('conditions + options + callback', function(done){
        name = 'findOneAndRemove + conds + options + cb';
        col.insert([{ name: name }, { name: 'a' }], { safe: true }, function (err) {
          assert.ifError(err);
          var m = mquery(col);
          m.findOneAndRemove({ name: name }, { sort: { name: 1 }}, function (err, res) {
            assert.ifError(err);
            assert.ok(res.value);
            assert.equal(name, res.value.name);
            done();
          });
        })
      })
    })
  })

  describe('exec', function(){
    beforeEach(function(done){
      col.insert([{ name: 'exec', age: 1 }, { name: 'exec', age: 2 }], done);
    })

    afterEach(function(done){
      mquery(col).remove(done);
    })

    it('requires an op', function(){
      assert.throws(function () {
        mquery().exec()
      }, /Missing query type/);
    })

    describe('find', function() {
      it('works', function(done){
        var m = mquery(col).find({ name: 'exec' });
        m.exec(function (err, docs) {
          assert.ifError(err);
          assert.equal(2, docs.length);
          done();
        })
      })

      it('works with readPreferences', function (done) {
        var m = mquery(col).find({ name: 'exec' });
        try {
          var rp = new require('mongodb').ReadPreference('primary');
          m.read(rp);
        } catch (e) {
          if (e.code === 'MODULE_NOT_FOUND')
            e = null;
          done(e);
          return;
        }
        m.exec(function (err, docs) {
          assert.ifError(err);
          assert.equal(2, docs.length);
          done();
        })
      })
    });

    it('findOne', function(done){
      var m = mquery(col).findOne({ age: 2 });
      m.exec(function (err, doc) {
        assert.ifError(err);
        assert.equal(2, doc.age);
        done();
      })
    })

    it('count', function(done){
      var m = mquery(col).count({ name: 'exec' });
      m.exec(function (err, count) {
        assert.ifError(err);
        assert.equal(2, count);
        done();
      })
    })

    it('distinct', function(done){
      var m = mquery({ name: 'exec' });
      m.collection(col);
      m.distinct('age');
      m.exec(function (err, array) {
        assert.ifError(err);
        assert.ok(Array.isArray(array));
        assert.equal(2, array.length);
        assert(~array.indexOf(1));
        assert(~array.indexOf(2));
        done();
      });
    })

    describe('update', function(){
      var num;

      it('with a callback', function(done){
        var m = mquery(col);
        m.where({ name: 'exec' })

        m.count(function (err, _num) {
          assert.ifError(err);
          num = _num;
          m.setOptions({ multi: true })
          m.update({ name: 'exec + update' });
          m.exec(function (err, res) {
            assert.ifError(err);
            assert.equal(num, res.result.n);
            mquery(col).find({ name: 'exec + update' }, function (err, docs) {
              assert.ifError(err);
              assert.equal(num, docs.length);
              done();
            })
          })
        })
      })

      describe('updateMany', function() {
        it('works', function(done) {
          mquery(col).updateMany({ name: 'exec' }, { name: 'test' }).
            exec(function(error) {
              assert.ifError(error);
              mquery(col).count({ name: 'test' }).exec(function(error, res) {
                assert.ifError(error);
                assert.equal(res, 2);
                done();
              });
            });
        });
      });

      describe('updateOne', function() {
        it('works', function(done) {
          mquery(col).updateOne({ name: 'exec' }, { name: 'test' }).
            exec(function(error) {
              assert.ifError(error);
              mquery(col).count({ name: 'test' }).exec(function(error, res) {
                assert.ifError(error);
                assert.equal(res, 1);
                done();
              });
            });
        });
      });

      describe('replaceOne', function() {
        it('works', function(done) {
          mquery(col).replaceOne({ name: 'exec' }, { name: 'test' }).
            exec(function(error) {
              assert.ifError(error);
              mquery(col).findOne({ name: 'test' }).exec(function(error, res) {
                assert.ifError(error);
                assert.equal(res.name, 'test');
                assert.ok(res.age == null);
                done();
              });
            });
        });
      });

      it('without a callback', function(done){
        var m = mquery(col)
        m.where({ name: 'exec + update' }).setOptions({ multi: true })
        m.update({ name: 'exec' });

        // unsafe write
        m.exec();

        setTimeout(function () {
          mquery(col).find({ name: 'exec' }, function (err, docs) {
            assert.ifError(err);
            assert.equal(2, docs.length);
            done();
          })
        }, 200)
      })
      it('preserves key ordering', function(done) {
        var m = mquery(col);

        var m2 = m.update({ _id : 'something' }, { '1' : 1, '2' : 2, '3' : 3});
        var doc = m2._updateForExec().$set;
        var count = 0;
        for (var i in doc) {
          if (count == 0) {
            assert.equal('1', i);
          } else if (count == 1) {
            assert.equal('2', i);
          } else if (count ==2) {
            assert.equal('3', i);
          }
          count++;
        }
        done();
      });
    })

    describe('remove', function(){
      it('with a callback', function(done){
        var m = mquery(col).where({ age: 2 }).remove();
        m.exec(function (err, res) {
          assert.ifError(err);
          assert.equal(1, res.result.n);
          done();
        })
      })

      it('without a callback', function(done){
        var m = mquery(col).where({ age: 1 }).remove();
        m.exec();

        setTimeout(function () {
          mquery(col).where('name', 'exec').count(function(err, num) {
            assert.equal(1, num);
            done();
          })
        }, 200)
      })
    })

    describe('deleteOne', function(){
      it('with a callback', function(done){
        var m = mquery(col).where({ age: { $gte: 0 } }).deleteOne();
        m.exec(function (err, res) {
          assert.ifError(err);
          assert.equal(res.result.n, 1);
          done();
        })
      })

      it('with justOne set', function(done){
        var m = mquery(col).where({ age: { $gte: 0 } }).
          // Should ignore `justOne`
          setOptions({ justOne: false }).
          deleteOne();
        m.exec(function (err, res) {
          assert.ifError(err);
          assert.equal(res.result.n, 1);
          done();
        })
      })
    })

    describe('deleteMany', function(){
      it('with a callback', function(done){
        var m = mquery(col).where({ age: { $gte: 0 } }).deleteMany();
        m.exec(function (err, res) {
          assert.ifError(err);
          assert.equal(res.result.n, 2);
          done();
        })
      })
    })

    describe('findOneAndUpdate', function(){
      it('with a callback', function(done){
        var m = mquery(col);
        m.findOneAndUpdate({ name: 'exec', age: 1 }, { $set: { name: 'findOneAndUpdate' }});
        m.exec(function (err, res) {
          assert.ifError(err);
          assert.equal('findOneAndUpdate', res.value.name);
          done();
        });
      })
    })

    describe('findOneAndRemove', function(){
      it('with a callback', function(done){
        var m = mquery(col);
        m.findOneAndRemove({ name: 'exec', age: 2 });
        m.exec(function (err, res) {
          assert.ifError(err);
          assert.equal('exec', res.value.name);
          assert.equal(2, res.value.age);
          mquery(col).count({ name: 'exec' }, function (err, num) {
            assert.ifError(err);
            assert.equal(1, num);
            done();
          });
        });
      })
    })
  })

  describe('setTraceFunction', function() {
    beforeEach(function(done){
      col.insert([{ name: 'trace', age: 93 }], done);
    })

    it('calls trace function when executing query', function(done) {
      var m = mquery(col);

      var resultTraceCalled;

      m.setTraceFunction(function (method, queryInfo) {
        try {
          assert.equal('findOne', method);
          assert.equal('trace', queryInfo.conditions.name);
        } catch (e) {
          done(e);
        }

        return function(err, result, millis) {
          try {
            assert.equal(93, result.age);
          } catch (e) {
            done(e);
          }
          resultTraceCalled = true;
        };
      });

      m.findOne({name: 'trace'}, function (err, doc) {
        assert.ifError(err);
        assert.equal(resultTraceCalled, true);
        assert.equal(93, doc.age);
        done();
      });
    });

    it('inherits trace function when calling toConstructor', function(done) {
      function traceFunction () { return function() {} };

      var tracedQuery = mquery().setTraceFunction(traceFunction).toConstructor();

      var query = tracedQuery();
      assert.equal(traceFunction, query._traceFunction);

      done();
    });
  });

  describe('thunk', function() {
    it('returns a function', function(done) {
      assert.equal('function', typeof mquery().thunk());
      done();
    });

    it('passes the fn arg to `exec`', function(done) {
      function cb() {}
      var m = mquery();

      m.exec = function testing(fn) {
        assert.equal(this, m);
        assert.equal(cb, fn);
        done();
      }

      m.thunk()(cb);
    });
  });

  describe('then', function() {
    before(function(done){
      col.insert([{ name: 'then', age: 1 }, { name: 'then', age: 2 }], done);
    })

    after(function(done){
      mquery(col).remove({ name: 'then' }).exec(done);
    })

    it('returns a promise A+ compat object', function(done) {
      var m = mquery(col).find();
      assert.equal('function', typeof m.then);
      done();
    });

    it('creates a promise that is resolved on success', function(done) {
      var promise = mquery(col).count({ name: 'then' }).then();
      promise.then(function(count){
        assert.equal(2, count);
        done();
      }, done);
    });

    it('supports exec() cb being called synchronously #66', function(done) {
      var query = mquery(col).count({ name: 'then' });
      query.exec = function(cb) {
        cb(null, 66);
      }

      query.then(success, done);
      function success(count){
        assert.equal(66, count);
        done();
      }
    });

    it('supports other Promise libs', function(done) {
      var bluebird = mquery.Promise;

      // hack for testing
      mquery.Promise = function P() {
        mquery.Promise = bluebird;
        this.then = function(x, y) {
          return x + y;
        }
      }

      var val = mquery(col).count({ name: 'exec' }).then(1, 2);
      assert.equal(val, 3);
      done();
    });
  });

  describe('stream', function() {
    before(function(done){
      col.insert([{ name: 'stream', age: 1 }, { name: 'stream', age: 2 }], done);
    })

    after(function(done){
      mquery(col).remove({ name: 'stream' }).exec(done);
    })

    describe('throws', function() {
      describe('if used with non-find operations', function() {
        var ops = ['update', 'findOneAndUpdate', 'remove', 'count', 'distinct'];

        ops.forEach(function(op) {
          assert.throws(function(){
            mquery(col)[op]().stream();
          });
        });
      });
    });

    it('returns a stream', function(done) {
      var stream = mquery(col).find({ name: 'stream' }).stream();
      var count = 0;
      var err;

      stream.on('data', function(doc){
        assert.equal('stream', doc.name);
        ++count;
      });

      stream.on('error', function(er) {
        err = er;
      });

      stream.on('end', function(){
        if (err) return done(err);
        assert.equal(2, count);
        done();
      });
    });
  });

  function noDistinct (type) {
    it('cannot be used with distinct()', function(done){
      assert.throws(function () {
        mquery().distinct('name')[type](4);
      }, new RegExp(type + ' cannot be used with distinct'));
      done();
    })
  }

  function no (method, type) {
    it('cannot be used with ' + method + '()', function(done){
      assert.throws(function () {
        mquery()[method]()[type](4);
      }, new RegExp(type + ' cannot be used with ' + method));
      done();
    })
  }

  // query internal

  describe('_updateForExec', function(){
    it('returns a clone of the update object with same key order #19', function(done){
      var update = {};
      update.$push = { n: { $each: [{x:10}], $slice: -1, $sort: {x:1}}};

      var q = mquery().update({ x: 1 }, update);

      // capture original key order
      var order = [];
      for (var key in q._update.$push.n) {
        order.push(key);
      }

      // compare output
      var doc = q._updateForExec();
      var i = 0;
      for (var key in doc.$push.n) {
        assert.equal(key, order[i]);
        i++;
      }

      done();
    })
  })
})
