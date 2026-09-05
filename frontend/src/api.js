const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
const TOKEN_KEY = "reckon_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

// Every failed call throws an Error carrying the API's error_code, so callers
// can branch on the code instead of parsing messages.
export async function api(path, { method = "GET", body } = {}) {
  const token = getToken();
  const response = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });

  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(data?.message || "Something went wrong.");
    error.code = data?.error_code;
    error.details = data?.details;
    error.status = response.status;
    throw error;
  }
  return data;
}
