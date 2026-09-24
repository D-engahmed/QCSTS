export type AppRole =
  | "admin"
  | "qa_manager"
  | "supervisor"
  | "analyst"
  | "viewer"
  | "system";

export const ROLE_LABELS: Record<AppRole, string> = {
  admin: "Admin",
  qa_manager: "QA Manager",
  supervisor: "Supervisor",
  analyst: "Analyst",
  viewer: "Viewer",
  system: "System",
};

const ROLE_SECTIONS: Record<AppRole, Set<string>> = {
  admin: new Set([
    "workspace",
    "master-data",
    "stability-setup",
    "execution",
    "quality",
    "audit",
    "reports",
    "compliance",
    "administration",
  ]),
  qa_manager: new Set([
    "workspace",
    "master-data",
    "quality",
    "audit",
    "reports",
    "compliance",
    "personal-settings",
  ]),
  supervisor: new Set([
    "workspace",
    "stability-setup",
    "execution",
    "personal-settings",
  ]),
  analyst: new Set([
    "workspace",
    "execution",
    "personal-settings",
  ]),
  viewer: new Set([
    "workspace",
    "master-data",
    "stability-setup",
    "execution",
    "quality",
    "audit",
    "reports",
    "compliance",
    "personal-settings",
  ]),
  system: new Set([]),
};

const ROUTE_SECTION: Array<[string, string]> = [
  ["/app/organization", "administration"],
  ["/app/users", "administration"],
  ["/app/billing", "administration"],
  ["/app/settings", "personal-settings"],

  ["/app/compliance", "compliance"],
  ["/app/audit", "audit"],
  ["/app/reports", "reports"],
  ["/app/quality", "quality"],

  ["/app/products", "master-data"],
  ["/app/monographs", "master-data"],

  ["/app/storage-conditions", "stability-setup"],
  ["/app/protocols", "stability-setup"],
  ["/app/protocol-versions", "stability-setup"],
  ["/app/specifications", "stability-setup"],
  ["/app/specification-versions", "stability-setup"],

  ["/app/batches", "execution"],
  ["/app/studies", "execution"],
  ["/app/study-batches", "execution"],
  ["/app/timepoints", "execution"],
  ["/app/samples", "execution"],
  ["/app/sample-pulls", "execution"],
  ["/app/chambers", "execution"],
  ["/app/results", "workspace"],
  ["/app/test-points", "workspace"],
  ["/app/search", "workspace"],
  ["/app/notifications", "workspace"],
];

export function normalizeRole(value?: string | null): AppRole {
  const role = String(value ?? "").trim().toLowerCase();
  return role in ROLE_LABELS ? (role as AppRole) : "system";
}

export function roleCanSeeSection(roleValue: string | null | undefined, section: string) {
  const role = normalizeRole(roleValue);
  return ROLE_SECTIONS[role].has(section);
}

export function roleCanAccessPath(roleValue: string | null | undefined, pathname: string) {
  const role = normalizeRole(roleValue);

  if (!pathname.startsWith("/app")) return true;
  if (role === "admin") return true;

  const matched = ROUTE_SECTION.find(([prefix]) =>
    pathname === prefix || pathname.startsWith(prefix + "/"),
  );

  if (!matched) return roleCanSeeSection(role, "workspace");

  return roleCanSeeSection(role, matched[1]);
}
