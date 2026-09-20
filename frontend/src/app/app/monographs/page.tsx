"use client";

import { useEffect, useState } from "react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import { authStorage } from "@/lib/auth";

type Test = {id:string;name:string;method:string;specification:string;unit:string;sequence:number};
type Monograph = {id:string;name:string;version:string;effective_date:string;status:string;approved_by_name?:string|null;approved_at?:string|null;tests?:Test[]};

export default function MonographsPage(){
  const [rows,setRows]=useState<Monograph[]>([]);
  const [selected,setSelected]=useState<Monograph|null>(null);
  const [tests,setTests]=useState<Test[]>([]);
  const [createOpen,setCreateOpen]=useState(false);
  const [testOpen,setTestOpen]=useState(false);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const [form,setForm]=useState({name:"",version:"",effective_date:""});
  const [testForm,setTestForm]=useState({name:"",method:"",specification:"",unit:""});

  const role=String(authStorage.user?.role||authStorage.user?.organization_role||"").toLowerCase();
  const canApprove=["admin","qa_manager"].includes(role);

  const load=async()=>{
    try{
      setError("");
      const r=await api<ApiEnvelope<Monograph[]>>("/products/monographs/");
      setRows(Array.isArray(r.data)?r.data:[]);
    }catch(v){setError(v instanceof Error?v.message:"Unable to load monographs.")}
  };
  useEffect(()=>{void load()},[]);

  async function openDetail(id:string){
    try{
      setError("");
      const [m,t]=await Promise.all([
        api<ApiEnvelope<Monograph>>("/products/monographs/"+id+"/"),
        api<ApiEnvelope<Test[]>>("/products/monographs/"+id+"/tests/")
      ]);
      setSelected(m.data); setTests(Array.isArray(t.data)?t.data:[]);
    }catch(v){setError(v instanceof Error?v.message:"Unable to load monograph.")}
  }

  async function create(){
    setBusy(true);setError("");
    try{
      await api("/products/monographs/",{method:"POST",body:JSON.stringify({...form,status:"draft"})});
      setForm({name:"",version:"",effective_date:""});setCreateOpen(false);await load();
    }catch(v){setError(v instanceof Error?v.message:"Unable to create monograph.")}finally{setBusy(false)}
  }

  async function addTest(){
    if(!selected)return;
    setBusy(true);setError("");
    try{
      const r=await api<ApiEnvelope<Test[]>>("/products/monographs/"+selected.id+"/tests/",{
        method:"POST",
        body:JSON.stringify({...testForm,sequence:tests.length+1})
      });
      if(r.data) setTests((current)=>[...current,r.data as unknown as Test]);
      setTestForm({name:"",method:"",specification:"",unit:""});setTestOpen(false);
    }catch(v){setError(v instanceof Error?v.message:"Unable to add monograph test.")}finally{setBusy(false)}
  }

  async function approve(){
    if(!selected)return;
    setBusy(true);setError("");
    try{
      const r=await api<ApiEnvelope<Monograph>>("/products/monographs/"+selected.id+"/approve/",{method:"POST"});
      setSelected(r.data); await load();
    }catch(v){setError(v instanceof Error?v.message:"Unable to approve monograph.")}finally{setBusy(false)}
  }

  return <div className="content">
    <div className="page-header"><div><span className="eyebrow">MASTER DATA</span><h1>Monographs</h1><p>Controlled specifications used by products and stability batches.</p></div><button className="btn primary" onClick={()=>setCreateOpen(!createOpen)}>{createOpen?"Close":"Create monograph"}</button></div>
    {error&&<div className="inline-error">{error}</div>}

    {createOpen&&<section className="card form-card"><h3>Create draft monograph</h3><div className="form-grid">
      <label className="field"><span>Name</span><input value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required/></label>
      <label className="field"><span>Version</span><input value={form.version} onChange={e=>setForm({...form,version:e.target.value})} required/></label>
      <label className="field"><span>Effective date</span><input type="date" value={form.effective_date} onChange={e=>setForm({...form,effective_date:e.target.value})} required/></label>
    </div><div className="modal-actions"><button className="btn" onClick={()=>setCreateOpen(false)}>Cancel</button><button className="btn primary" disabled={busy} onClick={create}>{busy?"Creating…":"Create draft"}</button></div></section>}

    <section className="card table-card"><div className="card-header"><strong>Monographs</strong><span>{rows.length} records</span></div><div className="table-wrap"><table><thead><tr><th>Name</th><th>Version</th><th>Effective</th><th>Status</th><th>Tests</th><th/></tr></thead><tbody>{rows.map(m=><tr key={m.id}><td><b>{m.name}</b><div className="muted">{m.id}</div></td><td>{m.version}</td><td>{m.effective_date}</td><td><span className={"status "+(m.status==="approved"?"active":"warning")}>{m.status}</span></td><td>{m.tests?.length??0}</td><td><button className="btn" onClick={()=>void openDetail(m.id)}>Open</button></td></tr>)}</tbody></table>{!rows.length&&<div className="empty">No monographs returned by the backend.</div>}</div></section>

    {selected&&<section className="card detail-card"><div className="card-header"><div><strong>{selected.name} · v{selected.version}</strong><span>{selected.status}</span></div><div className="actions">{canApprove&&selected.status!=="approved"&&<button className="btn primary" disabled={busy} onClick={approve}>Approve</button>}<button className="btn" onClick={()=>setTestOpen(!testOpen)} disabled={selected.status==="approved"}>{testOpen?"Close":"Add test"}</button><button className="btn" onClick={()=>setSelected(null)}>Close</button></div></div>
      {testOpen&&<div className="form-card"><div className="form-grid">
        <label className="field"><span>Test name</span><input value={testForm.name} onChange={e=>setTestForm({...testForm,name:e.target.value})} required/></label>
        <label className="field"><span>Method</span><input value={testForm.method} onChange={e=>setTestForm({...testForm,method:e.target.value})} required/></label>
        <label className="field"><span>Specification</span><input value={testForm.specification} onChange={e=>setTestForm({...testForm,specification:e.target.value})} required/></label>
        <label className="field"><span>Unit</span><input value={testForm.unit} onChange={e=>setTestForm({...testForm,unit:e.target.value})}/></label>
      </div><button className="btn primary" disabled={busy} onClick={addTest}>{busy?"Adding…":"Add test"}</button></div>}
      <div className="table-wrap"><table><thead><tr><th>Seq</th><th>Name</th><th>Method</th><th>Specification</th><th>Unit</th></tr></thead><tbody>{tests.map(t=><tr key={t.id}><td>{t.sequence}</td><td><b>{t.name}</b></td><td>{t.method}</td><td>{t.specification}</td><td>{t.unit||"—"}</td></tr>)}</tbody></table>{!tests.length&&<div className="empty">No tests are defined for this monograph.</div>}</div>
    </section>}
  </div>
}
