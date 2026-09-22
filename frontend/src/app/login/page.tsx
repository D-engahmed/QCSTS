"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, ShieldCheck, Building2 } from "lucide-react";
import { useAuth } from "@/components/AuthProvider";
import ThemeToggle from "@/components/ThemeToggle";

export default function Login() {
  const { user, login } = useAuth();
  const [email, setEmail] = useState(""); const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  const [needsOtp, setNeedsOtp] = useState(false); const [otp, setOtp] = useState("");

  useEffect(() => { if (user) window.location.replace("/app"); }, [user]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    try { await login(email.trim(), password, needsOtp ? otp : undefined); window.location.assign("/app"); }
    catch (value) { const message = value instanceof Error ? value.message : "Unable to sign in."; if (message.toLowerCase().includes("mfa code is required")) setNeedsOtp(true); setError(message); }
    finally { setBusy(false); }
  }

  return <main className="auth-page">
    <div className="auth-toolbar"><Link className="brand" href="/"><div className="brand-mark">Q</div><div><strong>QCSTS</strong><small>Quality & Stability</small></div></Link><ThemeToggle /></div>
    <div className="auth-layout">
      <aside className="auth-side"><span className="eyebrow">QCSTS WORKSPACE</span><h2>Continue where controlled quality work happens.</h2><p>Access your organization, assigned site and authorized quality workflows from one secure workspace.</p><div className="auth-side-list"><span><ShieldCheck size={16}/> Server-enforced tenant isolation</span><span><Building2 size={16}/> Organization and site context</span><span><ArrowRight size={16}/> Controlled workflow navigation</span></div></aside>
      <div className="auth-card">
        <span className="eyebrow">EXISTING CUSTOMER</span><h1>Sign in</h1><p>Use your QCSTS work account to access your organization workspace.</p>
        {error && <div className="form-error" role="alert">{error}</div>}
        <form onSubmit={submit}>
          <label className="field"><span>Work email</span><input value={email} onChange={e=>setEmail(e.target.value)} type="email" autoComplete="username" required placeholder="name@company.com"/></label>
          <label className="field"><span>Password</span><input value={password} onChange={e=>setPassword(e.target.value)} type="password" autoComplete="current-password" required/></label>
          <div className="auth-alt" style={{justifyContent:"flex-end",marginTop:-6}}><Link href="/forgot-password">Forgot password?</Link></div>
          {needsOtp && <label className="field"><span>Authenticator code</span><input value={otp} onChange={e=>setOtp(e.target.value)} inputMode="numeric" pattern="\d{6}" maxLength={6} autoComplete="one-time-code" required placeholder="123456"/><small>Enter the current 6-digit code from your authenticator app.</small></label>}
          <button className="btn primary full" disabled={busy}>{busy ? "Signing in…" : "Sign in"}{!busy && <ArrowRight size={15}/>}</button>
        </form>
        <div className="auth-switch"><span>New pharmaceutical organization?</span><Link href="/register">Create a new workspace <ArrowRight size={14}/></Link></div>
        <div className="security-note"><ShieldCheck size={16}/><span>Authentication and tenant authorization are controlled server-side.</span></div>
        <Link className="back-link" href="/">← Back to QCSTS</Link>
      </div>
    </div>
  </main>;
}
