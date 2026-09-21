"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { ArrowRight, Mail } from "lucide-react";
import { api, endpoints } from "@/lib/api";

export default function ForgotPassword() {
  const [email,setEmail]=useState(""),[busy,setBusy]=useState(false),[done,setDone]=useState(false),[error,setError]=useState("");
  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault();setBusy(true);setError("");
    try{await api(endpoints.passwordReset,{method:"POST",body:JSON.stringify({email:email.trim()})});setDone(true);}
    catch(e){setError(e instanceof Error?e.message:"Unable to start password recovery.");}
    finally{setBusy(false);}
  }
  return <main className="auth-page"><div className="auth-card"><span className="eyebrow">ACCOUNT RECOVERY</span><h1>Reset your password</h1><p>Enter your work email. QCSTS returns the same response whether or not the account exists.</p>{error&&<div className="form-error" role="alert">{error}</div>}{done?<div className="form-success"><Mail size={16}/><span>Recovery instructions have been sent when an active account matches that address.</span></div>:<form onSubmit={submit}><label className="field"><span>Work email</span><input required type="email" autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="name@company.com"/></label><button className="btn primary full" disabled={busy}>{busy?"Sending…":"Send recovery link"}{!busy&&<ArrowRight size={15}/>}</button></form>}<div className="auth-alt"><Link href="/login">← Back to sign in</Link></div></div></main>;
}
