import axiosInstance from "./axiosInstance.js";

const api = "http://localhost:8080";

async function postLogin(email, password, rememberMe) {
  try {
    const response = await axiosInstance.post(`${api}/login/postLogin`, {
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
    const response = await axiosInstance.post(`${api}/login/postRegister`, {
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
    const response = await axiosInstance.get(`${api}/login/getLogout`);
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
      const response = await axiosInstance.get(`${api}/login/isAuth`);
      console.log("response", response);
      return response.data;
    } catch (error) {
      console.error(
        "Error checking auth:",
        error.response ? error.response.data : error.message
      );
      throw new Error(
        "Failed to check auth: " +
          (error.response ? error.response.data : error.message)
      );
    }
  }
  export function isAuth() {
    return isUserAuthenticated();
  }
  
