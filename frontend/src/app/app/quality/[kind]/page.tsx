"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, type ApiEnvelope } from "@/lib/api";
import { authStorage } from "@/lib/auth";

type RecordValue = Record<string, any>;

const configs: Record<string, {
  title: string;
  endpoint: string;
  description: string;
  extra?: string[];
  requiresResult?: boolean;
}> = {
  oos: {
    title: "OOS investigations",
    endpoint: "/quality/oos/",
    description: "Investigate results that fall outside approved specification.",
    extra: ["phase", "laboratory_assessment", "manufacturing_assessment", "disposition"],
    requiresResult: true,
  },
  oot: {
    title: "OOT investigations",
    endpoint: "/quality/oot/",
    description: "Investigate out-of-trend results and document the statistical assessment.",
    extra: ["trend_description", "statistical_assessment", "disposition"],
    requiresResult: true,
  },
  deviations: {
    title: "Deviations",
    endpoint: "/quality/deviations/",
    description: "Document departures from approved procedures and assess impact.",
    extra: ["detected_at", "process_area", "immediate_action", "risk_score"],
  },
  capa: {
    title: "CAPA",
    endpoint: "/quality/capa/",
    description: "Manage corrective and preventive actions and effectiveness checks.",
    extra: ["corrective_action", "preventive_action", "effectiveness_check", "effectiveness_due_at"],
  },
  "change-control": {
    title: "Change control",
    endpoint: "/quality/change-control/",
    description: "Track controlled changes, risk assessment and implementation.",
    extra: ["change_type", "current_state", "proposed_state", "risk_assessment", "implementation_plan"],
  },
};

const base = {
  reference: "",
  title: "",
  description: "",
  severity: "medium",
  due_at: "",
};

function listOf(value: any) {
  const data = value?.data ?? value;
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

export default function QualityEventWorkspace() {
  const { kind } = useParams<{ kind: string }>();
  const router = useRouter();
  const config = configs[String(kind)];

  const [rows, setRows] = useState<RecordValue[]>([]);
  const [results, setResults] = useState<RecordValue[]>([]);
  const [users, setUsers] = useState<RecordValue[]>([]);
  const [form, setForm] = useState<RecordValue>({ ...base });
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const role = String(authStorage.user?.role || authStorage.user?.organization_role || "").toLowerCase();
  const canCreate = ["admin", "qa_manager", "supervisor"].includes(role);

  const load = async () => {
    if (!config) return;
    setError("");

    try {
      const requests: Promise<any>[] = [
        api<ApiEnvelope<any>>(config.endpoint),
      ];

      if (config.requiresResult) {
        requests.push(api<ApiEnvelope<any>>("/results/"));
      }

      requests.push(api<ApiEnvelope<any>>("/auth/users/"));

      const values = await Promise.all(requests);
      setRows(listOf(values[0]));

      if (config.requiresResult) {
        setResults(listOf(values[1]));
        setUsers(listOf(values[2]));
      } else {
        setUsers(listOf(values[1]));
      }
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to load quality events.");
    }
  };

  useEffect(() => {
    void load();
  }, [kind]);

  const resultOptions = useMemo(
    () => results.map((result) => ({
      id: result.id,
      label: (result.test_name || "Result") + " · " + result.id,
    })),
    [results],
  );

  function setField(key: string, value: any) {
    setForm((current) => ({ ...current, [key]: value }));
    setError("");
  }

  async function create() {
    if (!config) return;

    if (!form.reference.trim() || !form.title.trim() || !form.description.trim()) {
      setError("Reference, title and description are required.");
      return;
    }

    if (config.requiresResult && !form.result) {
      setError("Select the result that caused the investigation.");
      return;
    }

    if (kind === "capa" && !form.corrective_action?.trim()) {
      setError("Corrective action is required for CAPA.");
      return;
    }

    if (kind === "change-control" && (!form.change_type?.trim() || !form.current_state?.trim() || !form.proposed_state?.trim() || !form.risk_assessment?.trim())) {
      setError("Change type, current state, proposed state and risk assessment are required.");
      return;
    }

    setBusy(true);
    setError("");

    const payload: RecordValue = {
      reference: form.reference.trim(),
      title: form.title.trim(),
      description: form.description.trim(),
      severity: form.severity,
    };

    if (form.due_at) payload.due_at = new Date(form.due_at).toISOString();
    if (form.owner) payload.owner = form.owner;
    if (config.requiresResult) payload.result = form.result;

    for (const key of config.extra || []) {
      if (form[key] !== undefined && form[key] !== "") payload[key] = form[key];
    }

    try {
      await api(config.endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      });

      setForm({ ...base });
      setOpen(false);
      await load();
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to create quality event.");
    } finally {
      setBusy(false);
    }
  }

  if (!config) {
    return <div className="content"><div className="inline-error">Unknown quality event type.</div></div>;
  }

  return (
    <div className="content">
      <div className="page-header">
        <div>
          <span className="eyebrow">QUALITY</span>
          <h1>{config.title}</h1>
          <p>{config.description}</p>
        </div>
        <div className="actions">
          <button className="btn" onClick={() => router.push("/app/quality")}>Back</button>
          {canCreate && <button className="btn primary" onClick={() => setOpen((value) => !value)}>{open ? "Close" : "Create"}</button>}
        </div>
      </div>

      {error && <div className="inline-error">{error}</div>}

      {open && canCreate && (
        <section className="card form-card">
          <h3>Create {config.title.slice(0, -1).toLowerCase()}</h3>
          <div className="form-grid">
            <label className="field"><span>Reference</span><input required value={form.reference} onChange={e=>setField("reference",e.target.value)} /></label>
            <label className="field"><span>Title</span><input required value={form.title} onChange={e=>setField("title",e.target.value)} /></label>
            <label className="field"><span>Severity</span><select value={form.severity} onChange={e=>setField("severity",e.target.value)}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></select></label>
            <label className="field"><span>Due date</span><input type="datetime-local" value={form.due_at} onChange={e=>setField("due_at",e.target.value)} /></label>
            <label className="field"><span>Owner</span><select value={form.owner || ""} onChange={e=>setField("owner",e.target.value)}><option value="">Unassigned</option>{users.map(user=><option key={user.id} value={user.id}>{user.full_name}</option>)}</select></label>

            {config.requiresResult && (
              <label className="field">
                <span>Related result</span>
                <select value={form.result || ""} onChange={e=>setField("result",e.target.value)} required>
                  <option value="">Select result</option>
                  {resultOptions.map(option=><option key={option.id} value={option.id}>{option.label}</option>)}
                </select>
              </label>
            )}

            <label className="field" style={{gridColumn:"1/-1"}}><span>Description</span><textarea required value={form.description} onChange={e=>setField("description",e.target.value)} /></label>

            {(config.extra || []).map((key) => (
              <label className="field" key={key} style={{gridColumn:key==="risk_assessment"||key==="corrective_action"||key==="disposition"||key==="description"?"1/-1":undefined}}>
                <span>{key.replaceAll("_"," ")}</span>
                <textarea value={form[key] || ""} onChange={e=>setField(key,e.target.value)} />
              </label>
            ))}
          </div>
          <div className="modal-actions">
            <button className="btn" onClick={()=>setOpen(false)} disabled={busy}>Cancel</button>
            <button className="btn primary" onClick={()=>void create()} disabled={busy}>{busy ? "Creating…" : "Create event"}</button>
          </div>
        </section>
      )}

      <section className="card table-card">
        <div className="card-header"><div><strong>{config.title}</strong><span>{rows.length} records returned by the backend</span></div><button className="btn" onClick={()=>void load()}>Refresh</button></div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Reference</th><th>Title</th><th>Severity</th><th>Status</th><th>Owner</th><th>Due</th></tr></thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td><b>{row.reference || row.id}</b></td>
                  <td>{row.title || "—"}</td>
                  <td>{row.severity || "—"}</td>
                  <td><span className="status active">{row.status || "—"}</span></td>
                  <td>{row.owner || "—"}</td>
                  <td>{row.due_at ? new Date(row.due_at).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!rows.length && <div className="empty">No records were returned for this workspace.</div>}
        </div>
      </section>
    </div>
  );
}
