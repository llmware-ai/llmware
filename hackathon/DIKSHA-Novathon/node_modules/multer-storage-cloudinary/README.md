# Multer Storage Cloudinary

A multer storage engine for Cloudinary. Also consult the [Cloudinary API](https://github.com/cloudinary/cloudinary_npm).

## Installation

```sh
npm install multer-storage-cloudinary
```

## Usage

```javascript
const cloudinary = require('cloudinary').v2;
const { CloudinaryStorage } = require('multer-storage-cloudinary');
const express = require('express');
const multer = require('multer');

const app = express();

const storage = new CloudinaryStorage({
  cloudinary: cloudinary,
  params: {
    folder: 'some-folder-name',
    format: async (req, file) => 'png', // supports promises as well
    public_id: (req, file) => 'computed-filename-using-request',
  },
});

const parser = multer({ storage: storage });

app.post('/upload', parser.single('image'), function (req, res) {
  res.json(req.file);
});
```

### File properties

File objects will expose the following properties mapped from the [Cloudinary API](https://github.com/cloudinary/cloudinary_npm#upload):

| Key        | Description                         |
| ---------- | ----------------------------------- |
| `filename` | public_id of the file on cloudinary |
| `path`     | A URL for fetching the file         |
| `size`     | Size of the file in bytes           |

### Options

Storage can be configured using the `options` argument passed to the `CloudinaryStorage` constructor.

```javascript
const { CloudinaryStorage } = require('multer-storage-cloudinary');

const storage = new CloudinaryStorage({
  cloudinary: cloudinary,
  params: {
    // upload paramters
  },
});
```

All parameters are optional except the configured Cloudinary API object:

| Parameter            | Description                                                                                                                                                                                                                                           | Type                      |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| `options.cloudinary` | A Cloudinary API object <br>The API must be configured by the user                                                                                                                                                                                    | `object` <br>**required** |
| `options.params`     | An object or a function that resolves to an object which can contain any/all properties described in the [Cloudinary upload API docs](https://cloudinary.com/documentation/image_upload_api_reference#upload_method). Read below for more information | `object` or `function`    |

Each property in the params object (either directly or resolved from the function)
can either be a static value or an async function that resolves to the required value.
All upload parameters specified in the [Cloudinary docs](https://cloudinary.com/documentation/image_upload_api_reference#upload_method) are supported.

_Note: `public_id` is different in that it must always be a functional parameter_

Functional parameters are called on every request and can be used in the following way:

```javascript
const cloudinary = require('cloudinary').v2;
const { CloudinaryStorage } = require('multer-storage-cloudinary');

const storage = new CloudinaryStorage({
  cloudinary: cloudinary,
  params: {
    folder: (req, file) => 'folder_name',
    format: async (req, file) => {
      // async code using `req` and `file`
      // ...
      return 'jpeg';
    },
    public_id: (req, file) => 'some_unique_id',
  },
});
```

You can also provide all params using a single function

```javascript
const cloudinary = require('cloudinary').v2;
const { CloudinaryStorage } = require('multer-storage-cloudinary');

const storage = new CloudinaryStorage({
  cloudinary: cloudinary,
  params: async (req, file) => {
    // async code using `req` and `file`
    // ...
    return {
      folder: 'folder_name',
      format: 'jpeg',
      public_id: 'some_unique_id',
    };
  },
});
```

### Typescript

This library is written is typescript and so provides all types necessary for use
in a typescript project.

## Testing

The Cloudinary API must be configured using the `CLOUDINARY_URL` environment variable in order to run the tests.
All test files are stored in a seperate Cloudinary folder, which is deleted after tests finish.

```sh
npm test
```
