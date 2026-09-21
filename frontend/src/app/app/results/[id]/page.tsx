"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { SignaturePanel } from "@/components/ui/SignaturePanel";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { useToast } from "@/components/ui/Toast";

type Result = {
  id:string;
  test_point:string;
  test_name:string;
  value:string;
  unit:string;
  specification_snapshot:string;
  pass_fail:string;
  analyst_name:string;
  submitted_at:string;
  notes:string;
  workflow_state:string;
};

function unwrap<T>(x:any):T{return x?.data??x;}
function displayState(value:string){return value.replaceAll("_"," ").replace(/\b\w/g,(x)=>x.toUpperCase());}

export default function ResultDetail(){
 const {id}=useParams<{id:string}>(); const {show}=useToast();
 const [result,setResult]=useState<Result|null>(null),[error,setError]=useState(""),[action,setAction]=useState<string|null>(null),[correction,setCorrection]=useState(false),[pending,setPending]=useState(false),[correctionValue,setCorrectionValue]=useState(""),[correctionReason,setCorrectionReason]=useState("");
 const load=async()=>{try{setError("");const p=await api<ApiEnvelope<Result[]>>(endpoints.results);const rows=unwrap<Result[]>(p)||[];setResult(rows.find(x=>String(x.id)===String(id))||null)}catch(e){setError(e instanceof Error?e.message:"Unable to load result.")}};
 useEffect(()=>{void load()},[id]);
 const transition=async(reason:string,password:string)=>{if(!result||!action)return;setPending(true);setError("");try{const sig=await api<ApiEnvelope<{signature_token:string}>>(endpoints.signatureVerify,{method:"POST",body:JSON.stringify({password})});const path=action==="Review"?endpoints.resultReview(result.id):action==="Approve"?endpoints.resultApprove(result.id):endpoints.resultReject(result.id);const r=await api<ApiEnvelope<any>>(path,{method:"POST",headers:{"X-Signature-Token":unwrap<{signature_token:string}>(sig).signature_token},body:JSON.stringify({comments:reason})});show(action+" recorded successfully.");setAction(null);setResult((current)=>current?{...current,...(unwrap<any>(r)||{})}:current);await load()}catch(e){setError(e instanceof Error?e.message:"Controlled action failed.")}finally{setPending(false)}};
 const correct=async(e:React.FormEvent)=>{e.preventDefault();if(!result)return;setPending(true);setError("");try{const sig=await api<ApiEnvelope<{signature_token:string}>>(endpoints.signatureVerify,{method:"POST",body:JSON.stringify({password:(document.getElementById("correction-password") as HTMLInputElement)?.value||""})});await api(endpoints.resultCorrect(result.id),{method:"POST",headers:{"X-Signature-Token":unwrap<{signature_token:string}>(sig).signature_token},body:JSON.stringify({value:correctionValue,reason:correctionReason,unit:result.unit,notes:result.notes})});show("Controlled correction recorded successfully.");setCorrection(false);setCorrectionValue("");setCorrectionReason("");await load()}catch(e){setError(e instanceof Error?e.message:"Correction failed.")}finally{setPending(false)}};
 if(error&&!result)return <div className="content"><ErrorBanner message={error}/></div>;
 if(!result)return <div className="content"><div className="empty">Loading result…</div></div>;
 const state=result.workflow_state||"unknown"; const human=displayState(state);
 return <div className="content"><div className="breadcrumb"><Link href="/app/results">Results & Review</Link><span>/</span><span>{result.id.slice(0,12)}</span></div><header className="detail-header"><div><span className="eyebrow">CONTROLLED RESULT</span><h1>{result.test_name||"Result"}</h1><div className="detail-meta">{result.analyst_name||"Unknown analyst"} · {result.submitted_at?new Date(result.submitted_at).toLocaleString():"Not submitted"}</div></div><StatusBadge status={human}/></header>{error&&<ErrorBanner message={error}/>}<div className="action-row">{state==="submitted"&&<button className="btn" onClick={()=>setAction("Review")}>Review</button>}{state==="under_review"&&<><button className="btn approve" onClick={()=>setAction("Approve")}>Approve</button><button className="btn reject" onClick={()=>setAction("Reject")}>Reject</button></>}{state!=="approved"&&<button className="btn correction" onClick={()=>setCorrection(true)}>Controlled correction</button>}<Link className="btn" href="/app/results">← Results</Link></div><div className="detail-grid"><section className="card detail-card"><h2>Result</h2><dl><dt>Measured value</dt><dd>{result.value??"—"} {result.unit||""}</dd><dt>Outcome</dt><dd>{result.pass_fail||"Pending"}</dd><dt>Specification snapshot</dt><dd>{result.specification_snapshot||"—"}</dd><dt>Test point</dt><dd>{result.test_point||"—"}</dd><dt>Workflow</dt><dd>{human}</dd><dt>Notes</dt><dd>{result.notes||"—"}</dd></dl></section><section className="card detail-card"><h2>Control boundary</h2><p>Review, approval, rejection and correction are authenticated against the backend. The UI never changes the authoritative workflow state itself.</p></section></div>{action&&<SignaturePanel action={action} onCancel={()=>setAction(null)} onConfirm={(reason,password)=>transition(reason,password)} pending={pending} requiresReason={action==="Reject"}/>} {correction&&<div className="modal-backdrop"><section className="signature-panel"><span className="eyebrow">CONTROLLED CORRECTION</span><h2>Supersede result</h2><p>The original result remains traceable; Django decides whether the record can still be corrected.</p><form onSubmit={correct}><label className="field"><span>Replacement value</span><input required value={correctionValue} onChange={e=>setCorrectionValue(e.target.value)}/></label><label className="field"><span>Reason</span><textarea required value={correctionReason} onChange={e=>setCorrectionReason(e.target.value)}/></label><label className="field"><span>Password re-authentication</span><input id="correction-password" required type="password"/></label><div className="modal-actions"><button className="btn" type="button" onClick={()=>setCorrection(false)} disabled={pending}>Cancel</button><button className="btn correction" disabled={pending}>{pending?"Recording…":"Sign correction"}</button></div></form></section></div>}</div>;
}