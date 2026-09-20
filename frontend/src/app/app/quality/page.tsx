"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";

type EventRecord = {
  id: string;
  reference?: string;
  title?: string;
  status?: string;
  severity?: string;
  due_at?: string | null;
  owner?: string | null;
  result?: string | null;
};

const resources = [
  ["OOS investigations", "oos", endpoints.oos],
  ["OOT investigations", "oot", endpoints.oot],
  ["Deviations", "deviations", endpoints.deviations],
  ["CAPA", "capa", endpoints.capa],
] as const;

function rowsOf(data: unknown): EventRecord[] {
  const value = (data as ApiEnvelope<EventRecord[]> | undefined)?.data ?? data;
  if (Array.isArray(value)) return value;
  if (value && typeof value === "object" && Array.isArray((value as { results?: EventRecord[] }).results)) {
    return (value as { results: EventRecord[] }).results;
  }
  return [];
}

export default function QualityPage() {
  const [data, setData] = useState<Record<string, EventRecord[]>>({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    setError("");

    try {
      const entries = await Promise.all(
        resources.map(async ([, key, endpoint]) => {
          const response = await api<ApiEnvelope<EventRecord[]>>(endpoint);
          return [key, rowsOf(response)] as const;
        }),
      );

      setData(Object.fromEntries(entries));
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to load quality events.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  return (
    <div className="content">
      <div className="page-header">
        <div>
          <span className="eyebrow">QUALITY</span>
          <h1>Quality events</h1>
          <p>Live OOS, OOT, deviation and CAPA records from the QCSTS backend.</p>
        </div>
        <button className="btn" onClick={() => void load()} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {error && <div className="inline-error">{error}</div>}

      <div className="stats four">
        {resources.map(([label, key]) => (
          <div className="stat-card" key={key}>
            <span>{label}</span>
            <strong>{data[key]?.length ?? (loading ? "—" : 0)}</strong>
            <small>Returned by API</small>
          </div>
        ))}
      </div>

      {resources.map(([label, key]) => (
        <section className="card table-card" key={key}>
          <div className="card-header">
            <div><strong>{label}</strong><span>{data[key]?.length ?? 0} records</span></div>
            <Link className="btn" href={"/app/quality/" + key}>Open queue</Link>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Reference</th><th>Title</th><th>Severity</th><th>Status</th><th>Due</th></tr></thead>
              <tbody>
                {(data[key] || []).slice(0, 10).map((item) => (
                  <tr key={item.id}>
                    <td><b>{item.reference || item.id}</b></td>
                    <td>{item.title || "—"}</td>
                    <td>{item.severity || "—"}</td>
                    <td><span className="status active">{item.status || "—"}</span></td>
                    <td>{item.due_at ? new Date(item.due_at).toLocaleString() : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!data[key]?.length && !loading && <div className="empty">No records returned by the backend.</div>}
          </div>
        </section>
      ))}

      <section className="card table-card">
        <div className="card-header"><div><strong>Change control</strong><span>Controlled change requests are available from the backend API.</span></div><Link className="btn" href="/app/change-control">Open</Link></div>
      </section>
    </div>
  );
}
