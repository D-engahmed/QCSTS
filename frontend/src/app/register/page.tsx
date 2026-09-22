"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, Building2, CheckCircle2, ShieldCheck } from "lucide-react";
import { useAuth } from "@/components/AuthProvider";
import ThemeToggle from "@/components/ThemeToggle";

const initialForm={organization_name:"",slug:"",country:"EG",timezone:"Africa/Cairo",currency:"EGP",site_name:"Primary Site",site_address:"",full_name:"",email:"",password:"",confirm_password:""};

export default function Register(){
  const {user,register}=useAuth(); const [form,setForm]=useState(initialForm); const [busy,setBusy]=useState(false); const [error,setError]=useState("");
  useEffect(()=>{if(user) window.location.replace("/app")},[user]);
  const update=(key:keyof typeof initialForm,value:string)=>{setForm(c=>({...c,[key]:value}));setError("")};
  async function submit(event:FormEvent<HTMLFormElement>){event.preventDefault();setError("");if(form.password!==form.confirm_password){setError("Passwords do not match.");return}if(form.password.length<12){setError("Password must be at least 12 characters.");return}setBusy(true);try{await register({organization_name:form.organization_name.trim(),slug:form.slug.trim(),country:form.country.trim().toUpperCase(),timezone:form.timezone.trim(),currency:form.currency.trim().toUpperCase(),site_name:form.site_name.trim(),site_address:form.site_address.trim(),full_name:form.full_name.trim(),email:form.email.trim().toLowerCase(),password:form.password});window.location.assign("/app")}catch(value){setError(value instanceof Error?value.message:"Unable to create the organization.")}finally{setBusy(false)}}
  return <main className="auth-page">
    <div className="auth-toolbar"><Link className="brand" href="/"><div className="brand-mark">Q</div><div><strong>QCSTS</strong><small>Quality & Stability</small></div></Link><ThemeToggle/></div>
    <div className="register-layout">
      <aside className="auth-side register-side"><span className="eyebrow">NEW CUSTOMER ONBOARDING</span><h2>Create a controlled QCSTS workspace.</h2><p>Your first account becomes the organization owner. QCSTS creates the organization, primary site, membership and trial subscription together.</p><div className="onboarding-steps"><span><b>01</b> Organization & site</span><span><b>02</b> Owner account</span><span><b>03</b> Secure workspace</span></div></aside>
      <div className="auth-card register-card">
        <span className="eyebrow">CREATE WORKSPACE</span><h1>Start with your organization</h1><p>Set up the first tenant administrator and primary facility. You can configure the workspace after onboarding.</p>
        {error&&<div className="form-error" role="alert">{error}</div>}
        <form onSubmit={submit}>
          <div className="form-section-title"><Building2 size={16}/><span>Organization</span></div>
          <label className="field"><span>Organization name</span><input value={form.organization_name} onChange={e=>update("organization_name",e.target.value)} autoComplete="organization" required placeholder="Acme Pharma"/></label>
          <label className="field"><span>Organization slug</span><input value={form.slug} onChange={e=>update("slug",e.target.value)} required placeholder="acme-pharma"/></label>
          <div className="form-grid"><label className="field"><span>Country</span><input value={form.country} onChange={e=>update("country",e.target.value)} maxLength={2} required/></label><label className="field"><span>Currency</span><input value={form.currency} onChange={e=>update("currency",e.target.value)} maxLength={3} required/></label></div>
          <label className="field"><span>Timezone</span><input value={form.timezone} onChange={e=>update("timezone",e.target.value)} required/></label>
          <label className="field"><span>Primary site / facility</span><input value={form.site_name} onChange={e=>update("site_name",e.target.value)} required placeholder="Cairo QC Laboratory"/></label>
          <label className="field"><span>Site address <em>Optional</em></span><textarea value={form.site_address} onChange={e=>update("site_address",e.target.value)} placeholder="Facility address"/></label>
          <div className="form-section-title"><ShieldCheck size={16}/><span>Organization owner</span></div>
          <label className="field"><span>Full name</span><input value={form.full_name} onChange={e=>update("full_name",e.target.value)} autoComplete="name" required placeholder="Ahmed Admin"/></label>
          <label className="field"><span>Work email</span><input value={form.email} onChange={e=>update("email",e.target.value)} type="email" autoComplete="email" required placeholder="admin@company.com"/></label>
          <div className="form-grid"><label className="field"><span>Password</span><input value={form.password} onChange={e=>update("password",e.target.value)} type="password" autoComplete="new-password" minLength={12} required/></label><label className="field"><span>Confirm password</span><input value={form.confirm_password} onChange={e=>update("confirm_password",e.target.value)} type="password" autoComplete="new-password" minLength={12} required/></label></div>
          <div className="onboarding-note"><CheckCircle2 size={15}/><span>Your tenant boundary and owner role are assigned by the backend.</span></div>
          <button className="btn primary full" disabled={busy}>{busy?"Creating workspace…":"Create workspace"}{!busy&&<ArrowRight size={15}/>}</button>
        </form>
        <div className="auth-switch"><span>Already have a QCSTS account?</span><Link href="/login">Sign in <ArrowRight size={14}/></Link></div>
        <Link className="back-link" href="/">← Back to QCSTS</Link>
      </div>
    </div>
  </main>;
}
