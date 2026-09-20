import { authStorage } from "./auth";

export type ApiOptions = RequestInit & {
  token?: string;
  organizationId?: string;
  siteId?: string;
  skipRefresh?: boolean;
};
export type ApiEnvelope<T> = { success: boolean; data: T; message?: string; errors?: unknown };

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");

function errorMessage(payload: unknown, status: number) {
  if (payload && typeof payload === "object") {
    const p = payload as { message?: string; errors?: Record<string, string[] | string> };
    if (p.message) return p.message;
    if (p.errors) {
      return Object.entries(p.errors)
        .map(([k, v]) => k + ": " + (Array.isArray(v) ? v.join(", ") : v))
        .join(" · ");
    }
    const detail = (payload as { detail?: string }).detail;
    if (detail) return detail;
  }
  return `Request failed (${status})`;
}

async function refreshAccess() {
  const refresh = authStorage.refresh;
  if (!refresh || typeof window === "undefined") return null;

  const response = await fetch(API_URL + "/auth/token/refresh/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) return null;

  const payload = await response.json();
  const access = payload?.access ?? payload?.data?.access;
  if (!access) return null;

  localStorage.setItem("qc_access_token", access);
  return access as string;
}

async function parsePayload(response: Response) {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function api<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { token, organizationId, siteId, skipRefresh, ...init } = options;
  const headers = new Headers(init.headers);

  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const access = token ?? authStorage.access;
  if (access) headers.set("Authorization", "Bearer " + access);

  const organization = organizationId ?? authStorage.organizationId;
  const site = siteId ?? authStorage.siteId;
  if (organization) headers.set("X-Organization-ID", organization);
  if (site) headers.set("X-Site-ID", site);

  let response = await fetch(API_URL + path, {
    ...init,
    headers,
    credentials: "include",
    cache: "no-store",
  });

  if (response.status === 401 && !skipRefresh && typeof window !== "undefined") {
    const renewed = await refreshAccess();
    if (renewed) {
      return api<T>(path, { ...options, token: renewed, skipRefresh: true });
    }

    authStorage.clear();
    window.location.assign("/login");
    throw new Error("Your session has expired. Please login again.");
  }

  const payload = await parsePayload(response);

  if (!response.ok) {
    throw new Error(errorMessage(payload, response.status));
  }

  if (response.status === 204 || payload === null) {
    return undefined as T;
  }

  return payload as T;
}

export const endpoints = {
  register: "/auth/register/",
  login: "/auth/login/",
  logout: "/auth/logout/",
  me: "/auth/me/",
  users: "/auth/users/",
  changePassword: "/auth/change-password/",
  organizations: "/platform/organizations/",
  sites: "/platform/sites/",
  dashboard: "/reports/dashboard/",
  studies: "/stability/studies/",
  protocols: "/stability/protocols/",
  specifications: "/stability/specifications/",
  batches: "/batches/",
  testPoints: "/test-points/",
  samples: "/stability/samples/",
  timepoints: "/stability/timepoints/",
  results: "/results/",
  chambers: "/chamber/",
  audit: "/audit/",
  oos: "/quality/oos/",
  oot: "/quality/oot/",
  deviations: "/quality/deviations/",
  capa: "/quality/capa/",
  billing: "/billing/subscription/",
  plans: "/billing/plans/",
  usage: "/billing/usage/",
};

export type RegistrationInput = {
  organization_name: string;
  legal_name?: string;
  slug?: string;
  country: string;
  timezone?: string;
  currency?: string;
  site_name?: string;
  site_address?: string;
  full_name: string;
  email: string;
  password: string;
};

export type AuthResponse = {
  access: string;
  refresh: string;
  user: import("./auth").User;
  organization?: import("./auth").Organization | null;
  site?: import("./auth").Site | null;
  membership?: import("./auth").Membership | null;
};
