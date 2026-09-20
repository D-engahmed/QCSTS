"use client";

import { useEffect, useState } from "react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import type { User } from "@/lib/auth";

const initialForm = { email: "", full_name: "", role: "analyst", password: "" };

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [form, setForm] = useState(initialForm);
  const [editing, setEditing] = useState<User | null>(null);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await api<ApiEnvelope<User[]>>(endpoints.users);
      setUsers(Array.isArray(response.data) ? response.data : []);
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to load organization members.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  function startCreate() {
    setEditing(null);
    setForm(initialForm);
    setOpen(true);
    setError("");
  }

  function startEdit(user: User) {
    setEditing(user);
    setForm({ email: user.email, full_name: user.full_name, role: user.organization_role || "analyst", password: "" });
    setOpen(true);
    setError("");
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");

    try {
      if (editing) {
        await api<ApiEnvelope<User>>(endpoints.users + "/" + editing.id + "/", {
          method: "PATCH",
          body: JSON.stringify({ full_name: form.full_name }),
        });
      } else {
        await api<ApiEnvelope<User>>(endpoints.users, {
          method: "POST",
          body: JSON.stringify({
            email: form.email.trim().toLowerCase(),
            full_name: form.full_name.trim(),
            role: form.role,
            password: form.password,
          }),
        });
      }

      setOpen(false);
      setEditing(null);
      setForm(initialForm);
      await load();
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to save member.");
    } finally {
      setBusy(false);
    }
  }

  async function revoke(user: User) {
    if (!window.confirm("Revoke this user's access to the organization?")) return;

    setBusy(true);
    setError("");

    try {
      await api(endpoints.users + "/" + user.id + "/", { method: "DELETE" });
      await load();
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to revoke organization access.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="content">
      <div className="page-header">
        <div>
          <span className="eyebrow">ADMINISTRATION</span>
          <h1>Users & memberships</h1>
          <p>Manage users through the real organization-scoped account API.</p>
        </div>
        <button className="btn primary" onClick={startCreate}>Add member</button>
      </div>

      {error && <div className="inline-error">{error}</div>}

      {open && (
        <section className="card form-card">
          <h3>{editing ? "Edit member" : "Create organization member"}</h3>
          <form onSubmit={submit}>
            <div className="form-grid">
              <label className="field">
                <span>Full name</span>
                <input required value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})} />
              </label>

              {!editing && (
                <>
                  <label className="field">
                    <span>Email</span>
                    <input required type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} />
                  </label>

                  <label className="field">
                    <span>Role</span>
                    <select value={form.role} onChange={e=>setForm({...form,role:e.target.value})}>
                      <option value="analyst">Analyst</option>
                      <option value="supervisor">Supervisor</option>
                      <option value="qa_manager">QA Manager</option>
                      <option value="admin">Admin</option>
                    </select>
                  </label>

                  <label className="field">
                    <span>Temporary password</span>
                    <input required minLength={12} type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} />
                    <small>Minimum 12 characters.</small>
                  </label>
                </>
              )}

              {editing && (
                <label className="field">
                  <span>Email</span>
                  <input value={form.email} readOnly />
                </label>
              )}
            </div>

            <div className="modal-actions">
              <button className="btn" type="button" onClick={()=>setOpen(false)} disabled={busy}>Cancel</button>
              <button className="btn primary" disabled={busy}>{busy ? "Saving…" : editing ? "Save changes" : "Create member"}</button>
            </div>
          </form>
        </section>
      )}

      <section className="card table-card">
        <div className="card-header">
          <div><strong>Organization members</strong><span>{users.length} records</span></div>
          <button className="btn" onClick={()=>void load()} disabled={loading}>Refresh</button>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Name</th><th>Email</th><th>Organization role</th><th>Status</th><th>Created</th><th/></tr></thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td><b>{user.full_name}</b></td>
                  <td>{user.email}</td>
                  <td>{user.organization_role || "—"}</td>
                  <td><span className={"status " + (user.is_active ? "active" : "critical")}>{user.is_active ? "Active" : "Inactive"}</span></td>
                  <td>{new Date(user.created_at).toLocaleDateString()}</td>
                  <td>
                    <div className="actions">
                      <button className="btn" onClick={()=>startEdit(user)} disabled={busy}>Edit</button>
                      {user.is_active && <button className="btn" onClick={()=>void revoke(user)} disabled={busy}>Revoke</button>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {loading && <div className="empty">Loading members…</div>}
          {!loading && !users.length && <div className="empty">No organization members returned by the backend.</div>}
        </div>
      </section>
    </div>
  );
}
