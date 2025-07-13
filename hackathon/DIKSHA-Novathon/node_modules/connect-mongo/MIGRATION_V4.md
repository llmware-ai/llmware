# V4 migration guide

To migrate the library from V3 to V4, re-install the dependencies.

If you are using `npm`

```
npm uninstall connect-mongo
npm uninstall @types/connect-mongo
npm install connect-mongo
```

If you are using `yarn`

```
yarn remove connect-mongo
yarn remove @types/connect-mongo
yarn add connect-mongo
```

Next step is to import the dependencies

Javascript:
```js
const MongoStore = require('connect-mongo');
```

Typescript:
```ts
import MongoStore from 'connect-mongo';
```

Create the store using `MongoStore.create(options)` instead of `new MongoStore(options)`

```js
app.use(session({
  secret: 'foo',
  store: MongoStore.create(options)
}));
```

For the options, you should make the following changes:

* Change `url` to `mongoUrl`
* Change `collection` to `collectionName` if you are using it
* Keep `clientPromise` if you are using it
* `mongooseConnection` has been removed. Please update your application code to use either `mongoUrl`, `client` or `clientPromise`
* To reuse an existing mongoose connection retreive the mongoDb driver from you mongoose connection using `Connection.prototype.getClient()` and pass it to the store in the `client`-option.
* Remove `fallbackMemory` option and if you are using it, you can import from:

```js
const session = require('express-session');

app.use(session({
  store: isDev ? new session.MemoryStore() : MongoStore.create(options)
}));
```

> You can also take a look at [example](example) directory for example usage.
