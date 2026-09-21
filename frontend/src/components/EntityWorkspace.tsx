"use client";

import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { api, type ApiEnvelope } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { ErrorBanner } from "@/components/ui/ErrorBanner";

export type WorkspaceField = {
  key: string; label: string;
  type?: "text" | "date" | "number" | "textarea" | "select";
  required?: boolean; placeholder?: string;
  options?: { value: string; label: string }[];
  optionsEndpoint?: string; optionLabel?: string;
};
export type WorkspaceColumn = { key: string; label: string; render?: (row: any) => ReactNode; sortable?: boolean };
export type TransitionOption = { value: string; label: string };

function unwrap<T>(payload: any): T {
  return payload && typeof payload === "object" && "data" in payload ? payload.data as T : payload as T;
}
function asRows(value: any): any[] {
  if (Array.isArray(value)) return value;
  if (value && Array.isArray(value.results)) return value.results;
  if (value && Array.isArray(value.items)) return value.items;
  return [];
}

export default function EntityWorkspace({
  eyebrow="WORKSPACE", title, description, endpoint, columns, fields=[],
  createLabel="Create record", emptyTitle="No records", readonly=false,
  transitionStatuses, headerAction, transformCreate,
}: {
  eyebrow?: string; title: string; description: string; endpoint: string; columns: WorkspaceColumn[];
  fields?: WorkspaceField[]; createLabel?: string; emptyTitle?: string; readonly?: boolean;
  transitionStatuses?: (row:any) => TransitionOption[]; headerAction?: ReactNode;
  transformCreate?: (data: Record<string,string>) => Record<string,unknown>;
}) {
  const [rows,setRows]=useState<any[]>([]),[values,setValues]=useState<Record<string,string>>({});
  const [options,setOptions]=useState<Record<string,{value:string;label:string}[]>>({});
  const [open,setOpen]=useState(false),[query,setQuery]=useState(""),[busy,setBusy]=useState(false);
  const [loading,setLoading]=useState(true),[error,setError]=useState("");
  const [transitionRow,setTransitionRow]=useState<any|null>(null),[transitionStatus,setTransitionStatus]=useState("");
  const [transitionComments,setTransitionComments]=useState(""),[transitionPassword,setTransitionPassword]=useState(""),[transitionBusy,setTransitionBusy]=useState(false);

  const load=async()=>{setLoading(true);setError("");try{const payload=await api<ApiEnvelope<unknown>>(endpoint);setRows(asRows(unwrap(payload)));}catch(value){setError(value instanceof Error?value.message:"Unable to load records.");}finally{setLoading(false);}};
  useEffect(()=>{void load();},[endpoint]);
  const lookupSpec=fields.filter(f=>f.optionsEndpoint).map(f=>`${f.key}:${f.optionsEndpoint}:${f.optionLabel??""}`).join("|");
  useEffect(()=>{const lookupFields=fields.filter(f=>f.optionsEndpoint);if(!lookupFields.length)return;let cancelled=false;void Promise.all(lookupFields.map(async field=>{try{const payload=await api<ApiEnvelope<unknown>>(field.optionsEndpoint!);const data=asRows(unwrap(payload));const result=data.map(item=>({value:String(item.id??item.value??""),label:String(item[field.optionLabel??"name"]??item.title??item.code??item.id??"Option")})).filter(x=>x.value);if(!cancelled)setOptions(current=>({...current,[field.key]:result}));}catch{if(!cancelled)setOptions(current=>({...current,[field.key]:[]}));}}));return()=>{cancelled=true;};},[lookupSpec]);

  const filteredRows=useMemo(()=>{const needle=query.trim().toLowerCase();if(!needle)return rows;return rows.filter(row=>Object.values(row).some(value=>String(value??"").toLowerCase().includes(needle)));},[rows,query]);

  const submit=async(event:FormEvent<HTMLFormElement>)=>{event.preventDefault();setBusy(true);setError("");try{const payload=transformCreate?transformCreate(values):Object.fromEntries(Object.entries(values).filter(([,v])=>v!==""));await api(endpoint,{method:"POST",body:JSON.stringify(payload)});setValues({});setOpen(false);await load();}catch(value){setError(value instanceof Error?value.message:"Unable to create record.");}finally{setBusy(false);}};

  const submitTransition=async(event:FormEvent<HTMLFormElement>)=>{event.preventDefault();if(!transitionRow||!transitionStatus||!transitionComments.trim()||!transitionPassword)return;setTransitionBusy(true);setError("");try{const sig=await api<ApiEnvelope<{signature_token:string}>>("/results/signature/verify/",{method:"POST",body:JSON.stringify({password:transitionPassword})});const token=unwrap<{signature_token:string}>(sig).signature_token;await api((endpoint.endsWith("/") ? endpoint.slice(0, -1) : endpoint)+"/"+transitionRow.id+"/transition/",{method:"POST",headers:{"X-Signature-Token":token},body:JSON.stringify({status:transitionStatus,comments:transitionComments.trim()})});setTransitionRow(null);setTransitionStatus("");setTransitionComments("");setTransitionPassword("");await load();}catch(value){setError(value instanceof Error?value.message:"Unable to record the controlled transition.");}finally{setTransitionBusy(false);}};

  const actionColumn:WorkspaceColumn|null=transitionStatuses?{key:"__actions",label:"Actions",render:row=>{const opts=transitionStatuses(row);return <button className="btn" disabled={!opts.length} onClick={event=>{event.stopPropagation();if(!opts.length)return;setTransitionRow(row);setTransitionStatus(opts[0].value);}}>{opts.length?"Transition":"—"}</button>;}}:null;
  const tableColumns=actionColumn?[...columns,actionColumn]:columns;
  const transitionOptions=transitionRow&&transitionStatuses?transitionStatuses(transitionRow):[];

  return <div className="content">
    <div className="page-header"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div><div className="action-row">{headerAction}{!readonly&&fields.length>0&&<button className="btn primary" onClick={()=>setOpen(v=>!v)}>{open?"Close":createLabel}</button>}</div></div>
    {error&&<ErrorBanner message={error} onRetry={load}/>}
    {open&&!readonly&&<section className="card form-card" style={{maxWidth:760,marginBottom:14}}><div className="card-header" style={{margin:"-20px -20px 8px"}}><div><strong>New record</strong><span>Server-side validation remains authoritative.</span></div></div><form onSubmit={submit}><div className="form-grid">{fields.map(field=>{const opts=field.options??options[field.key]??[];if(field.type==="textarea")return <label className="field" key={field.key} style={{gridColumn:"1 / -1"}}><span>{field.label}</span><textarea value={values[field.key]??""} onChange={e=>setValues(current=>({...current,[field.key]:e.target.value}))} placeholder={field.placeholder} required={field.required}/></label>;if(field.type==="select")return <label className="field" key={field.key}><span>{field.label}</span><select value={values[field.key]??""} onChange={e=>setValues(current=>({...current,[field.key]:e.target.value}))} required={field.required}><option value="">Select…</option>{opts.map(o=><option key={o.value} value={o.value}>{o.label}</option>)}</select></label>;return <label className="field" key={field.key}><span>{field.label}</span><input value={values[field.key]??""} onChange={e=>setValues(current=>({...current,[field.key]:e.target.value}))} type={field.type??"text"} placeholder={field.placeholder} required={field.required}/></label>;})}</div><button className="btn primary" disabled={busy}>{busy?"Saving…":createLabel}</button></form></section>}
    <section className="card table-card"><div className="card-header"><div><strong>{filteredRows.length} records</strong><span>{loading?"Loading authorized data…":"Live API data for the current organization"}</span></div><div style={{display:"flex",gap:8,alignItems:"center"}}><input aria-label="Filter records" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Filter records" style={{border:"1px solid var(--line)",borderRadius:7,padding:"8px 10px",fontSize:11}}/><button className="btn" onClick={()=>void load()}>Refresh</button></div></div><DataTable rows={filteredRows} columns={tableColumns} emptyTitle={loading?"Loading…":emptyTitle} emptyText={loading?"":"No authorized records were returned for this workspace."}/></section>
    {transitionRow&&transitionStatuses&&transitionOptions.length>0&&<div className="modal-backdrop"><section className="signature-panel" role="dialog" aria-modal="true" aria-labelledby="transition-title"><span className="eyebrow">CONTROLLED TRANSITION</span><h2 id="transition-title">{title}</h2><p>Choose a server-allowed state transition. The operation is signed and audit recorded by Django.</p><form onSubmit={submitTransition}><label className="field"><span>Target state</span><select value={transitionStatus} onChange={e=>setTransitionStatus(e.target.value)} required>{transitionOptions.map(o=><option key={o.value} value={o.value}>{o.label}</option>)}</select></label><label className="field"><span>Reason / comments</span><textarea value={transitionComments} onChange={e=>setTransitionComments(e.target.value)} required/></label><label className="field"><span>Password re-authentication</span><input type="password" value={transitionPassword} onChange={e=>setTransitionPassword(e.target.value)} required/></label><div className="modal-actions"><button className="btn" type="button" onClick={()=>setTransitionRow(null)} disabled={transitionBusy}>Cancel</button><button className="btn approve" disabled={transitionBusy}>{transitionBusy?"Recording…":"Sign transition"}</button></div></form></section></div>}
  </div>;
}
