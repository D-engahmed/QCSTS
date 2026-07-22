import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CustomSelect from "../components/CustomSelect";
import { getMonographs, createMonograph, getCurrentUser } from "../services/api";

function AddMonographModal({ isOpen, onClose, onSave }) {
  const [form, setForm] = useState({ name: "", version: "", date: "", status: "Active" });
  if (!isOpen) return null;
  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const handleSubmit = () => { if (!form.name || !form.version || !form.date) { alert("Fill required fields"); return; } onSave(form); setForm({ name: "", version: "", date: "", status: "Active" }); onClose(); };
  return (
    <div className="modal-overlay open">
      <div className="modal"><div className="modal-header"><h3>📋 Add New Monograph</h3></div><div className="modal-body"><div className="form-group"><label>Monograph Name *</label><input type="text" name="name" placeholder="e.g. BP Monograph – Antibiotics" value={form.name} onChange={handleChange} className="form-control" /></div><div className="form-row" style={{ display: "flex", gap: "16px" }}><div className="form-group" style={{ flex: 1 }}><label>Version *</label><input type="text" name="version" placeholder="1.0" value={form.version} onChange={handleChange} className="form-control" /></div><div className="form-group" style={{ flex: 1 }}><label>Effective Date *</label><input type="date" name="date" value={form.date} onChange={handleChange} className="form-control" /></div></div><div className="form-group"><label>Status</label><CustomSelect options={[{ value: "Active", label: "Active" }, { value: "Inactive", label: "Inactive" }]} value={form.status} onChange={(val) => setForm({ ...form, status: val })} placeholder="Select status" /></div></div><div className="modal-footer"><button className="btn btn-primary" onClick={handleSubmit}>💾 Save</button><button className="btn btn-outline" onClick={onClose}>Cancel</button></div></div>
    </div>
  );
}

function MonographsPage() {
  const [monographs, setMonographs] = useState([]);
  const [search, setSearch] = useState("");
  const [showAddMonographModal, setShowAddMonographModal] = useState(false);
  const navigate = useNavigate();
  const user = getCurrentUser();
  const canAddMonograph = user?.role === "admin" || user?.role === "qa_manager";

  const formatDate = (dateString) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return `${String(date.getDate()).padStart(2, "0")} ${date.toLocaleDateString("en-US", { month: "short" })} ${date.getFullYear()}`;
  };

  useEffect(() => { getMonographs().then(setMonographs).catch(console.error); }, []);
  const handleAddMonographFromModal = async (formData) => {
    try {
      const created = await createMonograph({ name: formData.name, version: formData.version, effective_date: formData.date, status: formData.status === "Active" ? "draft" : "inactive" });
      setMonographs(prev => [created, ...prev]);
    } catch (err) { alert("Error creating monograph: " + err.message); }
  };
  const viewMonograph = (m) => navigate(`/monograph/${m.id}`);
  const displayStatus = (status) => {
    if (status === "approved") return { label: "Active", cls: "badge-success" };
    if (status === "inactive") return { label: "Inactive", cls: "badge-gray" };
    return { label: "Draft", cls: "badge-warning" };
  };
  const filtered = monographs.filter(m => m.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="page active">
      <div className="page-header"><h2>📋 Monographs</h2></div>
      <div className="page-body">
        <div className="filter-bar"><div className="search-inline"><span>🔍</span><input type="text" placeholder="Search monographs…" value={search} onChange={(e) => setSearch(e.target.value)} style={{ width: "330px" }} /></div>{canAddMonograph && <button className="btn btn-primary" onClick={() => setShowAddMonographModal(true)}>+ Add Monograph</button>}</div>
        <div className="card"><div className="table-wrap"><table><thead><tr><th>MONOGRAPH NAME</th><th>VERSION</th><th>EFFECTIVE DATE</th><th>STATUS</th><th># TESTS</th><th>ACTIONS</th></tr></thead><tbody>{filtered.map(m => { const { label, cls } = displayStatus(m.status); const count = Array.isArray(m.tests) ? m.tests.length : 0; return <tr key={m.id}><td><strong>{m.name}</strong></td><td className="inline-mono">{m.version}</td><td>{formatDate(m.effective_date)}</td><td><span className={`badge ${cls}`}>{label}</span></td><td><span className="badge badge-primary">{count}</span></td><td><span className="action-link" onClick={() => viewMonograph(m)}>View</span></td></tr>; })}</tbody></table></div></div>
      </div>
      <AddMonographModal isOpen={showAddMonographModal} onClose={() => setShowAddMonographModal(false)} onSave={handleAddMonographFromModal} />
    </div>
  );
}

export default MonographsPage;