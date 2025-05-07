import axios from "axios";

const api = "http://localhost:8080";
const axiosInstance = axios.create({
  baseURL: api,
  withCredentials: true,
});

export default axiosInstance;