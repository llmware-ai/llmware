Cloudinary Javascript Core SDK (Legacy)
=======================================

## About
The Javascript SDK allows you to quickly and easily integrate your application with Cloudinary.
Effortlessly optimize and transform your cloud's assets.

#### Note
This Readme provides basic installation and usage information.
For the complete documentation, see the [Javascript SDK Guide](https://cloudinary.com/documentation/javascript1_integration).


## Table of Contents
- [Key Features](#key-features)
- [Browser Support](#Browser-Support)
- [Installation](#installation)
- [Usage](#usage)
    - [Setup](#Setup)
    - [Transform and Optimize Assets](#Transform-and-Optimize-Assets)
    - [Generate Image and HTML Tags](#Generate-Image-and-Video-HTML-Tags)
    - [File upload](#File-upload)
- [Contributions](#Contributions)
- [About Cloudinary](#About-Cloudinary)
- [Additional Resources](#Additional-Resources)
- [Licence](#Licence)

## Key Features
- [Transform](https://cloudinary.com/documentation/javascript1_video_manipulation#video_transformation_examples) and [optimize](https://cloudinary.com/documentation/javascript1_image_manipulation#image_optimizations) assets.
- Generate [image](https://cloudinary.com/documentation/javascript1_image_manipulation#deliver_and_transform_images) and [video](https://cloudinary.com/documentation/javascript1_video_manipulation#video_element) tags.

## Browser Support
Chrome, Safari, Firefox, IE 11

## Installation
### Install using your favorite package manager (yarn, npm)
```bash
npm install cloudinary-core
```
Or
```bash
yarn add cloudinary-core
```

## Usage
### Setup
There are several ways to configure cloudinary-core:

##### Explicitly
```javascript
var cl = cloudinary.Cloudinary.new( { cloud_name: "demo"});
```

##### Using the config function
```javascript

// Using the config function
var cl = cloudinary.Cloudinary.new();
cl.config( "cloud_name", "demo");
```

##### From meta tags in the current HTML document
When using the library in a browser environment, you can use meta tags to define the configuration options.

The `init()` function is a convenience function that invokes both `fromDocument()` and `fromEnvironment()`.


For example, add the following to the header tag:
```html
<meta name="cloudinary_cloud_name" content="demo">
```

In your JavaScript source, invoke `fromDocument()`:
```javascript
var cl = cloudinary.Cloudinary.new();
cl.fromDocument();
// or
cl.init();
```

##### From environment variables

When using the library in a backend environment such as NodeJS, you can use an environment variable to define the configuration options.

Set the environment variable, for example:
```shell
export CLOUDINARY_URL=cloudinary://demo
```
In your JavaScript source, invoke `fromEnvironment()`:
```javascript
var cl = cloudinary.Cloudinary.new();
cl.fromEnvironment();
// or
cl.init();
```

### Transform and Optimize Assets
- [See full documentation](https://cloudinary.com/documentation/javascript1_image_manipulation)

```javascript
// Apply a single transformation
cl.url( "sample", { crop: "scale", width: "200", angle: "10" })

// Chain (compose) multiple transformations
cl.url( "sample", {
  transformation: [
    { angle: -45 },
    { effect: "trim", angle: "45", crop: "scale", width: "600" },
    { overlay: "text:Arial_100:Hello" }
  ]
});
```

### Generate Image and Video HTML Tags
- Use the ```image()``` function to generate an HTMLImageElement
- Use the ```imageTag()``` function to generate an ImageTag instance
- Use the ```video()``` function to generate an HTMLVideoElement
- Use the ```videoTag()``` function to generate a VideoTag instance

### File upload
See [cloudinary-jquery-file-upload](https://github.com/cloudinary/cloudinary_js/pkg/cloudinary-jquery-file-upload).

## Contributions
- Ensure tests run locally (```npm run test```)
- Open a PR and ensure Travis tests pass

## Get Help
If you run into an issue or have a question, you can either:
- [Open a Github issue](https://github.com/Cloudinary/cloudinary_js/issues)  (for issues related to the SDK)
- [Open a support ticket](https://cloudinary.com/contact) (for issues related to your account)

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
