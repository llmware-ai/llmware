var express = require('express');
var mongoose = require('mongoose');
var redis = require("redis");

var MongoStore = {
    client: null,
    options: {},
    get: function (sid, cb) {
        MongoStore.client.findOne({sid: sid}, function (err, doc) {
            try {
                if (err) return cb(err, null);

                if (!doc) return cb();

                cb(null, doc.data); // JSON.parse(doc.data)
            }
            catch (err) {
                cb(err);
            }
        });
    },
    set: function (sid, data, cb) {
        try {
            var lastAccess = new Date();
            var expires = lastAccess.setDate(lastAccess.getDate() + 1);

            if (typeof data.cookie != 'undefined') {
                expires = data.cookie._expires;
            }

            if (typeof data.lastAccess != 'undefined') {
                lastAccess = new Date(data.lastAccess);
            }

            MongoStore.client.findOneAndUpdate({sid: sid}, {
                data: JSON.parse(JSON.stringify(data)), //JSON.stringify(data)
                lastAccess: lastAccess,
                expires: expires
            }, { upsert: true }, cb);
        }
        catch (err) {
            console.log('express-sessions', err);

            cb && cb(err);
        }
    },
    destroy: function (sid, cb) {
        MongoStore.client.remove({ sid: sid }, cb);
    },
    all: function (cb) {
        MongoStore.client.find(function (err, doc) {
            if (err) {
                return cb && cb(err);
            }

            cb && cb(null, doc);
        });
    },
    length: function (cb) {
        MongoStore.client.count(function (err, count) {
            if (err) {
                return cb && cb(err);
            }

            cb && cb(null, count);
        });
    },
    clear: function (cb) {
        MongoStore.client.drop(function () {
            if (err) {
                return cb && cb(err);
            }

            cb && cb();
        });
    }
}

var RedisStore = {
    client: null,
    options: {},
    get: function (sid, cb) {
        RedisStore.client.get(RedisStore.options.collection + ':' + sid, function (err, doc) {
            try {
                if (err) return cb(err, null);

                if (!doc) return cb();

                cb(null, JSON.parse(doc)); // JSON.parse(doc.data)
            }
            catch (err) {
                cb(err);
            }
        });
    },
    set: function (sid, data, cb) {
        try {
            var lastAccess = new Date();
            var expires = lastAccess.setDate(lastAccess.getDate() + 1);

            if (typeof data.cookie != 'undefined') {
                expires = data.cookie._expires;
            }

            if (typeof data.lastAccess != 'undefined') {
                lastAccess = new Date(data.lastAccess);
            }

            RedisStore.client.set(RedisStore.options.collection + ':' + sid, JSON.stringify(data), cb);
            if (RedisStore.options.expire) {
                RedisStore.client.expire(RedisStore.options.collection + ':' + sid, parseInt(RedisStore.options.expire));
            }
        }
        catch (err) {
            console.log('express-sessions', err);
            cb && cb(err);
        }
    },
    destroy: function (sid, cb) {
        RedisStore.client.del(RedisStore.options.collection + ':' + sid, cb);
    },
    all: function (cb) {
        RedisStore.client.keys(RedisStore.options.collection + ':*', function (err, docs) {
            if (err) {
                return cb && cb(err);
            }

            cb && cb(null, docs);
        });
    },
    length: function (cb) {
        RedisStore.client.keys(RedisStore.options.collection + ':*', function (err, docs) {
            if (err) {
                return cb && cb(err);
            }

            cb && cb(null, docs.length);
        });
    },
    clear: function (cb) {
        RedisStore.client.del(RedisStore.options.collection + ':*', cb);
    }
}

var SessionStore = function (options, cb) {
    var options = {
        storage: options.storage || 'mongodb',
        host: options.host || 'localhost',
        port: options.port || (options.storage == 'redis' ? 6379 : 27017),
        db: options.db || 'test',
        collection: options.collection || 'sessions',
        instance: options.instance || null,
        expire: options.expire || 86400
    };

    express.session.Store.call(this, options);

    switch (options.storage) {
        case 'mongodb':
            if (options.instance) {
                mongoose = options.instance;
            } else {
                mongoose.connect('mongodb://' + options.host + ':' + options.port + '/' + options.db);
            }

            var schema = new mongoose.Schema({
                sid: { type: String, required: true, unique: true },
                data: { type: {} },
                lastAccess: { type: Date, index: { expires: parseInt(options.expire) * 1000} },
                expires: { type: Date, index: true }
            });

            MongoStore.options = options;
            MongoStore.client = mongoose.model(options.collection, schema);

            for (var i in MongoStore) {
                SessionStore.prototype[i] = MongoStore[i];
            }
            break;
        case 'redis':
            if (options.instance) {
                RedisStore.client = options.instance;
            } else {
                RedisStore.client = redis.createClient(options.port, options.host);
            }

            RedisStore.options = options;

            for (var i in RedisStore) {
                SessionStore.prototype[i] = RedisStore[i];
            }
            break;
    }


    if (cb) cb.call(null);
}

SessionStore.prototype = new express.session.Store();

module.exports = SessionStore;
