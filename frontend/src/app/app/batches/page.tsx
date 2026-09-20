"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type ApiEnvelope } from "@/lib/api";

type Product={id:string;name:string;strength:string;monograph?:string|null;monograph_name?:string|null};
type Batch={id:string;product:string;product_name:string;batch_number:string;mfg_date:string;expiry_date:string;incubation_date:string;study_type:string;status:string;shelf:string;rack:string;position:string;location:string;qty_placed:number;qty_remaining:number;test_points?:any[]};

const initial={product:"",batch_number:"",mfg_date:"",expiry_date:"",incubation_date:"",study_type:"long_term",shelf:"",rack:"",position:"",qty_placed:""};

export default function BatchesPage(){
 const [rows,setRows]=useState<Batch[]>([]);
 const [products,setProducts]=useState<Product[]>([]);
 const [open,setOpen]=useState(false);
 const [form,setForm]=useState(initial);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState("");

 const load=async()=>{
  try{
   setError("");
   const [b,p]=await Promise.all([
    api<ApiEnvelope<Batch[]>>("/batches/"),
    api<ApiEnvelope<Product[]>>("/products/")
   ]);
   setRows(Array.isArray(b.data)?b.data:[]);
   setProducts(Array.isArray(p.data)?p.data:[]);
  }catch(v){setError(v instanceof Error?v.message:"Unable to load batches.")}
 };
 useEffect(()=>{void load()},[]);

 const eligible=useMemo(()=>products.filter(p=>p.monograph),[products]);

 async function create(){
  setBusy(true);setError("");
  try{
   await api("/batches/",{method:"POST",body:JSON.stringify({
    ...form,
    qty_placed:Number(form.qty_placed),
   })});
   setForm(initial);setOpen(false);await load();
  }catch(v){setError(v instanceof Error?v.message:"Unable to create batch.")}finally{setBusy(false)}
 }

 return <div className="content">
  <div className="page-header"><div><span className="eyebrow">STABILITY EXECUTION</span><h1>Batches</h1><p>Live stability batch records. The backend generates test points when a valid batch is created.</p></div><button className="btn primary" onClick={()=>setOpen(!open)}>{open?"Close":"Add batch"}</button></div>
  {error&&<div className="inline-error">{error}</div>}

  {open&&<section className="card form-card"><h3>Create stability batch</h3><div className="form-grid">
   <label className="field"><span>Product</span><select value={form.product} onChange={e=>setForm({...form,product:e.target.value})}><option value="">Select approved product</option>{eligible.map(p=><option key={p.id} value={p.id}>{p.name} · {p.strength}</option>)}</select></label>
   <label className="field"><span>Batch number</span><input value={form.batch_number} onChange={e=>setForm({...form,batch_number:e.target.value})} required/></label>
   <label className="field"><span>Manufacturing date</span><input type="date" value={form.mfg_date} onChange={e=>setForm({...form,mfg_date:e.target.value})} required/></label>
   <label className="field"><span>Expiry date</span><input type="date" value={form.expiry_date} onChange={e=>setForm({...form,expiry_date:e.target.value})} required/></label>
   <label className="field"><span>Incubation date</span><input type="date" value={form.incubation_date} onChange={e=>setForm({...form,incubation_date:e.target.value})} required/></label>
   <label className="field"><span>Study type</span><select value={form.study_type} onChange={e=>setForm({...form,study_type:e.target.value})}><option value="long_term">Long-term</option><option value="accelerated">Accelerated</option></select></label>
   <label className="field"><span>Shelf</span><input value={form.shelf} onChange={e=>setForm({...form,shelf:e.target.value})} required/></label>
   <label className="field"><span>Rack</span><input value={form.rack} onChange={e=>setForm({...form,rack:e.target.value})} required/></label>
   <label className="field"><span>Position</span><input value={form.position} onChange={e=>setForm({...form,position:e.target.value})} required/></label>
   <label className="field"><span>Quantity placed</span><input type="number" min="1" value={form.qty_placed} onChange={e=>setForm({...form,qty_placed:e.target.value})} required/></label>
  </div><div className="modal-actions"><button className="btn" onClick={()=>setOpen(false)}>Cancel</button><button className="btn primary" disabled={busy} onClick={create}>{busy?"Creating…":"Create batch"}</button></div></section>}

  <section className="card table-card"><div className="card-header"><strong>Batches</strong><span>{rows.length} records</span></div><div className="table-wrap"><table><thead><tr><th>Batch</th><th>Product</th><th>Study</th><th>Manufactured</th><th>Incubation</th><th>Location</th><th>Qty</th><th>Status</th></tr></thead><tbody>{rows.map(b=><tr key={b.id}><td><b>{b.batch_number}</b><div className="muted">{b.id}</div></td><td>{b.product_name}</td><td>{b.study_type}</td><td>{b.mfg_date}</td><td>{b.incubation_date}</td><td>{b.location||[b.shelf,b.rack,b.position].join("/")}</td><td>{b.qty_remaining} / {b.qty_placed}</td><td><span className={"status "+(b.status==="active"?"active":b.status==="failed"?"critical":"warning")}>{b.status}</span></td></tr>)}</tbody></table>{!rows.length&&<div className="empty">No batch records returned by the backend.</div>}</div></section>
 </div>
}
