"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { ErrorBanner } from "@/components/ui/ErrorBanner";

type Test = { id:string; name:string; method:string; specification:string; unit:string; sequence:number };
type Monograph = {
  id:string; name:string; version:string; effective_date:string; status:string;
  approved_by_name?:string; approved_at?:string; tests?:Test[];
};
function unwrap<T>(x:any):T { return x?.data ?? x; }

export default function MonographsWorkspace() {
  const [rows,setRows]=useState<Monograph[]>([]);
  const [selected,setSelected]=useState<Monograph|null>(null);
  const [error,setError]=useState("");
  const [open,setOpen]=useState(false);
  const [editOpen,setEditOpen]=useState(false);
  const [testOpen,setTestOpen]=useState(false);
  const [busy,setBusy]=useState(false);
  const [password,setPassword]=useState("");
  const [reason,setReason]=useState("");
  const [form,setForm]=useState({name:"",version:"",effective_date:""});
  const [testForm,setTestForm]=useState({name:"",method:"",specification:"",unit:"",sequence:""});

  const load=async()=>{
    try{
      setError("");
      const p=await api<ApiEnvelope<Monograph[]>>(endpoints.monographs);
      setRows(unwrap<Monograph[]>(p)||[]);
    }catch(e){setError(e instanceof Error?e.message:"Unable to load monographs.");}
  };
  useEffect(()=>{void load()},[]);

  const create=async(e:FormEvent)=>{
    e.preventDefault();setBusy(true);setError("");
    try{
      await api(endpoints.monographs,{method:"POST",body:JSON.stringify(form)});
      setForm({name:"",version:"",effective_date:""});
      setOpen(false);await load();
    }catch(x){setError(x instanceof Error?x.message:"Unable to create monograph.");}
    finally{setBusy(false);}
  };

  const saveEdit=async(e:FormEvent)=>{
    e.preventDefault();if(!selected)return;setBusy(true);setError("");
    try{
      const r=await api<ApiEnvelope<Monograph>>(`${endpoints.monographs}${selected.id}/`,{method:"PATCH",body:JSON.stringify(form)});
      setSelected(unwrap<Monograph>(r));setEditOpen(false);await load();
    }catch(x){setError(x instanceof Error?x.message:"Unable to update monograph.");}
    finally{setBusy(false);}
  };

  const addTest=async(e:FormEvent)=>{
    e.preventDefault();if(!selected)return;setBusy(true);setError("");
    try{
      await api(endpoints.monographTests(selected.id),{
        method:"POST",
        body:JSON.stringify({
          ...testForm,
          sequence:Number(testForm.sequence||((selected.tests?.length||0)+1)),
        }),
      });
      setTestForm({name:"",method:"",specification:"",unit:"",sequence:String((selected.tests?.length||0)+2)});
      setTestOpen(false);await load();
      const refreshed=await api<ApiEnvelope<Monograph[]>>(endpoints.monographs);
      setSelected((unwrap<Monograph[]>(refreshed)||[]).find(x=>x.id===selected.id)||null);
    }catch(x){setError(x instanceof Error?x.message:"Unable to add monograph test.");}
    finally{setBusy(false);}
  };

  const approve=async()=>{
    if(!selected)return;setBusy(true);setError("");
    try{
      const token=unwrap<{signature_token:string}>(await api<ApiEnvelope<{signature_token:string}>>(endpoints.signatureVerify,{method:"POST",body:JSON.stringify({password})})).signature_token;
      await api(endpoints.monographApprove(selected.id),{method:"POST",headers:{"X-Signature-Token":token},body:JSON.stringify({reason})});
      setPassword("");setReason("");setSelected(null);await load();
    }catch(x){setError(x instanceof Error?x.message:"Approval failed.");}
    finally{setBusy(false);}
  };

  return (
    <div className="content">
      <div className="page-header">
        <div><span className="eyebrow">MASTER DATA</span><h1>Monographs</h1><p>Draft monographs support structured test definitions; approval is signed and server-controlled.</p></div>
        <button className="btn primary" onClick={()=>setOpen(v=>!v)}>{open?"Close":"New monograph"}</button>
      </div>
      {error&&<ErrorBanner message={error} onRetry={load}/>}
      {open&&<section className="card form-card" style={{maxWidth:760,marginBottom:14}}>
        <form onSubmit={create}>
          <div className="form-grid">
            <label className="field"><span>Name</span><input required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label>
            <label className="field"><span>Version</span><input required value={form.version} onChange={e=>setForm({...form,version:e.target.value})}/></label>
            <label className="field"><span>Effective date</span><input required type="date" value={form.effective_date} onChange={e=>setForm({...form,effective_date:e.target.value})}/></label>
          </div>
          <button className="btn primary" disabled={busy}>{busy?"Saving…":"Create draft"}</button>
        </form>
      </section>}
      <section className="card table-card">
        <div className="card-header"><div><strong>{rows.length} monographs</strong><span>Live organization-scoped records</span></div><button className="btn" onClick={()=>void load()}>Refresh</button></div>
        <DataTable rows={rows} columns={[{key:"name",label:"Monograph",sortable:true},{key:"version",label:"Version"},{key:"effective_date",label:"Effective"},{key:"status",label:"Status"},{key:"approved_by_name",label:"Approved by"}]} onRowClick={row=>{setSelected(row);setForm({name:row.name,version:row.version,effective_date:row.effective_date});setTestForm({name:"",method:"",specification:"",unit:"",sequence:String((row.tests?.length||0)+1)})}} emptyTitle="No monographs" emptyText="Create the first draft monograph for this organization."/>
      </section>

      {selected&&<div className="modal-backdrop"><section className="signature-panel wide" role="dialog" aria-modal="true">
        <div className="page-header" style={{marginBottom:14}}><div><span className="eyebrow">MONOGRAPH</span><h2>{selected.name} v{selected.version}</h2><p>Status: <b>{selected.status}</b>. {selected.tests?.length||0} defined tests.</p></div></div>
        {selected.status!=="approved"&&<div className="action-row">
          <button className="btn" onClick={()=>setEditOpen(v=>!v)}>{editOpen?"Close edit":"Edit draft"}</button>
          <button className="btn" onClick={()=>setTestOpen(v=>!v)}>{testOpen?"Close test form":"Add test"}</button>
        </div>}
        {editOpen&&selected.status!=="approved"&&<form onSubmit={saveEdit} className="card form-card" style={{marginTop:14}}>
          <div className="form-grid"><label className="field"><span>Name</span><input required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label><label className="field"><span>Version</span><input required value={form.version} onChange={e=>setForm({...form,version:e.target.value})}/></label><label className="field"><span>Effective date</span><input required type="date" value={form.effective_date} onChange={e=>setForm({...form,effective_date:e.target.value})}/></label></div><button className="btn primary" disabled={busy}>{busy?"Saving…":"Save draft"}</button>
        </form>}
        {testOpen&&selected.status!=="approved"&&<form onSubmit={addTest} className="card form-card" style={{marginTop:14}}>
          <div className="form-grid"><label className="field"><span>Test name</span><input required value={testForm.name} onChange={e=>setTestForm({...testForm,name:e.target.value})}/></label><label className="field"><span>Method</span><input required value={testForm.method} onChange={e=>setTestForm({...testForm,method:e.target.value})}/></label><label className="field"><span>Specification</span><input required value={testForm.specification} onChange={e=>setTestForm({...testForm,specification:e.target.value})}/></label><label className="field"><span>Unit</span><input required value={testForm.unit} onChange={e=>setTestForm({...testForm,unit:e.target.value})}/></label><label className="field"><span>Sequence</span><input required type="number" min="1" value={testForm.sequence} onChange={e=>setTestForm({...testForm,sequence:e.target.value})}/></label></div><button className="btn primary" disabled={busy}>{busy?"Saving…":"Add test"}</button>
        </form>}
        <section className="card table-card" style={{marginTop:14}}><div className="card-header"><div><strong>Defined tests</strong><span>Tests are immutable after monograph approval.</span></div></div><div className="table-wrap"><table><thead><tr><th>Sequence</th><th>Test</th><th>Method</th><th>Specification</th><th>Unit</th></tr></thead><tbody>{(selected.tests||[]).sort((a,b)=>a.sequence-b.sequence).map(t=><tr key={t.id}><td>{t.sequence}</td><td><b>{t.name}</b></td><td>{t.method}</td><td>{t.specification}</td><td>{t.unit}</td></tr>)}</tbody></table>{!(selected.tests||[]).length&&<div className="empty">No tests defined.</div>}</div></section>
        {selected.status!=="approved"&&<div className="card form-card" style={{marginTop:14}}><div className="form-section-title"><span>Approval signature</span></div><label className="field"><span>Password re-authentication</span><input type="password" value={password} onChange={e=>setPassword(e.target.value)}/></label><label className="field"><span>Approval reason</span><textarea value={reason} onChange={e=>setReason(e.target.value)}/></label><div className="modal-actions"><button className="btn" onClick={()=>setSelected(null)}>Close</button><button className="btn approve" disabled={busy||!password||!reason} onClick={()=>void approve()}>{busy?"Approving…":"Approve & sign"}</button></div></div>}
        {selected.status==="approved"&&<div className="modal-actions"><button className="btn" onClick={()=>setSelected(null)}>Close</button></div>}
      </section></div>}
    </div>
  );
}
