[![NPM](https://nodei.co/npm/mongodb.png?downloads=true&downloadRank=true)](https://nodei.co/npm/mongodb/) [![NPM](https://nodei.co/npm-dl/mongodb.png?months=6&height=3)](https://nodei.co/npm/mongodb/)

[![Build Status](https://secure.travis-ci.org/mongodb/node-mongodb-native.svg?branch=2.1)](http://travis-ci.org/mongodb/node-mongodb-native)
[![Coverage Status](https://coveralls.io/repos/github/mongodb/node-mongodb-native/badge.svg?branch=2.1)](https://coveralls.io/github/mongodb/node-mongodb-native?branch=2.1)
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/mongodb/node-mongodb-native?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

# Description

The official [MongoDB](https://www.mongodb.com/) driver for Node.js. Provides a high-level API on top of [mongodb-core](https://www.npmjs.com/package/mongodb-core) that is meant for end users.

## MongoDB Node.JS Driver

| what          | where                                          |
|---------------|------------------------------------------------|
| documentation | http://mongodb.github.io/node-mongodb-native/  |
| api-doc        | http://mongodb.github.io/node-mongodb-native/2.2/api/  |
| source        | https://github.com/mongodb/node-mongodb-native |
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

# Installation

The recommended way to get started using the Node.js 2.0 driver is by using the `NPM` (Node Package Manager) to install the dependency in your project.

## MongoDB Driver

Given that you have created your own project using `npm init` we install the mongodb driver and it's dependencies by executing the following `NPM` command.

```
npm install mongodb --save
```

This will download the MongoDB driver and add a dependency entry in your `package.json` file.

## Troubleshooting

The MongoDB driver depends on several other packages. These are.

* mongodb-core
* bson
* kerberos
* node-gyp

The `kerberos` package is a C++ extension that requires a build environment to be installed on your system. You must be able to build node.js itself to be able to compile and install the `kerberos` module. Furthermore the `kerberos` module requires the MIT Kerberos package to correctly compile on UNIX operating systems. Consult your UNIX operation system package manager what libraries to install.

{{% note class="important" %}}
Windows already contains the SSPI API used for Kerberos authentication. However you will need to install a full compiler tool chain using visual studio C++ to correctly install the kerberos extension.
{{% /note %}}

### Diagnosing on UNIX

If you don’t have the build essentials it won’t build. In the case of linux you will need gcc and g++, node.js with all the headers and python. The easiest way to figure out what’s missing is by trying to build the kerberos project. You can do this by performing the following steps.

```
git clone https://github.com/christkv/kerberos.git
cd kerberos
npm install
```

If all the steps complete you have the right toolchain installed. If you get node-gyp not found you need to install it globally by doing.

```
npm install -g node-gyp
```

If correctly compiles and runs the tests you are golden. We can now try to install the mongod driver by performing the following command.

```
cd yourproject
npm install mongodb --save
```

If it still fails the next step is to examine the npm log. Rerun the command but in this case in verbose mode.

```
npm --loglevel verbose install mongodb
```

This will print out all the steps npm is performing while trying to install the module.

### Diagnosing on Windows

A known compiler tool chain known to work for compiling `kerberos` on windows is the following.

* Visual Studio c++ 2010 (do not use higher versions)
* Windows 7 64bit SDK
* Python 2.7 or higher

Open visual studio command prompt. Ensure node.exe is in your path and install node-gyp.

```
npm install -g node-gyp
```

Next you will have to build the project manually to test it. Use any tool you use with git and grab the repo.

```
git clone https://github.com/christkv/kerberos.git
cd kerberos
npm install
node-gyp rebuild
```

This should rebuild the driver successfully if you have everything set up correctly.

### Other possible issues

Your python installation might be hosed making gyp break. I always recommend that you test your deployment environment first by trying to build node itself on the server in question as this should unearth any issues with broken packages (and there are a lot of broken packages out there).

Another thing is to ensure your user has write permission to wherever the node modules are being installed.

QuickStart
==========
The quick start guide will show you how to setup a simple application using node.js and MongoDB. Its scope is only how to set up the driver and perform the simple crud operations. For more in depth coverage we encourage reading the tutorials.

Create the package.json file
----------------------------
Let's create a directory where our application will live. In our case we will put this under our projects directory.

```
mkdir myproject
cd myproject
```

Enter the following command and answer the questions to create the initial structure for your new project

```
npm init
```

Next we need to edit the generated package.json file to add the dependency for the MongoDB driver. The package.json file below is just an example and your will look different depending on how you answered the questions after entering `npm init`

```
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
    "mongodb": "~2.0"
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

Connecting to MongoDB
---------------------
Let's create a new **app.js** file that we will use to show the basic CRUD operations using the MongoDB driver.

First let's add code to connect to the server and the database **myproject**.

```js
var MongoClient = require('mongodb').MongoClient
  , assert = require('assert');

// Connection URL
var url = 'mongodb://localhost:27017/myproject';
// Use connect method to connect to the Server
MongoClient.connect(url, function(err, db) {
  assert.equal(null, err);
  console.log("Connected correctly to server");

  db.close();
});
```

Given that you booted up the **mongod** process earlier the application should connect successfully and print **Connected correctly to server** to the console.

Let's Add some code to show the different CRUD operations available.

Inserting a Document
--------------------
Let's create a function that will insert some documents for us.

```js
var insertDocuments = function(db, callback) {
  // Get the documents collection
  var collection = db.collection('documents');
  // Insert some documents
  collection.insertMany([
    {a : 1}, {a : 2}, {a : 3}
  ], function(err, result) {
    assert.equal(err, null);
    assert.equal(3, result.result.n);
    assert.equal(3, result.ops.length);
    console.log("Inserted 3 documents into the document collection");
    callback(result);
  });
}
```

The insert command will return a results object that contains several fields that might be useful.

* **result** Contains the result document from MongoDB
* **ops** Contains the documents inserted with added **_id** fields
* **connection** Contains the connection used to perform the insert

Let's add call the **insertDocuments** command to the **MongoClient.connect** method callback.

```js
var MongoClient = require('mongodb').MongoClient
  , assert = require('assert');

// Connection URL
var url = 'mongodb://localhost:27017/myproject';
// Use connect method to connect to the Server
MongoClient.connect(url, function(err, db) {
  assert.equal(null, err);
  console.log("Connected correctly to server");

  insertDocuments(db, function() {
    db.close();
  });
});
```

We can now run the update **app.js** file.

```
node app.js
```

You should see the following output after running the **app.js** file.

```
Connected correctly to server
Inserted 3 documents into the document collection
```

Updating a document
-------------------
Let's look at how to do a simple document update by adding a new field **b** to the document that has the field **a** set to **2**.

```js
var updateDocument = function(db, callback) {
  // Get the documents collection
  var collection = db.collection('documents');
  // Update document where a is 2, set b equal to 1
  collection.updateOne({ a : 2 }
    , { $set: { b : 1 } }, function(err, result) {
    assert.equal(err, null);
    assert.equal(1, result.result.n);
    console.log("Updated the document with the field a equal to 2");
    callback(result);
  });  
}
```

The method will update the first document where the field **a** is equal to **2** by adding a new field **b** to the document set to **1**. Let's update the callback function from **MongoClient.connect** to include the update method.

```js
var MongoClient = require('mongodb').MongoClient
  , assert = require('assert');

// Connection URL
var url = 'mongodb://localhost:27017/myproject';
// Use connect method to connect to the Server
MongoClient.connect(url, function(err, db) {
  assert.equal(null, err);
  console.log("Connected correctly to server");

  insertDocuments(db, function() {
    updateDocument(db, function() {
      db.close();
    });
  });
});
```

Delete a document
-----------------
Next lets delete the document where the field **a** equals to **3**.

```js
var deleteDocument = function(db, callback) {
  // Get the documents collection
  var collection = db.collection('documents');
  // Delete document where a is 3
  collection.deleteOne({ a : 3 }, function(err, result) {
    assert.equal(err, null);
    assert.equal(1, result.result.n);
    console.log("Removed the document with the field a equal to 3");
    callback(result);
  });
}
```

This will delete the first document where the field **a** equals to **3**. Let's add the method to the **MongoClient
.connect** callback function.

```js
var MongoClient = require('mongodb').MongoClient
  , assert = require('assert');

// Connection URL
var url = 'mongodb://localhost:27017/myproject';
// Use connect method to connect to the Server
MongoClient.connect(url, function(err, db) {
  assert.equal(null, err);
  console.log("Connected correctly to server");

  insertDocuments(db, function() {
    updateDocument(db, function() {
      deleteDocument(db, function() {
        db.close();
      });
    });
  });
});
```

Finally let's retrieve all the documents using a simple find.

Find All Documents
------------------
We will finish up the Quickstart CRUD methods by performing a simple query that returns all the documents matching the query.

```js
var findDocuments = function(db, callback) {
  // Get the documents collection
  var collection = db.collection('documents');
  // Find some documents
  collection.find({}).toArray(function(err, docs) {
    assert.equal(err, null);
    assert.equal(2, docs.length);
    console.log("Found the following records");
    console.dir(docs);
    callback(docs);
  });
}
```

This query will return all the documents in the **documents** collection. Since we deleted a document the total
documents returned is **2**. Finally let's add the findDocument method to the **MongoClient.connect** callback.

```js
var MongoClient = require('mongodb').MongoClient
  , assert = require('assert');

// Connection URL
var url = 'mongodb://localhost:27017/myproject';
// Use connect method to connect to the Server
MongoClient.connect(url, function(err, db) {
  assert.equal(null, err);
  console.log("Connected correctly to server");

  insertDocuments(db, function() {
    updateDocument(db, function() {
      deleteDocument(db, function() {
        findDocuments(db, function() {
          db.close();
        });
      });
    });
  });
});
```

This concludes the QuickStart of connecting and performing some Basic operations using the MongoDB Node.js driver. For more detailed information you can look at the tutorials covering more specific topics of interest.

## Next Steps

 * [MongoDB Documentation](http://mongodb.org/)
 * [Read about Schemas](http://learnmongodbthehardway.com/)
 * [Star us on GitHub](https://github.com/mongodb/node-mongodb-native)
