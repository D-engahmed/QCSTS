 "use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { useAuth } from "@/components/AuthProvider";

export default function Login() {
  const { user, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [needsOtp, setNeedsOtp] = useState(false);
  const [otp, setOtp] = useState("");

  useEffect(() => {
    if (user) window.location.replace("/app");
  }, [user]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");

    try {
      await login(email.trim(), password, needsOtp ? otp : undefined);
      window.location.assign("/app");
    } catch (value) {
      const message = value instanceof Error ? value.message : "Unable to sign in.";
      if (message.toLowerCase().includes("mfa code is required")) setNeedsOtp(true);
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-brand">
        <Link className="brand" href="/">
          <div className="brand-mark">Q</div>
          <div>
            <strong>QCSTS</strong>
            <small>Quality & Stability</small>
          </div>
        </Link>
      </div>

      <div className="auth-card">
        <span className="eyebrow">SECURE WORKSPACE</span>
        <h1>Sign in to QCSTS</h1>
        <p>Use your organization account to access controlled quality and stability workflows.</p>

        {error && <div className="form-error" role="alert">{error}</div>}

        <form onSubmit={submit}>
          <label className="field">
            <span>Work email</span>
            <input
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              autoComplete="username"
              required
              placeholder="name@company.com"
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              autoComplete="current-password"
              required
            />
          </label>

          <div className="auth-alt" style={{ justifyContent: "flex-end", marginTop: -6 }}>
            <Link href="/forgot-password">Forgot password?</Link>
          </div>

          {needsOtp && (
            <label className="field">
              <span>Authenticator code</span>
              <input
                value={otp}
                onChange={(event) => setOtp(event.target.value)}
                inputMode="numeric"
                pattern="\d{6}"
                maxLength={6}
                autoComplete="one-time-code"
                required
                placeholder="123456"
              />
              <small>Enter the current 6-digit code from your authenticator app.</small>
            </label>
          )}

          <button className="btn primary full" disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
            {!busy && <ArrowRight size={15} />}
          </button>
        </form>

        <div className="security-note">
          <ShieldCheck size={16} />
          <span>Authentication and tenant authorization are controlled server-side.</span>
        </div>

        <div className="auth-alt">
          <span>New pharmaceutical organization?</span>
          <Link href="/register">Create your workspace</Link>
        </div>

        <Link className="back-link" href="/">
          ← Back to QCSTS
        </Link>
      </div>
    </main>
  );
}
