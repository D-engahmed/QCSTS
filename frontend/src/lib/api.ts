export type ApiOptions = RequestInit & { token?: string };

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export async function api<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (options.token) headers.set("Authorization", `Bearer ${options.token}`);
  const response = await fetch(`${API_URL}${path}`, { ...options, headers, credentials: "include" });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `API request failed: ${response.status}`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const endpoints = {
  me: "/auth/me/",
  organizations: "/organizations/",
  sites: "/sites/",
  studies: "/stability/studies/",
  protocols: "/stability/protocols/",
  specifications: "/stability/specifications/",
  batches: "/batches/",
  samples: "/stability/samples/",
  results: "/results/",
  chambers: "/chambers/",
  audit: "/audit/",
  billing: "/billing/subscription/",
  plans: "/billing/plans/",
};
