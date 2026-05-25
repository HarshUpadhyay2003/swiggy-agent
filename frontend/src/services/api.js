import axios from 'axios'

console.log("ENV:", import.meta.env);

const BASE_URL = import.meta.env.VITE_API_BASE_URL;
console.log("BASE_URL:", BASE_URL);

if (!BASE_URL) {
  console.warn("⚠️ VITE_API_BASE_URL is undefined. Requests will fail! Check your .env or .env.production file.");
}

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000, // Increased to 60s to handle Render free tier cold starts
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use((config) => config)

api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error)
)

export default api
