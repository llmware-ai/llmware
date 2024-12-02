[![Build Status](https://secure.travis-ci.org/christkv/mongodb-core.png)](http://travis-ci.org/christkv/mongodb-core)
[![Coverage Status](https://coveralls.io/repos/github/christkv/mongodb-core/badge.svg?branch=1.3)](https://coveralls.io/github/christkv/mongodb-core?branch=1.3)

# Description

The MongoDB Core driver is the low level part of the 2.0 or higher MongoDB driver and is meant for library developers not end users. It does not contain any abstractions or helpers outside of the basic management of MongoDB topology connections, CRUD operations and authentication.

## MongoDB Node.JS Core Driver

| what          | where                                          |
|---------------|------------------------------------------------|
| documentation | http://mongodb.github.io/node-mongodb-native/  |
| apidoc        | http://mongodb.github.io/node-mongodb-native/  |
| source        | https://github.com/christkv/mongodb-core       |
| mongodb       | http://www.mongodb.org/                        |

### Blogs of Engineers involved in the driver
- Christian Kvalheim [@christkv](https://twitter.com/christkv) <http://christiankvalheim.com>

### Bugs / Feature Requests

Think you’ve found a bug? Want to see a new feature in node-mongodb-native? Please open a
case in our issue management tool, JIRA:

- Create an account and login <https://jira.mongodb.org>.
- Navigate to the NODE project <https://jira.mongodb.org/browse/NODE>.
- Click **Create Issue** - Please provide as much information as possible about the issue type and how to reproduce it.

Bug reports in JIRA for all driver projects (i.e. NODE, PYTHON, CSHARP, JAVA) and the
Core Server (i.e. SERVER) project are **public**.

### Questions and Bug Reports

 * mailing list: https://groups.google.com/forum/#!forum/node-mongodb-native
 * jira: http://jira.mongodb.org/

### Change Log

http://jira.mongodb.org/browse/NODE

# QuickStart

The quick start guide will show you how to set up a simple application using Core driver and MongoDB. It scope is only how to set up the driver and perform the simple crud operations. For more inn depth coverage we encourage reading the tutorials.

## Create the package.json file

Let's create a directory where our application will live. In our case we will put this under our projects directory.

```
mkdir myproject
cd myproject
```

Create a **package.json** using your favorite text editor and fill it in.

```json
{
  "name": "myproject",
  "version": "1.0.0",
  "description": "My first project",
  "main": "index.js",
  "repository": {
    "type": "git",
    "url": "git://github.com/christkv/myfirstproject.git"
  },
  "dependencies": {
    "mongodb-core": "~1.0"
  },
  "author": "Christian Kvalheim",
  "license": "Apache 2.0",
  "bugs": {
    "url": "https://github.com/christkv/myfirstproject/issues"
  },
  "homepage": "https://github.com/christkv/myfirstproject"
}
```

Save the file and return to the shell or command prompt and use **NPM** to install all the dependencies.

```
npm install
```

You should see **NPM** download a lot of files. Once it's done you'll find all the downloaded packages under the **node_modules** directory.

Booting up a MongoDB Server
---------------------------
Let's boot up a MongoDB server instance. Download the right MongoDB version from [MongoDB](http://www.mongodb.org), open a new shell or command line and ensure the **mongod** command is in the shell or command line path. Now let's create a database directory (in our case under **/data**).

```
mongod --dbpath=/data --port 27017
```

You should see the **mongod** process start up and print some status information.

## Connecting to MongoDB

Let's create a new **app.js** file that we will use to show the basic CRUD operations using the MongoDB driver.

First let's add code to connect to the server. Notice that there is no concept of a database here and we use the topology directly to perform the connection.

```js
var Server = require('mongodb-core').Server
  , assert = require('assert');

// Set up server connection
var server = new Server({
    host: 'localhost'
  , port: 27017
  , reconnect: true
  , reconnectInterval: 50
});

// Add event listeners
server.on('connect', function(_server) {
  console.log('connected');
  test.done();
});

server.on('close', function() {
  console.log('closed');
});

server.on('reconnect', function() {
  console.log('reconnect');
});

// Start connection
server.connect();
```

To connect to a replicaset we would use the `ReplSet` class and for a set of Mongos proxies we use the `Mongos` class. Each topology class offer the same CRUD operations and you operate on the topology directly. Let's look at an example exercising all the different available CRUD operations.

```js
var Server = require('mongodb-core').Server
  , assert = require('assert');

// Set up server connection
var server = new Server({
    host: 'localhost'
  , port: 27017
  , reconnect: true
  , reconnectInterval: 50
});

// Add event listeners
server.on('connect', function(_server) {
  console.log('connected');

  // Execute the ismaster command
  _server.command('system.$cmd', {ismaster: true}, function(err, result) {

    // Perform a document insert
    _server.insert('myproject.inserts1', [{a:1}, {a:2}], {
      writeConcern: {w:1}, ordered:true
    }, function(err, results) {
      assert.equal(null, err);
      assert.equal(2, results.result.n);      

      // Perform a document update
      _server.update('myproject.inserts1', [{
        q: {a: 1}, u: {'$set': {b:1}}
      }], {
        writeConcern: {w:1}, ordered:true
      }, function(err, results) {
        assert.equal(null, err);
        assert.equal(1, results.result.n);

        // Remove a document
        _server.remove('myproject.inserts1', [{
          q: {a: 1}, limit: 1
        }], {
          writeConcern: {w:1}, ordered:true
        }, function(err, results) {
          assert.equal(null, err);
          assert.equal(1, results.result.n);

          // Get a document
          var cursor = _server.cursor('integration_tests.inserts_example4', {
              find: 'integration_tests.example4'
            , query: {a:1}
          });

          // Get the first document
          cursor.next(function(err, doc) {
            assert.equal(null, err);
            assert.equal(2, doc.a);

            // Execute the ismaster command
            _server.command("system.$cmd"
              , {ismaster: true}, function(err, result) {
                assert.equal(null, err)
                _server.destroy();              
            });
          });
      });
    });

    test.done();
  });
});

server.on('close', function() {
  console.log('closed');
});

server.on('reconnect', function() {
  console.log('reconnect');
});

// Start connection
server.connect();
```

The core driver does not contain any helpers or abstractions only the core crud operations. These consist of the following commands.

* `insert`, Insert takes an array of 1 or more documents to be inserted against the topology and allows you to specify a write concern and if you wish to execute the inserts in order or out of order.
* `update`, Update takes an array of 1 or more update commands to be executed against the server topology and also allows you to specify a write concern and if you wish to execute the updates in order or out of order.
* `remove`, Remove takes an array of 1 or more remove commands to be executed against the server topology and also allows you to specify a write concern and if you wish to execute the removes in order or out of order.
* `cursor`, Returns you a cursor for either the 'virtual' `find` command, a command that returns a cursor id or a plain cursor id. Read the cursor tutorial for more inn depth coverage.
* `command`, Executes a command against MongoDB and returns the result.
* `auth`, Authenticates the current topology using a supported authentication scheme.

The Core Driver is a building block for library builders and is not meant for usage by end users as it lacks a lot of features the end user might need such as automatic buffering of operations when a primary is changing in a replicaset or the db and collections abstraction.

## Next steps

The next step is to get more in depth information about how the different aspects of the core driver works and how to leverage them to extend the functionality of the cursors. Please view the tutorials for more detailed information.
