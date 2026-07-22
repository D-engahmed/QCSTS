import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getProducts, createBatch } from "../services/api";
import CustomSelect from "../components/CustomSelect";

function AddBatchPage() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({
    productId: "", batchNo: "", mfgDate: "", incubationDate: "",
    expiry: "", studyType: "Long Study",
    shelf: "", rack: "", position: "", qty: "",
  });
  const [preview, setPreview] = useState([]);

  const LONG_MONTHS = [0, 3, 6, 9, 12, 18, 24, 36];
  const ACCEL_MONTHS = [0, 3, 6];

  useEffect(() => { getProducts().then(setProducts).catch(console.error); }, []);

  const generatePreview = (data) => {
    if (!data.incubationDate) return;
    const months = data.studyType === "Long Study" ? LONG_MONTHS : ACCEL_MONTHS;
    const base = new Date(data.incubationDate);
    const result = months.map(m => {
      const d = new Date(base);
      d.setMonth(d.getMonth() + m);
      return { label: m === 0 ? "Initial" : `${m}M`, date: d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }) };
    });
    setPreview(result);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    const updated = { ...form, [name]: value };
    setForm(updated);
    if (name === "incubationDate" || name === "studyType") generatePreview(updated);
  };

  const isIncubationInvalid = form.incubationDate && form.mfgDate && new Date(form.incubationDate) < new Date(form.mfgDate);

  const saveBatch = async () => {
    if (!form.productId || !form.batchNo || !form.mfgDate || !form.incubationDate || !form.expiry) { alert("Fill all required fields"); return; }
    if (isIncubationInvalid) { alert("Incubation date must be ≥ manufacturing date"); return; }
    if (!form.shelf || !form.rack || !form.position) { alert("Fill all chamber location fields"); return; }
    try {
      await createBatch({
        product: form.productId,
        batch_number: form.batchNo,
        mfg_date: form.mfgDate,
        expiry_date: form.expiry,
        incubation_date: form.incubationDate,
        study_type: form.studyType === "Long Study" ? "long_term" : "accelerated",
        shelf: form.shelf,
        rack: form.rack,
        position: form.position,
        qty_placed: parseInt(form.qty),
      });
      navigate("/batches");
    } catch (err) { alert("Error creating batch: " + err.message); }
  };

  const productOptions = [{ value: "", label: "Select product" }, ...products.map(p => ({ value: p.id, label: `${p.name} – ${p.strength}` }))];

  return (
    <div className="page active">
      <div className="page-header"><h2>🧪 Add New Batch</h2><div className="page-header-actions"><span className="back-link" onClick={() => navigate("/batches")}>← Back</span></div></div>
      <div className="page-body"><div className="form-card" style={{ maxWidth: "100%" }}>
        <div className="form-group"><label>Product *</label><CustomSelect options={productOptions} value={form.productId} onChange={(val) => setForm({ ...form, productId: val })} placeholder="Select product" /></div>
        <div className="form-row"><div className="form-group"><label>Batch Number *</label><input type="text" name="batchNo" placeholder="e.g. AMX-2025-001" value={form.batchNo} onChange={(e) => handleChange({ target: { name: "batchNo", value: e.target.value.toUpperCase() } })} /></div><div className="form-group"><label>Manufacturing Date *</label><input type="date" name="mfgDate" value={form.mfgDate} onChange={handleChange} /></div></div>
        <div className="form-row"><div className="form-group"><label>Incubation Date * <span style={{ fontSize: "10px", color: "var(--accent)" }}>(used for schedule)</span></label><input type="date" name="incubationDate" value={form.incubationDate} onChange={handleChange} /><div className="field-hint" style={{ display: isIncubationInvalid ? "block" : "none" }}>Incubation Date must be ≥ Manufacturing Date</div></div><div className="form-group"><label>Expiry Date *</label><input type="date" name="expiry" value={form.expiry} onChange={handleChange} /></div></div>
        <div className="form-group"><label>Study Type *</label><div className="radio-group"><label className="radio-option"><input type="radio" name="studyType" value="Long Study" checked={form.studyType === "Long Study"} onChange={handleChange} /> Long Study</label><label className="radio-option"><input type="radio" name="studyType" value="Accelerated Study" checked={form.studyType === "Accelerated Study"} onChange={handleChange} /> Accelerated Study</label></div></div>
        <div style={{ background: "var(--gray-50)", border: "1px solid var(--gray-200)", borderRadius: "var(--radius)", padding: "16px", marginBottom: "16px" }}><div style={{ fontSize: "12px", fontWeight: 600, color: "var(--primary)", marginBottom: "12px", textTransform: "uppercase", letterSpacing: ".5px" }}>🏛️ Chamber Location</div><div className="form-row-3"><div className="form-group" style={{ marginBottom: 0 }}><label>Shelf *</label><input type="text" name="shelf" placeholder="e.g. S1" value={form.shelf} onChange={(e) => handleChange({ target: { name: "shelf", value: e.target.value.toUpperCase() } })} /></div><div className="form-group" style={{ marginBottom: 0 }}><label>Rack *</label><input type="text" name="rack" placeholder="e.g. R2" value={form.rack} onChange={(e) => handleChange({ target: { name: "rack", value: e.target.value.toUpperCase() } })} /></div><div className="form-group" style={{ marginBottom: 0 }}><label>Position *</label><input type="text" name="position" placeholder="e.g. P3" value={form.position} onChange={(e) => handleChange({ target: { name: "position", value: e.target.value.toUpperCase() } })} /></div></div></div>
        <div className="form-group"><label>Quantity Placed *</label><input type="number" name="qty" placeholder="e.g. 60" min="1" style={{ maxWidth: "250px", margin: "0" }} value={form.qty} onChange={handleChange} /></div>
        {preview.length > 0 && (<div id="schedule-preview" className="schedule-preview"><h4>📅 Generated Schedule <span className="schedule-subtitle">(based on incubation date)</span></h4><div className="schedule-points">{preview.map((p, i) => (<div key={i}><span>{p.label}</span><span>{p.date}</span></div>))}</div></div>)}
        <div className="form-actions"><button className="btn btn-accent" onClick={saveBatch}>📅 Save & Generate Schedule</button><button className="btn btn-outline" onClick={() => navigate("/batches")}>Cancel</button></div>
      </div></div>
    </div>
  );
}

export default AddBatchPage;