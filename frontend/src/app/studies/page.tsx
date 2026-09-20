"use client";

import { useEffect, useMemo, useState } from "react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";
import { DataWorkspace, Row } from "@/components/DataWorkspace";
import { ErrorBanner } from "@/components/ui/ErrorBanner";

type Study = { id: string; code: string; name: string; status: string; study_type: string; start_date?: string | null; target_end_date?: string | null };
type ProtocolVersion = { id: string; version: string; status: string };
type Product = { id: string; name: string; strength: string };

function CreateStudyForm({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const { sites } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [versions, setVersions] = useState<ProtocolVersion[]>([]);
  const [form, setForm] = useState({ code: "", name: "", site: sites[0]?.id ?? "", product: "", protocol_version: "", study_type: "long_term", start_date: "", target_end_date: "", objective: "" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([api<ApiEnvelope<Product[]>>(endpoints.products), api<ApiEnvelope<ProtocolVersion[]>>(endpoints.protocolVersions)])
      .then(([p, v]) => { setProducts(p.data ?? []); setVersions((v.data ?? []).filter((x) => x.status === "effective")); })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!form.product && products[0]) setForm((x) => ({ ...x, product: products[0].id }));
    if (!form.protocol_version && versions[0]) setForm((x) => ({ ...x, protocol_version: versions[0].id }));
  }, [products, versions, form.product, form.protocol_version]);

  async function submit(e: React.FormEvent) {
    e.preventDefault(); setSaving(true); setError("");
    try {
      await api(endpoints.studies, { method: "POST", body: JSON.stringify({ ...form, start_date: form.start_date || null, target_end_date: form.target_end_date || null }) });
      onCreated(); onClose();
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to create study."); }
    finally { setSaving(false); }
  }

  return <div className="modal-backdrop"><section className="modal">
    <div className="card-header"><strong>Create stability study</strong><button className="btn" onClick={onClose}>Close</button></div>
    {error && <ErrorBanner message={error} onRetry={() => setError("")} />}
    <form className="form-grid" onSubmit={submit}>
      <label className="field"><span>Study code</span><input required value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} /></label>
      <label className="field"><span>Name</span><input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
      <label className="field"><span>Site</span><select required value={form.site} onChange={(e) => setForm({ ...form, site: e.target.value })}>{sites.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}</select></label>
      <label className="field"><span>Product</span><select required value={form.product} onChange={(e) => setForm({ ...form, product: e.target.value })}>{products.map((p) => <option key={p.id} value={p.id}>{p.name} {p.strength}</option>)}</select></label>
      <label className="field"><span>Effective protocol version</span><select required value={form.protocol_version} onChange={(e) => setForm({ ...form, protocol_version: e.target.value })}>{versions.map((v) => <option key={v.id} value={v.id}>{v.version}</option>)}</select></label>
      <label className="field"><span>Study type</span><select value={form.study_type} onChange={(e) => setForm({ ...form, study_type: e.target.value })}><option value="long_term">Long-term</option><option value="accelerated">Accelerated</option><option value="photostability">Photostability</option></select></label>
      <label className="field"><span>Start date</span><input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} /></label>
      <label className="field"><span>Target end date</span><input type="date" value={form.target_end_date} onChange={(e) => setForm({ ...form, target_end_date: e.target.value })} /></label>
      <label className="field" style={{ gridColumn: "1 / -1" }}><span>Objective</span><textarea value={form.objective} onChange={(e) => setForm({ ...form, objective: e.target.value })} /></label>
      <div className="actions" style={{ gridColumn: "1 / -1" }}><button type="button" className="btn" onClick={onClose}>Cancel</button><button className="btn primary" disabled={saving}>{saving ? "Creating..." : "Create study"}</button></div>
    </form>
  </section></div>;
}

export default function Studies() {
  const [studies, setStudies] = useState<Study[]>([]); const [error, setError] = useState(""); const [open, setOpen] = useState(false);
  const load = () => api<ApiEnvelope<Study[]>>(endpoints.studies).then((r) => setStudies(r.data ?? [])).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);
  const rows = useMemo<Row[]>(() => studies.map((s) => ({ id: s.code, name: s.name, meta: [s.study_type, s.start_date ?? "No start date", s.target_end_date ? "End " + s.target_end_date : "No target end"].join(" · "), status: s.status.replaceAll("_", " "), tone: s.status === "active" ? "active" : s.status === "canceled" ? "critical" : "warning", extra: s.id })), [studies]);
  return <><div>{error && <div className="content"><ErrorBanner message={error} onRetry={() => { setError(""); load(); }} /></div>}</div><DataWorkspace title="Stability Studies" description="Manage controlled stability programs, protocols, batches, samples and review milestones." rows={rows} createLabel="New study" onCreate={() => setOpen(true)} detailHref={(id) => "/studies/" + id} />{open && <CreateStudyForm onClose={() => setOpen(false)} onCreated={load} />}</>;
}