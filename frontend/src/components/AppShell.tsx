"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Beaker,
  BookOpen,
  Boxes,
  Building2,
  CalendarClock,
  ClipboardCheck,
  FileCheck2,
  FileCog,
  FlaskConical,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Menu,
  PackageCheck,
  ReceiptText,
  Settings,
  ShieldCheck,
  Thermometer,
  Users,
  WalletCards,
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "./AuthProvider";

type NavItem = [string, string, any];

const groups: Array<[string, NavItem[]]> = [
  ["Workspace", [
    ["Overview", "/app", LayoutDashboard],
    ["Results", "/app/results", FileCheck2],
    ["Test points", "/app/test-points", ListChecks],
  ]],
  ["Master data", [
    ["Products", "/app/products", PackageCheck],
    ["Monographs", "/app/monographs", BookOpen],
  ]],
  ["Stability setup", [
    ["Storage conditions", "/app/storage-conditions", Thermometer],
    ["Protocols", "/app/protocols", FileCog],
    ["Protocol versions", "/app/protocol-versions", ClipboardCheck],
    ["Specifications", "/app/specifications", FileCog],
    ["Specification versions", "/app/specification-versions", ClipboardCheck],
  ]],
  ["Execution", [
    ["Batches", "/app/batches", Boxes],
    ["Studies", "/app/studies", FlaskConical],
    ["Study batches", "/app/study-batches", Beaker],
    ["Timepoints", "/app/timepoints", CalendarClock],
    ["Samples", "/app/samples", Activity],
    ["Sample pulls", "/app/sample-pulls", Beaker],
    ["Chambers", "/app/chambers", Thermometer],
  ]],
  ["Quality & evidence", [
    ["Quality", "/app/quality", ShieldCheck],
    ["Audit trail", "/app/audit", ReceiptText],
    ["Compliance", "/app/compliance", ClipboardCheck],
  ]],
  ["Administration", [
    ["Organization", "/app/organization", Building2],
    ["Users / Members", "/app/users", Users],
    ["Billing", "/app/billing", WalletCards],
    ["Security settings", "/app/settings", Settings],
  ]],
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const { user, membership, organization, site, logout, loading } = useAuth();

  if (pathname === "/" || pathname === "/login" || pathname === "/register") return <>{children}</>;
  if (loading) return <div className="loading-screen"><div className="spinner" /><span>Loading secure workspace…</span></div>;
  if (!user) return <>{children}</>;

  const role = String(membership?.role || user.organization_role || user.role || "viewer").toLowerCase();
  const canManageUsers = ["admin", "qa_manager"].includes(role);

  return (
    <div className="app-shell">
      {open && <button className="mobile-scrim" onClick={() => setOpen(false)} aria-label="Close navigation" />}
      <aside className={"sidebar " + (open ? "open" : "")}>
        <div className="brand"><div className="brand-mark">Q</div><div><strong>QCSTS</strong><small>Quality & Stability</small></div></div>
        <Link className="tenant-switcher" href="/app/organization" onClick={() => setOpen(false)} aria-label="Assigned workspace">
          <Building2 size={16} />
          <div className="tenant-selects">
            <strong>{organization?.name || "Organization"}</strong>
            <span>{site?.name || "Assigned site"} · {membership?.role || user.organization_role || "Member"}</span>
          </div>
        </Link>

        <nav>
          {groups.map(([group, items]) => {
            const visible = items.filter(([label]) => label !== "Users / Members" || canManageUsers);
            return <div className="nav-group" key={group}>
              <div className="nav-label">{group}</div>
              {visible.map(([label, href, Icon]) => (
                <Link
                  onClick={() => setOpen(false)}
                  className={"nav-item " + (pathname === href || (href !== "/app" && pathname.startsWith(href + "/")) ? "active" : "")}
                  href={href}
                  key={href}
                >
                  <Icon size={16} /><span>{label}</span>
                </Link>
              ))}
            </div>;
          })}
        </nav>

        <div className="sidebar-footer">
          <span>Signed in as</span>
          <strong>{user.full_name}</strong>
          <small>{membership?.role || user.organization_role || "Member"}</small>
        </div>
      </aside>

      <main className="main-shell">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setOpen(true)} aria-label="Open navigation"><Menu size={19} /></button>
          <form className="global-search" onSubmit={(event) => { event.preventDefault(); const input = event.currentTarget.elements.namedItem("q") as HTMLInputElement | null; const q = input?.value.trim() || ""; if (q) window.location.assign("/app/search?q=" + encodeURIComponent(q)); }}>
            <Activity size={16} />
            <input name="q" placeholder="Search results, batches, studies…" aria-label="Global search" />
            <kbd>Enter</kbd>
          </form>
          <div className="top-actions">
            <Link className="icon-button" href="/app/compliance" aria-label="Open compliance"><ShieldCheck size={17} /></Link>
            <Link className="profile" href="/app/settings" aria-label="Open security settings">
              <div className="avatar">{user.full_name.split(" ").map((x) => x[0]).slice(0, 2).join("").toUpperCase()}</div>
              <div><strong>{user.full_name}</strong><span>{membership?.role || user.organization_role || "Member"}</span></div>
            </Link>
            <button className="icon-button" onClick={() => void logout()} aria-label="Log out"><LogOut size={17} /></button>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}
