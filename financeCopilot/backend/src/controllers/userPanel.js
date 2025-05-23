const User = require("../models/users");

exports.doSurvey = async (req, res) => {
  if (!req.session || !req.session.user) {
    return res
      .status(401)
      .json({ message: "Unauthorized: User session not found" });
  }

  const userId = req.session.user.id;
  const surveyData = req.body.surveyData;

  if (!Array.isArray(surveyData)) {
    return res
      .status(400)
      .json({ message: "Invalid survey data format. Expected an array." });
  }

  try {
    const user = await User.findById(userId);

    if (!user) {
      return res.status(404).json({ message: "User not found" });
    }

    const newFields = surveyData.map((item) => ({
      name: item.name,
      content: item.content,
      deleted: 0,
    }));

    user.fields.push(...newFields);
    user.isSurvey = 1;

    await user.save();

    return res.status(200).json({
      message: "Survey data saved successfully",
      addedFields: newFields.length,
    });
  } catch (error) {
    console.error("Error saving survey data:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
};

exports.editSurvey = async (req, res) => {
  if (!req.session || !req.session.user) {
    return res
      .status(401)
      .json({ message: "Unauthorized: User session not found" });
  }

  const userId = req.session.user.id;
  const surveyData = req.body.surveyData;

  if (!Array.isArray(surveyData)) {
    return res
      .status(400)
      .json({ message: "Invalid survey data format. Expected an array." });
  }

  try {
    const user = await User.findById(userId);

    if (!user) {
      return res.status(404).json({ message: "User not found" });
    }

    surveyData.forEach((item) => {
      const existingField = user.fields.find((field) => field.name === item.name);
      if (existingField) {
        existingField.content = item.content;
        existingField.deleted = 0;
      } else {
        user.fields.push({
          name: item.name,
          content: item.content,
          deleted: 0,
        });
      }
    });

    await user.save();

    return res.status(200).json({
      message: "Survey data updated successfully",
      updatedFields: surveyData.length,
    });
  } catch (error) {
    console.error("Error updating survey data:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
};
exports.getFields = async (req, res) => {
    let userId;
    
    // Check if userId is provided in query params
    if (req.query.userId) {
        userId = req.query.userId;
    } else {
        // Fallback to session-based authentication
        if (!req.session || !req.session.user) {
            return res
                .status(401)
                .json({ message: "Unauthorized: User session not found" });
        }
        userId = req.session.user.id;
    }
    
    try {
        const user = await User.findById(userId);
    
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }
    
        return res.status(200).json(user.fields);
    } catch (error) {
        console.error("Error fetching user fields:", error);
        return res.status(500).json({ message: "Internal server error" });
    }
};

exports.invest = async (req, res) => {
  let userId;
  const { investData } = req.body;
  if (req.query.userId) {
    userId = req.query.userId;
} else {
    // Fallback to session-based authentication
    if (!req.session || !req.session.user) {
        return res
            .status(401)
            .json({ message: "Unauthorized: User session not found" });
    }
    userId = req.session.user.id;
}
  if (!userId || !Array.isArray(investData) || investData.length === 0) {
    return res.status(400).json({ message: "Invalid request data" });
  }

  try {
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ message: "User not found" });
    }

    // Convert symbols into fieldSchema-compliant objects
    const investmentFields = investData.map(symbol => ({
      name: "investment",     // or "stock" if you prefer
      content: symbol,
      deleted: 0
    }));

    user.fields.push(...investmentFields);
    await user.save();

    return res.status(200).json({ message: "Investments saved successfully" });
  } catch (error) {
    console.error("Error saving investments:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
};
