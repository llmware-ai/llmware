const mongoose = require("mongoose");
const Schema = mongoose.Schema;
const User = require("./user.js");


const profileSchema = new Schema({
  user:{
    type: Schema.Types.ObjectId,
    ref: "User",
  },
  name: String,
  gender: String,
  bio: String,
  
});

const Profile = new mongoose.model("Profile", profileSchema);
module.exports = Profile;