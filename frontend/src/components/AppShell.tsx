"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Activity, Bell, Beaker, BookOpen, Boxes, Building2, CalendarClock,
  ClipboardCheck, FileCheck2, FileCog, FlaskConical, LayoutDashboard,
  ListChecks, LogOut, Menu, PackageCheck, ReceiptText, Settings,
  ShieldCheck, Thermometer, Users, WalletCards,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "./AuthProvider";
import ThemeToggle from "./ThemeToggle";
import {
  normalizeRole,
  roleCanAccessPath,
  roleCanSeeSection,
  ROLE_LABELS,
} from "@/lib/rbac";

type NavItem = [string, string, any, string];

const groups: Array<[string, NavItem[]]> = [
  ["Workspace", [
    ["Overview", "/app", LayoutDashboard, "workspace"],
    ["Results", "/app/results", FileCheck2, "workspace"],
    ["Test points", "/app/test-points", ListChecks, "workspace"],
  ]],
  ["Master data", [
    ["Products", "/app/products", PackageCheck, "master-data"],
    ["Monographs", "/app/monographs", BookOpen, "master-data"],
  ]],
  ["Stability setup", [
    ["Storage conditions", "/app/storage-conditions", Thermometer, "stability-setup"],
    ["Protocols", "/app/protocols", FileCog, "stability-setup"],
    ["Protocol versions", "/app/protocol-versions", ClipboardCheck, "stability-setup"],
    ["Specifications", "/app/specifications", FileCog, "stability-setup"],
    ["Specification versions", "/app/specification-versions", ClipboardCheck, "stability-setup"],
  ]],
  ["Execution", [
    ["Batches", "/app/batches", Boxes, "execution"],
    ["Studies", "/app/studies", FlaskConical, "execution"],
    ["Study batches", "/app/study-batches", Beaker, "execution"],
    ["Timepoints", "/app/timepoints", CalendarClock, "execution"],
    ["Samples", "/app/samples", Activity, "execution"],
    ["Sample pulls", "/app/sample-pulls", Beaker, "execution"],
    ["Chambers", "/app/chambers", Thermometer, "execution"],
  ]],
  ["Quality & evidence", [
    ["Quality", "/app/quality", ShieldCheck, "quality"],
    ["Audit trail", "/app/audit", ReceiptText, "audit"],
    ["Reports & exports", "/app/reports", ReceiptText, "reports"],
    ["Compliance", "/app/compliance", ClipboardCheck, "compliance"],
  ]],
  ["Administration", [
    ["Organization", "/app/organization", Building2, "administration"],
    ["Users / Members", "/app/users", Users, "administration"],
    ["Billing", "/app/billing", WalletCards, "administration"],
  ]],
  ["Account", [
    ["Security settings", "/app/settings", Settings, "personal-settings"],
  ]],
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const { user, membership, organization, site, logout, loading } = useAuth();

  const role = normalizeRole(user?.organization_role || membership?.role);
  const authorizedRoute =
    !pathname.startsWith("/app") || roleCanAccessPath(role, pathname);
  const roleLabel = ROLE_LABELS[role];

  useEffect(() => {
    if (!loading && user && !authorizedRoute) {
      router.replace("/app");
    }
  }, [authorizedRoute, loading, router, user]);

  if (pathname === "/" || pathname === "/login" || pathname === "/register") {
    return <>{children}</>;
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        <span>Loading secure workspace…</span>
      </div>
    );
  }

  if (!user) return <>{children}</>;

  if (!authorizedRoute) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        <span>Returning to your authorized workspace…</span>
      </div>
    );
  }

  const visibleGroups = groups
    .map(([group, items]) => [
      group,
      items.filter(([, , , section]) => roleCanSeeSection(role, section)),
    ] as [string, NavItem[]])
    .filter(([, items]) => items.length > 0);

  return (
    <div className="app-shell">
      {open && (
        <button
          className="mobile-scrim"
          onClick={() => setOpen(false)}
          aria-label="Close navigation"
        />
      )}

      <aside className={"sidebar " + (open ? "open" : "")}>
        <div className="brand">
          <div className="brand-mark">Q</div>
          <div>
            <strong>QCSTS</strong>
            <small>Quality & Stability</small>
          </div>
        </div>

        <Link
          className="tenant-switcher"
          href={roleCanSeeSection(role, "administration") ? "/app/organization" : "/app"}
          onClick={() => setOpen(false)}
          aria-label="Assigned workspace"
        >
          <Building2 size={16} />
          <div className="tenant-selects">
            <strong>{organization?.name || "Organization"}</strong>
            <span>{site?.name || "Assigned site"} · {roleLabel}</span>
          </div>
        </Link>

        <nav>
          {visibleGroups.map(([group, items]) => (
            <div className="nav-group" key={group}>
              <div className="nav-label">{group}</div>
              {items.map(([label, href, Icon]) => (
                <Link
                  onClick={() => setOpen(false)}
                  className={
                    "nav-item " +
                    (pathname === href ||
                    (href !== "/app" && pathname.startsWith(href + "/"))
                      ? "active"
                      : "")
                  }
                  href={href}
                  key={href}
                >
                  <Icon size={16} />
                  <span>{label}</span>
                </Link>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span>Signed in as</span>
          <strong>{user.full_name}</strong>
          <small>{roleLabel}</small>
        </div>
      </aside>

      <main className="main-shell">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setOpen(true)}
            aria-label="Open navigation"
          >
            <Menu size={19} />
          </button>

          <form
            className="global-search"
            onSubmit={(event) => {
              event.preventDefault();
              const input = event.currentTarget.elements.namedItem("q") as HTMLInputElement | null;
              const q = input?.value.trim() || "";
              if (q) window.location.assign("/app/search?q=" + encodeURIComponent(q));
            }}
          >
            <Activity size={16} />
            <input name="q" placeholder="Search results, batches, studies…" aria-label="Global search" />
            <kbd>Enter</kbd>
          </form>

          <div className="top-actions">
            <ThemeToggle />

            <Link
              className="icon-button"
              href="/app/notifications"
              aria-label="Open notifications"
            >
              <Bell size={17} />
            </Link>

            {roleCanSeeSection(role, "compliance") && (
              <Link
                className="icon-button"
                href="/app/compliance"
                aria-label="Open compliance"
              >
                <ShieldCheck size={17} />
              </Link>
            )}

            <Link className="profile" href="/app/settings" aria-label="Open security settings">
              <div className="avatar">
                {user.full_name
                  .split(" ")
                  .map((x) => x[0])
                  .slice(0, 2)
                  .join("")
                  .toUpperCase()}
              </div>
              <div>
                <strong>{user.full_name}</strong>
                <span>{roleLabel}</span>
              </div>
            </Link>

            <button
              className="icon-button"
              onClick={() => void logout()}
              aria-label="Log out"
            >
              <LogOut size={17} />
            </button>
          </div>
        </header>

        {children}
      </main>
    </div>
  );
}
