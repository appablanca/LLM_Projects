const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const fieldSchema = new Schema({
    name: {
      type: String,
      required: true,
    },
    content: {
      type: String,
      required: true,
    },
    deleted: {
      type: Number,
      default: 0,
      required: true,
    },

});

const userInfoSchema = new Schema({
  userId: {
    type: ObjectId,
    ref: "users",
    required: true,
  },
  deleted: {
    type: Number,
    default: 0,
    required: true,
  },
  fields: {
    type: [fieldSchema],
    default: [],
  }
});

module.exports = mongoose.model("userInfos", userInfoSchema);
