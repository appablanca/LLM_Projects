import axiosInstance from "./axiosInstance.js";

const api = "http://localhost:8080";

async function postLogin(email, password, rememberMe) {
  try {
    const response = await axiosInstance.post(`/login/postLogin`, {
      email: email,
      password: password,
      rememberMe: rememberMe,
    });
    return response.data;
  } catch (error) {
    console.error(
      "Error logining user:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to login user: " +
        (error.response ? error.response.data : error.message)
    );
  }
}
export function flogin(email, password, rememberMe) {
  return postLogin(email, password, rememberMe);
}

async function postRegister(email, name, surname, password) {
  try {
    const response = await axiosInstance.post(`/login/postRegister`, {
      email: email,
      name: name,
      surname: surname,
      password: password,
    });
    return response;
  } catch (error) {
    console.error(
      "Error registering user:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to register user: " +
        (error.response ? error.response.data : error.message)
    );
  }
}
export function fregister(email, name, surname, password) {
  return postRegister(email, name, surname, password);
}

async function getLogout() {
  try {
    const response = await axiosInstance.get(`/login/getLogout`);
    return response.data;
  } catch (error) {
    console.error(
      "Error loggingout user:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to logout user: " +
        (error.response ? error.response.data : error.message)
    );
  }
}
export function flogut() {
  return getLogout();
}

async function isUserAuthenticated() {
  try {
    console.log("Calling /login/isAuth...");
    const response = await axiosInstance.get("/login/isAuth");
    console.log("isAuth response:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ isAuth hatası:", error);
    console.error("❌ response içeriği:", error.response?.data);
    throw new Error(
      "Failed to check auth: " +
        (error.response ? error.response.data : error.message)
    );
  }
}
export function isAuth() {
  return isUserAuthenticated();
}

async function sendUserSurvey(surveyData) {
  try {
    const response = await axiosInstance.post(`/userPanel/doSurvey`,{
      surveyData: surveyData,
    });
    return response.data;
  } catch (error) {
    console.error(
      "Error getting user survey:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to get user survey: " +
        (error.response ? error.response.data : error.message)
    );
  }
}

export function sendSurvey(surveyData) {
  return sendUserSurvey(surveyData);
}

async function getUserSurvey() {
  try {
    const response = await axiosInstance.get(`/userPanel/getFields`);
    return response.data;
  } catch (error) {
    console.error(
      "Error getting user survey:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to get user survey: " +
        (error.response ? error.response.data : error.message)
    );
  }
}
export function getSurveyFields() {
  return getUserSurvey();
}

async function editSurveyFields (surveyData) {
  try {
    const response = await axiosInstance.post(`/userPanel/editSurvey`, {
      surveyData: surveyData,
    });
    return response.data;
  } catch (error) {
    console.error(
      "Error editing user survey:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to edit user survey: " +
        (error.response ? error.response.data : error.message)
    );
  }
}
export function editSurvey(surveyData) {
  return editSurveyFields(surveyData);
}

async function sendMessageToCopilot(message, file) {
  try {
    const formData = new FormData();
    if (message) formData.append('message', message);
    if (file) formData.append('file', file);

    const response = await axiosInstance.post(`/copilot/chat`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error(
      "Error sending message to copilot:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to send message to copilot: " +
        (error.response ? error.response.data : error.message)
    );
  }
}

export function sendCopilotMessage(message, file) {
  return sendMessageToCopilot(message, file);
}

async function saveTransactionsAndSpending(transactions, categoryTotals, cardLimit) {
  try {
    const response = await axiosInstance.post(`/transactions/saveTransactionsAndSpending`, {
      transactions,
      category_totals: categoryTotals,
      card_limit: cardLimit
    });
    return response.data;
  } catch (error) {
    console.error(
      "Error saving transactions:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to save transactions: " +
        (error.response ? error.response.data : error.message)
    );
  }
}

export function saveTransactions(transactions, categoryTotals, cardLimit) {
  return saveTransactionsAndSpending(transactions, categoryTotals, cardLimit);
}

async function getTransactionsAndSpending() {
  try {
    const response = await axiosInstance.get(`/transactions/getTransactionsAndSpending`);
    return response.data.data;
  } catch (error) {
    console.error(
      "Error fetching transactions:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to fetch transactions: " +
        (error.response ? error.response.data : error.message)
    );
  }
}

export function getTransactions() {
  return getTransactionsAndSpending();
}

async function getBudgetPlan() {
  try {
    const response = await axiosInstance.post(`/copilot/budget-plan`);
    return response.data;
  } catch (error) {
    console.error(
      "Error fetching budget plan:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to fetch budget plan: " +
        (error.response ? error.response.data : error.message)
    );
  }
}
export function getBudget() {
  return getBudgetPlan();
}

async function saveStocks(stocks) {
  try {
    const response = await axiosInstance.post(`/stocks/saveStocks`, {
      stocks: stocks,
    });
    return response.data;
  } catch (error) {
    console.error(
      "Error saving stocks:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to save stocks: " +
        (error.response ? error.response.data : error.message)
    );
  }
}
export function saveUserStocks(stocks) {
  return saveStocks(stocks);
}

async function getStocks() {
  try {
    const response = await axiosInstance.get(`/stocks/getStocks`);
    return response.data;
  } catch (error) {
    console.error(
      "Error fetching stocks:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to fetch stocks: " +
        (error.response ? error.response.data : error.message)
    );
  }
}
export function getUserStocks() {
  return getStocks();
}

async function removeStock(symbol) {
  try {
    const response = await axiosInstance.post(`/stocks/removeStock`, {
      symbol: symbol,
    });
    return response.data;
  } catch (error) {
    console.error(
      "Error removing stock:",
      error.response ? error.response.data : error.message
    );
    throw new Error(
      "Failed to remove stock: " +
        (error.response ? error.response.data : error.message)
    );
  }
}
export function removeUserStock(symbol) {
  return removeStock(symbol);
}
