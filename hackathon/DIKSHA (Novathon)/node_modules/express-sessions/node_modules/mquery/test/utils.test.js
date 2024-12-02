
var utils = require('../lib/utils');
var assert = require('assert');

var mongo;
try {
  mongo = new require('mongodb');
} catch (e) {}

describe('lib/utils', function() {
  describe('clone', function() {
    it('clones constructors named ObjectId', function(done) {
      function ObjectId (id) {
        this.id = id;
      }

      var o1 = new ObjectId('1234');
      var o2 = utils.clone(o1);
      assert.ok(o2 instanceof ObjectId);

      done();
    });

    it('clones constructors named ObjectID', function(done) {
      function ObjectID (id) {
        this.id = id;
      }

      var o1 = new ObjectID('1234');
      var o2 = utils.clone(o1);

      assert.ok(o2 instanceof ObjectID);
      done();
    });

    it('does not clone constructors named ObjectIdd', function(done) {
      function ObjectIdd (id) {
        this.id = id;
      }

      var o1 = new ObjectIdd('1234');
      var o2 = utils.clone(o1);
      assert.ok(!(o2 instanceof ObjectIdd));

      done();
    });

    it('optionally clones ObjectId constructors using its clone method', function(done) {
      function ObjectID (id) {
        this.id = id;
        this.cloned = false;
      }

      ObjectID.prototype.clone = function () {
        var ret = new ObjectID(this.id);
        ret.cloned = true;
        return ret;
      }

      var id = 1234;
      var o1 = new ObjectID(id);
      assert.equal(id, o1.id);
      assert.equal(false, o1.cloned);

      var o2 = utils.clone(o1);
      assert.ok(o2 instanceof ObjectID);
      assert.equal(id, o2.id);
      assert.ok(o2.cloned);
      done();
    });

    it('clones mongodb.ReadPreferences', function (done) {
      if (!mongo) return done();

      var tags = [
        {dc: 'tag1'}
      ];
      var prefs = [
        new mongo.ReadPreference("primary"),
        new mongo.ReadPreference(mongo.ReadPreference.PRIMARY_PREFERRED),
        new mongo.ReadPreference("primary", tags),
        mongo.ReadPreference("primary", tags)
      ];

      var prefsCloned = utils.clone(prefs);

      for (var i = 0; i < prefsCloned.length; i++) {
        assert.notEqual(prefs[i], prefsCloned[i]);
        assert.ok(prefsCloned[i] instanceof mongo.ReadPreference);
        assert.ok(prefsCloned[i].isValid());
        if (prefs[i].tags) {
          assert.ok(prefsCloned[i].tags);
          assert.notEqual(prefs[i].tags, prefsCloned[i].tags);
          assert.notEqual(prefs[i].tags[0], prefsCloned[i].tags[0]);
        } else {
          assert.equal(prefsCloned[i].tags, null);
        }
      }

      done();
    });

    it('clones mongodb.Binary', function(done){
      if (!mongo) return done();

      var buf = new Buffer('hi');
      var binary= new mongo.Binary(buf, 2);
      var clone = utils.clone(binary);
      assert.equal(binary.sub_type, clone.sub_type);
      assert.equal(String(binary.buffer), String(buf));
      assert.ok(binary !== clone);
      done();
    })

    it('handles objects with no constructor', function(done) {
      var name ='335';

      var o = Object.create(null);
      o.name = name;

      var clone;
      assert.doesNotThrow(function() {
        clone = utils.clone(o);
      });

      assert.equal(name, clone.name);
      assert.ok(o != clone);
      done();
    });

    it('handles buffers', function(done){
      var buff = new Buffer(10);
      buff.fill(1);
      var clone = utils.clone(buff);

      for (var i = 0; i < buff.length; i++) {
        assert.equal(buff[i], clone[i]);
      }

      done();
    });
  });
});
