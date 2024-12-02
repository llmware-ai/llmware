const express = require('express')
const mongoose = require('mongoose')
const session = require('express-session')
const MongoStore = require('connect-mongo')

// App Init
const app = express()
const port = 3000

// Starting Server
app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})

// Mongoose Connection
const appDBConnection = mongoose
  .createConnection('mongodb://root:example@127.0.0.1:27017', {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then((connection) => {
    console.log('Connected to AppDB.')
    return connection
  })

const sessionDBConnection = mongoose
  .createConnection('mongodb://root:example@127.0.0.1:27017', {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then((connection) => {
    console.log('Connected to SessionsDB.')
    return connection
  })

// Session Init
const sessionInit = (client) => {
  app.use(
    session({
      store: MongoStore.create({
        client: client,
        mongoOptions: {
          useNewUrlParser: true,
          useUnifiedTopology: true,
        },
      }),
      secret: 'hello',
      resave: false,
      saveUninitialized: false,
      cookie: { maxAge: 24 * 60 * 60 * 1000 },
    })
  )
}

// Router Init
const router = express.Router()

router.get('', (req, res) => {
  req.session.foo = 'bar'
  res.send('Session Updated')
})

(async function () {
  const connection = await sessionDBConnection
  const mongoClient = connection.getClient()
  sessionInit(mongoClient)
  app.use('/', router)
})()
