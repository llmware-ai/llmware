const express = require('express')
const session = require('express-session')
const MongoStore = require('connect-mongo')

const app = express()
const port = 3000

app.use(session({
  secret: 'foo',
  resave: false,
  saveUninitialized: false,
  store: MongoStore.create({
    mongoUrl: 'mongodb://root:example@127.0.0.1:27017',
    dbName: "example-db",
    stringify: false,
  })
}));

app.get('/', (req, res) => {
  req.session.foo = 'test-id'
  res.send('Hello World!')
})

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})
