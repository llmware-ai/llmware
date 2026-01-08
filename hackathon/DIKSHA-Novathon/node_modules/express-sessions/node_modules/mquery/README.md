# mquery

`mquery` is a fluent mongodb query builder designed to run in multiple environments. As of v0.1, `mquery` runs on `Node.js` only with support for the MongoDB shell and browser environments planned for upcoming releases.

## Features

  - fluent query builder api
  - custom base query support
  - MongoDB 2.4 geoJSON support
  - method + option combinations validation
  - node.js driver compatibility
  - environment detection
  - [debug](https://github.com/visionmedia/debug) support
  - separated collection implementations for maximum flexibility

[![Build Status](https://travis-ci.org/aheckmann/mquery.png)](https://travis-ci.org/aheckmann/mquery)

## Use

```js
require('mongodb').connect(uri, function (err, db) {
  if (err) return handleError(err);

  // get a collection
  var collection = db.collection('artists');

  // pass it to the constructor
  mquery(collection).find({..}, callback);

  // or pass it to the collection method
  mquery().find({..}).collection(collection).exec(callback)

  // or better yet, create a custom query constructor that has it always set
  var Artist = mquery(collection).toConstructor();
  Artist().find(..).where(..).exec(callback)
})
```

`mquery` requires a collection object to work with. In the example above we just pass the collection object created using the official [MongoDB driver](https://github.com/mongodb/node-mongodb-native).


## Fluent API

- [find](#find)
- [findOne](#findOne)
- [count](#count)
- [remove](#remove)
- [update](#update)
- [findOneAndUpdate](#findoneandupdate)
- [findOneAndRemove](#findoneandremove)
- [distinct](#distinct)
- [exec](#exec)
- [stream](#stream)
- [all](#all)
- [and](#and)
- [box](#box)
- [circle](#circle)
- [elemMatch](#elemmatch)
- [equals](#equals)
- [exists](#exists)
- [geometry](#geometry)
- [gt](#gt)
- [gte](#gte)
- [in](#in)
- [intersects](#intersects)
- [lt](#lt)
- [lte](#lte)
- [maxDistance](#maxdistance)
- [mod](#mod)
- [ne](#ne)
- [nin](#nin)
- [nor](#nor)
- [near](#near)
- [or](#or)
- [polygon](#polygon)
- [regex](#regex)
- [select](#select)
- [selected](#selected)
- [selectedInclusively](#selectedinclusively)
- [selectedExclusively](#selectedexclusively)
- [size](#size)
- [slice](#slice)
- [within](#within)
- [where](#where)
- [$where](#where-1)
- [batchSize](#batchsize)
- [comment](#comment)
- [hint](#hint)
- [limit](#limit)
- [maxScan](#maxscan)
- [maxTime](#maxtime)
- [skip](#skip)
- [sort](#sort)
- [read](#read)
- [slaveOk](#slaveok)
- [snapshot](#snapshot)
- [tailable](#tailable)

## Helpers

- [collection](#collection)
- [then](#then)
- [thunk](#thunk)
- [merge](#mergeobject)
- [setOptions](#setoptionsoptions)
- [setTraceFunction](#settracefunctionfunc)
- [mquery.setGlobalTraceFunction](#mquerysetglobaltracefunctionfunc)
- [mquery.canMerge](#mquerycanmerge)
- [mquery.use$geoWithin](#mqueryusegeowithin)

### find()

Declares this query a _find_ query. Optionally pass a match clause and / or callback. If a callback is passed the query is executed.

```js
mquery().find()
mquery().find(match)
mquery().find(callback)
mquery().find(match, function (err, docs) {
  assert(Array.isArray(docs));
})
```

### findOne()

Declares this query a _findOne_ query. Optionally pass a match clause and / or callback. If a callback is passed the query is executed.

```js
mquery().findOne()
mquery().findOne(match)
mquery().findOne(callback)
mquery().findOne(match, function (err, doc) {
  if (doc) {
    // the document may not be found
    console.log(doc);
  }
})
```

### count()

Declares this query a _count_ query. Optionally pass a match clause and / or callback. If a callback is passed the query is executed.

```js
mquery().count()
mquery().count(match)
mquery().count(callback)
mquery().count(match, function (err, number){
  console.log('we found %d matching documents', number);
})
```

### remove()

Declares this query a _remove_ query. Optionally pass a match clause and / or callback. If a callback is passed the query is executed.

```js
mquery().remove()
mquery().remove(match)
mquery().remove(callback)
mquery().remove(match, function (err){})
```

### update()

Declares this query an _update_ query. Optionally pass an update document, match clause, options or callback. If a callback is passed, the query is executed. To force execution without passing a callback, run `update(true)`.

```js
mquery().update()
mquery().update(match, updateDocument)
mquery().update(match, updateDocument, options)

// the following all execute the command
mquery().update(callback)
mquery().update({$set: updateDocument, callback)
mquery().update(match, updateDocument, callback)
mquery().update(match, updateDocument, options, function (err, result){})
mquery().update(true) // executes (unsafe write)
```

##### the update document

All paths passed that are not `$atomic` operations will become `$set` ops. For example:

```js
mquery(collection).where({ _id: id }).update({ title: 'words' }, callback)
```

becomes

```js
collection.update({ _id: id }, { $set: { title: 'words' }}, callback)
```

This behavior can be overridden using the `overwrite` option (see below).

##### options

Options are passed to the `setOptions()` method.

- overwrite

Passing an empty object `{ }` as the update document will result in a no-op unless the `overwrite` option is passed. Without the `overwrite` option, the update operation will be ignored and the callback executed without sending the command to MongoDB to prevent accidently overwritting documents in the collection.

```js
var q = mquery(collection).where({ _id: id }).setOptions({ overwrite: true });
q.update({ }, callback); // overwrite with an empty doc
```

The `overwrite` option isn't just for empty objects, it also provides a means to override the default `$set` conversion and send the update document as is.

```js
// create a base query
var base = mquery({ _id: 108 }).collection(collection).toConstructor();

base().findOne(function (err, doc) {
  console.log(doc); // { _id: 108, name: 'cajon' })

  base().setOptions({ overwrite: true }).update({ changed: true }, function (err) {
    base.findOne(function (err, doc) {
      console.log(doc); // { _id: 108, changed: true }) - the doc was overwritten
    });
  });
})
```

- multi

Updates only modify a single document by default. To update multiple documents, set the `multi` option to `true`.

```js
mquery()
  .collection(coll)
  .update({ name: /^match/ }, { $addToSet: { arr: 4 }}, { multi: true }, callback)

// another way of doing it
mquery({ name: /^match/ })
  .collection(coll)
  .setOptions({ multi: true })
  .update({ $addToSet: { arr: 4 }}, callback)

// update multiple documents with an empty doc
var q = mquery(collection).where({ name: /^match/ });
q.setOptions({ multi: true, overwrite: true })
q.update({ });
q.update(function (err, result) {
  console.log(arguments);
});
```

### findOneAndUpdate()

Declares this query a _findAndModify_ with update query. Optionally pass a match clause, update document, options, or callback. If a callback is passed, the query is executed.

When executed, the first matching document (if found) is modified according to the update document and passed back to the callback.

##### options

Options are passed to the `setOptions()` method.

- `new`: boolean - true to return the modified document rather than the original. defaults to true
- `upsert`: boolean - creates the object if it doesn't exist. defaults to false
- `sort`: if multiple docs are found by the match condition, sets the sort order to choose which doc to update

```js
query.findOneAndUpdate()
query.findOneAndUpdate(updateDocument)
query.findOneAndUpdate(match, updateDocument)
query.findOneAndUpdate(match, updateDocument, options)

// the following all execute the command
query.findOneAndUpdate(callback)
query.findOneAndUpdate(updateDocument, callback)
query.findOneAndUpdate(match, updateDocument, callback)
query.findOneAndUpdate(match, updateDocument, options, function (err, doc) {
  if (doc) {
    // the document may not be found
    console.log(doc);
  }
})
 ```

### findOneAndRemove()

Declares this query a _findAndModify_ with remove query. Optionally pass a match clause, options, or callback. If a callback is passed, the query is executed.

When executed, the first matching document (if found) is modified according to the update document, removed from the collection and passed to the callback.

##### options

Options are passed to the `setOptions()` method.

- `sort`: if multiple docs are found by the condition, sets the sort order to choose which doc to modify and remove

```js
A.where().findOneAndRemove()
A.where().findOneAndRemove(match)
A.where().findOneAndRemove(match, options)

// the following all execute the command
A.where().findOneAndRemove(callback)
A.where().findOneAndRemove(match, callback)
A.where().findOneAndRemove(match, options, function (err, doc) {
  if (doc) {
    // the document may not be found
    console.log(doc);
  }
})
 ```

### distinct()

Declares this query a _distinct_ query. Optionally pass the distinct field, a match clause or callback. If a callback is passed the query is executed.

```js
mquery().distinct()
mquery().distinct(match)
mquery().distinct(match, field)
mquery().distinct(field)

// the following all execute the command
mquery().distinct(callback)
mquery().distinct(field, callback)
mquery().distinct(match, callback)
mquery().distinct(match, field, function (err, result) {
  console.log(result);
})
```

### exec()

Executes the query.

```js
mquery().findOne().where('route').intersects(polygon).exec(function (err, docs){})
```

### stream()

Executes the query and returns a stream.

```js
var stream = mquery().find().stream(options);
stream.on('data', cb);
stream.on('close', fn);
```

Note: this only works with `find()` operations.

Note: returns the stream object directly from the node-mongodb-native driver. (currently streams1 type stream). Any options will be passed along to the [driver method](http://mongodb.github.io/node-mongodb-native/api-generated/cursor.html#stream).

-------------

### all()

Specifies an `$all` query condition

```js
mquery().where('permission').all(['read', 'write'])
```

[MongoDB documentation](http://docs.mongodb.org/manual/reference/operator/all/)

### and()

Specifies arguments for an `$and` condition

```js
mquery().and([{ color: 'green' }, { status: 'ok' }])
```

[MongoDB documentation](http://docs.mongodb.org/manual/reference/operator/and/)

### box()

Specifies a `$box` condition

```js
var lowerLeft = [40.73083, -73.99756]
var upperRight= [40.741404,  -73.988135]

mquery().where('location').within().box(lowerLeft, upperRight)
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/box/)

### circle()

Specifies a `$center` or `$centerSphere` condition.

```js
var area = { center: [50, 50], radius: 10, unique: true }
query.where('loc').within().circle(area)
query.circle('loc', area);

// for spherical calculations
var area = { center: [50, 50], radius: 10, unique: true, spherical: true }
query.where('loc').within().circle(area)
query.circle('loc', area);
```

- [MongoDB Documentation - center](http://docs.mongodb.org/manual/reference/operator/center/)
- [MongoDB Documentation - centerSphere](http://docs.mongodb.org/manual/reference/operator/centerSphere/)

### elemMatch()

Specifies an `$elemMatch` condition

```js
query.where('comment').elemMatch({ author: 'autobot', votes: {$gte: 5}})

query.elemMatch('comment', function (elem) {
  elem.where('author').equals('autobot');
  elem.where('votes').gte(5);
})
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/elemMatch/)

### equals()

Specifies the complementary comparison value for the path specified with `where()`.

```js
mquery().where('age').equals(49);

// is the same as

mquery().where({ 'age': 49 });
```

### exists()

Specifies an `$exists` condition

```js
// { name: { $exists: true }}
mquery().where('name').exists()
mquery().where('name').exists(true)
mquery().exists('name')

// { name: { $exists: false }}
mquery().where('name').exists(false);
mquery().exists('name', false);
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/exists/)

### geometry()

Specifies a `$geometry` condition

```js
var polyA = [[[ 10, 20 ], [ 10, 40 ], [ 30, 40 ], [ 30, 20 ]]]
query.where('loc').within().geometry({ type: 'Polygon', coordinates: polyA })

// or
var polyB = [[ 0, 0 ], [ 1, 1 ]]
query.where('loc').within().geometry({ type: 'LineString', coordinates: polyB })

// or
var polyC = [ 0, 0 ]
query.where('loc').within().geometry({ type: 'Point', coordinates: polyC })

// or
query.where('loc').intersects().geometry({ type: 'Point', coordinates: polyC })

// or
query.where('loc').near().geometry({ type: 'Point', coordinates: [3,5] })
```

`geometry()` **must** come after `intersects()`, `within()`, or `near()`.

The `object` argument must contain `type` and `coordinates` properties.

- type `String`
- coordinates `Array`

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/geometry/)

### gt()

Specifies a `$gt` query condition.

```js
mquery().where('clicks').gt(999)
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/gt/)

### gte()

Specifies a `$gte` query condition.

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/gte/)

```js
mquery().where('clicks').gte(1000)
```

### in()

Specifies an `$in` query condition.

```js
mquery().where('author_id').in([3, 48901, 761])
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/in/)

### intersects()

Declares an `$geoIntersects` query for `geometry()`.

```js
query.where('path').intersects().geometry({
    type: 'LineString'
  , coordinates: [[180.0, 11.0], [180, 9.0]]
})

// geometry arguments are supported
query.where('path').intersects({
    type: 'LineString'
  , coordinates: [[180.0, 11.0], [180, 9.0]]
})
```

**Must** be used after `where()`.

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/geoIntersects/)

### lt()

Specifies a `$lt` query condition.

```js
mquery().where('clicks').lt(50)
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/lt/)

### lte()

Specifies a `$lte` query condition.

```js
mquery().where('clicks').lte(49)
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/lte/)

### maxDistance()

Specifies a `$maxDistance` query condition.

```js
mquery().where('location').near({ center: [139, 74.3] }).maxDistance(5)
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/maxDistance/)

### mod()

Specifies a `$mod` condition

```js
mquery().where('count').mod(2, 0)
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/mod/)

### ne()

Specifies a `$ne` query condition.

```js
mquery().where('status').ne('ok')
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/ne/)

### nin()

Specifies an `$nin` query condition.

```js
mquery().where('author_id').nin([3, 48901, 761])
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/nin/)

### nor()

Specifies arguments for an `$nor` condition.

```js
mquery().nor([{ color: 'green' }, { status: 'ok' }])
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/nor/)

### near()

Specifies arguments for a `$near` or `$nearSphere` condition.

These operators return documents sorted by distance.

#### Example

```js
query.where('loc').near({ center: [10, 10] });
query.where('loc').near({ center: [10, 10], maxDistance: 5 });
query.near('loc', { center: [10, 10], maxDistance: 5 });

// GeoJSON
query.where('loc').near({ center: { type: 'Point', coordinates: [10, 10] }});
query.where('loc').near({ center: { type: 'Point', coordinates: [10, 10] }, maxDistance: 5, spherical: true });
query.where('loc').near().geometry({ type: 'Point', coordinates: [10, 10] });

// For a $nearSphere condition, pass the `spherical` option.
query.near({ center: [10, 10], maxDistance: 5, spherical: true });
```

[MongoDB Documentation](http://www.mongodb.org/display/DOCS/Geospatial+Indexing)

### or()

Specifies arguments for an `$or` condition.

```js
mquery().or([{ color: 'red' }, { status: 'emergency' }])
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/or/)

### polygon()

Specifies a `$polygon` condition

```js
mquery().where('loc').within().polygon([10,20], [13, 25], [7,15])
mquery().polygon('loc', [10,20], [13, 25], [7,15])
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/polygon/)

### regex()

Specifies a `$regex` query condition.

```js
mquery().where('name').regex(/^sixstepsrecords/)
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/regex/)

### select()

Specifies which document fields to include or exclude

```js
// 1 means include, 0 means exclude
mquery().select({ name: 1, address: 1, _id: 0 })

// or

mquery().select('name address -_id')
```

##### String syntax

When passing a string, prefixing a path with `-` will flag that path as excluded. When a path does not have the `-` prefix, it is included.

```js
// include a and b, exclude c
query.select('a b -c');

// or you may use object notation, useful when
// you have keys already prefixed with a "-"
query.select({a: 1, b: 1, c: 0});
```

_Cannot be used with `distinct()`._

### selected()

Determines if the query has selected any fields.

```js
var query = mquery();
query.selected() // false
query.select('-name');
query.selected() // true
```

### selectedInclusively()

Determines if the query has selected any fields inclusively.

```js
var query = mquery().select('name');
query.selectedInclusively() // true

var query = mquery();
query.selected() // false
query.select('-name');
query.selectedInclusively() // false
query.selectedExclusively() // true
```

### selectedExclusively()

Determines if the query has selected any fields exclusively.

```js
var query = mquery().select('-name');
query.selectedExclusively() // true

var query = mquery();
query.selected() // false
query.select('name');
query.selectedExclusively() // false
query.selectedInclusively() // true
```

### size()

Specifies a `$size` query condition.

```js
mquery().where('someArray').size(6)
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/size/)

### slice()

Specifies a `$slice` projection for a `path`

```js
mquery().where('comments').slice(5)
mquery().where('comments').slice(-5)
mquery().where('comments').slice([-10, 5])
```

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/projection/slice/)

### within()

Sets a `$geoWithin` or `$within` argument for geo-spatial queries.

```js
mquery().within().box()
mquery().within().circle()
mquery().within().geometry()

mquery().where('loc').within({ center: [50,50], radius: 10, unique: true, spherical: true });
mquery().where('loc').within({ box: [[40.73, -73.9], [40.7, -73.988]] });
mquery().where('loc').within({ polygon: [[],[],[],[]] });

mquery().where('loc').within([], [], []) // polygon
mquery().where('loc').within([], []) // box
mquery().where('loc').within({ type: 'LineString', coordinates: [...] }); // geometry
```

As of mquery 2.0, `$geoWithin` is used by default. This impacts you if running MongoDB < 2.4. To alter this behavior, see [mquery.use$geoWithin](#mqueryusegeowithin).

**Must** be used after `where()`.

[MongoDB Documentation](http://docs.mongodb.org/manual/reference/operator/geoWithin/)

### where()

Specifies a `path` for use with chaining

```js
// instead of writing:
mquery().find({age: {$gte: 21, $lte: 65}});

// we can instead write:
mquery().where('age').gte(21).lte(65);

// passing query conditions is permitted too
mquery().find().where({ name: 'vonderful' })

// chaining
mquery()
.where('age').gte(21).lte(65)
.where({ 'name': /^vonderful/i })
.where('friends').slice(10)
.exec(callback)
```

### $where()

Specifies a `$where` condition.

Use `$where` when you need to select documents using a JavaScript expression.

```js
query.$where('this.comments.length > 10 || this.name.length > 5').exec(callback)

query.$where(function () {
  return this.comments.length > 10 || this.name.length > 5;
})
```

Only use `$where` when you have a condition that cannot be met using other MongoDB operators like `$lt`. Be sure to read about all of [its caveats](http://docs.mongodb.org/manual/reference/operator/where/) before using.

-----------

### batchSize()

Specifies the batchSize option.

```js
query.batchSize(100)
```

_Cannot be used with `distinct()`._

[MongoDB documentation](http://docs.mongodb.org/manual/reference/method/cursor.batchSize/)

### comment()

Specifies the comment option.

```js
query.comment('login query');
```

_Cannot be used with `distinct()`._

[MongoDB documentation](http://docs.mongodb.org/manual/reference/operator/)

### hint()

Sets query hints.

```js
mquery().hint({ indexA: 1, indexB: -1 })
```

_Cannot be used with `distinct()`._

[MongoDB documentation](http://docs.mongodb.org/manual/reference/operator/hint/)

### limit()

Specifies the limit option.

```js
query.limit(20)
```

_Cannot be used with `distinct()`._

[MongoDB documentation](http://docs.mongodb.org/manual/reference/method/cursor.limit/)

### maxScan()

Specifies the maxScan option.

```js
query.maxScan(100)
```

_Cannot be used with `distinct()`._

[MongoDB documentation](http://docs.mongodb.org/manual/reference/operator/maxScan/)

### maxTime()

Specifies the maxTimeMS option.

```js
query.maxTime(100)
```

[MongoDB documentation](http://docs.mongodb.org/manual/reference/method/cursor.maxTimeMS/)


### skip()

Specifies the skip option.

```js
query.skip(100).limit(20)
```

_Cannot be used with `distinct()`._

[MongoDB documentation](http://docs.mongodb.org/manual/reference/method/cursor.skip/)

### sort()

Sets the query sort order.

If an object is passed, key values allowed are `asc`, `desc`, `ascending`, `descending`, `1`, and `-1`.

If a string is passed, it must be a space delimited list of path names. The sort order of each path is ascending unless the path name is prefixed with `-` which will be treated as descending.

```js
// these are equivalent
query.sort({ field: 'asc', test: -1 });
query.sort('field -test');
```

_Cannot be used with `distinct()`._

[MongoDB documentation](http://docs.mongodb.org/manual/reference/method/cursor.sort/)

### read()

Sets the readPreference option for the query.

```js
mquery().read('primary')
mquery().read('p')  // same as primary

mquery().read('primaryPreferred')
mquery().read('pp') // same as primaryPreferred

mquery().read('secondary')
mquery().read('s')  // same as secondary

mquery().read('secondaryPreferred')
mquery().read('sp') // same as secondaryPreferred

mquery().read('nearest')
mquery().read('n')  // same as nearest
```

##### Preferences:

- `primary` - (default) Read from primary only. Operations will produce an error if primary is unavailable. Cannot be combined with tags.
- `secondary` - Read from secondary if available, otherwise error.
- `primaryPreferred` - Read from primary if available, otherwise a secondary.
- `secondaryPreferred` - Read from a secondary if available, otherwise read from the primary.
- `nearest` - All operations read from among the nearest candidates, but unlike other modes, this option will include both the primary and all secondaries in the random selection.

Aliases

- `p`   primary
- `pp`  primaryPreferred
- `s`   secondary
- `sp`  secondaryPreferred
- `n`   nearest

##### Preference Tags:

To keep the separation of concerns between `mquery` and your driver
clean, `mquery#read()` no longer handles specifying a second `tags` argument as of version 0.5.
If you need to specify tags, pass any non-string argument as the first argument.
`mquery` will pass this argument untouched to your collections methods later.
For example:

```js
// example of specifying tags using the Node.js driver
var ReadPref = require('mongodb').ReadPreference;
var preference = new ReadPref('secondary', [{ dc:'sf', s: 1 },{ dc:'ma', s: 2 }]);
mquery(..).read(preference).exec();
```

Read more about how to use read preferences [here](http://docs.mongodb.org/manual/applications/replication/#read-preference) and [here](http://mongodb.github.com/node-mongodb-native/driver-articles/anintroductionto1_1and2_2.html#read-preferences).

### slaveOk()

Sets the slaveOk option. `true` allows reading from secondaries.

**deprecated** use [read()](#read) preferences instead if on mongodb >= 2.2

```js
query.slaveOk() // true
query.slaveOk(true)
query.slaveOk(false)
```

[MongoDB documentation](http://docs.mongodb.org/manual/reference/method/rs.slaveOk/)

### snapshot()

Specifies this query as a snapshot query.

```js
mquery().snapshot() // true
mquery().snapshot(true)
mquery().snapshot(false)
```

_Cannot be used with `distinct()`._

[MongoDB documentation](http://docs.mongodb.org/manual/reference/operator/snapshot/)

### tailable()

Sets tailable option.

```js
mquery().tailable() <== true
mquery().tailable(true)
mquery().tailable(false)
```

_Cannot be used with `distinct()`._

[MongoDB Documentation](http://docs.mongodb.org/manual/tutorial/create-tailable-cursor/)

## Helpers

### collection()

Sets the querys collection.

```js
mquery().collection(aCollection)
```

### then()

Executes the query and returns a promise which will be resolved with the query results or rejected if the query responds with an error.

```js
mquery().find(..).then(success, error);
```

This is very useful when combined with [co](https://github.com/visionmedia/co) or [koa](https://github.com/koajs/koa), which automatically resolve promise-like objects for you.

```js
co(function*(){
  var doc = yield mquery().findOne({ _id: 499 });
  console.log(doc); // { _id: 499, name: 'amazing', .. }
})();
```

_NOTE_:
The returned promise is a [bluebird](https://github.com/petkaantonov/bluebird/) promise but this is customizable. If you want to
use your favorite promise library, simply set `mquery.Promise = YourPromiseConstructor`.
Your `Promise` must be [promises A+](http://promisesaplus.com/) compliant.

### thunk()

Returns a thunk which when called runs the query's `exec` method passing the results to the callback.

```js
var thunk = mquery(collection).find({..}).thunk();

thunk(function(err, results) {

})
```

### merge(object)

Merges other mquery or match condition objects into this one. When an mquery instance is passed, its match conditions, field selection and options are merged.

```js
var drum = mquery({ type: 'drum' }).collection(instruments);
var redDrum = mquery({ color: 'red' }).merge(drum);
redDrum.count(function (err, n) {
  console.log('there are %d red drums', n);
})
```

Internally uses `mquery.canMerge` to determine validity.

### setOptions(options)

Sets query options.

```js
mquery().setOptions({ collection: coll, limit: 20 })
```

##### options

- [tailable](#tailable) *
- [sort](#sort) *
- [limit](#limit) *
- [skip](#skip) *
- [maxScan](#maxscan) *
- [maxTime](#maxtime) *
- [batchSize](#batchSize) *
- [comment](#comment) *
- [snapshot](#snapshot) *
- [hint](#hint) *
- [slaveOk](#slaveOk) *
- [safe](http://docs.mongodb.org/manual/reference/write-concern/): Boolean - passed through to the collection. Setting to `true` is equivalent to `{ w: 1 }`
- [collection](#collection): the collection to query against

_* denotes a query helper method is also available_

### setTraceFunction(func)

Set a function to trace this query. Useful for profiling or logging.

```js
function traceFunction (method, queryInfo, query) {
  console.log('starting ' + method + ' query');

  return function (err, result, millis) {
    console.log('finished ' + method + ' query in ' + millis + 'ms');
  };
}

mquery().setTraceFunction(traceFunction).findOne({name: 'Joe'}, cb);
```

The trace function is passed (method, queryInfo, query)

- method is the name of the method being called (e.g. findOne)
- queryInfo contains information about the query:
 - conditions: query conditions/criteria
 - options: options such as sort, fields, etc
 - doc: document being updated
- query is the query object

The trace function should return a callback function which accepts:
- err: error, if any
- result: result, if any
- millis: time spent waiting for query result

NOTE: stream requests are not traced.

### mquery.setGlobalTraceFunction(func)

Similar to `setTraceFunction()` but automatically applied to all queries.

```js
mquery.setTraceFunction(traceFunction);
```

### mquery.canMerge(conditions)

Determines if `conditions` can be merged using `mquery().merge()`.

```js
var query = mquery({ type: 'drum' });
var okToMerge = mquery.canMerge(anObject)
if (okToMerge) {
  query.merge(anObject);
}
```

## mquery.use$geoWithin

MongoDB 2.4 introduced the `$geoWithin` operator which replaces and is 100% backward compatible with `$within`. As of mquery 0.2, we default to using `$geoWithin` for all `within()` calls.

If you are running MongoDB < 2.4 this will be problematic. To force `mquery` to be backward compatible and always use `$within`, set the `mquery.use$geoWithin` flag to `false`.

```js
mquery.use$geoWithin = false;
```

## Custom Base Queries

Often times we want custom base queries that encapsulate predefined criteria. With `mquery` this is easy. First create the query you want to reuse and call its `toConstructor()` method which returns a new subclass of `mquery` that retains all options and criteria of the original.

```js
var greatMovies = mquery(movieCollection).where('rating').gte(4.5).toConstructor();

// use it!
greatMovies().count(function (err, n) {
  console.log('There are %d great movies', n);
});

greatMovies().where({ name: /^Life/ }).select('name').find(function (err, docs) {
  console.log(docs);
});
```

## Validation

Method and options combinations are checked for validity at runtime to prevent creation of invalid query constructs. For example, a `distinct` query does not support specifying options like `hint` or field selection. In this case an error will be thrown so you can catch these mistakes in development.

## Debug support

Debug mode is provided through the use of the [debug](https://github.com/visionmedia/debug) module. To enable:

    DEBUG=mquery node yourprogram.js

Read the debug module documentation for more details.

## General compatibility

#### ObjectIds

`mquery` clones query arguments before passing them to a `collection` method for execution.
This prevents accidental side-affects to the objects you pass.
To clone `ObjectIds` we need to make some assumptions.

First, to check if an object is an `ObjectId`, we check its constructors name. If it matches either
`ObjectId` or `ObjectID` we clone it.

To clone `ObjectIds`, we call its optional `clone` method. If a `clone` method does not exist, we fall
back to calling `new obj.constructor(obj.id)`. We assume, for compatibility with the
Node.js driver, that the `ObjectId` instance has a public `id` property and that
when creating an `ObjectId` instance we can pass that `id` as an argument.

#### Read Preferences

`mquery` supports specifying [Read Preferences]() to control from which MongoDB node your query will read.
The Read Preferences spec also support specifying tags. To pass tags, some
drivers (Node.js driver) require passing a special constructor that handles both the read preference and its tags.
If you need to specify tags, pass an instance of your drivers ReadPreference constructor or roll your own. `mquery` will store whatever you provide and pass later to your collection during execution.

## Future goals

  - mongo shell compatibility
  - browser compatibility

## Installation

    $ npm install mquery

## License

[MIT](https://github.com/aheckmann/mquery/blob/master/LICENSE)

