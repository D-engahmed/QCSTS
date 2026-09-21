"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import { ErrorBanner } from "@/components/ui/ErrorBanner";

type Study={id:string;code:string;name:string;status:string;study_type:string;start_date:string;target_end_date:string;product_name:string;site_name:string;protocol_version:string;objective:string};
type Row={id:string;[key:string]:any};

function unwrap<T>(x:any):T{return x?.data??x;}
function rows(x:any):any[]{const d=unwrap(x);return Array.isArray(d)?d:(d?.results??d?.items??[]);}

export default function StudyDetail(){
 const { id } = useParams<{ id: string }>();
 const [study,setStudy]=useState<Study|null>(null),[batches,setBatches]=useState<Row[]>([]),[timepoints,setTimepoints]=useState<Row[]>([]),[samples,setSamples]=useState<Row[]>([]),[loading,setLoading]=useState(true),[error,setError]=useState("");
 const load=async()=>{setLoading(true);setError("");try{const [s,b,t,sm]=await Promise.all([api<ApiEnvelope<Study[]>>(endpoints.studies),api<ApiEnvelope<Row[]>>(endpoints.studyBatches),api<ApiEnvelope<Row[]>>(endpoints.timePoints),api<ApiEnvelope<Row[]>>(endpoints.samples)]);const current=(unwrap<Study[]>(s)||[]).find(x=>x.id===id);setStudy(current||null);setBatches(rows(b).filter(x=>String(x.study??x.study_id)===id));setTimepoints(rows(t).filter(x=>String(x.study??x.study_id)===id));setSamples(rows(sm).filter(x=>String(x.study??x.study_id)===id));}catch(e){setError(e instanceof Error?e.message:"Unable to load study.")}finally{setLoading(false)}};
 useEffect(()=>{void load()},[id]);
 if(loading)return <div className="content"><div className="empty">Loading study…</div></div>;
 if(!study)return <div className="content"><ErrorBanner message={error||"Study not found in the authorized organization."} onRetry={load}/></div>;
 return <div className="content"><div className="breadcrumb"><Link href="/app/studies">Studies</Link><span>/</span><span>{study.code}</span></div><header className="detail-header"><div><span className="eyebrow">STABILITY STUDY</span><h1>{study.name}</h1><div className="detail-meta">{study.code} · {study.study_type} · {study.site_name||"Assigned site"}</div></div><span className="status active">{study.status}</span></header>{error&&<ErrorBanner message={error}/>}<div className="detail-grid"><section className="card detail-card"><h2>Study configuration</h2><dl><dt>Product</dt><dd>{study.product_name||"—"}</dd><dt>Protocol version</dt><dd>{study.protocol_version||"—"}</dd><dt>Start date</dt><dd>{study.start_date||"—"}</dd><dt>Target end</dt><dd>{study.target_end_date||"—"}</dd><dt>Objective</dt><dd>{study.objective||"—"}</dd></dl></section><section className="card detail-card"><h2>Execution summary</h2><div className="stats compact"><div className="stat-card"><span>Enrolled batches</span><strong>{batches.length}</strong></div><div className="stat-card"><span>Timepoints</span><strong>{timepoints.length}</strong></div><div className="stat-card"><span>Samples</span><strong>{samples.length}</strong></div></div></section></div><section className="card table-card"><div className="card-header"><div><strong>Enrolled batches</strong><span>Live study membership data</span></div><Link className="btn" href="/app/study-batches">Manage enrollment</Link></div><div className="table-wrap"><table><thead><tr><th>Batch</th><th>Status</th><th>Enrolled</th><th>Planned quantity</th></tr></thead><tbody>{batches.map(x=><tr key={x.id}><td><b>{x.batch_number||x.batch||"—"}</b></td><td>{x.status||"—"}</td><td>{x.enrolled_at||"—"}</td><td>{x.planned_quantity??"—"}</td></tr>)}</tbody></table>{!batches.length&&<div className="empty">No enrolled batches.</div>}</div></section><section className="card table-card"><div className="card-header"><div><strong>Timepoints</strong><span>Controlled schedule for this study</span></div><Link className="btn" href="/app/timepoints">Manage timepoints</Link></div><div className="table-wrap"><table><thead><tr><th>Code</th><th>Nominal days</th><th>Target date</th><th>Status</th></tr></thead><tbody>{timepoints.map(x=><tr key={x.id}><td><b>{x.code||"—"}</b></td><td>{x.nominal_days??"—"}</td><td>{x.target_date||"—"}</td><td>{x.status||"—"}</td></tr>)}</tbody></table>{!timepoints.length&&<div className="empty">No timepoints.</div>}</div></section></div>;
}
