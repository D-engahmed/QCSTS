import React, { useState, useEffect } from "react";
import CustomSelect from "../components/CustomSelect";
import { getTestPoints, getProducts, getBatches, recordPull } from "../services/api";
import { formatDate } from "../utils/locationUtils";

function computeTPStatus(tp) {
  if (tp.status === "completed") return "Tested";
  if (tp.status === "failed") return "Failed";
  if (tp.status === "overdue") return "Overdue";
  if (tp.status === "pulled") return "Pulled";
  return "Pending";
}

function PullListPage() {
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [filters, setFilters] = useState({ study: "", product: "" });
  const [allTestPoints, setAllTestPoints] = useState([]);
  const [products, setProducts] = useState([]);
  const [pullList, setPullList] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { getProducts().then(setProducts).catch(console.error); }, []);

  const renderPullList = async () => {
    setLoading(true);
    try {
      const [tps, allBatches] = await Promise.all([getTestPoints({}), getBatches()]);
      const batchesMap = {};
      allBatches.forEach(b => { batchesMap[b.id] = b; });

      const rows = tps
        .filter(tp => {
          const batch = batchesMap[tp.batch];
          if (!batch) return false;
          const st = computeTPStatus(tp);
          // We show Pending, Overdue, and Pulled. Hide Tested/Failed
          if (st === "Tested" || st === "Failed") return false;
          const sched = new Date(tp.scheduled_date);
          if (fromDate && sched < new Date(fromDate + "T00:00:00")) return false;
          if (toDate && sched > new Date(toDate + "T00:00:00")) return false;
          if (filters.study) {
            const apiStudy = filters.study === "Long Study" ? "long_term" : "accelerated";
            if (batch.study_type !== apiStudy) return false;
          }
          if (filters.product && batch.product !== filters.product) return false;
          return true;
        })
        .sort((a, b) => new Date(a.scheduled_date) - new Date(b.scheduled_date))
        .map(tp => {
          const batch = batchesMap[tp.batch];
          return {
            tp,
            status: computeTPStatus(tp),
            productName: batch.product_name,
            batchNo: batch.batch_number,
            studyType: batch.study_type === "long_term" ? "Long Study" : "Accelerated Study",
            location: batch.location || `${batch.shelf}/${batch.rack}/${batch.position}`,
            qtyRemaining: batch.qty_remaining,
            qtyPlaced: batch.qty_placed,
          };
        });
      setPullList(rows);
    } catch (err) { console.error(err); } finally { setLoading(false); }
  };

  useEffect(() => { renderPullList(); }, [fromDate, toDate, filters.study, filters.product]);

  const handlePull = async (tp) => {
    const qty = parseInt(window.prompt(`Pull samples for ${tp.batchNo} – ${tp.month === 0 ? "Initial" : `${tp.month}M`}.\nEnter quantity:`) || "0");
    if (!qty || qty <= 0) return;
    try {
      await recordPull({ batch: tp.batch, test_point: tp.id, qty_pulled: qty });
      alert(`✅ ${qty} units pulled from ${tp.batchNo}`);
      renderPullList();
    } catch (err) { alert("Error: " + err.message); }
  };

  const handleEnterResults = (tp) => { window.location.href = `/test-entry/${tp.batch}/${tp.id}`; };

  const productOptions = [{ value: "", label: "All Products" }, ...products.map(p => ({ value: p.id, label: p.name }))];

  return (
    <div className="page active">
      <div className="page-header"><h2>📤 Pull List</h2></div>
      <div className="page-body">
        <div className="card mb-6" style={{ padding: "16px 18px" }}>
          <div style={{ display: "flex", gap: "12px", alignItems: "flex-end", flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: "140px" }}><label>From Date *</label><input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} style={{ width: "100%" }} /></div>
            <div style={{ flex: 1, minWidth: "140px" }}><label>To Date *</label><input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} style={{ width: "100%" }} /></div>
            <div style={{ flex: 1, minWidth: "130px" }}><label>Study Type</label><CustomSelect options={[{ value: "", label: "All Study Types" }, { value: "Long Study", label: "Long Study" }, { value: "Accelerated Study", label: "Accelerated Study" }]} value={filters.study} onChange={(val) => setFilters({ ...filters, study: val })} placeholder="All Study Types" /></div>
            <div style={{ flex: 1, minWidth: "140px" }}><label>Product</label><CustomSelect options={productOptions} value={filters.product} onChange={(val) => setFilters({ ...filters, product: val })} placeholder="All Products" /></div>
            <button className="btn btn-primary" onClick={renderPullList}>Apply Filter</button>
          </div>
        </div>
        <div className="card">
          <div className="card-header"><h3>📤 Samples to Pull</h3><span className={`badge ${pullList.length === 0 ? "badge-gray" : "badge-primary"}`}>{loading ? "…" : `${pullList.length} item${pullList.length !== 1 ? "s" : ""}`}</span></div>
          <div className="table-wrap"><table><thead><tr><th>Product</th><th>Batch No</th><th>Study Type</th><th>Test Point</th><th>Scheduled Date</th><th>Chamber Location</th><th>Qty Remaining</th><th>Status</th><th>Action</th></tr></thead><tbody>
            {loading ? <tr><td colSpan="9" className="empty-state">Loading...</td></tr> : pullList.map(({ tp, status, productName, batchNo, studyType, location, qtyRemaining, qtyPlaced }) => {
              const isOv = status === "Overdue";
              const isPulled = status === "Pulled";
              const pct = qtyPlaced > 0 ? Math.round((qtyRemaining / qtyPlaced) * 100) : 0;
              const barColor = pct > 50 ? "var(--success)" : pct > 20 ? "var(--warning)" : "var(--danger)";
              const label = tp.month === 0 ? "Initial" : `${tp.month}M`;
              let bCls = "warning";
              let bIcon = "⏳";
              if (isOv) { bCls = "danger"; bIcon = "🚨"; }
              if (isPulled) { bCls = "purple"; bIcon = "📤"; }
              return <tr key={tp.id} className={isOv ? "overdue" : ""}>
                <td><strong>{productName}</strong></td><td className="inline-mono">{batchNo}</td><td><span className={`badge badge-${studyType === "Long Study" ? "primary" : "info"}`}>{studyType}</span></td><td><span className="badge badge-gray">{label}</span></td><td>{formatDate(tp.scheduled_date)}</td><td><span className="location-badge">📍 {location}</span></td>
                <td><span style={{ fontWeight: "600" }}>{qtyRemaining}</span><div className="qty-bar-wrap"><div className="qty-bar" style={{ width: `${pct}%`, background: barColor }} /></div></td>
                <td><span className={`badge badge-${bCls}`}>{bIcon} {status}</span></td>
                <td>
                  {isPulled ? (
                    <a className="action-link" onClick={() => handleEnterResults(tp)}>Enter Results</a>
                  ) : (
                    <a className="action-link" onClick={() => handlePull(tp)}>📤 Pull</a>
                  )}
                </td>
              </tr>;
            })}
          </tbody></table></div>
        </div>
      </div>
    </div>
  );
}

export default PullListPage
