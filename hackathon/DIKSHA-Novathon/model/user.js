const mongoose = require("mongoose");
const Schema = mongoose.Schema;
const passportLocalMongoose = require("passport-local-mongoose");


const userSchema = new Schema({
  email: {
    type: String,
    unique: true,
  },
  phone: Number,
});
userSchema.plugin(passportLocalMongoose);
const User = new mongoose.model("User", userSchema);
module.exports = User;