const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const fieldSchema = new Schema({
    name: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
    deleted: {
      type: Number,
      default: 0,
      required: true,
    },
});

const userSchema = new Schema({
  email: {
    type: String,
    required: true,
  },
  name: {
    type: String,
    required: true,
  },
  surname: {
    type: String,
    required: true,
  },
  deleted: {
    type: Number,
    default: 0,
    required: true,
  },
  password: {
    type: String,
    required: true,
  },
  fields: {
    type: [fieldSchema],
    default: [],
  }
});

module.exports = mongoose.model("users", userSchema);
