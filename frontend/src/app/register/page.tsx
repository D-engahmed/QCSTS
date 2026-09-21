"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, Building2, ShieldCheck } from "lucide-react";
import { useAuth } from "@/components/AuthProvider";

const initialForm = {
  organization_name: "",
  slug: "",
  country: "EG",
  timezone: "Africa/Cairo",
  currency: "EGP",
  site_name: "Primary Site",
  site_address: "",
  full_name: "",
  email: "",
  password: "",
  confirm_password: "",
};

export default function Register() {
  const { user, register } = useAuth();
  const [form, setForm] = useState(initialForm);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (user) window.location.replace("/app");
  }, [user]);

  const update = (key: keyof typeof initialForm, value: string) => {
    setForm((current) => ({ ...current, [key]: value }));
    setError("");
  };

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (form.password !== form.confirm_password) {
      setError("Passwords do not match.");
      return;
    }

    if (form.password.length < 12) {
      setError("Password must be at least 12 characters.");
      return;
    }

    setBusy(true);

    try {
      await register({
        organization_name: form.organization_name.trim(),
        slug: form.slug.trim(),
        country: form.country.trim().toUpperCase(),
        timezone: form.timezone.trim(),
        currency: form.currency.trim().toUpperCase(),
        site_name: form.site_name.trim(),
        site_address: form.site_address.trim(),
        full_name: form.full_name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
      });

      window.location.assign("/app");
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to create the organization.");
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
        <span className="eyebrow">NEW CUSTOMER</span>
        <h1>Create your QCSTS workspace</h1>
        <p>
          Register the first organization administrator. The server creates the
          initial tenant membership atomically.
        </p>

        {error && <div className="form-error" role="alert">{error}</div>}

        <form onSubmit={submit}>
          <div className="form-section-title">
            <Building2 size={16} />
            <span>Organization</span>
          </div>

          <label className="field">
            <span>Organization name</span>
            <input
              value={form.organization_name}
              onChange={(event) => update("organization_name", event.target.value)}
              autoComplete="organization"
              required
              placeholder="Acme Pharma"
            />
          </label>

          <label className="field">
            <span>Organization slug</span>
            <input
              value={form.slug}
              onChange={(event) => update("slug", event.target.value)}
              required
              placeholder="acme-pharma"
            />
          </label>

          <div className="form-grid">
            <label className="field">
              <span>Country</span>
              <input
                value={form.country}
                onChange={(event) => update("country", event.target.value)}
                maxLength={2}
                required
              />
            </label>

            <label className="field">
              <span>Currency</span>
              <input
                value={form.currency}
                onChange={(event) => update("currency", event.target.value)}
                maxLength={3}
                required
              />
            </label>
          </div>

          <label className="field">
            <span>Timezone</span>
            <input
              value={form.timezone}
              onChange={(event) => update("timezone", event.target.value)}
              required
            />
          </label>
          <label className="field">
            <span>Primary site</span>
            <input
              value={form.site_name}
              onChange={(event) => update("site_name", event.target.value)}
              required
              placeholder="Cairo QC Laboratory"
            />
          </label>

          <label className="field">
            <span>Site address</span>
            <textarea
              value={form.site_address}
              onChange={(event) => update("site_address", event.target.value)}
              placeholder="Facility address"
            />
          </label>

          <div className="form-section-title">
            <ShieldCheck size={16} />
            <span>Administrator</span>
          </div>

          <label className="field">
            <span>Full name</span>
            <input
              value={form.full_name}
              onChange={(event) => update("full_name", event.target.value)}
              autoComplete="name"
              required
              placeholder="Ahmed Admin"
            />
          </label>

          <label className="field">
            <span>Work email</span>
            <input
              value={form.email}
              onChange={(event) => update("email", event.target.value)}
              type="email"
              autoComplete="email"
              required
              placeholder="admin@company.com"
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              value={form.password}
              onChange={(event) => update("password", event.target.value)}
              type="password"
              autoComplete="new-password"
              minLength={12}
              required
            />
          </label>

          <label className="field">
            <span>Confirm password</span>
            <input
              value={form.confirm_password}
              onChange={(event) => update("confirm_password", event.target.value)}
              type="password"
              autoComplete="new-password"
              minLength={12}
              required
            />
          </label>

          <button className="btn primary full" disabled={busy}>
            {busy ? "Creating workspace…" : "Create organization"}
            {!busy && <ArrowRight size={15} />}
          </button>
        </form>

        <div className="security-note">
          <ShieldCheck size={16} />
          <span>
            Roles and tenant membership are assigned by the backend. This form
            never grants its own permissions.
          </span>
        </div>

        <Link className="back-link" href="/login">
          Already have an account? Sign in
        </Link>
      </div>
    </main>
  );
}
