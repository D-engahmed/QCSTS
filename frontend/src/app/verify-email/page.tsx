"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle2, XCircle } from "lucide-react";
import { api, endpoints } from "@/lib/api";

export default function VerifyEmail(){
 const [status,setStatus]=useState<"pending"|"success"|"error">("pending"),[message,setMessage]=useState("Verifying your email…");
 useEffect(()=>{const token=new URLSearchParams(window.location.search).get("token")||"";if(!token){setStatus("error");setMessage("Verification token is missing.");return}api(endpoints.verifyEmail,{method:"POST",body:JSON.stringify({token})}).then(()=>{setStatus("success");setMessage("Email verified successfully.")}).catch(e=>{setStatus("error");setMessage(e instanceof Error?e.message:"Verification link is invalid or expired.")})},[]);
 return <main className="auth-page"><div className="auth-card">{status==="pending"?<><span className="eyebrow">EMAIL VERIFICATION</span><h1>Verifying email</h1><p>{message}</p></>:status==="success"?<><CheckCircle2 size={28}/><span className="eyebrow">VERIFIED</span><h1>Email verified</h1><p>{message}</p><Link className="btn primary full" href="/login">Continue to sign in</Link></>:<><XCircle size={28}/><span className="eyebrow">VERIFICATION FAILED</span><h1>Link unavailable</h1><p>{message}</p><Link className="btn full" href="/login">Return to sign in</Link></>}</div></main>;
}
