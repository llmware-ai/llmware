
var mpath = require('./')
var Bench = require('benchmark');
var sha = require('child_process').exec("git log --pretty=format:'%h' -n 1", function (err, sha) {
  if (err) throw err;

  var fs = require('fs')
  var filename = __dirname + '/bench.out';
  var out = fs.createWriteStream(filename, { flags: 'a', encoding: 'utf8' });

  /**
   * test doc creator
   */

  function doc () {
    var o = { first: { second: { third: [3,{ name: 'aaron' }, 9] }}};
    o.comments = [
        { name: 'one' }
      , { name: 'two', _doc: { name: '2' }}
      , { name: 'three'
          , comments: [{},{ comments: [{val: 'twoo'}]}]
          , _doc: { name: '3', comments: [{},{ _doc: { comments: [{ val: 2 }] }}]  }}
    ];
    o.name = 'jiro';
    o.array = [
        { o: { array: [{x: {b: [4,6,8]}}, { y: 10} ] }}
      , { o: { array: [{x: {b: [1,2,3]}}, { x: {z: 10 }}, { x: {b: 'hi'}}] }}
      , { o: { array: [{x: {b: null }}, { x: { b: [null, 1]}}] }}
      , { o: { array: [{x: null }] }}
      , { o: { array: [{y: 3 }] }}
      , { o: { array: [3, 0, null] }}
      , { o: { name: 'ha' }}
    ];
    o.arr = [
        { arr: [{ a: { b: 47 }}, { a: { c: 48 }}, { d: 'yep' }] }
      , { yep: true }
    ]
    return o;
  }

  var o = doc();

  var s = new Bench.Suite;
  s.add('mpath.get("first", obj)', function () {
    mpath.get('first', o);
  })
  s.add('mpath.get("first.second", obj)', function () {
    mpath.get('first.second', o);
  })
  s.add('mpath.get("first.second.third.1.name", obj)', function () {
    mpath.get('first.second.third.1.name', o);
  })
  s.add('mpath.get("comments", obj)', function () {
    mpath.get('comments', o);
  })
  s.add('mpath.get("comments.1", obj)', function () {
    mpath.get('comments.1', o);
  })
  s.add('mpath.get("comments.2.name", obj)', function () {
    mpath.get('comments.2.name', o);
  })
  s.add('mpath.get("comments.2.comments.1.comments.0.val", obj)', function () {
    mpath.get('comments.2.comments.1.comments.0.val', o);
  })
  s.add('mpath.get("comments.name", obj)', function () {
    mpath.get('comments.name', o);
  })

  s.add('mpath.set("first", obj, val)', function () {
    mpath.set('first', o, 1);
  })
  s.add('mpath.set("first.second", obj, val)', function () {
    mpath.set('first.second', o, 1);
  })
  s.add('mpath.set("first.second.third.1.name", obj, val)', function () {
    mpath.set('first.second.third.1.name', o, 1);
  })
  s.add('mpath.set("comments", obj, val)', function () {
    mpath.set('comments', o, 1);
  })
  s.add('mpath.set("comments.1", obj, val)', function () {
    mpath.set('comments.1', o, 1);
  })
  s.add('mpath.set("comments.2.name", obj, val)', function () {
    mpath.set('comments.2.name', o, 1);
  })
  s.add('mpath.set("comments.2.comments.1.comments.0.val", obj, val)', function () {
    mpath.set('comments.2.comments.1.comments.0.val', o, 1);
  })
  s.add('mpath.set("comments.name", obj, val)', function () {
    mpath.set('comments.name', o, 1);
  })

  s.on('start', function () {
    console.log('starting...');
    out.write('*' + sha + ': ' + String(new Date()) + '\n');
  });
  s.on('cycle', function (e) {
    var s = String(e.target);
    console.log(s);
    out.write(s + '\n');
  })
  s.on('complete', function () {
    console.log('done')
    out.end('');
  })
  s.run()
})

