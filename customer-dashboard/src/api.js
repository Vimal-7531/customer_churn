const BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

const API_KEY = "mysecretkey";

export const api = {
  get: async (endpoint) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers: {
        "X-API-Key": API_KEY
      }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `Request failed with status ${response.status}`
      );
    }

    return response.json();
  },

  post: async (endpoint, data) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `Request failed with status ${response.status}`
      );
    }

    return response.json();
  }
};