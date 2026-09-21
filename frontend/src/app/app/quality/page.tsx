"use client";
import Link from "next/link";
import { FileWarning, GitBranch, ShieldAlert, Target, Workflow } from "lucide-react";

const areas = [
  ["OOS investigations", "/app/quality/oos", "Out-of-specification investigation records.", FileWarning],
  ["OOT investigations", "/app/quality/oot", "Out-of-trend investigation records.", Target],
  ["Deviations", "/app/quality/deviations", "Controlled deviation records.", ShieldAlert],
  ["CAPA", "/app/quality/capa", "Corrective and preventive actions.", Workflow],
  ["Change control", "/app/quality/change-control", "Controlled change requests.", GitBranch],
] as const;

export default function Quality(){return <div className="content"><div className="page-header"><div><span className="eyebrow">QUALITY SYSTEM</span><h1>Quality management</h1><p>Quality investigations are live, tenant-scoped records. State transitions remain backend-controlled.</p></div></div><div className="feature-grid">{areas.map(([title,href,copy,Icon])=><Link href={href} className="feature-card" key={href}><Icon size={20}/><h3>{title}</h3><p>{copy}</p><span className="btn">Open workspace →</span></Link>)}</div></div>}