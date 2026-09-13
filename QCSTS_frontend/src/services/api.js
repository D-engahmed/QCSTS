// src/services/api.js
// ─────────────────────────────────────────────────────────────────────────────
// CQSTS Backend API Service
// BASE URL: change this one line to switch between dev / docker / production
// ─────────────────────────────────────────────────────────────────────────────

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

// ── Token helpers ─────────────────────────────────────────────────────────────
export const getToken = () => localStorage.getItem("qc_access_token");
export const getRefreshToken = () => localStorage.getItem("qc_refresh_token");

export const saveAuth = (access, refresh, user) => {
  localStorage.setItem("qc_access_token", access);
  localStorage.setItem("qc_refresh_token", refresh);
  localStorage.setItem("qc_user", JSON.stringify(user));
  localStorage.setItem("qc_logged_in", "true");
};

export const clearAuth = () => {
  localStorage.removeItem("qc_access_token");
  localStorage.removeItem("qc_refresh_token");
  localStorage.removeItem("qc_user");
  localStorage.removeItem("qc_logged_in");
};

export const getCurrentUser = () => {
  try {
    return JSON.parse(localStorage.getItem("qc_user") || "null");
  } catch {
    return null;
  }
};

// ── Core request with auto token refresh ─────────────────────────────────────
let isRefreshing = false;
let refreshSubscribers = [];

const onRefreshed = (token) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

const addRefreshSubscriber = (cb) => {
  refreshSubscribers.push(cb);
};

const request = async (method, path, body = null, extraHeaders = {}) => {
  const makeHeaders = (token) => ({
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extraHeaders,
  });

  const fetchOptions = (token) => ({
    method,
    headers: makeHeaders(token),
    ...(body ? { body: JSON.stringify(body) } : {}),
  });

  let res = await fetch(`${BASE_URL}${path}`, fetchOptions(getToken()));

  // If token expired, try to refresh once
  if (res.status === 401 && !isRefreshing) {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      isRefreshing = true;
      try {
        const refreshRes = await fetch(`${BASE_URL}/auth/token/refresh/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh: refreshToken }),
        });
        if (refreshRes.ok) {
          const refreshData = await refreshRes.json();
          const newAccess = refreshData.access || refreshData.data?.access;
          if (newAccess) {
            localStorage.setItem("qc_access_token", newAccess);
            onRefreshed(newAccess);
            // Retry the original request with new token
            res = await fetch(`${BASE_URL}${path}`, fetchOptions(newAccess));
          } else {
            clearAuth();
            window.location.href = "/";
            throw new Error("Session expired. Please login again.");
          }
        } else {
          clearAuth();
          window.location.href = "/";
          throw new Error("Session expired. Please login again.");
        }
      } catch (err) {
        clearAuth();
        window.location.href = "/";
        throw err;
      } finally {
        isRefreshing = false;
      }
    } else {
      clearAuth();
      window.location.href = "/";
      throw new Error("Session expired. Please login again.");
    }
  }

  // If still 401 after refresh attempt, logout
  if (res.status === 401) {
    clearAuth();
    window.location.href = "/";
    throw new Error("Session expired. Please login again.");
  }

  const data = await res.json();
  if (!res.ok) {
    const errors = data?.errors || {};
    const msg =
      errors?.non_field_errors?.[0] ||
      errors?.detail ||
      Object.values(errors)?.[0]?.[0] ||
      data?.message ||
      "Something went wrong";
    throw new Error(msg);
  }

  // Backend always returns { success: true, data: ... }
  return data.data ?? data;
};

// Convenience helpers
const get = (path, params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request("GET", qs ? `${path}?${qs}` : path);
};
const post = (path, body, extraHeaders = {}) =>
  request("POST", path, body, extraHeaders);
const patch = (path, body) => request("PATCH", path, body);
const del = (path) => request("DELETE", path);

// ── AUTH ──────────────────────────────────────────────────────────────────────
export const login = async (email, password) => {
  const data = await post("/auth/login/", { email, password });
  saveAuth(data.access, data.refresh, data.user);
  return data;
};

export const logout = async () => {
  try {
    await post("/auth/logout/", { refresh: getRefreshToken() });
  } catch {
    // ignore errors on logout
  } finally {
    clearAuth();
  }
};

export const getMe = () => get("/auth/me/");
export const changePassword = (currentPassword, newPassword) =>
  post("/auth/change-password/", {
    current_password: currentPassword,
    new_password: newPassword,
  });

// ── USER MANAGEMENT (admin only) ─────────────────────────────────────────────
export const getUsers = () => get("/auth/users/");
export const createUser = (data) => post("/auth/users/", data);
export const updateUser = (id, data) => patch(`/auth/users/${id}/`, data);
export const deactivateUser = (id) => del(`/auth/users/${id}/`);

// ── ROLES & PERMISSIONS (Dynamic System) ────────────────────────────────────
export const getRoles = () => get("/auth/roles/");
export const createRole = (data) => post("/auth/roles/", data);
export const getPermissions = () => get("/auth/permissions/");

// ── MONOGRAPHS ────────────────────────────────────────────────────────────────
export const getMonographs = () => get("/products/monographs/");
export const getMonograph = (id) => get(`/products/monographs/${id}/`);
export const createMonograph = (data) => post("/products/monographs/", data);
export const updateMonograph = (id, data) =>
  patch(`/products/monographs/${id}/`, data);
export const approveMonograph = (id) =>
  post(`/products/monographs/${id}/approve/`);

// ── MONOGRAPH TESTS ───────────────────────────────────────────────────────────
export const getMonographTests = (monographId) =>
  get(`/products/monographs/${monographId}/tests/`);
export const addMonographTest = (monographId, data) =>
  post(`/products/monographs/${monographId}/tests/`, data);

// ── PRODUCTS ──────────────────────────────────────────────────────────────────
export const getProducts = () => get("/products/");
export const getProduct = (id) => get(`/products/${id}/`);
export const createProduct = (data) => post("/products/", data);
export const updateProduct = (id, data) => patch(`/products/${id}/`, data);

// ── BATCHES ───────────────────────────────────────────────────────────────────
export const getBatches = (filters = {}) => get("/batches/", filters);
export const getBatch = (id) => get(`/batches/${id}/`);
export const createBatch = (data) => post("/batches/", data);
export const updateBatch = (id, data) => patch(`/batches/${id}/`, data);

// ── TEST POINTS ───────────────────────────────────────────────────────────────
export const getTestPoints = (filters = {}) => get("/test-points/", filters);
export const getOverdueTests = () => get("/test-points/", { status: "overdue" });
export const getUpcomingTests = () => get("/test-points/", { upcoming: "true" });
export const getBatchTestPoints = (batchId) =>
  get("/test-points/", { batch: batchId });

// ── CHAMBER ───────────────────────────────────────────────────────────────────
export const getChamberInventory = (filters = {}) => get("/chamber/", filters);
export const getSamplePulls = (batchId = null) =>
  get("/chamber/pulls/", batchId ? { batch: batchId } : {});
export const recordPull = (data) => post("/chamber/pulls/", data);
export const moveBatch = (data) => post("/chamber/move/", data);
export const getLocationHistory = (batchId) =>
  get(`/chamber/locations/${batchId}/`);

// ── RESULTS ───────────────────────────────────────────────────────────────────
export const verifySignature = (password) =>
  post("/results/signature/verify/", { password });
export const submitResult = (data, signatureToken) =>
  post("/results/", data, { "X-Signature-Token": signatureToken });
export const getResults = (filters = {}) => get("/results/", filters);
export const getResult = (id) => get(`/results/${id}/`);
// All submitted results for a batch, across every test point, in one call.
export const getBatchResults = (batchId) => get("/results/", { batch: batchId });

// ── DASHBOARD ─────────────────────────────────────────────────────────────────
export const getDashboard = () => get("/reports/dashboard/");

// ── AUDIT ─────────────────────────────────────────────────────────────────────
export const getAuditLog = (filters = {}) => get("/audit/", filters);

// ── Default export for convenience ────────────────────────────────────────────
export default {
  // auth
  login,
  logout,
  getMe,
  changePassword,
  // users
  getUsers,
  createUser,
  updateUser,
  deactivateUser,
  // roles & permissions
  getRoles,
  createRole,
  getPermissions,
  // monographs
  getMonographs,
  getMonograph,
  createMonograph,
  updateMonograph,
  approveMonograph,
  getMonographTests,
  addMonographTest,
  // products
  getProducts,
  getProduct,
  createProduct,
  updateProduct,
  // batches
  getBatches,
  getBatch,
  createBatch,
  updateBatch,
  // test points
  getTestPoints,
  getOverdueTests,
  getUpcomingTests,
  getBatchTestPoints,
  // chamber
  getChamberInventory,
  getSamplePulls,
  recordPull,
  moveBatch,
  getLocationHistory,
  // results
  verifySignature,
  submitResult,
  getResults,
  getResult,
  getBatchResults,
  // dashboard
  getDashboard,
  // audit
  getAuditLog,
  // helpers
  getToken,
  getCurrentUser,
  clearAuth,
};