"use client";
import Link from "next/link";
import {usePathname} from "next/navigation";
import {Activity,BarChart3,Bell,Building2,ClipboardCheck,Database,FileCheck2,FlaskConical,LayoutDashboard,LogOut,Menu,Package,Search,Settings2,ShieldCheck,Users,WalletCards} from "lucide-react";
import type {LucideIcon} from "lucide-react";
import {useState} from "react";
import {useAuth} from "./AuthProvider";

type NavItem={label:string;href:string;icon:LucideIcon};
type NavGroup={title:string;items:NavItem[]};
const groups:NavGroup[]=[
 {title:"Workspace",items:[{label:"Overview",href:"/app",icon:LayoutDashboard},{label:"Stability Studies",href:"/app/studies",icon:FlaskConical},{label:"Samples & Timepoints",href:"/app/samples",icon:Package},{label:"Results & Review",href:"/app/results",icon:FileCheck2},{label:"Chambers",href:"/app/chambers",icon:Activity}]},
 {title:"Quality",items:[{label:"OOS / OOT",href:"/app/quality",icon:ShieldCheck},{label:"Deviations",href:"/app/deviations",icon:ClipboardCheck},{label:"CAPA",href:"/app/capa",icon:ShieldCheck},{label:"Audit & Compliance",href:"/app/audit",icon:ShieldCheck}]},
 {title:"Master Data",items:[{label:"Products & Batches",href:"/app/master-data",icon:Database},{label:"Protocols",href:"/app/protocols",icon:ClipboardCheck},{label:"Specifications",href:"/app/specifications",icon:FileCheck2},{label:"Reports & Analytics",href:"/app/analytics",icon:BarChart3}]}
];

export default function AppShell({children}:{children:React.ReactNode}){
 const pathname=usePathname(),[open,setOpen]=useState(false);const {user,organizations,sites,organization,site,selectOrganization,selectSite,logout,loading}=useAuth();
 if(pathname==="/"||pathname==="/login")return <>{children}</>;if(loading)return <div className="loading-screen"><div className="spinner"/><span>Loading secure workspace…</span></div>;if(!user)return <>{children}</>;
 return <div className="app-shell">{open&&<button className="mobile-scrim" onClick={()=>setOpen(false)} aria-label="Close navigation"/>}<aside className={"sidebar "+(open?"open":"")}>
 <div className="brand"><div className="brand-mark">Q</div><div><strong>QCSTS</strong><small>Quality & Stability</small></div></div>
 <div className="tenant-switcher"><Building2 size={16}/><div className="tenant-selects"><select value={organization?.id||""} onChange={e=>void selectOrganization(e.target.value)} aria-label="Organization">{organizations.map(o=><option key={o.id} value={o.id}>{o.name}</option>)}</select><select value={site?.id||""} onChange={e=>selectSite(e.target.value||null)} aria-label="Site"><option value="">All sites</option>{sites.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></div></div>
 <nav>{groups.map(group=><div className="nav-group" key={group.title}><div className="nav-label">{group.title}</div>{group.items.map(item=>{const Icon=item.icon;const active=pathname===item.href||(item.href!=="/app"&&pathname.startsWith(item.href));return <Link onClick={()=>setOpen(false)} className={"nav-item "+(active?"active":"")} href={item.href} key={item.label}><Icon size={16}/><span>{item.label}</span></Link>})}</div>)}
 <div className="nav-group"><div className="nav-label">Administration</div><Link className={"nav-item "+(pathname.startsWith("/app/organization")?"active":"")} href="/app/organization"><Building2 size={16}/><span>Organization</span></Link><Link className={"nav-item "+(pathname.startsWith("/app/users")?"active":"")} href="/app/users"><Users size={16}/><span>Users & Roles</span></Link><Link className={"nav-item "+(pathname.startsWith("/app/billing")?"active":"")} href="/app/billing"><WalletCards size={16}/><span>Billing</span></Link><Link className={"nav-item "+(pathname.startsWith("/app/settings")?"active":"")} href="/app/settings"><Settings2 size={16}/><span>Settings</span></Link></div></nav>
 <div className="sidebar-footer"><span>Signed in as</span><strong>{user.full_name}</strong><small>{user.organization_role||user.role||"Member"}</small></div></aside>
 <main className="main-shell"><header className="topbar"><button className="mobile-menu" onClick={()=>setOpen(true)} aria-label="Open navigation"><Menu size={19}/></button><div className="global-search"><Search size={16}/><input placeholder="Search studies, batches, products, samples…" aria-label="Global search"/><kbd>Ctrl K</kbd></div><div className="top-actions"><button className="icon-button" aria-label="Notifications"><Bell size={17}/></button><div className="profile"><div className="avatar">{user.full_name.split(" ").map(x=>x[0]).slice(0,2).join("").toUpperCase()}</div><div><strong>{user.full_name}</strong><span>{user.organization_role||"Member"}</span></div></div><button className="icon-button" onClick={()=>void logout()} aria-label="Log out"><LogOut size={17}/></button></div></header>{children}</main></div>
}
