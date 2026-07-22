import React, { useState, useEffect } from "react";
import CustomSelect from "../components/CustomSelect";
import { getDashboard, getBatches, getProducts, getCurrentUser } from "../services/api";
import "../styles/style.css";

function ReportsPage() {
  const [selectedReportType, setSelectedReportType] = useState("stability");
  const [filters, setFilters] = useState({ product: "", dateRange: "all", studyType: "" });
  const [reportData, setReportData] = useState({ headers: [], rows: [], title: "Stability Summary Report" });
  const [batches, setBatches] = useState([]);
  const [products, setProducts] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const user = getCurrentUser();
  const canExport = user?.role === "admin" || user?.role === "qa_manager" || user?.role === "supervisor";

  const formatDate = (dateString) => {
    if (!dateString) return "—";
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return "—";
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  };

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [batchData, productData, dashData] = await Promise.all([getBatches(), getProducts(), getDashboard()]);
        setBatches(batchData || []);
        setProducts(productData || []);
        setDashboard(dashData);
      } catch (err) { console.error(err); } finally { setLoading(false); }
    };
    load();
  }, []);

  const runReport = () => {
    if (loading) return;
    const today = new Date(); today.setHours(0,0,0,0);
    const cutoffDays = parseInt(filters.dateRange) || 0;
    const cutoff = cutoffDays ? new Date(today.getTime() - cutoffDays * 86400000) : null;
    let filtered = [...batches];
    if (filters.product) filtered = filtered.filter(b => b.product === filters.product);
    if (filters.studyType) {
      const apiStudy = filters.studyType === "Long Study" ? "long_term" : "accelerated";
      filtered = filtered.filter(b => b.study_type === apiStudy);
    }
    const studyLabel = (st) => st === "long_term" ? "Long Study" : "Accelerated Study";

    if (selectedReportType === "stability") {
      setReportData({
        title: "Stability Summary Report",
        headers: ["Product", "Batch No", "Study Type", "Location", "Total TPs", "Completed", "Overdue", "Pending"],
        rows: filtered.map(b => {
          const tps = b.test_points || [];
          const completed = tps.filter(t => t.status === "completed").length;
          const overdueCount = tps.filter(t => t.status === "overdue").length;
          const pending = tps.filter(t => t.status === "pending").length;
          return { product: b.product_name, batchNo: b.batch_number, studyType: studyLabel(b.study_type), location: `${b.shelf}/${b.rack}/${b.position}`, totalTPs: tps.length, completed, overdue: overdueCount, pending };
        }),
      });
    } else if (selectedReportType === "history") {
      const rows = [];
      filtered.forEach(b => { (b.test_points || []).forEach(tp => { if (cutoff && tp.scheduled_date && new Date(tp.scheduled_date) < cutoff) return; rows.push({ product: b.product_name, batchNo: b.batch_number, testPoint: tp.month === 0 ? "Initial" : `${tp.month}M`, scheduledDate: formatDate(tp.scheduled_date), status: tp.status, isOverdue: tp.status === "overdue" }); }); });
      setReportData({ title: "Batch History Report", headers: ["Product", "Batch No", "Test Point", "Scheduled Date", "Status"], rows });
    } else if (selectedReportType === "upcoming") {
      const in30 = new Date(today); in30.setDate(in30.getDate() + 30);
      const rows = [];
      filtered.forEach(b => { (b.test_points || []).forEach(tp => { const sched = new Date(tp.scheduled_date); if (tp.status === "pending" && sched >= today && sched <= in30) { const days = Math.floor((sched - today) / 86400000); rows.push({ product: b.product_name, batchNo: b.batch_number, studyType: studyLabel(b.study_type), location: `${b.shelf}/${b.rack}/${b.position}`, testPoint: tp.month === 0 ? "Initial" : `${tp.month}M`, scheduledDate: formatDate(tp.scheduled_date), daysUntilDue: days }); } }); });
      setReportData({ title: "Upcoming Tests Report", headers: ["Product", "Batch No", "Study Type", "Location", "Test Point", "Scheduled Date", "Days Until Due"], rows });
    } else if (selectedReportType === "overdue") {
      const overdueList = dashboard?.overdue_test_points || [];
      const rows = overdueList.map(tp => { const daysLate = Math.floor((today - new Date(tp.scheduled_date)) / (1000*60*60*24)); return { product: tp.product_name, batchNo: tp.batch_number, testPoint: tp.month === 0 ? "Initial" : `${tp.month}M`, dueDate: formatDate(tp.scheduled_date), daysLate }; });
      setReportData({ title: "Overdue Tests Report", headers: ["Product", "Batch No", "Test Point", "Due Date", "Days Late"], rows });
    }
  };

  useEffect(() => { if (!loading) runReport(); }, [selectedReportType, filters, loading]);

  // ── EXPORT CSV ──────────────────────────────────────────────
  const exportCSV = () => {
    const csv = [reportData.headers.join(","), ...reportData.rows.map(row => Object.values(row).map(v => `"${v}"`).join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${selectedReportType}_report.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // ── EXPORT PROFESSIONAL PDF (Native Print) ────────────────
  const printReport = () => {
    if (reportData.rows.length === 0) { alert("No data to print."); return; }

    const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    const timeStr = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const docId = `RPT-${selectedReportType.toUpperCase()}-${new Date().toISOString().split('T')[0]}`;
    
    // Build table rows
    const headers = reportData.headers.map(h => `<th>${h}</th>`).join('');
    const bodyRows = reportData.rows.map(row => {
      const cells = Object.values(row).map(val => `<td>${val}</td>`).join('');
      return `<tr>${cells}</tr>`;
    }).join('');

    const printWindow = window.open('', '_blank', 'width=900,height=700');
    printWindow.document.write(`
      <html>
        <head>
          <title>${reportData.title}</title>
          <style>
            body { font-family: 'IBM Plex Sans', sans-serif; padding: 40px; color: #1a202c; max-width: 900px; margin: 0 auto; background: white; }
            /* Header */
            .report-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 2px solid #0a3d7c; }
            .header-left h1 { color: #0a3d7c; font-size: 22px; font-weight: 700; margin: 0; line-height: 1.2; }
            .header-left span { display: block; color: #6b7a99; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
            .header-right { text-align: right; font-size: 12px; color: #4a5568; }
            .header-right strong { display: block; font-size: 14px; color: #0a3d7c; }
            
            /* Table */
            table { width: 100%; border-collapse: collapse; margin: 20px 0; border: 1px solid #e2e6f0; }
            th { background: #0a3d7c; color: white; text-align: left; padding: 12px 16px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
            td { padding: 12px 16px; border-bottom: 1px solid #e2e6f0; font-size: 13px; }
            tr:last-child td { border-bottom: 2px solid #0a3d7c; }

            /* Signatures - Spaces to sign after printing */
            .signatures-container { display: flex; justify-content: space-between; margin-top: 50px; gap: 20px; }
            .sig-col { flex: 1; }
            .sig-line { border-top: 1.5px solid #1a202c; margin-top: 40px; margin-bottom: 4px; width: 100%; }
            .sig-label { font-size: 10px; font-weight: 600; color: #6b7a99; text-transform: uppercase; letter-spacing: 0.5px; }
            .sig-role { font-size: 12px; font-weight: 600; color: #1a202c; margin-bottom: 8px; }
            .sig-date { font-size: 11px; color: #6b7a99; margin-top: 8px; }
            .sig-date span { display: inline-block; width: 70px; border-bottom: 1px solid #6b7a99; margin-left: 4px; }

            /* Footer */
            .footer { margin-top: 40px; padding-top: 12px; border-top: 1px solid #e2e6f0; font-size: 10px; color: #9aa5bc; display: flex; justify-content: space-between; }
          </style>
        </head>
        <body>
          <!-- Header -->
          <div class="report-header">
            <div class="header-left">
              <h1>QC Stability Tracking System</h1>
              <span>Pharmaceutical Quality Control</span>
            </div>
            <div class="header-right">
              <strong>${reportData.title}</strong>
              <div>Doc No: ${docId}</div>
              <div>Report Date: ${dateStr}</div>
            </div>
          </div>

          <!-- Table -->
          <table>
            <thead><tr>${headers}</tr></thead>
            <tbody>${bodyRows}</tbody>
          </table>

          <!-- Physical Signature Spaces (To be signed after printing) -->
          <div class="signatures-container">
            <div class="sig-col">
              <div class="sig-line"></div>
              <div class="sig-label">Prepared By</div>
              <div class="sig-role">QC Analyst / Specialist</div>
              <div class="sig-date">Date: <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></div>
            </div>
            <div class="sig-col">
              <div class="sig-line"></div>
              <div class="sig-label">Reviewed By</div>
              <div class="sig-role">QC Supervisor</div>
              <div class="sig-date">Date: <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></div>
            </div>
            <div class="sig-col">
              <div class="sig-line"></div>
              <div class="sig-label">Approved By</div>
              <div class="sig-role">QA Manager</div>
              <div class="sig-date">Date: <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></div>
            </div>
          </div>

          <!-- Footer -->
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

  const handleFilterChange = (key, value) => setFilters(prev => ({ ...prev, [key]: value }));
  const selectReport = (type) => setSelectedReportType(type);
  
  const renderReportRow = (row, index) => {
    if (selectedReportType === "stability") return <tr key={index}><td><strong>{row.product}</strong></td><td className="inline-mono">{row.batchNo}</td><td><span className={`badge badge-${row.studyType === "Long Study" ? "primary" : "info"}`}>{row.studyType}</span></td><td className="location-badge">{row.location}</td><td>{row.totalTPs}</td><td><span className="badge badge-success">{row.completed}</span></td><td><span className={`badge badge-${row.overdue > 0 ? "danger" : "gray"}`}>{row.overdue}</span></td><td><span className="badge badge-warning">{row.pending}</span></td></tr>;
    if (selectedReportType === "history") return <tr key={index} className={row.isOverdue ? "overdue" : ""}><td>{row.product}</td><td className="inline-mono">{row.batchNo}</td><td><span className="badge badge-gray">{row.testPoint}</span></td><td>{row.scheduledDate}</td><td><span className={`badge badge-${row.status === "completed" ? "success" : row.status === "overdue" ? "danger" : "warning"}`}>{row.status}</span></td></tr>;
    if (selectedReportType === "upcoming") return <tr key={index}><td>{row.product}</td><td className="inline-mono">{row.batchNo}</td><td><span className={`badge badge-${row.studyType === "Long Study" ? "primary" : "info"}`}>{row.studyType}</span></td><td className="location-badge">{row.location}</td><td><span className="badge badge-gray">{row.testPoint}</span></td><td>{row.scheduledDate}</td><td><span className="badge badge-warning">{row.daysUntilDue}d</span></td></tr>;
    if (selectedReportType === "overdue") return <tr key={index} className="overdue"><td>{row.product}</td><td className="inline-mono">{row.batchNo}</td><td><span className="badge badge-gray">{row.testPoint}</span></td><td>{row.dueDate}</td><td><span className="badge badge-danger">⚠️ {row.daysLate}d</span></td></tr>;
  };

  return (
    <div className="page active">
      <div className="page-header"><h2>📈 Reports</h2></div>
      <div className="page-body">
        <div className="report-cards">
          {[{ type: "stability", icon: "📊", title: "Stability Summary", desc: "Pass/fail summary per batch" }, { type: "history", icon: "📁", title: "Batch History", desc: "Full test history" }, { type: "upcoming", icon: "⏰", title: "Upcoming Tests", desc: "Next 30 days" }, { type: "overdue", icon: "🚨", title: "Overdue Tests", desc: "All overdue tests" }].map(({ type, icon, title, desc }) => <div key={type} className={`report-card ${selectedReportType === type ? "selected" : ""}`} onClick={() => selectReport(type)}><div className="report-card-icon">{icon}</div><div className="report-card-info"><h4>{title}</h4><p>{desc}</p></div></div>)}
        </div>
        
        <div className="reports-filters">
          <div className="form-group"><label>Product</label><CustomSelect value={filters.product} onChange={(val) => handleFilterChange("product", val)} placeholder="All Products" options={[{ value: "", label: "All Products" }, ...products.map(p => ({ value: p.id, label: `${p.name} – ${p.strength}` }))]} /></div>
          <div className="form-group"><label>Date Range</label><CustomSelect value={filters.dateRange} onChange={(val) => handleFilterChange("dateRange", val)} placeholder="All Time" options={[{ value: "all", label: "All Time" }, { value: "30", label: "Last 30 Days" }, { value: "90", label: "Last 90 Days" }, { value: "180", label: "Last 180 Days" }, { value: "365", label: "Last Year" }]} /></div>
          <div className="form-group"><label>Study Type</label><CustomSelect value={filters.studyType} onChange={(val) => handleFilterChange("studyType", val)} placeholder="All" options={[{ value: "", label: "All" }, { value: "Long Study", label: "Long Study" }, { value: "Accelerated Study", label: "Accelerated Study" }]} /></div>
          
          {canExport && (
            <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
              <button className="btn btn-primary" onClick={exportCSV}>⬇️ CSV</button>
              <button className="btn btn-accent" onClick={printReport}>🖨️ Print PDF</button>
            </div>
          )}
        </div>

        <div className="card"><div className="card-header"><h3>{reportData.title}</h3></div><div className="table-wrap"><table><thead><tr>{reportData.headers.map((h,i) => <th key={i}>{h}</th>)}</tr></thead><tbody>{loading ? <tr><td colSpan={reportData.headers.length || 1} className="empty-state">Loading...</td></tr> : reportData.rows.length > 0 ? reportData.rows.map((row,i) => renderReportRow(row,i)) : <tr><td colSpan={reportData.headers.length || 1} className="empty-state">No records found.</td></tr>}</tbody></table></div></div>
      </div>
    </div>
  );
}

export default ReportsPage; 