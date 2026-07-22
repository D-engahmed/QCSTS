  import React, { useState, useEffect } from "react";
  import { useParams, useNavigate } from "react-router-dom";
  import { getMonograph, getMonographTests, addMonographTest, approveMonograph, getCurrentUser } from "../services/api";

  function AddTestModal({ isOpen, onClose, onSave }) {
    const [form, setForm] = useState({ name: "", spec: "", method: "" });
    if (!isOpen) return null;
    const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
    const handleSubmit = () => { if (!form.name || !form.spec) { alert("Fill required fields"); return; } onSave(form); setForm({ name: "", spec: "", method: "" }); onClose(); };
    return (
      <div className="modal-overlay open">
        <div className="modal"><h3>🧬 Add Test to Monograph</h3><div className="form-group"><label>Test Name *</label><input type="text" name="name" placeholder="e.g. Assay, pH, Dissolution" value={form.name} onChange={handleChange} /></div><div className="form-group"><label>Specification *</label><input type="text" name="spec" placeholder="e.g. 90.0 – 110.0%, NLT 80%" value={form.spec} onChange={handleChange} /></div><div className="form-group"><label>Method Reference</label><input type="text" name="method" placeholder="e.g. BP 2023, USP <711>" value={form.method} onChange={handleChange} /></div><div className="form-actions"><button className="btn btn-primary" onClick={handleSubmit}>💾 Add Test</button><button className="btn btn-outline" onClick={onClose}>Cancel</button></div></div>
      </div>
    );
  }

  function MonographDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [currentMonograph, setCurrentMonograph] = useState(null);
    const [tests, setTests] = useState([]);
    const [showAddTestModal, setShowAddTestModal] = useState(false);
    const [loading, setLoading] = useState(true);
    const user = getCurrentUser();
    const isQAManager = user?.role === "qa_manager" || user?.role === "admin";

    useEffect(() => {
      const load = async () => {
        try {
          setLoading(true);
          const [mono, testList] = await Promise.all([getMonograph(id), getMonographTests(id)]);
          setCurrentMonograph(mono);
          setTests(testList || []);
        } catch (err) { console.error(err); } finally { setLoading(false); }
      };
      load();
    }, [id]);

    const handleAddTestFromModal = async (testData) => {
      try {
        const newTest = await addMonographTest(id, { name: testData.name, specification: testData.spec, method: testData.method, unit: "", sequence: tests.length + 1 });
        setTests(prev => [...prev, newTest]);
      } catch (err) { alert("Error adding test: " + err.message); }
    };
    const handleApprove = async () => {
      if (!window.confirm("Approve this monograph? It will be locked from further edits.")) return;
      try {
        const updated = await approveMonograph(id);
        setCurrentMonograph(updated);
        alert("Monograph approved ✅");
      } catch (err) { alert("Error: " + err.message); }
    };

    if (loading) return <div className="page active"><div className="page-header"><h2>Loading...</h2></div></div>;
    if (!currentMonograph) return <div className="page active"><div className="page-header"><h2>Monograph not found</h2></div></div>;

    const statusLabel = currentMonograph.status === "approved" ? "Active" : currentMonograph.status === "draft" ? "Draft" : "Inactive";
    const statusCls = currentMonograph.status === "approved" ? "badge-success" : currentMonograph.status === "draft" ? "badge-warning" : "badge-gray";
    const isLocked = currentMonograph.status === "approved";

    return (
      <div className="page active">
        <div className="page-header"><h2>📋 Monograph Detail</h2><span className="back-link" onClick={() => navigate("/monographs")}>← Back</span></div>
        <div className="page-body">
          <div className="detail-header"><div className="detail-header-info"><h3>{currentMonograph.name}</h3><p>Version {currentMonograph.version} · {currentMonograph.effective_date}</p></div><div style={{ display: "flex", gap: "10px", alignItems: "center" }}><span className={`badge ${statusCls}`}>{statusLabel}</span>{isQAManager && !isLocked && <button className="btn btn-primary btn-sm" onClick={handleApprove}>✅ Approve</button>}</div></div>
          <div className="info-grid"><div className="info-item"><label>Version</label><span>{currentMonograph.version}</span></div><div className="info-item"><label>Date</label><span>{currentMonograph.effective_date}</span></div><div className="info-item"><label>Status</label><span>{statusLabel}</span></div><div className="info-item"><label>Total Tests</label><span>{tests.length}</span></div></div>
          <div className="card"><div className="card-header"><h3>🧬 Test Items</h3>{!isLocked && <button className="btn btn-primary btn-sm" onClick={() => setShowAddTestModal(true)}>+ Add Test</button>}{isLocked && <span className="text-muted" style={{ fontSize: "12px" }}>🔒 Locked — monograph is approved</span>}</div><div className="table-wrap"><table><thead><tr><th>Seq</th><th>Name</th><th>Spec</th><th>Method</th></tr></thead><tbody>{tests.map(t => <tr key={t.id}><td>{t.sequence}</td><td>{t.name}</td><td>{t.specification}</td><td style={{ color: "var(--gray-500)" }}>{t.method}</td></tr>)}</tbody></table></div></div>
        </div>
        <AddTestModal isOpen={showAddTestModal} onClose={() => setShowAddTestModal(false)} onSave={handleAddTestFromModal} />
      </div>
    );
  }

  export default MonographDetailPage;