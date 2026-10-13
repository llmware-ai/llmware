Cloudinary Node SDK
=========================
## About
The Cloudinary Node SDK allows you to quickly and easily integrate your application with Cloudinary.
Effortlessly optimize, transform, upload and manage your cloud's assets.


#### Note
This Readme provides basic installation and usage information. 
For the complete documentation, see the [Node SDK Guide](https://cloudinary.com/documentation/node_integration).

## Table of Contents
- [Key Features](#key-features)
- [Version Support](#Version-Support)
- [Installation](#installation)
- [Usage](#usage)
    - [Setup](#Setup)
    - [Transform and Optimize Assets](#Transform-and-Optimize-Assets)
    - [Generate Image and HTML Tags](#Generate-Image-and-Video-HTML-Tags)


## Key Features
- [Transform](https://cloudinary.com/documentation/node_video_manipulation#video_transformation_examples) and
 [optimize](https://cloudinary.com/documentation/node_image_manipulation#image_optimizations) assets.
- Generate [image](https://cloudinary.com/documentation/node_image_manipulation#deliver_and_transform_images) and
 [video](https://cloudinary.com/documentation/node_video_manipulation#video_element) tags.
- [Asset Management](https://cloudinary.com/documentation/node_asset_administration).
- [Secure URLs](https://cloudinary.com/documentation/video_manipulation_and_delivery#generating_secure_https_urls_using_sdks).



## Version Support
| SDK Version   | node 6-16 |
|---------------|-----------|
| 1.0.0 & up   | V         |


## Installation
```bash
npm install cloudinary
```

# Usage
### Setup
```js
// Require the Cloudinary library
const cloudinary = require('cloudinary').v2
```

### Transform and Optimize Assets
- [See full documentation](https://cloudinary.com/documentation/node_image_manipulation).

```js
cloudinary.url("sample.jpg", {width: 100, height: 150, crop: "fill", fetch_format: "auto"})
```

### Upload
- [See full documentation](https://cloudinary.com/documentation/node_image_and_video_upload).
- [Learn more about configuring your uploads with upload presets](https://cloudinary.com/documentation/upload_presets). 
```js
cloudinary.v2.uploader.upload("/home/my_image.jpg", {upload_preset: "my_preset"}, (error, result)=>{
  console.log(result, error);
});
```
### Large/Chunked Upload
- [See full documentation](https://cloudinary.com/documentation/node_image_and_video_upload#node_js_video_upload).
```js
   cloudinary.v2.uploader.upload_large(LARGE_RAW_FILE, {
          chunk_size: 7000000
        }, (error, result) => {console.log(error)});
```
### Security options
- [See full documentation](https://cloudinary.com/documentation/solution_overview#security).

## Contributions
- Ensure tests run locally (add test command)
- Open a PR and ensure Travis tests pass


## Get Help
If you run into an issue or have a question, you can either:
- Issues related to the SDK: [Open a Github issue](https://github.com/cloudinary/cloudinary_npm/issues).
- Issues related to your account: [Open a support ticket](https://cloudinary.com/contact)


## About Cloudinary
Cloudinary is a powerful media API for websites and mobile apps alike, Cloudinary enables developers to efficiently manage, transform, optimize, and deliver images and videos through multiple CDNs. Ultimately, viewers enjoy responsive and personalized visual-media experiences—irrespective of the viewing device.


## Additional Resources
- [Cloudinary Transformation and REST API References](https://cloudinary.com/documentation/cloudinary_references): Comprehensive references, including syntax and examples for all SDKs.
- [MediaJams.dev](https://mediajams.dev/): Bite-size use-case tutorials written by and for Cloudinary Developers
- [DevJams](https://www.youtube.com/playlist?list=PL8dVGjLA2oMr09amgERARsZyrOz_sPvqw): Cloudinary developer podcasts on YouTube.
- [Cloudinary Academy](https://training.cloudinary.com/): Free self-paced courses, instructor-led virtual courses, and on-site courses.
- [Code Explorers and Feature Demos](https://cloudinary.com/documentation/code_explorers_demos_index): A one-stop shop for all code explorers, Postman collections, and feature demos found in the docs.
- [Cloudinary Roadmap](https://cloudinary.com/roadmap): Your chance to follow, vote, or suggest what Cloudinary should develop next. 
- [Cloudinary Facebook Community](https://www.facebook.com/groups/CloudinaryCommunity): Learn from and offer help to other Cloudinary developers.
- [Cloudinary Account Registration](https://cloudinary.com/users/register/free): Free Cloudinary account registration.
- [Cloudinary Website](https://cloudinary.com): Learn about Cloudinary's products, partners, customers, pricing, and more.


## Licence
Released under the MIT license.
