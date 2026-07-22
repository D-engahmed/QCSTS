import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CustomSelect from "../components/CustomSelect";
import { getMonographs, createProduct, createMonograph, getCurrentUser } from "../services/api";

function AddProductPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ name: "", strength: "", dosage: "", desc: "", monographId: "" });
  const [monographs, setMonographs] = useState([]);
  const [showQuickMono, setShowQuickMono] = useState(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [quickMonoForm, setQuickMonoForm] = useState({ name: "", version: "", date: "", status: "Active" });
  const user = getCurrentUser();
  const canAddProduct = user && ["admin", "qa_manager", "supervisor", "analyst"].includes(user.role);

  useEffect(() => {
    if (!canAddProduct) navigate("/products");
  }, [canAddProduct, navigate]);

  useEffect(() => { getMonographs().then(setMonographs).catch(console.error); }, []);

  const monographOptions = [{ value: "", label: "Select monograph" }, ...monographs.map(m => ({ value: m.id, label: `${m.name} (v${m.version})` })), { value: "__new__", label: "➕ Add New Monograph…" }];
  const saveQuickMonograph = async () => {
    if (!quickMonoForm.name || !quickMonoForm.version || !quickMonoForm.date) { alert("Fill all monograph fields"); return; }
    try {
      const newM = await createMonograph({ name: quickMonoForm.name, version: quickMonoForm.version, effective_date: quickMonoForm.date, status: "draft" });
      setMonographs(prev => [newM, ...prev]);
      setFormData({ ...formData, monographId: newM.id });
      setShowQuickMono(false);
      setQuickMonoForm({ name: "", version: "", date: "", status: "Active" });
    } catch (err) { alert("Error creating monograph: " + err.message); }
  };
  const saveProduct = async () => {
    if (!formData.name || !formData.strength || !formData.dosage || !formData.monographId) { alert("Fill all required fields"); return; }
    try {
      await createProduct({ name: formData.name, strength: formData.strength, dosage_form: formData.dosage.toLowerCase(), description: formData.desc, monograph: formData.monographId });
      setShowSuccessMessage(true);
      setTimeout(() => navigate("/products"), 1500);
    } catch (err) { alert("Error creating product: " + err.message); }
  };

  return (
    <div className="page active">
      <div className="page-header"><h2>💊 Add New Product</h2>{showSuccessMessage && <div style={{ backgroundColor: "#d4edda", color: "#155724", padding: "10px 30px", borderRadius: "6px", position: "fixed", bottom: "10px", right: "20px" }}>Product saved ✅</div>}<div className="page-header-actions"><span className="back-link" onClick={() => navigate("/products")}>← Back</span></div></div>
      <div className="page-body"><div className="form-card">
        <div className="form-group"><label>Product Name *</label><input type="text" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value.replace(/\b\w/g, c => c.toUpperCase()) })} /></div>
        <div className="form-row"><div className="form-group"><label>Strength *</label><input type="text" value={formData.strength} onChange={e => setFormData({ ...formData, strength: e.target.value })} /></div><div className="form-group"><label>Dosage Form *</label><CustomSelect options={[{ value: "Tablet", label: "Tablet" }, { value: "Capsule", label: "Capsule" }, { value: "Syrup", label: "Syrup" }, { value: "Injection", label: "Injection" }, { value: "Cream", label: "Cream" }, { value: "Ointment", label: "Ointment" }, { value: "Gel", label: "Gel" }, { value: "Suppository", label: "Suppository" }, { value: "Suspension", label: "Suspension" }, { value: "Solution", label: "Solution" }]} value={formData.dosage} onChange={val => setFormData({ ...formData, dosage: val })} placeholder="Select" /></div></div>
        <div className="form-group"><label>Description</label><input type="text" value={formData.desc} onChange={e => setFormData({ ...formData, desc: e.target.value })} /></div>
        <div className="form-group"><label>Assign Monograph *</label><CustomSelect options={monographOptions} value={formData.monographId} onChange={val => { if (val === "__new__") setShowQuickMono(true); else { setShowQuickMono(false); setFormData({ ...formData, monographId: val }); } }} placeholder="Select Monograph" /></div>
        {showQuickMono && (<div className="mono-quick-add"><h5>➕ New Monograph</h5><div className="form-row"><div className="form-group"><label>Monograph Name *</label><input type="text" value={quickMonoForm.name} onChange={e => setQuickMonoForm({ ...quickMonoForm, name: e.target.value })} /></div><div className="form-group"><label>Version *</label><input type="text" value={quickMonoForm.version} onChange={e => setQuickMonoForm({ ...quickMonoForm, version: e.target.value })} /></div></div><div className="form-row"><div className="form-group"><label>Effective Date *</label><input type="date" value={quickMonoForm.date} onChange={e => setQuickMonoForm({ ...quickMonoForm, date: e.target.value })} /></div></div><div className="form-row"><button className="btn btn-accent btn-sm" onClick={saveQuickMonograph}>💾 Save & Select Monograph</button><button className="btn btn-outline btn-sm" onClick={() => setShowQuickMono(false)}>Cancel</button></div></div>)}
        <div className="form-actions"><button className="btn btn-primary" onClick={saveProduct}>💾 Save Product</button><button className="btn btn-outline" onClick={() => navigate("/products")}>Cancel</button></div>
      </div></div>
    </div>
  );
}

export default AddProductPage;