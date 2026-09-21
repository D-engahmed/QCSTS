"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, ShieldCheck } from "lucide-react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { useAuth } from "@/components/AuthProvider";

type TestPoint={id:string;batch:string;batch_number:string;product_name:string;month:number;scheduled_date:string;status:string};
type Monograph={id:string;name:string;version:string;status:string;tests?:Test[]};
type Test={id:string;name:string;method:string;specification:string;unit:string;sequence:number};

function unwrap<T>(x:any):T{return x?.data??x;}

export default function NewResult(){
 const {user}=useAuth();
 const [points,setPoints]=useState<TestPoint[]>([]),[tests,setTests]=useState<Test[]>([]),[point,setPoint]=useState(""),[test,setTest]=useState(""),[value,setValue]=useState(""),[unit,setUnit]=useState(""),[notes,setNotes]=useState(""),[password,setPassword]=useState(""),[error,setError]=useState(""),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 useEffect(()=>{Promise.all([api<ApiEnvelope<TestPoint[]>>(endpoints.testPoints),api<ApiEnvelope<Monograph[]>>(endpoints.monographs)]).then(([p,m])=>{setPoints(unwrap<TestPoint[]>(p)||[]);const ms=unwrap<Monograph[]>(m)||[];setTests(ms.filter(x=>x.status==="approved").flatMap(x=>x.tests||[]))}).catch(e=>setError(e instanceof Error?e.message:"Unable to load result-entry data."))},[]);
 const selected=tests.find(x=>x.id===test);
 useEffect(()=>{if(selected?.unit)setUnit(selected.unit)},[selected?.unit]);
 async function submit(e:React.FormEvent){e.preventDefault();setBusy(true);setError("");setMessage("");try{const auth=await api<ApiEnvelope<{signature_token:string}>>(endpoints.signatureVerify,{method:"POST",body:JSON.stringify({password})});const token=unwrap<{signature_token:string}>(auth).signature_token;await api(endpoints.results,{method:"POST",headers:{"X-Signature-Token":token},body:JSON.stringify({test_point:point,monograph_test:test,value,unit,notes})});setMessage("Result submitted successfully.");setValue("");setNotes("");setPassword("");}catch(x){setError(x instanceof Error?x.message:"Unable to submit result.")}finally{setBusy(false)}}
 return <div className="content"><div className="breadcrumb"><Link href="/app/results">Results</Link><span>→</span><span>New result</span></div><div className="page-header"><div><span className="eyebrow">RESULT ENTRY</span><h1>Record test result</h1><p>Create a real result against a scheduled test point and approved monograph test.</p></div></div>{error&&<ErrorBanner message={error}/>} {message&&<div className="form-success">{message}</div>}<section className="card form-card" style={{maxWidth:760}}><form onSubmit={submit}><label className="field"><span>Test point</span><select required value={point} onChange={e=>setPoint(e.target.value)}><option value="">Select test point…</option>{points.map(x=><option key={x.id} value={x.id}>{x.batch_number} · Month {x.month} · {x.product_name} · {x.scheduled_date}</option>)}</select></label><label className="field"><span>Monograph test</span><select required value={test} onChange={e=>setTest(e.target.value)}><option value="">Select test…</option>{tests.map(x=><option key={x.id} value={x.id}>{x.name} · {x.method}</option>)}</select></label><div className="form-grid"><label className="field"><span>Measured value</span><input required value={value} onChange={e=>setValue(e.target.value)} /></label><label className="field"><span>Unit</span><input value={unit} onChange={e=>setUnit(e.target.value)} placeholder="%, mg, pH" /></label></div><label className="field"><span>Notes</span><textarea value={notes} onChange={e=>setNotes(e.target.value)} /></label><div className="security-note"><ShieldCheck size={16}/><span>Signed submission for {user?.full_name||"the current analyst"}. Django owns pass/fail evaluation.</span></div><label className="field"><span>Password re-authentication</span><input required type="password" value={password} onChange={e=>setPassword(e.target.value)} /></label><div className="modal-actions"><Link className="btn" href="/app/results"><ArrowLeft size={14}/> Back</Link><button className="btn primary" disabled={busy}>{busy?"Signing & submitting…":"Sign & submit"}</button></div></form></section></div>;
}
