"use client";

import { useEffect, useMemo, useState } from "react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";

type Product = {
  id: string;
  name: string;
  strength: string;
  dosage_form: string;
  description: string;
  monograph: string | null;
  monograph_name?: string | null;
  is_active: boolean;
  created_at: string;
};

type Monograph = { id: string; name: string; version: string; status: string };

const dosageForms = [
  "tablet","capsule","syrup","injection","cream","ointment",
  "gel","suppository","suspension","solution",
];

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [monographs, setMonographs] = useState<Monograph[]>([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({name:"",strength:"",dosage_form:"tablet",description:"",monograph:""});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setError("");
      const [productResponse, monographResponse] = await Promise.all([
        api<ApiEnvelope<Product[]>>(endpoints.products ?? "/products/"),
        api<ApiEnvelope<Monograph[]>>("/products/monographs/"),
      ]);
      setProducts(Array.isArray(productResponse.data) ? productResponse.data : []);
      setMonographs(Array.isArray(monographResponse.data) ? monographResponse.data : []);
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to load products.");
    }
  };

  useEffect(() => { void load(); }, []);

  const approvedMonographs = useMemo(
    () => monographs.filter((item) => item.status === "approved"),
    [monographs],
  );

  async function create() {
    if (!form.name.trim() || !form.strength.trim()) {
      setError("Product name and strength are required.");
      return;
    }

    setBusy(true);
    setError("");

    try {
      await api<ApiEnvelope<Product>>("/products/", {
        method: "POST",
        body: JSON.stringify({
          name: form.name.trim(),
          strength: form.strength.trim(),
          dosage_form: form.dosage_form,
          description: form.description.trim(),
          monograph: form.monograph || null,
        }),
      });
      setForm({name:"",strength:"",dosage_form:"tablet",description:"",monograph:""});
      setOpen(false);
      await load();
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to create product.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="content">
      <div className="page-header">
        <div>
          <span className="eyebrow">MASTER DATA</span>
          <h1>Products</h1>
          <p>Live product records from the QCSTS backend.</p>
        </div>
        <button className="btn primary" onClick={() => setOpen((value) => !value)}>
          {open ? "Close" : "Add product"}
        </button>
      </div>

      {error && <div className="inline-error">{error}</div>}

      {open && (
        <section className="card form-card">
          <h3>Create product</h3>
          <div className="form-grid">
            <label className="field"><span>Name</span><input value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required /></label>
            <label className="field"><span>Strength</span><input value={form.strength} onChange={e=>setForm({...form,strength:e.target.value})} required /></label>
            <label className="field"><span>Dosage form</span><select value={form.dosage_form} onChange={e=>setForm({...form,dosage_form:e.target.value})}>{dosageForms.map(x=><option key={x}>{x}</option>)}</select></label>
            <label className="field"><span>Approved monograph</span><select value={form.monograph} onChange={e=>setForm({...form,monograph:e.target.value})}><option value="">None</option>{approvedMonographs.map(x=><option value={x.id} key={x.id}>{x.name} · v{x.version}</option>)}</select></label>
            <label className="field" style={{gridColumn:"1/-1"}}><span>Description</span><textarea value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/></label>
          </div>
          <div className="modal-actions">
            <button className="btn" onClick={()=>setOpen(false)} disabled={busy}>Cancel</button>
            <button className="btn primary" onClick={create} disabled={busy}>{busy?"Creating…":"Create product"}</button>
          </div>
        </section>
      )}

      <section className="card table-card">
        <div className="card-header"><strong>Products</strong><span>{products.length} records</span></div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Name</th><th>Strength</th><th>Dosage</th><th>Monograph</th><th>Status</th></tr></thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td><b>{product.name}</b><div className="muted">{product.id}</div></td>
                  <td>{product.strength}</td>
                  <td>{product.dosage_form}</td>
                  <td>{product.monograph_name || product.monograph || "—"}</td>
                  <td><span className={"status " + (product.is_active ? "active" : "critical")}>{product.is_active ? "Active" : "Inactive"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
          {!products.length && <div className="empty">No product records returned by the backend.</div>}
        </div>
      </section>
    </div>
  );
}
