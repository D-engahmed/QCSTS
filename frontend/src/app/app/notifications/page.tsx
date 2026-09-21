"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Bell, CheckCheck } from "lucide-react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import { ErrorBanner } from "@/components/ui/ErrorBanner";

type Notification = {
  id:string; kind:string; severity:string; title:string; body:string;
  action_url:string; read_at:string|null; created_at:string;
};

function unwrap<T>(x:any):T { return x?.data ?? x; }

export default function NotificationsPage() {
  const [items,setItems]=useState<Notification[]>([]);
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);

  async function load(){
    setError("");
    try{
      const response=await api<ApiEnvelope<Notification[]>>(endpoints.notifications);
      setItems(unwrap<Notification[]>(response) ?? []);
    }catch(e){ setError(e instanceof Error ? e.message : "Unable to load notifications."); }
  }
  useEffect(()=>{void load()},[]);

  async function markRead(id:string){
    try{await api(endpoints.notificationRead(id),{method:"POST"});setItems(v=>v.map(n=>n.id===id?{...n,read_at:new Date().toISOString()}:n));}
    catch(e){setError(e instanceof Error?e.message:"Unable to mark notification read.");}
  }

  async function markAll(){
    setBusy(true);
    try{await api(endpoints.notificationsReadAll,{method:"POST"});setItems(v=>v.map(n=>({...n,read_at:n.read_at||new Date().toISOString()})));}
    catch(e){setError(e instanceof Error?e.message:"Unable to mark notifications read.");}
    finally{setBusy(false);}
  }

  return <div className="content">
    <div className="page-header">
      <div><span className="eyebrow">NOTIFICATIONS</span><h1>Notifications</h1><p>Tenant-scoped operational alerts, approvals and quality reminders.</p></div>
      <button className="btn" onClick={()=>void markAll()} disabled={busy}><CheckCheck size={15}/>{busy?"Updating…":"Mark all read"}</button>
    </div>
    {error&&<ErrorBanner message={error} onRetry={load}/>}
    <section className="card table-card">
      {!items.length?<div className="empty"><Bell size={20}/><strong>No notifications</strong><span>Operational alerts will appear here.</span></div>:
      <div className="notification-list">{items.map(item=><div className={"notification-item "+(!item.read_at?"unread":"")} key={item.id}>
        <div className="notification-icon"><Bell size={16}/></div>
        <div className="notification-content"><div className="notification-title"><strong>{item.title}</strong><span className={"status "+item.severity}>{item.severity}</span></div><p>{item.body}</p><small>{new Date(item.created_at).toLocaleString()}</small></div>
        <div className="notification-actions">{item.action_url&&<Link className="btn" href={item.action_url}>Open</Link>}{!item.read_at&&<button className="btn" onClick={()=>void markRead(item.id)}>Mark read</button>}</div>
      </div>)}</div>}
    </section>
  </div>;
}
