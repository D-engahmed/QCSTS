import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import CustomSelect from "../components/CustomSelect";
import {
  getProducts,
  getBatches,
  getBatch,
  getProduct,
  getMonographTests,
  getBatchResults,
  getCurrentUser,
} from "../services/api";
import { formatDate } from "../utils/locationUtils";
import "../styles/style.css";

const studyLabel = (st) => (st === "long_term" ? "Long Study" : "Accelerated Study");
const titleCase = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);

function statusBadge(status) {
  switch (status) {
    case "completed":
      return <span className="badge badge-success">✅ Tested</span>;
    case "failed":
      return <span className="badge badge-danger">❌ Tested (Fail)</span>;
    case "pulled":
      return <span className="badge badge-purple">📤 Pulled</span>;
    case "overdue":
      return <span className="badge badge-danger">🚨 Overdue</span>;
    default:
      return <span className="badge badge-warning">⏳ Pending</span>;
  }
}

function resultCell(result) {
  if (!result) return <span className="text-muted" style={{ fontStyle: "italic" }}>Not Tested</span>;
  const pf = result.pass_fail;
  const pfBadge =
    pf === "pass" ? (
      <span className="badge badge-success">Pass</span>
    ) : pf === "fail" ? (
      <span className="badge badge-danger">Fail</span>
    ) : (
      <span className="badge badge-gray">—</span>
    );
  return (
    <span>
      {result.value}
      {result.unit ? ` ${result.unit}` : ""} {pfBadge}
    </span>
  );
}

function BatchStabilityReportPage() {
  const navigate = useNavigate();
  const user = getCurrentUser();
  const canExport = user?.role === "admin" || user?.role === "qa_manager" || user?.role === "supervisor";

  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState("");

  const [batches, setBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState("");
  const [batchesLoading, setBatchesLoading] = useState(false);

  const [batch, setBatch] = useState(null);
  const [monographTests, setMonographTests] = useState([]);
  const [results, setResults] = useState([]);
  const [reportLoading, setReportLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load products once
  useEffect(() => {
    getProducts()
      .then((data) => setProducts(data || []))
      .catch((err) => console.error(err));
  }, []);

  // Product changes -> load that product's batches, reset batch + report
  useEffect(() => {
    setSelectedBatch("");
    setBatch(null);
    setMonographTests([]);
    setResults([]);
    setError(null);
    if (!selectedProduct) {
      setBatches([]);
      return;
    }
    setBatchesLoading(true);
    getBatches({ product: selectedProduct })
      .then((data) => setBatches(data || []))
      .catch((err) => console.error(err))
      .finally(() => setBatchesLoading(false));
  }, [selectedProduct]);

  // Batch changes -> load batch detail, monograph tests (columns), and all results in one call
  useEffect(() => {
    if (!selectedBatch) {
      setBatch(null);
      setMonographTests([]);
      setResults([]);
      return;
    }
    let cancelled = false;
    const load = async () => {
      try {
        setReportLoading(true);
        setError(null);
        const batchData = await getBatch(selectedBatch);
        if (cancelled) return;
        setBatch(batchData);

        let tests = [];
        if (batchData.product) {
          const productData = await getProduct(batchData.product);
          if (productData.monograph) {
            tests = (await getMonographTests(productData.monograph)) || [];
          }
        }
        if (cancelled) return;
        setMonographTests(tests);

        const resultData = await getBatchResults(selectedBatch);
        if (cancelled) return;
        setResults(resultData || []);
      } catch (err) {
        if (!cancelled) setError("Failed to load stability report: " + err.message);
      } finally {
        if (!cancelled) setReportLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [selectedBatch]);

  // resultsMap[testPointId][monographTestId] = result
  const resultsMap = useMemo(() => {
    const map = {};
    results.forEach((r) => {
      if (!map[r.test_point]) map[r.test_point] = {};
      map[r.test_point][r.monograph_test] = r;
    });
    return map;
  }, [results]);

  const testPoints = batch?.test_points || [];

  const exportCSV = () => {
    if (!batch || testPoints.length === 0) return;
    const headers = ["Test Point", "Scheduled Date", "Status", ...monographTests.map((t) => t.name)];
    const rows = testPoints.map((tp) => {
      const label = tp.month === 0 ? "Initial" : `${tp.month}M`;
      const cells = monographTests.map((t) => {
        const r = resultsMap[tp.id]?.[t.id];
        return r ? `${r.value}${r.unit ? " " + r.unit : ""} (${r.pass_fail})` : "Not Tested";
      });
      return [label, formatDate(tp.scheduled_date), tp.status, ...cells];
    });
    const csv = [headers, ...rows].map((row) => row.map((v) => `"${v}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${batch.batch_number}_stability_report.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const printReport = () => {
    if (!batch || testPoints.length === 0) { alert("No data to print."); return; }
    const dateStr = new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
    const docId = `RPT-BATCH-${batch.batch_number}-${new Date().toISOString().split("T")[0]}`;

    const headerCells = ["Test Point", "Scheduled Date", "Status", ...monographTests.map((t) => `${t.name} (${t.specification})`)]
      .map((h) => `<th>${h}</th>`).join("");
    const bodyRows = testPoints.map((tp) => {
      const label = tp.month === 0 ? "Initial" : `${tp.month}M`;
      const cells = monographTests.map((t) => {
        const r = resultsMap[tp.id]?.[t.id];
        return `<td>${r ? `${r.value}${r.unit ? " " + r.unit : ""} — ${r.pass_fail.toUpperCase()}` : "Not Tested"}</td>`;
      }).join("");
      return `<tr><td>${label}</td><td>${formatDate(tp.scheduled_date)}</td><td>${tp.status}</td>${cells}</tr>`;
    }).join("");

    const printWindow = window.open("", "_blank", "width=1000,height=700");
    printWindow.document.write(`
      <html>
        <head>
          <title>Batch Stability Report — ${batch.batch_number}</title>
          <style>
            body { font-family: 'IBM Plex Sans', sans-serif; padding: 40px; color: #1a202c; max-width: 1000px; margin: 0 auto; background: white; }
            .report-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 2px solid #0a3d7c; }
            .header-left h1 { color: #0a3d7c; font-size: 22px; font-weight: 700; margin: 0; line-height: 1.2; }
            .header-left span { display: block; color: #6b7a99; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
            .header-right { text-align: right; font-size: 12px; color: #4a5568; }
            .header-right strong { display: block; font-size: 14px; color: #0a3d7c; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; border: 1px solid #e2e6f0; }
            th { background: #0a3d7c; color: white; text-align: left; padding: 10px 12px; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
            td { padding: 10px 12px; border-bottom: 1px solid #e2e6f0; font-size: 12px; }
            tr:last-child td { border-bottom: 2px solid #0a3d7c; }
            .signatures-container { display: flex; justify-content: space-between; margin-top: 50px; gap: 20px; }
            .sig-col { flex: 1; }
            .sig-line { border-top: 1.5px solid #1a202c; margin-top: 40px; margin-bottom: 4px; width: 100%; }
            .sig-label { font-size: 10px; font-weight: 600; color: #6b7a99; text-transform: uppercase; letter-spacing: 0.5px; }
            .sig-role { font-size: 12px; font-weight: 600; color: #1a202c; margin-bottom: 8px; }
            .footer { margin-top: 40px; padding-top: 12px; border-top: 1px solid #e2e6f0; font-size: 10px; color: #9aa5bc; display: flex; justify-content: space-between; }
          </style>
        </head>
        <body>
          <div class="report-header">
            <div class="header-left">
              <h1>QC Stability Tracking System</h1>
              <span>Pharmaceutical Quality Control</span>
            </div>
            <div class="header-right">
              <strong>Batch Stability Report</strong>
              <div>Product: ${batch.product_name}</div>
              <div>Batch: ${batch.batch_number}</div>
              <div>Doc No: ${docId}</div>
              <div>Report Date: ${dateStr}</div>
            </div>
          </div>
          <table>
            <thead><tr>${headerCells}</tr></thead>
            <tbody>${bodyRows}</tbody>
          </table>
          <div class="signatures-container">
            <div class="sig-col"><div class="sig-line"></div><div class="sig-label">Prepared By</div><div class="sig-role">QC Analyst / Specialist</div></div>
            <div class="sig-col"><div class="sig-line"></div><div class="sig-label">Reviewed By</div><div class="sig-role">QC Supervisor</div></div>
            <div class="sig-col"><div class="sig-line"></div><div class="sig-label">Approved By</div><div class="sig-role">QA Manager</div></div>
          </div>
          <div class="footer">
            <span>QC Stability Tracking System v2.1 · Confidential Internal Document</span>
            <span>Document: ${docId} · ${dateStr}</span>
          </div>
          <script>window.print(); window.close();</script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  return (
    <div className="page active">
      <div className="page-header">
        <h2>🧪 Batch Stability Report</h2>
        <div className="page-header-actions">
          <span className="back-link" onClick={() => navigate("/reports")}>← Back to Reports</span>
        </div>
      </div>

      <div className="page-body">
        <div className="reports-filters">
          <div className="form-group">
            <label>Product</label>
            <CustomSelect
              value={selectedProduct}
              onChange={setSelectedProduct}
              placeholder="Select a product…"
              options={products.map((p) => ({ value: p.id, label: `${p.name} (${p.strength})` }))}
            />
          </div>
          <div className="form-group">
            <label>Batch</label>
            <CustomSelect
              value={selectedBatch}
              onChange={setSelectedBatch}
              placeholder={!selectedProduct ? "Select a product first" : batchesLoading ? "Loading…" : "Select a batch…"}
              options={batches.map((b) => ({
                value: b.id,
                label: `${b.batch_number} – ${studyLabel(b.study_type)} (${titleCase(b.status)})`,
              }))}
            />
          </div>

          {canExport && batch && (
            <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
              <button className="btn btn-primary" onClick={exportCSV}>⬇️ CSV</button>
              <button className="btn btn-accent" onClick={printReport}>🖨️ Print PDF</button>
            </div>
          )}
        </div>

        {!selectedProduct && (
          <div className="card"><div className="empty-state" style={{ padding: "40px" }}>Select a product to see its batches.</div></div>
        )}

        {selectedProduct && !selectedBatch && (
          <div className="card">
            <div className="empty-state" style={{ padding: "40px" }}>
              {batchesLoading ? "Loading batches…" : batches.length === 0 ? "This product has no batches yet." : "Select a batch to view its stability report."}
            </div>
          </div>
        )}

        {error && <div className="card"><p style={{ color: "var(--danger)", padding: "20px" }}>{error}</p></div>}

        {selectedBatch && batch && !reportLoading && (
          <div className="card">
            <div className="card-header">
              <h3>Batch: {batch.batch_number}</h3>
              <p className="text-muted" style={{ fontSize: "13px", margin: "4px 0 0" }}>
                Product: {batch.product_name} | Study Type: {studyLabel(batch.study_type)} | Incubation Date: {formatDate(batch.incubation_date)}
              </p>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Test Point</th>
                    <th>Scheduled Date</th>
                    <th>Status</th>
                    {monographTests.map((t) => (
                      <th key={t.id}>
                        {t.name}
                        <div style={{ fontWeight: 400, fontSize: "11px", opacity: 0.8 }}>({t.specification})</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {testPoints.length === 0 ? (
                    <tr><td colSpan={3 + monographTests.length} className="empty-state">No test points scheduled for this batch.</td></tr>
                  ) : (
                    testPoints.map((tp) => {
                      const label = tp.month === 0 ? "Initial" : `${tp.month}M`;
                      return (
                        <tr key={tp.id} className={tp.status === "overdue" ? "overdue" : ""}>
                          <td><span className="badge badge-gray" style={{ fontFamily: "var(--font-mono)" }}>{label}</span></td>
                          <td>{formatDate(tp.scheduled_date)}</td>
                          <td>{statusBadge(tp.status)}</td>
                          {monographTests.map((t) => (
                            <td key={t.id}>{resultCell(resultsMap[tp.id]?.[t.id])}</td>
                          ))}
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", padding: "12px 16px", fontSize: "11px", color: "var(--gray-500)" }}>
              <span>Report generated: {new Date().toLocaleString()}</span>
              <span>
                <span className="badge badge-success" style={{ marginRight: 6 }}>Pass</span>
                <span className="badge badge-danger" style={{ marginRight: 6 }}>Fail</span>
                Not Tested – no result recorded
              </span>
            </div>
          </div>
        )}

        {selectedBatch && reportLoading && (
          <div className="card"><div className="empty-state" style={{ padding: "40px" }}>Loading stability report…</div></div>
        )}
      </div>
    </div>
  );
}

export default BatchStabilityReportPage;
