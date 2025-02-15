import test from 'ava'
import request from 'supertest'
import express from 'express'
import session, { SessionOptions } from 'express-session'
import MongoStore from '../'
import { ConnectMongoOptions } from '../lib/MongoStore'

declare module 'express-session' {
  interface SessionData {
    [key: string]: any
  }
}

function createSupertetAgent(
  sessionOpts: SessionOptions,
  mongoStoreOpts: ConnectMongoOptions
) {
  const app = express()
  const store = MongoStore.create(mongoStoreOpts)
  app.use(
    session({
      ...sessionOpts,
      store: store,
    })
  )
  app.get('/', function (req, res) {
    if (typeof req.session.views === 'number') {
      req.session.views++
    } else {
      req.session.views = 0
    }
    res.status(200).send({ views: req.session.views })
  })
  app.get('/ping', function (req, res) {
    res.status(200).send({ views: req.session.views })
  })
  const agent = request.agent(app)
  return agent
}

function createSupertetAgentWithDefault(
  sessionOpts: Omit<SessionOptions, 'secret'> = {},
  mongoStoreOpts: ConnectMongoOptions = {}
) {
  return createSupertetAgent(
    { secret: 'foo', ...sessionOpts },
    {
      mongoUrl: 'mongodb://root:example@127.0.0.1:27017',
      dbName: 'itegration-test-db',
      stringify: false,
      ...mongoStoreOpts,
    }
  )
}

test.serial.cb('simple case', (t) => {
  const agent = createSupertetAgentWithDefault()
  agent
    .get('/')
    .expect(200)
    .then((response) => response.headers['set-cookie'])
    .then((cookie) => {
      agent
        .get('/')
        .expect(200)
        .end((err, res) => {
          t.is(err, null)
          t.deepEqual(res.body, { views: 1 })
          return t.end()
        })
    })
})

test.serial.cb('simple case with touch after', (t) => {
  const agent = createSupertetAgentWithDefault(
    { resave: false, saveUninitialized: false, rolling: true },
    { touchAfter: 1 }
  )
  agent
    .get('/')
    .expect(200)
    .then(() => {
      agent
        .get('/')
        .expect(200)
        .end((err, res) => {
          t.is(err, null)
          t.deepEqual(res.body, { views: 1 })
          new Promise<void>((resolve) => {
            setTimeout(() => {
              resolve()
            }, 1200)
          }).then(() => {
            agent
              .get('/ping')
              .expect(200)
              .end((err, res) => {
                t.is(err, null)
                t.deepEqual(res.body, { views: 1 })
                return t.end()
              })
          })
        })
    })
})
