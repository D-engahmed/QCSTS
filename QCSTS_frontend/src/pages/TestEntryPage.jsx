import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getBatch, getProduct, getMonographTests, verifySignature, submitResult, getResults } from "../services/api";
import { formatDate } from "../utils/locationUtils.js";

function autoPassFail(value, spec) {
  if (!value || !spec) return "";
  const num = parseFloat(String(value).replace(/[%,]/g, ""));
  const rng = spec.match(/(\d+\.?\d*)\s*[–\-]\s*(\d+\.?\d*)/);
  if (rng && !isNaN(num)) return num >= parseFloat(rng[1]) && num <= parseFloat(rng[2]) ? "PASS" : "FAIL";
  const nlt = spec.match(/NLT\s*(\d+\.?\d*)/i);
  if (nlt && !isNaN(num)) return num >= parseFloat(nlt[1]) ? "PASS" : "FAIL";
  const nmt = spec.match(/NMT\s*(\d+\.?\d*)/i);
  if (nmt && !isNaN(num)) return num <= parseFloat(nmt[1]) ? "PASS" : "FAIL";
  return "PASS";
}

function pfBadge(pf) {
  if (pf === "PASS") return '<span class="badge badge-success">✅ PASS</span>';
  if (pf === "FAIL") return '<span class="badge badge-danger">❌ FAIL</span>';
  return '<span class="badge badge-gray">—</span>';
}

function TestEntryPage() {
  const navigate = useNavigate();
  const { batchId, testPointId } = useParams();
  const [batch, setBatch] = useState(null);
  const [testPoint, setTestPoint] = useState(null);
  const [tests, setTests] = useState([]);
  const [results, setResults] = useState({});
  const [overallStatus, setOverallStatus] = useState("pending");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Signature State
  const [sigPassword, setSigPassword] = useState("");
  const [sigToken, setSigToken] = useState(null);
  const [sigLoading, setSigLoading] = useState(false);
  const [sigError, setSigError] = useState("");
  const [showSigModal, setShowSigModal] = useState(false);

  // View Mode - determines if we disable editing (when status is completed or failed)
  const [isViewOnly, setIsViewOnly] = useState(false);

  useEffect(() => {
    if (!batchId || !testPointId) { setError("Missing batch or test point ID"); setLoading(false); return; }
    const load = async () => {
      try {
        setLoading(true);
        
        // 1. Load Batch and Test Point details
        const batchData = await getBatch(batchId);
        setBatch(batchData);
        const tp = (batchData.test_points || []).find(t => t.id === testPointId);
        if (!tp) { setError("Test point not found in this batch."); return; }
        setTestPoint(tp);
        
        // 2. Determine View Mode (if already completed or failed)
        if (tp.status === "completed" || tp.status === "failed") {
          setIsViewOnly(true);
        }

        // 3. Load Monograph Tests
        let monographTests = [];
        if (batchData.product) {
          try {
            const productData = await getProduct(batchData.product);
            const monographId = productData.monograph;
            if (monographId) {
              monographTests = await getMonographTests(monographId) || [];
              setTests(monographTests);
            } 
          } catch { setTests([]); }
        }

        // 4. Load Saved Results FROM API
        const savedResults = await getResults({ test_point: testPointId });
        const resultMap = {};
        (savedResults || []).forEach(r => {
          resultMap[r.monograph_test] = { 
            value: r.value, 
            pf: r.pass_fail === "pass" ? "PASS" : r.pass_fail === "fail" ? "FAIL" : "" 
          };
        });

        // 5. Initialize state with saved results
        setResults(resultMap);

      } catch (err) { setError("Failed to load test entry data: " + err.message); } 
      finally { setLoading(false); }
    };
    load();
  }, [batchId, testPointId]);

  // Update overall status whenever `results` or `tests` changes
  useEffect(() => {
    if (!tests.length) return;
    let allIn = true;
    let anyFail = false;
    tests.forEach(t => {
      const val = results[t.id]?.value?.trim();
      if (!val) { allIn = false; return; }
      if (autoPassFail(val, t.specification) === "FAIL") anyFail = true;
    });
    if (!allIn) setOverallStatus("pending");
    else if (anyFail) setOverallStatus("fail");
    else setOverallStatus("pass");
  }, [results, tests]);

  const updatePF = (testId, spec, e) => {
    if (isViewOnly) return; // Prevent editing if view only
    const val = e.target.value.trim();
    setResults(prev => ({ ...prev, [testId]: { value: val, pf: val ? autoPassFail(val, spec) : "" } }));
  };

  const handleVerifySignature = async () => {
    setSigLoading(true);
    setSigError("");
    try {
      const data = await verifySignature(sigPassword);
      setSigToken(data.signature_token);
      setShowSigModal(false);
      setSigPassword("");
      await saveWithToken(data.signature_token);
    } catch (err) {
      setSigError(err.message || "Wrong password");
    } finally { setSigLoading(false); }
  };

  const handleSaveClick = () => {
    if (!tests.length) { alert("No tests to submit."); return; }
    setShowSigModal(true);
  };

  const saveWithToken = async (token) => {
    try {
      for (const t of tests) {
        const val = results[t.id]?.value?.trim();
        if (!val) continue;
        await submitResult({ test_point: testPointId, monograph_test: t.id, value: val, unit: t.unit || "", notes: "" }, token);
      }
      alert("Results saved ✅");
      navigate(`/schedule/${batchId}`);
    } catch (err) { alert("Error saving results: " + err.message); }
  };

  if (loading) return <div className="page active"><div className="page-header"><h2>🔬 Test Entry</h2><div className="page-header-actions"><span className="back-link" onClick={() => navigate(`/schedule/${batchId}`)}>← Back to Schedule</span></div></div><div className="page-body"><div style={{ textAlign: "center", padding: "50px" }}>Loading test data...</div></div></div>;
  if (error) return <div className="page active"><div className="page-header"><h2>🔬 Test Entry</h2><div className="page-header-actions"><span className="back-link" onClick={() => navigate(`/schedule/${batchId}`)}>← Back to Schedule</span></div></div><div className="page-body"><div className="card"><p style={{ color: "red", padding: "20px" }}>Error: {error}</p><button className="btn btn-outline" style={{ margin: "0 20px 20px" }} onClick={() => navigate(`/schedule/${batchId}`)}>← Back</button></div></div></div>;

  const label = testPoint?.month === 0 ? "Initial" : `${testPoint?.month}M`;

  return (
    <div className="page active">
      <div className="page-header">
        <h2>{isViewOnly ? "📄 View Test Results" : "🔬 Test Entry"}</h2>
        <div className="page-header-actions"><span className="back-link" onClick={() => navigate(`/schedule/${batchId}`)}>← Back to Schedule</span></div>
      </div>
      <div className="page-body">
        <div className="info-grid mb-6">
          <div className="info-item"><label>Product</label><span>{batch?.product_name || "-"}</span></div>
          <div className="info-item"><label>Batch</label><span className="inline-mono">{batch?.batch_number || "-"}</span></div>
          <div className="info-item"><label>Test Point</label><span>{label}</span></div>
          <div className="info-item"><label>Scheduled Date</label><span>{testPoint ? formatDate(testPoint.scheduled_date) : "-"}</span></div>
          <div className="info-item"><label>Chamber Location</label><span className="location-badge">📍 {batch?.location || `${batch?.shelf}/${batch?.rack}/${batch?.position}`}</span></div>
        </div>
        
        <div className="card">
          <div className="card-header"><h3>🧬 Test Results</h3></div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Test Name</th>
                  <th>Specification</th>
                  <th>Result</th>
                  <th>Pass / Fail</th>
                </tr>
              </thead>
              <tbody>
                {tests.length ? tests.map(t => { 
                  const sv = results[t.id] || { value: "", pf: "" }; 
                  return <tr key={t.id}>
                    <td><strong>{t.name}</strong></td>
                    <td className="text-muted" style={{ fontSize: "12px" }}>{t.specification}</td>
                    <td>
                      {isViewOnly ? (
                        // VIEW MODE: Display plain text instead of input
                        <div style={{ fontFamily: "var(--font-mono)", fontSize: "15px", fontWeight: "600", padding: "6px 0", color: "var(--gray-700)" }}>
                          {sv.value || "—"}
                        </div>
                      ) : (
                        // EDIT MODE: Show input field
                        <input 
                          type="text" 
                          className="result-input" 
                          value={sv.value} 
                          onChange={(e) => updatePF(t.id, t.specification, e)} 
                          placeholder="Enter result" 
                        />
                      )}
                    </td>
                    <td dangerouslySetInnerHTML={{ __html: sv.pf ? pfBadge(sv.pf) : '<span class="badge badge-gray">—</span>' }} />
                  </tr>;
                }) : <tr><td colSpan="4" className="empty-state">No tests defined in monograph.<br /><small>Make sure the product's monograph has tests added before entering results.</small></td></tr>}
              </tbody>
            </table>
          </div>
        </div>
        
        <div className={`overall-status ${overallStatus}`}>
          {overallStatus === "pending" && "⏳ Enter all results to calculate overall status"}
          {overallStatus === "fail" && "❌ Overall Status: FAIL — One or more tests failed"}
          {overallStatus === "pass" && "✅ Overall Status: PASS — All tests within specification"}
        </div>
        
        {/* Only show the Save button if it's NOT view-only */}
        {!isViewOnly && (
          <div style={{ marginTop: "14px" }}>
            <button className="btn btn-primary" onClick={handleSaveClick} disabled={!tests.length}>
              🔏 Save Results (requires e-signature)
            </button>
          </div>
        )}
      </div>

      {/* Signature Modal (only used in Edit mode) */}
      {showSigModal && <div className="modal-overlay open"><div className="modal"><h3>🔏 Electronic Signature</h3><p style={{ color: "var(--gray-500)", fontSize: "13px", marginBottom: "16px" }}>Re-enter your password to confirm and submit these test results.</p><div className="form-group"><label>Password *</label><input type="password" placeholder="Enter your password" value={sigPassword} onChange={(e) => setSigPassword(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleVerifySignature()} autoFocus />{sigError && <div style={{ color: "var(--danger)", fontSize: "12px", marginTop: "6px" }}>{sigError}</div>}</div><div className="form-actions"><button className="btn btn-primary" onClick={handleVerifySignature} disabled={sigLoading}>{sigLoading ? "Verifying…" : "✅ Confirm & Submit"}</button><button className="btn btn-outline" onClick={() => { setShowSigModal(false); setSigPassword(""); setSigError(""); }}>Cancel</button></div></div></div>}
    </div>
  );
}

export default TestEntryPage;