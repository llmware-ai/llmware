<a name="2.2.34"></a>
## [2.2.34](https://github.com/mongodb/node-mongodb-native/compare/v2.2.33...v2.2.34) (2018-01-03)


### Bug Fixes

* **collection:** allow { upsert: 1 } for findOneAndUpdate() and update() ([#1580](https://github.com/mongodb/node-mongodb-native/issues/1580)) ([0f338c8](https://github.com/mongodb/node-mongodb-native/commit/0f338c8)), closes [Automattic/mongoose#5839](https://github.com/Automattic/mongoose/issues/5839)
* **GridFS:** fix TypeError: doc.data.length is not a function ([811de0c](https://github.com/mongodb/node-mongodb-native/commit/811de0c))
* **import:** adds missing import to lib/authenticate.js ([10db9a2](https://github.com/mongodb/node-mongodb-native/commit/10db9a2))
* **list-collections:** ensure default of primary ReadPreference ([0935306](https://github.com/mongodb/node-mongodb-native/commit/0935306))


### Features

* **ss:** adds missing ssl options ssl options for `ciphers` and `ecdhCurve` ([bd4fb53](https://github.com/mongodb/node-mongodb-native/commit/bd4fb53))
* **url parser:** add dns seedlist support ([2d357bc](https://github.com/mongodb/node-mongodb-native/commit/2d357bc))



<a name="2.2.33"></a>
## [2.2.33](https://github.com/mongodb/node-mongodb-native/compare/v2.2.32...v2.2.33) (2017-10-12)



<a name="2.2.32"></a>
## [2.2.32](https://github.com/mongodb/node-mongodb-native/compare/v2.2.31...v2.2.32) (2017-10-12)


### Bug Fixes

* **aggregation:** ensure that the `cursor` key is always present ([beccc83](https://github.com/mongodb/node-mongodb-native/commit/beccc83))
* **collection:** allow passing `noCursorTimeout` as an option to `find()` ([7bd839b](https://github.com/mongodb/node-mongodb-native/commit/7bd839b))
* **cursor:** `hasNext` should propagate errors when using callback ([129d540](https://github.com/mongodb/node-mongodb-native/commit/129d540))
* **db:** bubble up `reconnectFailed` event from Server topology ([d159eab](https://github.com/mongodb/node-mongodb-native/commit/d159eab))



<a name="2.2.31"></a>
## [2.2.31](https://github.com/mongodb/node-mongodb-native/compare/v0.9.3...v2.2.31) (2017-08-08)


### Bug Fixes

* **bulk:** bulk operations should not throw an error on empty batch ([84433e7](https://github.com/mongodb/node-mongodb-native/commit/84433e7))
* **url-parser:** ensure user options are applied to parsing ([7116ea4](https://github.com/mongodb/node-mongodb-native/commit/7116ea4))


### Features

* **auth:** allow auth option in MongoClient.connect ([fd686d7](https://github.com/mongodb/node-mongodb-native/commit/fd686d7))
* **MongoClient:** add `appname` to list of valid option names ([bd4bdf6](https://github.com/mongodb/node-mongodb-native/commit/bd4bdf6))



<a name="2.2.29"></a>
## 2.2.29 (2017-06-19)



<a name="2.2.28"></a>
## 2.2.28 (2017-06-02)



<a name="2.2.27"></a>
## 2.2.27 (2017-05-22)



<a name="2.2.26"></a>
## 2.2.26 (2017-04-18)


### Bug Fixes

* **db:** don't remove database name if collectionName == dbName ([ec88b07](https://github.com/mongodb/node-mongodb-native/commit/ec88b07))



<a name="2.2.25"></a>
## 2.2.25 (2017-03-17)


### Bug Fixes

* **collection:** pass batchSize to AggregationCursor ([b5c188b](https://github.com/mongodb/node-mongodb-native/commit/b5c188b))
* **UnorderedBulkOperation:** push correct index for INSERT ops ([e53d02c](https://github.com/mongodb/node-mongodb-native/commit/e53d02c))
* don't rely on global toString() for checking if object ([6ef70b8](https://github.com/mongodb/node-mongodb-native/commit/6ef70b8)), closes [tmpvar/jsdom#1752](https://github.com/tmpvar/jsdom/issues/1752) [Automattic/mongoose#5033](https://github.com/Automattic/mongoose/issues/5033)



<a name="2.2.24"></a>
## 2.2.24 (2017-02-14)



<a name="2.2.23"></a>
## 2.2.23 (2017-02-13)



<a name="2.2.22"></a>
## 2.2.22 (2017-01-24)



<a name="2.2.21"></a>
## 2.2.21 (2017-01-13)



<a name="2.2.20"></a>
## 2.2.20 (2017-01-11)



<a name="2.2.19"></a>
## 2.2.19 (2017-01-03)



<a name="2.2.18"></a>
## 2.2.18 (2017-01-03)



<a name="2.2.17"></a>
## 2.2.17 (2017-01-03)



<a name="2.2.16"></a>
## 2.2.16 (2016-12-13)



<a name="2.2.15"></a>
## 2.2.15 (2016-12-10)



<a name="2.2.14"></a>
## 2.2.14 (2016-12-08)



<a name="2.2.13"></a>
## 2.2.13 (2016-11-30)



<a name="2.2.12"></a>
## 2.2.12 (2016-11-29)



<a name="2.2.11"></a>
## 2.2.11 (2016-10-21)



<a name="2.2.10"></a>
## 2.2.10 (2016-09-15)


### Bug Fixes

* **db:** don't fall back to insert if 'IndexOptionsConflict' error ([a26fe5f](https://github.com/mongodb/node-mongodb-native/commit/a26fe5f)), closes [Automattic/mongoose#4459](https://github.com/Automattic/mongoose/issues/4459)



<a name="2.2.9"></a>
## 2.2.9 (2016-08-29)


### Bug Fixes

* **collection:** don't treat ObjectId as object for mapReduce scope ([a1ca631](https://github.com/mongodb/node-mongodb-native/commit/a1ca631))



<a name="2.2.8"></a>
## 2.2.8 (2016-08-23)



<a name="2.2.6"></a>
## 2.2.6 (2016-08-16)


### Bug Fixes

* allow passing in an array of tags to ReadPreference constructor ([5b8067c](https://github.com/mongodb/node-mongodb-native/commit/5b8067c))



<a name="2.2.5"></a>
## 2.2.5 (2016-07-28)



<a name="2.2.4"></a>
## 2.2.4 (2016-07-19)



<a name="2.2.3"></a>
## 2.2.3 (2016-07-19)



<a name="2.2.2"></a>
## 2.2.2 (2016-07-15)



<a name="2.2.1"></a>
## 2.2.1 (2016-07-11)



<a name="2.2.0"></a>
# 2.2.0 (2016-07-08)



<a name="2.2.0-alpha2"></a>
# 2.2.0-alpha2 (2016-07-06)



<a name="2.2.0-alpha1"></a>
# 2.2.0-alpha1 (2016-07-05)



<a name="2.1.21"></a>
## 2.1.21 (2016-05-30)



<a name="2.1.18"></a>
## 2.1.18 (2016-04-27)



<a name="2.1.17"></a>
## 2.1.17 (2016-04-26)



<a name="2.1.16"></a>
## 2.1.16 (2016-04-07)



<a name="2.1.15"></a>
## 2.1.15 (2016-04-06)



<a name="2.1.14"></a>
## 2.1.14 (2016-03-30)



<a name="2.1.13"></a>
## 2.1.13 (2016-03-29)



<a name="2.1.12"></a>
## 2.1.12 (2016-03-29)



<a name="2.1.11"></a>
## 2.1.11 (2016-03-23)



<a name="2.1.10"></a>
## 2.1.10 (2016-03-21)



<a name="2.1.9"></a>
## 2.1.9 (2016-03-16)



<a name="2.1.8"></a>
## 2.1.8 (2016-03-14)


### Bug Fixes

* **db:** one possible fix for Automattic/mongoose[#3864](https://github.com/mongodb/node-mongodb-native/issues/3864) ([4712aab](https://github.com/mongodb/node-mongodb-native/commit/4712aab))



<a name="2.1.7"></a>
## 2.1.7 (2016-02-09)



<a name="2.1.6"></a>
## 2.1.6 (2016-02-05)



<a name="2.1.5"></a>
## 2.1.5 (2016-02-04)



<a name="2.1.4"></a>
## 2.1.4 (2016-01-14)



<a name="2.1.3"></a>
## 2.1.3 (2016-01-04)



<a name="2.1.2"></a>
## 2.1.2 (2015-12-23)



<a name="2.1.1"></a>
## 2.1.1 (2015-12-13)



<a name="2.0.50"></a>
## 2.0.50 (2015-12-06)



<a name="2.1.0"></a>
# 2.1.0 (2015-12-06)


### Bug Fixes

* **url_parser:** readPreference option ([db57c6b](https://github.com/mongodb/node-mongodb-native/commit/db57c6b))



<a name="2.0.49"></a>
## 2.0.49 (2015-11-20)



<a name="2.1.0-rc1"></a>
# 2.1.0-rc1 (2015-11-16)



<a name="2.0.48"></a>
## 2.0.48 (2015-11-07)



<a name="2.0.47"></a>
## 2.0.47 (2015-10-28)



<a name="2.0.46"></a>
## 2.0.46 (2015-10-15)



<a name="2.0.45"></a>
## 2.0.45 (2015-09-30)



<a name="2.0.44"></a>
## 2.0.44 (2015-09-28)



<a name="2.0.43"></a>
## 2.0.43 (2015-09-14)



<a name="2.0.42"></a>
## 2.0.42 (2015-08-18)



<a name="2.0.40"></a>
## 2.0.40 (2015-08-06)



<a name="2.0.39"></a>
## 2.0.39 (2015-07-14)



<a name="2.0.38"></a>
## 2.0.38 (2015-07-14)



<a name="2.0.37"></a>
## 2.0.37 (2015-07-14)



<a name="2.0.36"></a>
## 2.0.36 (2015-07-07)



<a name="2.0.35"></a>
## 2.0.35 (2015-06-22)



<a name="2.0.34"></a>
## 2.0.34 (2015-06-17)



<a name="2.0.33"></a>
## 2.0.33 (2015-05-19)



<a name="2.0.32"></a>
## 2.0.32 (2015-05-18)



<a name="2.0.31"></a>
## 2.0.31 (2015-05-08)



<a name="2.0.30"></a>
## 2.0.30 (2015-05-07)



<a name="2.0.29"></a>
## 2.0.29 (2015-05-07)



<a name="2.0.28"></a>
## 2.0.28 (2015-04-24)



<a name="2.0.27"></a>
## 2.0.27 (2015-04-07)



<a name="2.0.26"></a>
## 2.0.26 (2015-04-07)



<a name="2.0.25"></a>
## 2.0.25 (2015-03-26)



<a name="2.0.24"></a>
## 2.0.24 (2015-03-24)



<a name="2.0.23"></a>
## 2.0.23 (2015-03-21)



<a name="2.0.22"></a>
## 2.0.22 (2015-03-16)



<a name="2.0.21"></a>
## 2.0.21 (2015-03-06)



<a name="2.0.20"></a>
## 2.0.20 (2015-03-04)



<a name="2.0.19"></a>
## 2.0.19 (2015-03-03)



<a name="2.0.18"></a>
## 2.0.18 (2015-02-27)



<a name="2.0.17"></a>
## 2.0.17 (2015-02-27)



<a name="2.0.16"></a>
## 2.0.16 (2015-02-16)



<a name="2.0.15"></a>
## 2.0.15 (2015-02-02)



<a name="2.0.14"></a>
## 2.0.14 (2015-01-21)



<a name="2.0.13"></a>
## 2.0.13 (2015-01-08)



<a name="2.0.12"></a>
## 2.0.12 (2014-12-22)



<a name="2.0.11"></a>
## 2.0.11 (2014-12-18)



<a name="2.0.10"></a>
## 2.0.10 (2014-12-18)



<a name="2.0.9"></a>
## 2.0.9 (2014-12-02)



<a name="2.0.8"></a>
## 2.0.8 (2014-11-28)



<a name="2.0.7"></a>
## 2.0.7 (2014-11-20)



<a name="2.0.5"></a>
## 2.0.5 (2014-10-29)



<a name="2.0.4"></a>
## 2.0.4 (2014-10-23)



<a name="2.0.3"></a>
## 2.0.3 (2014-10-14)



<a name="2.0.2"></a>
## 2.0.2 (2014-10-08)



<a name="2.0.1"></a>
## 2.0.1 (2014-10-07)



<a name="2.0.0"></a>
# 2.0.0 (2014-10-07)



<a name="1.4.8"></a>
## 1.4.8 (2014-08-01)



<a name="1.4.7"></a>
## 1.4.7 (2014-06-18)



<a name="1.4.5"></a>
## 1.4.5 (2014-05-20)



<a name="1.4.4"></a>
## 1.4.4 (2014-05-13)



<a name="1.4.3"></a>
## 1.4.3 (2014-05-01)



<a name="1.4.2"></a>
## 1.4.2 (2014-04-15)



<a name="1.4.1"></a>
## 1.4.1 (2014-04-09)



<a name="1.4.0"></a>
# 1.4.0 (2014-04-03)



<a name="1.4.0-RC10"></a>
# 1.4.0-RC10 (2014-03-22)



<a name="1.4.0-RC9"></a>
# 1.4.0-RC9 (2014-03-12)



<a name="1.4.0-RC4"></a>
# 1.4.0-RC4 (2014-01-10)



<a name="1.3.23"></a>
## 1.3.23 (2013-12-13)



<a name="1.3.22"></a>
## 1.3.22 (2013-12-11)



<a name="1.3.21"></a>
## 1.3.21 (2013-12-11)



<a name="1.4.0-RC2"></a>
# 1.4.0-RC2 (2013-12-10)



<a name="1.4.0-RC1"></a>
# 1.4.0-RC1 (2013-12-10)



<a name="1.3.19"></a>
## 1.3.19 (2013-08-21)



<a name="1.3.17"></a>
## 1.3.17 (2013-08-07)



<a name="1.3.16"></a>
## 1.3.16 (2013-08-05)



<a name="1.3.15"></a>
## 1.3.15 (2013-08-01)



<a name="1.3.14"></a>
## 1.3.14 (2013-08-01)



<a name="1.3.13"></a>
## 1.3.13 (2013-07-31)



<a name="1.3.11"></a>
## 1.3.11 (2013-07-04)



<a name="1.3.10"></a>
## 1.3.10 (2013-06-17)



<a name="1.3.9"></a>
## 1.3.9 (2013-06-06)



<a name="1.3.8"></a>
## 1.3.8 (2013-05-31)



<a name="1.3.7"></a>
## 1.3.7 (2013-05-29)



<a name="1.3.6"></a>
## 1.3.6 (2013-05-27)



<a name="1.3.5"></a>
## 1.3.5 (2013-05-14)



<a name="1.3.4"></a>
## 1.3.4 (2013-05-14)



<a name="1.3.3"></a>
## 1.3.3 (2013-05-09)



<a name="1.3.2"></a>
## 1.3.2 (2013-05-08)



<a name="1.3.1"></a>
## 1.3.1 (2013-05-06)



<a name="1.3.0"></a>
# 1.3.0 (2013-04-26)



<a name="1.2.14"></a>
## 1.2.14 (2013-03-14)



<a name="1.2.13"></a>
## 1.2.13 (2013-02-22)



<a name="1.2.12"></a>
## 1.2.12 (2013-02-13)



<a name="1.2.11"></a>
## 1.2.11 (2013-01-29)



<a name="1.2.10"></a>
## 1.2.10 (2013-01-25)



<a name="1.2.9"></a>
## 1.2.9 (2013-01-15)



<a name="1.2.8"></a>
## 1.2.8 (2013-01-07)



<a name="1.2.7"></a>
## 1.2.7 (2012-12-23)



<a name="1.2.6"></a>
## 1.2.6 (2012-12-19)



<a name="1.2.5"></a>
## 1.2.5 (2012-12-12)



<a name="1.2.4"></a>
## 1.2.4 (2012-12-11)



<a name="1.2.3"></a>
## 1.2.3 (2012-12-10)



<a name="1.2.0"></a>
# 1.2.0 (2012-11-27)



<a name="1.1.11"></a>
## 1.1.11 (2012-10-10)



<a name="1.1.8"></a>
## 1.1.8 (2012-10-01)



<a name="1.1.7"></a>
## 1.1.7 (2012-09-10)



<a name="1.1.5"></a>
## 1.1.5 (2012-08-29)



<a name="1.0.2"></a>
## 1.0.2 (2012-05-15)



<a name="0.9.9"></a>
## 0.9.9 (2012-02-13)



<a name="0.9.8"></a>
## 0.9.8 (2012-01-17)



<a name="0.9.7"></a>
## 0.9.7 (2011-11-10)



<a name="0.6.8"></a>
## 0.6.8 (2011-08-01)



<a name="0.9.6-5"></a>
## 0.9.6-5 (2011-07-06)



<a name="0.9.5"></a>
## 0.9.5 (2011-06-20)



<a name="0.9.4"></a>
## 0.9.4 (2011-04-29)



<a name="0.9.3"></a>
## 0.9.3 (2011-04-15)



<a name="0.9.2"></a>
## 0.9.2 (2011-03-22)



<a name="0.9.0"></a>
# 0.9.0 (2011-02-27)



<a name="0.8.1"></a>
## 0.8.1 (2010-08-21)



<a name="0.7.9"></a>
## 0.7.9 (2010-07-05)



<a name="0.7.7"></a>
## 0.7.7 (2010-06-15)



<a name="0.7.6"></a>
## 0.7.6 (2010-06-10)



<a name="0.7.5"></a>
## 0.7.5 (2010-05-27)



