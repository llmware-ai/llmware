# express-sessions

ExpressJS/Mongoose Session Storage

## Installation

```
npm install express-sessions
```

## Usage

``` js
var mongoose = require('mongoose');

mongoose.connect();

app.use(express.session({
    secret: 'a4f8071f-c873-4447-8ee2',
    cookie: { maxAge: 2628000000 },
    store: new (require('express-sessions'))({
        storage: 'mongodb',
        instance: mongoose, // optional
        host: 'localhost', // optional
        port: 27017, // optional
        db: 'test', // optional
        collection: 'sessions', // optional
        expire: 86400 // optional
    })
}));
```
Or

``` js
var redis = require('redis');
var client = redis.createClient(6379, 'localhost');

app.use(express.session({
    secret: 'a4f8071f-c873-4447-8ee2',
    cookie: { maxAge: 2628000000 },
    store: new (require('express-sessions'))({
        storage: 'redis',
        instance: client, // optional
        host: 'localhost', // optional
        port: 6379, // optional
        collection: 'sessions', // optional
        expire: 86400 // optional
    })
}));
```

That's it!