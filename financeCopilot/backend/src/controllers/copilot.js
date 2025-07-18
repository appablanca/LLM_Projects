const axios = require("axios");
const FormData = require("form-data");
const financeCopilotUrl = "http://localhost:5001";

exports.sendMessageToCopilot = async (req, res) => {
  try {
    const { message } = req.body;
    const file = req.file;

    if (!message && !file) {
      return res.status(400).json({
        success: false,
        message: "Message or file is required",
      });
    }

    const formData = new FormData();
    if (message) formData.append("message", message);
    if (file) {
      formData.append("file", file.buffer, {
        filename: file.originalname,
        contentType: file.mimetype,
      });
    }
    if (req.session.user) {
      formData.append("user", JSON.stringify(req.session.user));
    }

    const response = await axios.post(`${financeCopilotUrl}/chat`, formData, {
      headers: {
        ...formData.getHeaders(),
      },
    });

    return res.status(200).json(response.data);
  } catch (error) {
    console.error("Error sending message to Finance Copilot:", error);
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: "Failed to communicate with Finance Copilot",
        error: error.response.data,
      });
    }
    return res.status(500).json({
      success: false,
      message: "Failed to communicate with Finance Copilot",
      error: error.message,
    });
  }
};

exports.getBudgetPlan = async (req, res) => {
  try {
    const userId = req.session.user.id;
    if (!userId) {
      return res.status(401).json({
        success: false,
        message: "User not authenticated",
      });
    }

    const response = await axios.post(`${financeCopilotUrl}/budget-analysis`, {
      userId: userId,
    });

    return res.status(200).json(response.data);
  } catch (error) {
    console.error("Error sending message to Finance Copilot:", error);
    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        message: "Failed to communicate with Finance Copilot",
        error: error.response.data,
      });
    }
    return res.status(500).json({
      success: false,
      message: "Failed to communicate with Finance Copilot",
      error: error.message,
    });
  }
};
