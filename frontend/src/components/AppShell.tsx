"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Activity,Bell,Beaker,BookOpen,Boxes,Building2,CalendarClock,ClipboardCheck,FileCheck2,FileCog,FlaskConical,LayoutDashboard,ListChecks,LogOut,Menu,PackageCheck,ReceiptText,Settings,ShieldCheck,Thermometer,Users,WalletCards } from "lucide-react";
import { useState } from "react";
import { useAuth } from "./AuthProvider";
import ThemeToggle from "./ThemeToggle";
import { normalizeRole, roleCanAccessPath, roleCanSeeSection, ROLE_LABELS } from "@/lib/rbac";

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
    ["Security settings", "/app/settings", Settings, "personal-settings"],
  ]],
];
