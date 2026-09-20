"use client";

import { useEffect, useState } from "react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";

type Audit = {
  id: string;
  action: string;
  model_name: string;
  object_id: string;
  object_repr: string;
  performed_by_name?: string;
  timestamp: string;
  notes?: string;
};

export default function AuditPage() {
  const [rows, setRows] = useState<Audit[]>([]);
  const [filters, setFilters] = useState({ model_name: "", action: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await api<ApiEnvelope<Audit[]>>(endpoints.audit + "?" + new URLSearchParams(
        Object.entries(filters).filter(([, value]) => Boolean(value)),
      ).toString());
      const value = response.data;
      setRows(Array.isArray(value) ? value : []);
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to load the audit trail.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, [filters.model_name, filters.action]);

  return (
    <div className="content">
      <div className="page-header">
        <div>
          <span className="eyebrow">AUDIT & COMPLIANCE</span>
          <h1>Audit trail</h1>
          <p>Immutable tenant-scoped activity recorded by the QCSTS backend.</p>
        </div>
        <button className="btn" onClick={() => void load()} disabled={loading}>
          {loading ? "Loading…" : "Refresh"}
        </button>
      </div>

      {error && <div className="inline-error">{error}</div>}

      <section className="card">
        <div className="form-grid">
          <label className="field">
            <span>Model</span>
            <input value={filters.model_name} onChange={(event) => setFilters({ ...filters, model_name: event.target.value })} placeholder="Batch, TestResult, Product…" />
          </label>
          <label className="field">
            <span>Action</span>
            <select value={filters.action} onChange={(event) => setFilters({ ...filters, action: event.target.value })}>
              <option value="">All actions</option>
              <option value="CREATE">CREATE</option>
              <option value="UPDATE">UPDATE</option>
              <option value="APPROVE">APPROVE</option>
              <option value="DELETE">DELETE</option>
              <option value="LOGIN">LOGIN</option>
              <option value="SIGN">SIGN</option>
            </select>
          </label>
        </div>
      </section>

      <section className="card table-card">
        <div className="card-header"><div><strong>Activity</strong><span>{rows.length} records</span></div></div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Timestamp</th><th>Action</th><th>Model</th><th>Object</th><th>Performed by</th><th>Notes</th></tr></thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td>{new Date(row.timestamp).toLocaleString()}</td>
                  <td><span className="status active">{row.action}</span></td>
                  <td>{row.model_name}</td>
                  <td><b>{row.object_repr || row.object_id}</b></td>
                  <td>{row.performed_by_name || "System"}</td>
                  <td>{row.notes || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!rows.length && !loading && <div className="empty">No audit records returned for the selected filters.</div>}
          {loading && <div className="empty">Loading audit records…</div>}
        </div>
      </section>
    </div>
  );
}
