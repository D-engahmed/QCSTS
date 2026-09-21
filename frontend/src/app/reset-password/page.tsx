"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { api, endpoints } from "@/lib/api";

export default function ResetPassword(){
 const [uid,setUid]=useState(""),[token,setToken]=useState(""),[password,setPassword]=useState(""),[confirm,setConfirm]=useState(""),[busy,setBusy]=useState(false),[done,setDone]=useState(false),[error,setError]=useState("");
 useEffect(()=>{const q=new URLSearchParams(window.location.search);setUid(q.get("uid")||"");setToken(q.get("token")||"")},[]);
 async function submit(e:FormEvent){e.preventDefault();setError("");if(password!==confirm){setError("Passwords do not match.");return}setBusy(true);try{await api(endpoints.passwordResetConfirm,{method:"POST",body:JSON.stringify({uid,token,new_password:password})});setDone(true)}catch(x){setError(x instanceof Error?x.message:"Unable to reset password.")}finally{setBusy(false)}}
 return <main className="auth-page"><div className="auth-card"><span className="eyebrow">ACCOUNT RECOVERY</span><h1>Create a new password</h1><p>Use at least 12 characters. The reset token is single-use and expires automatically.</p>{error&&<div className="form-error" role="alert">{error}</div>}{done?<div className="form-success"><ShieldCheck size={16}/><span>Password changed successfully. Sign in with the new credential.</span></div>:<form onSubmit={submit}><label className="field"><span>New password</span><input required minLength={12} type="password" autoComplete="new-password" value={password} onChange={e=>setPassword(e.target.value)}/></label><label className="field"><span>Confirm password</span><input required minLength={12} type="password" autoComplete="new-password" value={confirm} onChange={e=>setConfirm(e.target.value)}/></label><button className="btn primary full" disabled={busy||!uid||!token}>{busy?"Updating…":"Set new password"}{!busy&&<ArrowRight size={15}/>}</button></form>}<div className="auth-alt"><Link href="/login">← Back to sign in</Link></div></div></main>;
}
