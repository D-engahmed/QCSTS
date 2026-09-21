import { authStorage } from "./auth";

export type ApiOptions = RequestInit & {
  token?: string;
  organizationId?: string;
  siteId?: string;
  skipRefresh?: boolean;
};
export type ApiEnvelope<T> = { success: boolean; data: T; message?: string; errors?: unknown };

const configuredApiUrl = (
  process.env.NEXT_PUBLIC_API_URL ?? "/api/backend"
).replace(/\/$/, "");

const API_URL =
  typeof window !== "undefined" &&
  /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?\/api\/v1$/i.test(configuredApiUrl)
    ? "/api/backend"
    : configuredApiUrl;

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

  let response: Response;

  try {
    response = await fetch(API_URL + path, {
      ...init,
      headers,
      credentials: "include",
      cache: "no-store",
    });
  } catch (error) {
    const origin = typeof window !== "undefined" ? window.location.origin : "unknown-origin";
    const detail = error instanceof Error ? error.message : "Network request failed";
    throw new Error(
      `Unable to reach QCSTS API at ${API_URL}. Browser origin: ${origin}. ${detail} Check that Django is running and CORS_ALLOWED_ORIGINS includes the frontend origin.`,
    );
  }

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
  monographs: "/products/monographs/",
  monographTests: (id: string) => `/products/monographs/${id}/tests/`,
  monographApprove: (id: string) => `/products/monographs/${id}/approve/`,
  signatureVerify: "/results/signature/verify/",
  login: "/auth/login/",
  logout: "/auth/logout/",
  me: "/auth/me/",
  users: "/auth/users/",
  user: (id: string) => `/auth/users/${id}/`,
  changePassword: "/auth/change-password/",
  passwordReset: "/auth/password-reset/",
  passwordResetConfirm: "/auth/password-reset/confirm/",
  verifyEmail: "/auth/verify-email/",
  organizations: "/platform/organizations/",
  sites: "/platform/sites/",
  site: (id: string) => `/platform/sites/${id}/`,
  dashboard: "/reports/dashboard/",
  exports: "/reports/export.csv/",
  studies: "/stability/studies/",
  storageConditions: "/stability/storage-conditions/",
  protocols: "/stability/protocols/",
  protocolVersions: "/stability/protocol-versions/",
  specifications: "/stability/specifications/",
  specificationVersions: "/stability/specification-versions/",
  products: "/products/",
  batches: "/batches/",
  timePoints: "/stability/timepoints/",
  studyBatches: "/stability/study-batches/",
  testPoints: "/test-points/",
  samples: "/stability/samples/",
  samplePulls: "/chamber/pulls/",
  results: "/results/",
  resultReview: (id: string) => `/results/${id}/review/`,
  resultApprove: (id: string) => `/results/${id}/approve/`,
  resultReject: (id: string) => `/results/${id}/reject/`,
  resultCorrect: (id: string) => `/results/${id}/correct/`,
  chambers: "/chamber/",
  locationMove: "/chamber/move/",
  audit: "/audit/",
  oos: "/quality/oos/",
  oot: "/quality/oot/",
  deviations: "/quality/deviations/",
  capa: "/quality/capa/",
  changeControls: "/quality/change-control/",
  qualityTransition: (resource: string, id: string) => `/quality/${resource}/${id}/transition/`,
  complianceSignatures: "/compliance/signatures/",
  controlledRecords: "/compliance/records/",
  validationArtifacts: "/compliance/validation/",
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
