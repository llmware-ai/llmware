const cloudinary = require("cloudinary").v2;
const { CloudinaryStorage } = require("multer-storage-cloudinary");

cloudinary.config({
  cloud_name: process.env.CLOUD_NAME,
  api_key: process.env.CLOUD_API_KEY,
  api_secret: process.env.CLOUD_SECRET_KEY,
});

const storage = new CloudinaryStorage({
  cloudinary: cloudinary,
  params: {
    folder: "WanderLust_DEV",
    allowedFormats: ["png", "jpeg", "jpg", "pdf"], // allowed file formats
    fileFilter: (req, file) => {
      // Ensure that only pdf files are allowed
      if (file.mimetype === 'application/pdf') {
        // Accept the file
        return true;
      } else {
        // Reject the file
        return false;
      }
    }
  },
});

module.exports = {
  cloudinary, storage,
};
