"use client";

import { useEffect, useState } from "react";
import { api, type ApiEnvelope } from "@/lib/api";

type Batch={
 id:string;batch_number:string;product_name:string;study_type:string;
 shelf:string;rack:string;position:string;location:string;qty_placed:number;qty_remaining:number;status:string;
};

export default function ChambersPage(){
 const [rows,setRows]=useState<Batch[]>([]);
 const [history,setHistory]=useState<any[]>([]);
 const [selected,setSelected]=useState<Batch|null>(null);
 const [form,setForm]=useState({new_shelf:"",new_rack:"",new_position:"",reason:""});
 const [busy,setBusy]=useState(false),[error,setError]=useState("");

 const load=async()=>{
  try{setError("");const r=await api<ApiEnvelope<Batch[]>>("/chamber/");setRows(Array.isArray(r.data)?r.data:[])}
  catch(v){setError(v instanceof Error?v.message:"Unable to load chamber inventory.")}
 };
 useEffect(()=>{void load()},[]);

 async function showHistory(batch:Batch){
  try{
   const r=await api<ApiEnvelope<any[]>>("/chamber/locations/"+batch.id+"/");
   setHistory(Array.isArray(r.data)?r.data:[]);setSelected(batch);
  }catch(v){setError(v instanceof Error?v.message:"Unable to load location history.")}
 }

 async function move(){
  if(!selected)return;
  setBusy(true);setError("");
  try{
   await api("/chamber/move/",{method:"POST",body:JSON.stringify({batch:selected.id,...form})});
   setSelected(null);setHistory([]);setForm({new_shelf:"",new_rack:"",new_position:"",reason:""});await load();
  }catch(v){setError(v instanceof Error?v.message:"Unable to move batch.")}finally{setBusy(false)}
 }

 return <div className="content">
  <div className="page-header"><div><span className="eyebrow">CHAMBER OPERATIONS</span><h1>Chamber inventory</h1><p>Live active batches, quantities and controlled location movements.</p></div><button className="btn" onClick={()=>void load()}>Refresh</button></div>
  {error&&<div className="inline-error">{error}</div>}
  <section className="card table-card"><div className="card-header"><strong>Active chamber inventory</strong><span>{rows.length} batches</span></div><div className="table-wrap"><table><thead><tr><th>Batch</th><th>Product</th><th>Study</th><th>Location</th><th>Remaining</th><th>Action</th></tr></thead><tbody>{rows.map(b=><tr key={b.id}><td><b>{b.batch_number}</b></td><td>{b.product_name}</td><td>{b.study_type}</td><td>{b.location||[b.shelf,b.rack,b.position].join("/")}</td><td>{b.qty_remaining} / {b.qty_placed}</td><td><button className="btn" onClick={()=>void showHistory(b)}>History / Move</button></td></tr>)}</tbody></table>{!rows.length&&<div className="empty">No active chamber batches returned by the backend.</div>}</div></section>

  {selected&&<section className="card detail-card"><div className="card-header"><div><strong>{selected.batch_number}</strong><span>{selected.product_name}</span></div><button className="btn" onClick={()=>setSelected(null)}>Close</button></div>
   <div className="form-card"><h3>Move batch</h3><div className="form-grid">
    <label className="field"><span>New shelf</span><input value={form.new_shelf} onChange={e=>setForm({...form,new_shelf:e.target.value})}/></label>
    <label className="field"><span>New rack</span><input value={form.new_rack} onChange={e=>setForm({...form,new_rack:e.target.value})}/></label>
    <label className="field"><span>New position</span><input value={form.new_position} onChange={e=>setForm({...form,new_position:e.target.value})}/></label>
    <label className="field"><span>Reason</span><textarea value={form.reason} onChange={e=>setForm({...form,reason:e.target.value})}/></label>
   </div><button className="btn primary" disabled={busy} onClick={move}>{busy?"Moving…":"Move batch"}</button></div>
   <div className="card-header"><strong>Location history</strong><span>{history.length} entries</span></div>
   <div className="table-wrap"><table><thead><tr><th>Date</th><th>From</th><th>To</th><th>Reason</th></tr></thead><tbody>{history.map(h=><tr key={h.id}><td>{h.created_at?new Date(h.created_at).toLocaleString():"—"}</td><td>{h.old_shelf}/{h.old_rack}/{h.old_position}</td><td>{h.new_shelf}/{h.new_rack}/{h.new_position}</td><td>{h.reason||"—"}</td></tr>)}</tbody></table>{!history.length&&<div className="empty">No location history returned.</div>}</div>
  </section>}
 </div>
}
