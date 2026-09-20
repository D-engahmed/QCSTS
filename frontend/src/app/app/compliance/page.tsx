"use client";

import { useEffect, useState } from "react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";

type Signature = {
  id: string;
  record_type?: string;
  record_id?: string;
  record_version?: string;
  meaning?: string;
  reason?: string;
  signer?: string;
  signed_at?: string;
  signature_digest?: string;
};

type ControlledRecord = {
  id: string;
  record_type?: string;
  record_id?: string;
  version?: number;
  status?: string;
  locked_at?: string | null;
  locked_by?: string | null;
  approved_at?: string | null;
  approved_by?: string | null;
};

type ValidationArtifact = {
  id: string;
  artifact_type?: string;
  version?: string;
  title?: string;
  content_hash?: string;
  approved?: boolean;
  approved_at?: string | null;
  approved_by?: string | null;
};

function listOf<T>(value: unknown): T[] {
  if (Array.isArray(value)) return value as T[];
  if (value && typeof value === "object") {
    const data = (value as { data?: unknown }).data;
    if (Array.isArray(data)) return data as T[];
    const results = (value as { results?: unknown }).results;
    if (Array.isArray(results)) return results as T[];
  }
  return [];
}

export default function CompliancePage() {
  const [signatures, setSignatures] = useState<Signature[]>([]);
  const [records, setRecords] = useState<ControlledRecord[]>([]);
  const [artifacts, setArtifacts] = useState<ValidationArtifact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");

    try {
      const [signatureResponse, recordResponse, artifactResponse] = await Promise.all([
        api<ApiEnvelope<Signature[]>>("/compliance/signatures/"),
        api<ApiEnvelope<ControlledRecord[]>>("/compliance/records/"),
        api<ApiEnvelope<ValidationArtifact[]>>("/compliance/validation/"),
      ]);

      setSignatures(listOf<Signature>(signatureResponse));
      setRecords(listOf<ControlledRecord>(recordResponse));
      setArtifacts(listOf<ValidationArtifact>(artifactResponse));
    } catch (value) {
      setError(
        value instanceof Error
          ? value.message
          : "Unable to load compliance records.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="content">
      <div className="page-header">
        <div>
          <span className="eyebrow">COMPLIANCE</span>
          <h1>Compliance records</h1>
          <p>
            Live controlled records, electronic signatures and validation artifacts
            returned by the QCSTS compliance API.
          </p>
        </div>
        <button className="btn" onClick={() => void load()} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {error && <div className="inline-error">{error}</div>}

      <div className="stats three">
        <div className="stat-card">
          <span>Electronic signatures</span>
          <strong>{signatures.length}</strong>
          <small>Immutable server records</small>
        </div>
        <div className="stat-card">
          <span>Controlled records</span>
          <strong>{records.length}</strong>
          <small>Workflow-controlled records</small>
        </div>
        <div className="stat-card">
          <span>Validation artifacts</span>
          <strong>{artifacts.length}</strong>
          <small>Versioned evidence</small>
        </div>
      </div>

      <section className="card table-card">
        <div className="card-header">
          <div>
            <strong>Electronic signatures</strong>
            <span>Server-issued and immutable</span>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Meaning</th>
                <th>Record</th>
                <th>Version</th>
                <th>Reason</th>
                <th>Signed at</th>
              </tr>
            </thead>
            <tbody>
              {signatures.map((signature) => (
                <tr key={signature.id}>
                  <td><b>{signature.meaning || "—"}</b></td>
                  <td>{signature.record_type || "—"} · {signature.record_id || "—"}</td>
                  <td>{signature.record_version || "—"}</td>
                  <td>{signature.reason || "—"}</td>
                  <td>{signature.signed_at ? new Date(signature.signed_at).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!signatures.length && !loading && (
            <div className="empty">No electronic signatures were returned.</div>
          )}
        </div>
      </section>

      <section className="card table-card">
        <div className="card-header">
          <div>
            <strong>Controlled records</strong>
            <span>Approval and locking state is owned by the backend</span>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Record</th>
                <th>Version</th>
                <th>Status</th>
                <th>Approved</th>
                <th>Locked</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record.id}>
                  <td><b>{record.record_type || "—"}</b><div className="muted">{record.record_id || record.id}</div></td>
                  <td>{record.version ?? "—"}</td>
                  <td><span className="status active">{record.status || "—"}</span></td>
                  <td>{record.approved_at ? new Date(record.approved_at).toLocaleString() : "—"}</td>
                  <td>{record.locked_at ? new Date(record.locked_at).toLocaleString() : "Not locked"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!records.length && !loading && (
            <div className="empty">No controlled records were returned.</div>
          )}
        </div>
      </section>

      <section className="card table-card">
        <div className="card-header">
          <div>
            <strong>Validation artifacts</strong>
            <span>Versioned validation evidence</span>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Title</th>
                <th>Version</th>
                <th>Approved</th>
                <th>Content hash</th>
              </tr>
            </thead>
            <tbody>
              {artifacts.map((artifact) => (
                <tr key={artifact.id}>
                  <td><b>{artifact.artifact_type || "—"}</b></td>
                  <td>{artifact.title || "—"}</td>
                  <td>{artifact.version || "—"}</td>
                  <td><span className={"status " + (artifact.approved ? "active" : "warning")}>{artifact.approved ? "Approved" : "Draft"}</span></td>
                  <td className="muted">{artifact.content_hash || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!artifacts.length && !loading && (
            <div className="empty">No validation artifacts were returned.</div>
          )}
        </div>
      </section>
    </div>
  );
}
