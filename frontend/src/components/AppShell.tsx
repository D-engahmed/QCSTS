"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bell, Building2, ClipboardList, FileCheck2, FlaskConical, LayoutDashboard,
  LogOut, Menu, Package, ReceiptText, Search, Settings2, ShieldCheck, Users, WalletCards
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "./AuthProvider";

const workspace = [
  ["Overview", "/app", LayoutDashboard],
  ["Products", "/app/products", Package],
  ["Monographs", "/app/monographs", FileCheck2],
  ["Batches", "/app/batches", FlaskConical],
  ["Test points", "/app/schedule", ClipboardList],
  ["Chambers", "/app/chambers", Building2],
  ["Results", "/app/results", FileCheck2],
  ["Quality", "/app/quality", ShieldCheck],
  ["Audit", "/app/audit", ReceiptText],
];

const admin = [
  ["Users / Members", "/app/users", Users, "users"],
  ["Billing", "/app/billing", WalletCards, "billing"],
  ["Settings", "/app/settings", Settings2, "settings"],
];

function canAccess(user: any, capability?: string) {
  if (!capability) return true;
  const role = String(user?.role || user?.organization_role || "").toLowerCase();
  if (capability === "users") return ["admin", "organization_admin"].includes(role);
  if (capability === "billing") return ["admin", "organization_admin", "billing_admin"].includes(role);
  return true;
}

function isActive(pathname: string, href: string) {
  if (href === "/app") return pathname === href;
  return pathname === href || pathname.startsWith(href + "/");
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const { user, organization, site, logout, loading } = useAuth();

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

  const showAdmin = admin.some(([, , , capability]) => canAccess(user, capability));

  return (
    <div className="app-shell">
      {open && (
        <button className="mobile-scrim" onClick={() => setOpen(false)} aria-label="Close navigation" />
      )}

      <aside className={"sidebar " + (open ? "open" : "")}>
        <div className="brand">
          <div className="brand-mark">Q</div>
          <div><strong>QCSTS</strong><small>Quality & Stability</small></div>
        </div>

        <div className="tenant-switcher" aria-label="Assigned workspace">
          <Building2 size={16} />
          <div className="tenant-selects">
            <strong>{organization?.name || "Organization"}</strong>
            <span>{site?.name || "Assigned site"} · {user.role || "Member"}</span>
          </div>
        </div>

        <nav>
          <div className="nav-group">
            <div className="nav-label">Workspace</div>
            {workspace.map(([label, href, Icon]: any) => (
              <Link
                key={href}
                href={href}
                onClick={() => setOpen(false)}
                className={"nav-item " + (isActive(pathname, href) ? "active" : "")}
              >
                <Icon size={16} />
                <span>{label}</span>
              </Link>
            ))}
          </div>

          {showAdmin && (
            <div className="nav-group">
              <div className="nav-label">Administration</div>
              {admin.filter(([, , , capability]) => canAccess(user, capability)).map(([label, href, Icon]: any) => (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setOpen(false)}
                  className={"nav-item " + (isActive(pathname, href) ? "active" : "")}
                >
                  <Icon size={16} />
                  <span>{label}</span>
                </Link>
              ))}
            </div>
          )}
        </nav>

        <div className="sidebar-footer">
          <span>Signed in as</span>
          <strong>{user.full_name}</strong>
          <small>{user.role || "Member"}</small>
        </div>
      </aside>

      <main className="main-shell">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setOpen(true)} aria-label="Open navigation">
            <Menu size={19} />
          </button>

          <div className="global-search">
            <Search size={16} />
            <input placeholder="Search results, batches, products…" aria-label="Global search" />
            <kbd>Ctrl K</kbd>
          </div>

          <div className="top-actions">
            <button className="icon-button" aria-label="Notifications"><Bell size={17} /></button>
            <div className="profile">
              <div className="avatar">
                {user.full_name.split(" ").map((part) => part[0]).slice(0, 2).join("").toUpperCase()}
              </div>
              <div><strong>{user.full_name}</strong><span>{user.role || "Member"}</span></div>
            </div>
            <button className="icon-button" onClick={() => void logout()} aria-label="Log out">
              <LogOut size={17} />
            </button>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}
