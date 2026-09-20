import axios from "axios";

/** Same-origin API client — the Django server serves both the app and /api/. */
const api = axios.create({
  baseURL: "/api/",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// Response interceptor — normalize errors into readable messages.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail =
      error.response?.data?.detail ||
      (error.response?.data &&
        typeof error.response.data === "object" &&
        Object.entries(error.response.data)
          .map(([field, msgs]) => `${field}: ${[].concat(msgs).join(", ")}`)
          .join(" · ")) ||
      (error.code === "ECONNABORTED"
        ? "Request timed out — is the server running?"
        : error.message) ||
      "Unexpected error";
    return Promise.reject(new Error(detail));
  }
);

export default api;
