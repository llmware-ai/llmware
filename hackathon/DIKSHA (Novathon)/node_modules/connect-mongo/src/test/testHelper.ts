// eslint-disable-next-line eslint-comments/disable-enable-pair
/* eslint-disable @typescript-eslint/explicit-module-boundary-types */
import util from 'util'
import ExpressSession from 'express-session'

import MongoStore, { ConnectMongoOptions } from '../lib/MongoStore'

// Create a connect cookie instance
export const makeCookie = () => {
  const cookie = new ExpressSession.Cookie()
  cookie.maxAge = 10000 // This sets cookie.expire through a setter
  cookie.secure = true
  cookie.domain = 'cow.com'
  cookie.sameSite = false

  return cookie
}

// Create session data
export const makeData = () => {
  return {
    foo: 'bar',
    baz: {
      cow: 'moo',
      chicken: 'cluck',
    },
    num: 1,
    cookie: makeCookie(),
  }
}

export const makeDataNoCookie = () => {
  return {
    foo: 'bar',
    baz: {
      cow: 'moo',
      fish: 'blub',
      fox: 'nobody knows!',
    },
    num: 2,
  }
}

export const createStoreHelper = (opt: Partial<ConnectMongoOptions> = {}) => {
  const store = MongoStore.create({
    mongoUrl: 'mongodb://root:example@127.0.0.1:27017',
    mongoOptions: {},
    dbName: 'testDb',
    collectionName: 'test-collection',
    ...opt,
  })

  const storePromise = {
    length: util.promisify(store.length).bind(store),
    clear: util.promisify(store.clear).bind(store),
    get: util.promisify(store.get).bind(store),
    set: util.promisify(store.set).bind(store),
    all: util.promisify(store.all).bind(store),
    touch: util.promisify(store.touch).bind(store),
    destroy: util.promisify(store.destroy).bind(store),
    close: store.close.bind(store),
  }
  return { store, storePromise }
}
