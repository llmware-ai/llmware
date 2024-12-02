const cloudinary = require('cloudinary').v2;
const { CloudinaryStorage } = require('../../');
const express = require('express');
const multer = require('multer');

const app = express();

const storage = new CloudinaryStorage({
  cloudinary: cloudinary,
  params: {
    folder: () => 'test-folder',
  },
});

const parser = multer({ storage: storage });

app.post('/upload', parser.single('image'), function (req, res) {
  res.json(req.file);
});

app.listen(8080);
