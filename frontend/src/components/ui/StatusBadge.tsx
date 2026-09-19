"use client";
const icons={Draft:"○",Submitted:"↑","Under Review":"◌",Rejected:"×","Correction Required":"!",Approved:"✓",Locked:"▣"} as Record<string,string>;
export function StatusBadge({status}:{status?:string|null}){const label=status||"Unknown";return <span className={"status-badge status-"+label.toLowerCase().replaceAll(" ","-")}><span aria-hidden>{icons[label]||"•"}</span>{label}</span>}
