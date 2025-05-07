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
    const response = await axiosInstance.post(`/userPanel/editSurveyFields`, {
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
export function editSurvey(surveyData) {
  return editSurveyFields(surveyData);
}
