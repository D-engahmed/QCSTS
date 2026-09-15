export type ApiOptions = RequestInit & { token?: string; organizationId?: string; siteId?: string };
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
export async function api<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const headers = new Headers(options.headers); headers.set("Content-Type", "application/json");
  if (options.token) headers.set("Authorization", `Bearer ${options.token}`);
  if (options.organizationId) headers.set("X-Organization-ID", options.organizationId);
  if (options.siteId) headers.set("X-Site-ID", options.siteId);
  const response = await fetch(`${API_URL}${path}`, { ...options, headers, credentials: "include" });
  if (!response.ok) throw new Error((await response.text()) || `API request failed: ${response.status}`);
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
export const endpoints = {
  me: "/auth/me/", organizations: "/platform/organizations/", sites: "/platform/sites/",
  studies: "/stability/studies/", protocols: "/stability/protocols/", protocolVersions: "/stability/protocol-versions/",
  specifications: "/stability/specifications/", specificationVersions: "/stability/specification-versions/", batches: "/batches/",
  samples: "/stability/samples/", timepoints: "/stability/timepoints/", results: "/results/", chambers: "/chamber/", audit: "/audit/",
  billing: "/billing/subscription/", plans: "/billing/plans/", usage: "/billing/usage/", oos: "/quality/oos/", oot: "/quality/oot/",
  deviations: "/quality/deviations/", capa: "/quality/capa/", changeControl: "/quality/change-control/", signatures: "/compliance/signatures/",
  controlledRecords: "/compliance/records/", validation: "/compliance/validation/",
};
