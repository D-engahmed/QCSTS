"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, type ApiEnvelope } from "@/lib/api";
import { SignaturePanel } from "@/components/ui/SignaturePanel";

type TestPoint={id:string;batch:string;month:number;scheduled_date:string;status:string};
type Batch={id:string;batch_number:string;product:string;product_name:string;status:string;location?:string;shelf:string;rack:string;position:string};
type Product={id:string;name:string;strength:string;monograph?:string|null};
type MonographTest={id:string;name:string;method:string;specification:string;unit:string;sequence:number};

export default function TestEntryPage(){
 const {id}=useParams<{id:string}>(); const router=useRouter();
 const [tp,setTp]=useState<TestPoint|null>(null),[batch,setBatch]=useState<Batch|null>(null),[tests,setTests]=useState<MonographTest[]>([]);
 const [values,setValues]=useState<Record<string,string>>({});
 const [showSignature,setShowSignature]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState("");

 useEffect(()=>{(async()=>{
  try{
   const point=await api<ApiEnvelope<TestPoint[]>>("/test-points/");
   const found=(point.data||[]).find(x=>x.id===id);
   if(!found){setError("Test point not found.");return}
   setTp(found);
   const b=await api<ApiEnvelope<Batch>>("/batches/"+found.batch+"/");
   setBatch(b.data);
   const p=await api<ApiEnvelope<Product>>("/products/"+b.data.product+"/");
   if(!p.data.monograph){setTests([]);return}
   const t=await api<ApiEnvelope<MonographTest[]>>("/products/monographs/"+p.data.monograph+"/tests/");
   setTests(Array.isArray(t.data)?t.data:[]);
  }catch(v){setError(v instanceof Error?v.message:"Unable to load test entry.")}})()},[id]);

 const submit=async(reason:string,password:string)=>{
  setBusy(true);setError("");
  try{
   const signature=await api<ApiEnvelope<{signature_token:string}>>("/results/signature/verify/",{method:"POST",body:JSON.stringify({password})});
   for(const test of tests){
    const value=(values[test.id]||"").trim();
    if(!value) throw new Error("All configured tests must have a result before submission.");
    await api("/results/",{method:"POST",headers:{"X-Signature-Token":signature.data.signature_token},body:JSON.stringify({
      test_point:id,monograph_test:test.id,value,unit:test.unit||"",notes:reason||""
    })});
   }
   setShowSignature(false);router.push("/app/results");
  }catch(v){setError(v instanceof Error?v.message:"Unable to submit results.")}finally{setBusy(false)}
 };

 if(error&&!tp)return <div className="content"><div className="inline-error">{error}</div></div>;
 if(!tp||!batch)return <div className="content"><div className="empty">Loading test entry…</div></div>;

 return <div className="content">
  <div className="page-header"><div><span className="eyebrow">RESULT ENTRY</span><h1>{batch.batch_number}</h1><p>{batch.product_name} · {tp.month===0?"Initial":tp.month+"M"} · scheduled {tp.scheduled_date}</p></div><button className="btn" onClick={()=>router.push("/app/schedule")}>Back to schedule</button></div>
  {error&&<div className="inline-error">{error}</div>}
  <section className="card table-card"><div className="card-header"><div><strong>Analytical results</strong><span>Pass/fail is calculated by the backend specification engine.</span></div></div><div className="table-wrap"><table><thead><tr><th>Test</th><th>Method</th><th>Specification</th><th>Unit</th><th>Result</th></tr></thead><tbody>{tests.map(test=><tr key={test.id}><td><b>{test.name}</b></td><td>{test.method}</td><td>{test.specification}</td><td>{test.unit||"—"}</td><td><input value={values[test.id]||""} onChange={e=>setValues({...values,[test.id]:e.target.value})} placeholder="Measured value"/></td></tr>)}</tbody></table>{!tests.length&&<div className="empty">No monograph tests are configured for this product.</div>}</div></section>
  <div className="modal-actions"><button className="btn primary" onClick={()=>setShowSignature(true)} disabled={!tests.length||busy}>Verify identity & submit</button></div>
  {showSignature&&<SignaturePanel action="Submit results" onCancel={()=>setShowSignature(false)} onConfirm={submit} pending={busy} requiresReason={true}/>}
 </div>
}
