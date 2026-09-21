"use client";

import { useEffect, useState } from "react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import type { User } from "@/lib/auth";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { useAuth } from "@/components/AuthProvider";

export default function Users() {
  const [users,setUsers]=useState<User[]>([]);
  const [error,setError]=useState("");
  const [loading,setLoading]=useState(true);
  const [open,setOpen]=useState(false);
  const [editing,setEditing]=useState<User|null>(null);
  const { sites } = useAuth();
  const [form,setForm]=useState({email:"",full_name:"",role:"analyst",password:"",site_id:""});

  const load=async()=>{setLoading(true);setError("");try{const r=await api<ApiEnvelope<User[]>>(endpoints.users);setUsers(r.data||[])}catch(e){setError(e instanceof Error?e.message:"Unable to load members.")}finally{setLoading(false)}};
  useEffect(()=>{void load()},[]);

  const create=async(e:React.FormEvent)=>{e.preventDefault();setError("");try{await api(endpoints.users,{method:"POST",body:JSON.stringify(form)});setForm({email:"",full_name:"",role:"analyst",password:"",site_id:""});setOpen(false);await load()}catch(x){setError(x instanceof Error?x.message:"Unable to create member.")}};
  const edit=async(e:React.FormEvent)=>{e.preventDefault();if(!editing)return;setError("");try{await api(endpoints.user(editing.id),{method:"PATCH",body:JSON.stringify({full_name:form.full_name,site_id:form.site_id||undefined})});setEditing(null);setForm({email:"",full_name:"",role:"analyst",password:"",site_id:""});await load()}catch(x){setError(x instanceof Error?x.message:"Unable to update member.")}};
  const revoke=async(user:User)=>{if(!window.confirm("Revoke this member's organization access?"))return;setError("");try{await api(endpoints.user(user.id),{method:"DELETE"});await load()}catch(x){setError(x instanceof Error?x.message:"Unable to revoke access.")}};

  return <div className="content">
    <div className="page-header"><div><span className="eyebrow">ADMINISTRATION</span><h1>Users & memberships</h1><p>Members are scoped to the active organization. The backend decides permissions and membership state.</p></div><button className="btn primary" onClick={()=>setOpen(v=>!v)}>{open?"Close":"Add member"}</button></div>
    {error&&<ErrorBanner message={error} onRetry={load}/>}
    {open&&<section className="card form-card member-form"><h3>Create organization member</h3><form onSubmit={create}><div className="form-grid"><label className="field"><span>Full name</span><input required value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})}/></label><label className="field"><span>Email</span><input required type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label><label className="field"><span>Role</span><select value={form.role} onChange={e=>setForm({...form,role:e.target.value})}><option value="analyst">Analyst</option><option value="supervisor">Supervisor</option><option value="qa_manager">QA Manager</option><option value="admin">Admin</option></select></label><label className="field"><span>Temporary password</span><input required minLength={12} type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></label></div><button className="btn primary">Create member</button></form></section>}
    {editing&&<section className="card form-card member-form"><h3>Edit member</h3><form onSubmit={edit}><label className="field"><span>Full name</span><input required value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})}/></label><label className="field"><span>Assigned site</span><select required value={form.site_id} onChange={e=>setForm({...form,site_id:e.target.value})}><option value="">Select site…</option>{sites.map(s=><option value={s.id} key={s.id}>{s.name}</option>)}</select></label><div className="modal-actions"><button className="btn" type="button" onClick={()=>setEditing(null)}>Cancel</button><button className="btn primary">Save changes</button></div></form></section>}
    <section className="card table-card"><div className="card-header"><div><strong>{users.length} members</strong><span>{loading?"Loading authorized members…":"Live organization membership data"}</span></div><button className="btn" onClick={()=>void load()}>Refresh</button></div><div className="table-wrap"><table><thead><tr><th>Name</th><th>Email</th><th>Organization role</th><th>Assigned site</th><th>Status</th><th>Created</th><th>Actions</th></tr></thead><tbody>{users.map(u=><tr key={u.id}><td><b>{u.full_name}</b></td><td>{u.email}</td><td>{u.organization_role||"—"}</td><td>{u.organization_site?.name||"—"}</td><td><span className={"status "+(u.is_active?"active":"critical")}>{u.is_active?"Active":"Inactive"}</span></td><td>{new Date(u.created_at).toLocaleDateString()}</td><td><div className="action-row"><button className="btn" onClick={()=>{setEditing(u);setOpen(false);setForm({email:u.email,full_name:u.full_name,role:u.organization_role||"analyst",password:"",site_id:u.organization_site?.id||""})}}>Edit</button>{u.is_active&&<button className="btn reject" onClick={()=>void revoke(u)}>Revoke</button>}</div></td></tr>)}</tbody></table>{loading&&<div className="empty">Loading members…</div>}{!loading&&!users.length&&!error&&<div className="empty"><b>No members</b><span>No organization members were returned.</span></div>}</div></section>
  </div>;
}
