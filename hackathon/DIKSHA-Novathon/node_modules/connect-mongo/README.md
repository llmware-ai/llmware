# connect-mongo

MongoDB session store for [Connect](https://github.com/senchalabs/connect) and [Express](http://expressjs.com/) written in Typescript.

[![npm version](https://img.shields.io/npm/v/connect-mongo.svg)](https://www.npmjs.com/package/connect-mongo)
[![downloads](https://img.shields.io/npm/dm/connect-mongo.svg)](https://www.npmjs.com/package/connect-mongo)
[![Sanity check](https://github.com/jdesboeufs/connect-mongo/actions/workflows/sanity.yml/badge.svg)](https://github.com/jdesboeufs/connect-mongo/actions/workflows/sanity.yml)
[![Coverage Status](https://coveralls.io/repos/jdesboeufs/connect-mongo/badge.svg?branch=master&service=github)](https://coveralls.io/github/jdesboeufs/connect-mongo?branch=master)

> Breaking change in V4 and rewritten the whole project using Typescript. Please checkout the [migration guide](MIGRATION_V4.md) and [changelog](CHANGELOG.md) for details.

- [Install](#install)
- [Compatibility](#compatibility)
- [Usage](#usage)
  - [Express or Connect integration](#express-or-connect-integration)
  - [Connection to MongoDB](#connection-to-mongodb)
- [Known issues](#known-issues)
  - [Native autoRemove causing error on close](#native-autoremove-causing-error-on-close)
  - [MongoError exports circular dependency](#mongoerror-exports-circular-dependency)
  - [Existing encrypted v3.2.0 sessions are not decrypted correctly by v4](#existing-encrypted-v320-sessions-are-not-decrypted-correctly-by-v4)
- [Events](#events)
- [Session expiration](#session-expiration)
- [Remove expired sessions](#remove-expired-sessions)
  - [Set MongoDB to clean expired sessions (default mode)](#set-mongodb-to-clean-expired-sessions-default-mode)
  - [Set the compatibility mode](#set-the-compatibility-mode)
  - [Disable expired sessions cleaning](#disable-expired-sessions-cleaning)
- [Lazy session update](#lazy-session-update)
- [Transparent encryption/decryption of session data](#transparent-encryptiondecryption-of-session-data)
- [Options](#options)
  - [Connection-related options (required)](#connection-related-options-required)
  - [More options](#more-options)
  - [Crypto-related options](#crypto-related-options)
- [Development](#development)
  - [Example application](#example-application)
  - [Release](#release)
- [License](#license)

## Install

```
npm install connect-mongo
yarn add connect-mongo
```

* You may also need to run install `mongodb` if you do not have it installed already because `mongodb` is not a `peerDependencies` instead.
* If you are upgrading from v3.x to v4, please checkout the [migration guide](./MIGRATION_V4.md) for details.
* If you are upgrading v4.x to latest version, you may check the [example](./example) and [options](#options) for details.

## Compatibility

* Support Express up to `5.0`
* Support [native MongoDB driver](http://mongodb.github.io/node-mongodb-native/) `5` and `6`
* Support Node.js 14, 16 and 18
* Support [MongoDB](https://www.mongodb.com/) `3.6+`

For extended compatibility, see previous versions [v3.x](https://github.com/jdesboeufs/connect-mongo/tree/v3.x).
But please note that we are not maintaining v3.x anymore.

## Usage

### Express or Connect integration

Express `4.x`, `5.0` and Connect `3.x`:

```js
const session = require('express-session');
const MongoStore = require('connect-mongo');

app.use(session({
  secret: 'foo',
  store: MongoStore.create(options)
}));
```

```ts
import session from 'express-session'
import MongoStore from 'connect-mongo'

app.use(session({
  secret: 'foo',
  store: MongoStore.create(options)
}));
```

### Connection to MongoDB

In many circumstances, `connect-mongo` will not be the only part of your application which need a connection to a MongoDB database. It could be interesting to re-use an existing connection.

Alternatively, you can configure `connect-mongo` to establish a new connection.

#### Create a new connection from a MongoDB connection string

[MongoDB connection strings](http://docs.mongodb.org/manual/reference/connection-string/) are __the best way__ to configure a new connection. For advanced usage, [more options](http://mongodb.github.io/node-mongodb-native/driver-articles/mongoclient.html#mongoclient-connect-options) can be configured with `mongoOptions` property.

```js
// Basic usage
app.use(session({
  store: MongoStore.create({ mongoUrl: 'mongodb://localhost/test-app' })
}));

// Advanced usage
app.use(session({
  store: MongoStore.create({
    mongoUrl: 'mongodb://user12345:foobar@localhost/test-app?authSource=admin&w=1',
    mongoOptions: advancedOptions // See below for details
  })
}));
```

#### Re-use an existing native MongoDB driver client promise

In this case, you just have to give your `MongoClient` instance to `connect-mongo`.

```js
/*
** There are many ways to create MongoClient.
** You should refer to the driver documentation.
*/

// Database name present in the connection string will be used
app.use(session({
  store: MongoStore.create({ clientPromise })
}));

// Explicitly specifying database name
app.use(session({
  store: MongoStore.create({
    clientPromise,
    dbName: 'test-app'
  })
}));
```

## Known issues

[Known issues](https://github.com/jdesboeufs/connect-mongo/issues?q=is%3Aopen+is%3Aissue+label%3Abug) in GitHub Issues page.

### Native autoRemove causing error on close

- Calling `close()` immediately after creating the session store may cause error when the async index creation is in process when `autoRemove: 'native'`. You may want to manually manage the autoRemove index. [#413](https://github.com/jdesboeufs/connect-mongo/issues/413)

### MongoError exports circular dependency

The following error can be safely ignored from [official reply](https://developer.mongodb.com/community/forums/t/warning-accessing-non-existent-property-mongoerror-of-module-exports-inside-circular-dependency/15411/5).

```
(node:16580) Warning: Accessing non-existent property 'MongoError' of module exports inside circular dependency
(Use `node --trace-warnings ...` to show where the warning was created)
```

### Existing encrypted v3.2.0 sessions are not decrypted correctly by v4

v4 cannot decrypt the session encrypted from v3.2 due to a bug. Please take a look on this issue for possible workaround. [#420](https://github.com/jdesboeufs/connect-mongo/issues/420)

## Events

A `MongoStore` instance will emit the following events:

| Event name | Description | Payload
| ----- | ----- | ----- |
| `create` | A session has been created | `sessionId` |
| `touch` | A session has been touched (but not modified) | `sessionId` |
| `update` | A session has been updated | `sessionId` |
| `set` | A session has been created OR updated _(for compatibility purpose)_ | `sessionId` |
| `destroy` | A session has been destroyed manually | `sessionId` |

## Session expiration

When the session cookie has an expiration date, `connect-mongo` will use it.

Otherwise, it will create a new one, using `ttl` option.

```js
app.use(session({
  store: MongoStore.create({
    mongoUrl: 'mongodb://localhost/test-app',
    ttl: 14 * 24 * 60 * 60 // = 14 days. Default
  })
}));
```

__Note:__ Each time a user interacts with the server, its session expiration date is refreshed.

## Remove expired sessions

By default, `connect-mongo` uses MongoDB's TTL collection feature (2.2+) to have mongodb automatically remove expired sessions. But you can change this behavior.

### Set MongoDB to clean expired sessions (default mode)

`connect-mongo` will create a TTL index for you at startup. You MUST have MongoDB 2.2+ and administration permissions.

```js
app.use(session({
  store: MongoStore.create({
    mongoUrl: 'mongodb://localhost/test-app',
    autoRemove: 'native' // Default
  })
}));
```

__Note:__ If you use `connect-mongo` in a very concurrent environment, you should avoid this mode and prefer setting the index yourself, once!

### Set the compatibility mode

In some cases you can't or don't want to create a TTL index, e.g. Azure Cosmos DB.

`connect-mongo` will take care of removing expired sessions, using defined interval.

```js
app.use(session({
  store: MongoStore.create({
    mongoUrl: 'mongodb://localhost/test-app',
    autoRemove: 'interval',
    autoRemoveInterval: 10 // In minutes. Default
  })
}));
```

### Disable expired sessions cleaning

You are in production environnement and/or you manage the TTL index elsewhere.

```js
app.use(session({
  store: MongoStore.create({
    mongoUrl: 'mongodb://localhost/test-app',
    autoRemove: 'disabled'
  })
}));
```

## Lazy session update

If you are using [express-session](https://github.com/expressjs/session) >= [1.10.0](https://github.com/expressjs/session/releases/tag/v1.10.0) and don't want to resave all the session on database every single time that the user refreshes the page, you can lazy update the session, by limiting a period of time.

```js
app.use(express.session({
  secret: 'keyboard cat',
  saveUninitialized: false, // don't create session until something stored
  resave: false, //don't save session if unmodified
  store: MongoStore.create({
    mongoUrl: 'mongodb://localhost/test-app',
    touchAfter: 24 * 3600 // time period in seconds
  })
}));
```

by doing this, setting `touchAfter: 24 * 3600` you are saying to the session be updated only one time in a period of 24 hours, does not matter how many request's are made (with the exception of those that change something on the session data)


## Transparent encryption/decryption of session data

When working with sensitive session data it is [recommended](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Session_Management_Cheat_Sheet.md) to use encryption

```js
const store = MongoStore.create({
  mongoUrl: 'mongodb://localhost/test-app',
  crypto: {
    secret: 'squirrel'
  }
})
```

## Options

### Connection-related options (required)

One of the following options should be provided. If more than one option are provided, each option will take precedence over others according to priority.

|Priority|Option|Description|
|:------:|------|-----------|
|1|`mongoUrl`|A [connection string](https://docs.mongodb.com/manual/reference/connection-string/) for creating a new MongoClient connection. If database name is not present in the connection string, database name should be provided using `dbName` option. |
|2|`clientPromise`|A Promise that is resolved with MongoClient connection. If the connection was established without database name being present in the connection string, database name should be provided using `dbName` option.|
|3|`client`|An existing MongoClient connection. If the connection was established without database name being present in the connection string, database name should be provided using `dbName` option.|

### More options

|Option|Default|Description|
|------|:-----:|-----------|
|`mongoOptions`|`{ useUnifiedTopology: true }`|Options object for [`MongoClient.connect()`](https://mongodb.github.io/node-mongodb-native/3.3/api/MongoClient.html#.connect) method. Can be used with `mongoUrl` option.|
|`dbName`||A name of database used for storing sessions. Can be used with `mongoUrl`, or `clientPromise` options. Takes precedence over database name present in the connection string.|
|`collectionName`|`'sessions'`|A name of collection used for storing sessions.|
|`ttl`|`1209600`|The maximum lifetime (in seconds) of the session which will be used to set `session.cookie.expires` if it is not yet set. Default is 14 days.|
|`autoRemove`|`'native'`|Behavior for removing expired sessions. Possible values: `'native'`, `'interval'` and `'disabled'`.|
|`autoRemoveInterval`|`10`|Interval (in minutes) used when `autoRemove` option is set to `interval`.|
|`touchAfter`|`0`|Interval (in seconds) between session updates.|
|`stringify`|`true`|If `true`, connect-mongo will serialize sessions using `JSON.stringify` before setting them, and deserialize them with `JSON.parse` when getting them. This is useful if you are using types that MongoDB doesn't support.|
|`serialize`||Custom hook for serializing sessions to MongoDB. This is helpful if you need to modify the session before writing it out.|
|`unserialize`||Custom hook for unserializing sessions from MongoDB. This can be used in scenarios where you need to support different types of serializations (e.g., objects and JSON strings) or need to modify the session before using it in your app.|
|`writeOperationOptions`||Options object to pass to every MongoDB write operation call that supports it (e.g. `update`, `remove`). Useful for adjusting the write concern. Only exception: If `autoRemove` is set to `'interval'`, the write concern from the `writeOperationOptions` object will get overwritten.|
|`transformId`||Transform original `sessionId` in whatever you want to use as storage key.|
|`crypto`||Crypto related options. See below.|

### Crypto-related options

|Option|Default|Description|
|------|:-----:|-----------|
|`secret`|`false`|Enables transparent crypto in accordance with [OWASP session management recommendations](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Session_Management_Cheat_Sheet.md).|
|`algorithm`|`'aes-256-gcm'`|Allows for changes to the default symmetric encryption cipher. See [`crypto.getCiphers()`](https://nodejs.org/api/crypto.html#crypto_crypto_getciphers) for supported algorithms.|
|`hashing`|`'sha512'`|May be used to change the default hashing algorithm. See [`crypto.getHashes()`](https://nodejs.org/api/crypto.html#crypto_crypto_gethashes) for supported hashing algorithms.|
|`encodeas`|`'hex'`|Specify to change the session data cipher text encoding.|
|`key_size`|`32`|When using varying algorithms the key size may be used. Default value `32` is based on the `AES` blocksize.|
|`iv_size`|`16`|This can be used to adjust the default [IV](https://csrc.nist.gov/glossary/term/IV) size if a different algorithm requires a different size.|
|`at_size`|`16`|When using newer `AES` modes such as the default `GCM` or `CCM` an authentication tag size can be defined.|

## Development

```
yarn install
docker-compose up -d
# Run these 2 lines in 2 shell
yarn watch:build
yarn watch:test
```

### Example application

```
yarn link
cd example
yarn link "connect-mongo"
yarn install
yarn start
```

### Release

Since I cannot access the setting page. I can only do it manually.

1. Bump version, update `CHANGELOG.md` and README. Commit and push.
2. Run `yarn build && yarn test && npm publish`
3. `git tag vX.Y.Z && git push --tags`

## License

The MIT License
