"use client";

import { useAuth } from "@/components/AuthProvider";
import { api, endpoints } from "@/lib/api";
import { useState } from "react";
import { ErrorBanner } from "@/components/ui/ErrorBanner";

export default function Organization() {
  const { organization, sites, membership } = useAuth();
  const [form,setForm]=useState({name:"",address:"",country:organization?.country||"EG",timezone:organization?.timezone||"Africa/Cairo"});
  const [open,setOpen]=useState(false);
  const [error,setError]=useState("");
  const [message,setMessage]=useState("");

  async function createSite(e:React.FormEvent){
    e.preventDefault();setError("");setMessage("");
    try{
      await api(endpoints.sites,{method:"POST",body:JSON.stringify(form)});
      setForm({name:"",address:"",country:organization?.country||"EG",timezone:organization?.timezone||"Africa/Cairo"});
      setOpen(false);setMessage("Site created. Refresh the workspace to load the updated tenant context.");
    }catch(x){setError(x instanceof Error?x.message:"Unable to create site.")}
  }

  return <div className="content">
    <div className="page-header"><div><span className="eyebrow">TENANT</span><h1>{organization?.name||"Organization"}</h1><p>Organization and site context is verified by the backend before protected requests are authorized.</p></div>{["admin","qa_manager"].includes(String(membership?.role||"").toLowerCase())&&<button className="btn primary" onClick={()=>setOpen(true)}>Add site</button>}</div>
    {error&&<ErrorBanner message={error}/>} {message&&<div className="form-success">{message}</div>}
    {open&&<section className="card form-card" style={{maxWidth:760,marginBottom:14}}><h3>Create site</h3><form onSubmit={createSite}><div className="form-grid"><label className="field"><span>Name</span><input required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label><label className="field"><span>Country</span><input required maxLength={2} value={form.country} onChange={e=>setForm({...form,country:e.target.value.toUpperCase()})}/></label><label className="field"><span>Timezone</span><input required value={form.timezone} onChange={e=>setForm({...form,timezone:e.target.value})}/></label></div><label className="field"><span>Address</span><textarea value={form.address} onChange={e=>setForm({...form,address:e.target.value})}/></label><div className="modal-actions"><button className="btn" type="button" onClick={()=>setOpen(false)}>Cancel</button><button className="btn primary">Create site</button></div></form></section>}
    <div className="grid-2">
      <section className="card detail-card"><h3>Organization</h3><dl><dt>Legal name</dt><dd>{organization?.legal_name||"—"}</dd><dt>Country</dt><dd>{organization?.country||"—"}</dd><dt>Timezone</dt><dd>{organization?.timezone||"—"}</dd><dt>Currency</dt><dd>{organization?.currency||"—"}</dd><dt>Status</dt><dd><span className={"status "+(organization?.status==="active"?"active":"critical")}>{organization?.status||"Unknown"}</span></dd></dl></section>
      <section className="card detail-card"><h3>Sites</h3>{sites.map(s=><div className="site-row" key={s.id}><div><b>{s.name}</b><span>{s.address||s.country||"No address"}</span></div><span className="status active">{s.status||"active"}</span></div>)}{!sites.length&&<div className="empty"><b>No sites</b><span>Customer onboarding should create a primary site automatically.</span></div>}</section>
    </div>
  </div>;
}
