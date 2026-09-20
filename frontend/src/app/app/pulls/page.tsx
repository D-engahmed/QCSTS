"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api, type ApiEnvelope } from "@/lib/api";

type Batch={id:string;batch_number:string;product_name:string;qty_placed:number;qty_remaining:number;study_type:string};
type TestPoint={id:string;batch:string;month:number;scheduled_date:string;status:string};
type Pull={id:string;batch:string;batch_number?:string;test_point:string;qty_pulled:number;pulled_by?:string;pulled_at:string;notes?:string};

export default function SamplePullsPage(){
  const [batches,setBatches]=useState<Batch[]>([]);
  const [points,setPoints]=useState<TestPoint[]>([]);
  const [pulls,setPulls]=useState<Pull[]>([]);
  const [selected,setSelected]=useState<TestPoint|null>(null);
  const [quantity,setQuantity]=useState("");
  const [notes,setNotes]=useState("");
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");

  const batchMap=useMemo(()=>new Map(batches.map(b=>[b.id,b])),[batches]);

  const load=async()=>{
    try{
      setError("");
      const [b,tp,p]=await Promise.all([
        api<ApiEnvelope<Batch[]>>("/batches/"),
        api<ApiEnvelope<TestPoint[]>>("/test-points/"),
        api<ApiEnvelope<Pull[]>>("/chamber/pulls/")
      ]);
      setBatches(Array.isArray(b.data)?b.data:[]);
      setPoints(Array.isArray(tp.data)?tp.data.filter(x=>x.status==="pending"||x.status==="overdue"):[]);
      setPulls(Array.isArray(p.data)?p.data:[]);
    }catch(v){setError(v instanceof Error?v.message:"Unable to load sample-pull data.")}
  };
  useEffect(()=>{void load()},[]);

  async function pull(){
    if(!selected)return;
    const qty=Number(quantity);
    const batch=batchMap.get(selected.batch);
    if(!batch){setError("The selected batch is no longer available.");return}
    if(!Number.isInteger(qty)||qty<1){setError("Enter a positive whole-number quantity.");return}
    if(qty>batch.qty_remaining){setError("Requested quantity exceeds the server-reported remaining quantity.");return}
    setBusy(true);setError("");
    try{
      await api("/chamber/pulls/",{method:"POST",body:JSON.stringify({
        batch:selected.batch,test_point:selected.id,qty_pulled:qty,notes:notes.trim()
      })});
      setSelected(null);setQuantity("");setNotes("");await load();
    }catch(v){setError(v instanceof Error?v.message:"Unable to record sample pull.")}finally{setBusy(false)}
  }

  return <div className="content">
    <div className="page-header"><div><span className="eyebrow">CHAMBER OPERATIONS</span><h1>Sample pulls</h1><p>Record physical sample withdrawals against the exact backend test point and batch.</p></div><button className="btn" onClick={()=>void load()}>Refresh</button></div>
    {error&&<div className="inline-error">{error}</div>}
    <section className="card table-card"><div className="card-header"><div><strong>Due test points</strong><span>{points.length} pending/overdue points</span></div></div><div className="table-wrap"><table><thead><tr><th>Batch</th><th>Product</th><th>Test point</th><th>Scheduled</th><th>Remaining</th><th/></tr></thead><tbody>{points.map(tp=>{const b=batchMap.get(tp.batch);return <tr key={tp.id}><td><b>{b?.batch_number||tp.batch}</b></td><td>{b?.product_name||"—"}</td><td>{tp.month===0?"Initial":tp.month+"M"}</td><td>{tp.scheduled_date}</td><td>{b?b.qty_remaining+" / "+b.qty_placed:"—"}</td><td><button className="btn" onClick={()=>setSelected(tp)}>Record pull</button></td></tr>})}</tbody></table>{!points.length&&<div className="empty">No pending or overdue test points require a sample pull.</div>}</div></section>

    <section className="card table-card"><div className="card-header"><strong>Pull history</strong><span>{pulls.length} records</span></div><div className="table-wrap"><table><thead><tr><th>Batch</th><th>Test point</th><th>Quantity</th><th>Pulled</th><th>Notes</th></tr></thead><tbody>{pulls.map(p=><tr key={p.id}><td>{p.batch_number||p.batch}</td><td>{p.test_point}</td><td>{p.qty_pulled}</td><td>{p.pulled_at?new Date(p.pulled_at).toLocaleString():"—"}</td><td>{p.notes||"—"}</td></tr>)}</tbody></table>{!pulls.length&&<div className="empty">No sample-pull records returned by the backend.</div>}</div></section>

    {selected&&<section className="card detail-card"><div className="card-header"><div><strong>Record sample pull</strong><span>{selected.month===0?"Initial":selected.month+"M"} · {batchMap.get(selected.batch)?.batch_number||selected.batch}</span></div><button className="btn" onClick={()=>setSelected(null)}>Cancel</button></div><div className="form-grid"><label className="field"><span>Quantity pulled</span><input type="number" min="1" step="1" value={quantity} onChange={e=>setQuantity(e.target.value)} required/></label><label className="field"><span>Remaining before pull</span><input value={String(batchMap.get(selected.batch)?.qty_remaining??"—")} readOnly/></label><label className="field" style={{gridColumn:"1/-1"}}><span>Notes</span><textarea value={notes} onChange={e=>setNotes(e.target.value)}/></label></div><button className="btn primary" disabled={busy} onClick={pull}>{busy?"Recording…":"Record sample pull"}</button></section>}
  </div>
}
