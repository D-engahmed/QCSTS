"use client";
import {useEffect,useState} from "react";
import {api,endpoints,type ApiEnvelope} from "@/lib/api";
import type {User} from "@/lib/auth";
import {useAuth} from "@/components/AuthProvider";

export default function Users(){
 const {sites}=useAuth();
 const [users,setUsers]=useState<User[]>([]),[error,setError]=useState(""),[loading,setLoading]=useState(true),[open,setOpen]=useState(false);
 const [form,setForm]=useState({email:"",full_name:"",role:"analyst",site_id:"",password:""});
 const load=()=>{setLoading(true);api<ApiEnvelope<User[]>>(endpoints.users).then(r=>setUsers(r.data||[])).catch(e=>setError(e.message)).finally(()=>setLoading(false))};
 useEffect(()=>{load();},[]);
 useEffect(()=>{if(!form.site_id&&sites[0])setForm(f=>({...f,site_id:sites[0].id}))},[sites,form.site_id]);
 async function create(e:React.FormEvent){
  e.preventDefault();setError("");
  try{
   await api(endpoints.users,{method:"POST",body:JSON.stringify(form)});
   setForm({email:"",full_name:"",role:"analyst",site_id:sites[0]?.id||"",password:""});setOpen(false);load()
  }catch(x){setError(x instanceof Error?x.message:"Unable to create member.")}
 }
 return <div className="content">
  <div className="page-header"><div><span className="eyebrow">ADMINISTRATION</span><h1>Users & memberships</h1><p>Every customer account has one organization, one site and one role. Workspace context is fixed by the backend.</p></div><button className="btn primary" onClick={()=>setOpen(!open)}>Add member</button></div>
  {error&&<div className="inline-error">{error}</div>}
  {open&&<section className="card form-card member-form"><h3>Create organization member</h3><form onSubmit={create}>
   <label className="field"><span>Full name</span><input required value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})}/></label>
   <label className="field"><span>Email</span><input required type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label>
   <label className="field"><span>Site</span><select required value={form.site_id} onChange={e=>setForm({...form,site_id:e.target.value})}>{sites.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></label>
   <label className="field"><span>Role</span><select value={form.role} onChange={e=>setForm({...form,role:e.target.value})}><option value="analyst">Analyst</option><option value="supervisor">Supervisor</option><option value="qa_manager">QA Manager</option><option value="admin">Organization Admin</option></select></label>
   <label className="field"><span>Temporary password</span><input required minLength={12} type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/><small>Minimum 12 characters. Share it through your approved onboarding process.</small></label>
   <button className="btn primary">Create member</button>
  </form></section>}
  <section className="card table-card"><div className="card-header"><div><strong>Organization members</strong><span>{users.length} members returned by the API</span></div><button className="btn" onClick={load}>Refresh</button></div>
   <div className="table-wrap"><table><thead><tr><th>Name</th><th>Email</th><th>Site</th><th>Role</th><th>Status</th><th>Created</th></tr></thead><tbody>{users.map(u=><tr key={u.id}><td><b>{u.full_name}</b></td><td>{u.email}</td><td>{u.site?.name||"—"}</td><td>{u.role||"—"}</td><td><span className={"status "+(u.is_active?"active":"critical")}>{u.is_active?"Active":"Inactive"}</span></td><td>{new Date(u.created_at).toLocaleDateString()}</td></tr>)}</tbody></table>{loading&&<div className="empty">Loading members…</div>}{!loading&&!users.length&&!error&&<div className="empty">No members were returned for this organization.</div>}</div>
  </section>
 </div>
}
