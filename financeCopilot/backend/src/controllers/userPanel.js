const User = require("../models/users");

exports.doSurvey = async (req, res) => {
  // Check if session and user exist
  if (!req.session || !req.session.user) {
    return res.status(401).json({ message: "Unauthorized: User session not found" });
  }

  const userId = req.session.user.id;
  const surveyData = req.body.surveyData;

  if (!Array.isArray(surveyData)) {
    return res.status(400).json({ message: "Invalid survey data format. Expected an array." });
  }

  try {
    // Find the user by ID
    const user = await User.findById(userId);

    if (!user) {
      return res.status(404).json({ message: "User not found" });
    }

    // Create a Set of existing field names to prevent duplicates
    const existingFieldNames = new Set(user.fields.map(field => field.name));

    // Filter out duplicates based on field name
    const newFields = surveyData.filter(field => 
      field.name && !existingFieldNames.has(field.name)
    );

    // Append new unique fields to user's fields array
    user.fields.push(...newFields);

    // Save updated user
    await user.save();

    // Update isSurvey flag
    user.isSurvey = 1;
    await user.save();

    return res.status(200).json({ message: "Survey data imported successfully", addedFields: newFields.length });
  } catch (error) {
    console.error("Error saving survey data:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
};