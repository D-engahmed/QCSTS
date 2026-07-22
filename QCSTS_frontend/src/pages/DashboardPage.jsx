import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  getDashboard,
  getTestPoints,
  getBatches,
  getProducts,
  getSamplePulls,
  getCurrentUser,
} from "../services/api";
import CustomSelect from "../components/CustomSelect";
import { formatDate } from "../utils/locationUtils";

function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [testPoints, setTestPoints] = useState([]);
  const [batches, setBatches] = useState([]);
  const [products, setProducts] = useState([]);
  const [pulls, setPulls] = useState({}); // testPointId -> total pulled
  const [loading, setLoading] = useState(true);

  // Filters
  const [filters, setFilters] = useState({
    search: "",
    fromDate: "",
    toDate: "",
    studyType: "",
    status: "",
  });

  // Chips for active filters
  const [activeChips, setActiveChips] = useState([]);

  const user = getCurrentUser();

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [dash, tps, batchesData, productsData, pullsData] = await Promise.all([
          getDashboard(),
          getTestPoints(),
          getBatches(),
          getProducts(),
          getSamplePulls(), // get all pulls
        ]);
        setStats(dash?.summary || {});
        setTestPoints(tps || []);
        setBatches(batchesData || []);
        setProducts(productsData || []);
        // Aggregate pulls by test point
        const pullsMap = {};
        (pullsData || []).forEach((pull) => {
          const tpId = pull.test_point;
          if (!pullsMap[tpId]) pullsMap[tpId] = 0;
          pullsMap[tpId] += pull.qty_pulled;
        });
        setPulls(pullsMap);
        // Set default date range: today → +30 days
        const today = new Date();
        const in30 = new Date(today);
        in30.setDate(in30.getDate() + 30);
        setFilters((prev) => ({
          ...prev,
          fromDate: today.toISOString().split("T")[0],
          toDate: in30.toISOString().split("T")[0],
        }));
      } catch (err) {
        console.error("Dashboard load error:", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // Update chips when filters change
  useEffect(() => {
    const chips = [];
    if (filters.search) chips.push({ label: `🔍 "${filters.search}"`, key: "search" });
    if (filters.fromDate) chips.push({ label: `From: ${formatDate(filters.fromDate)}`, key: "fromDate" });
    if (filters.toDate) chips.push({ label: `To: ${formatDate(filters.toDate)}`, key: "toDate" });
    if (filters.studyType) chips.push({ label: filters.studyType, key: "studyType" });
    if (filters.status) chips.push({ label: filters.status, key: "status" });
    setActiveChips(chips);
  }, [filters]);

  // Apply filters to test points
  const filteredTestPoints = testPoints.filter((tp) => {
    const batch = batches.find((b) => b.id === tp.batch);
    if (!batch) return false;
    const product = products.find((p) => p.id === batch.product);
    if (!product) return false;

    // Search
    if (filters.search) {
      const q = filters.search.toLowerCase();
      const hay = `${product.name} ${batch.batch_number} ${tp.month}M ${batch.study_type}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    // Date range
    const sched = new Date(tp.scheduled_date);
    if (filters.fromDate && sched < new Date(filters.fromDate + "T00:00:00")) return false;
    if (filters.toDate && sched > new Date(filters.toDate + "T00:00:00")) return false;
    // Study type
    if (filters.studyType && batch.study_type !== filters.studyType) return false;
    // Status
    if (filters.status && tp.status !== filters.status) return false;

    return true;
  });

  // Sort: overdue first, then by date
  const sortedTPs = [...filteredTestPoints].sort((a, b) => {
    const aOv = a.status === "overdue" ? 0 : 1;
    const bOv = b.status === "overdue" ? 0 : 1;
    if (aOv !== bOv) return aOv - bOv;
    return new Date(a.scheduled_date) - new Date(b.scheduled_date);
  });

  // Overdue test points (for separate table)
  const overdueTPs = testPoints.filter((tp) => {
    const batch = batches.find((b) => b.id === tp.batch);
    if (!batch) return false;
    const product = products.find((p) => p.id === batch.product);
    if (!product) return false;
    return tp.status === "overdue";
  });

  // Render status badge based on real backend status
  const statusBadge = (status) => {
    switch (status) {
      case "completed": return <span className="badge badge-success">✅ Completed</span>;
      case "failed": return <span className="badge badge-danger">❌ Failed</span>;
      case "overdue": return <span className="badge badge-danger">🚨 Overdue</span>;
      case "pulled": return <span className="badge badge-purple">📤 Pulled</span>;
      default: return <span className="badge badge-warning">⏳ Pending</span>;
    }
  };

  // Remove a chip
  const removeChip = (key) => {
    setFilters((prev) => ({ ...prev, [key]: "" }));
  };

  // Reset filters
  const resetFilters = () => {
    const today = new Date();
    const in30 = new Date(today);
    in30.setDate(in30.getDate() + 30);
    setFilters({
      search: "",
      fromDate: today.toISOString().split("T")[0],
      toDate: in30.toISOString().split("T")[0],
      studyType: "",
      status: "",
    });
  };

  if (loading) {
    return (
      <div className="page active">
        <div className="page-header"><h2>📊 Dashboard</h2></div>
        <div className="page-body"><div className="empty-state"><p>Loading...</p></div></div>
      </div>
    );
  }

  return (
    <div className="page active">
      <div className="page-header">
        <h2>📊 Dashboard</h2>
        <span className="text-muted">{new Date().toLocaleDateString()}</span>
      </div>

      <div className="page-body">
        {/* Stats */}
        <div className="stats-grid mb-6">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: "#e6edf8" }}>💊</div>
            <div>
              <div className="stat-value">{stats.total_products || 0}</div>
              <div className="stat-label">Products</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: "#e6f4ed" }}>🧪</div>
            <div>
              <div className="stat-value">{stats.active_batches || 0}</div>
              <div className="stat-label">Active Batches</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: "#f0ebfc" }}>🏛️</div>
            <div>
              <div className="stat-value">{stats.active_batches || 0}</div>
              <div className="stat-label">In Chamber</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: "#fef7e6" }}>⏰</div>
            <div>
              <div className="stat-value">{stats.upcoming_tests || 0}</div>
              <div className="stat-label">Upcoming (30d)</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: "#fdf0ee" }}>🚨</div>
            <div>
              <div className="stat-value">{stats.overdue_tests || 0}</div>
              <div className="stat-label">Overdue</div>
            </div>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="card mb-6" style={{ padding: "16px 18px" }}>
          <div style={{ display: "flex", gap: "12px", alignItems: "flex-end", flexWrap: "wrap" }}>
            <div style={{ flex: 2, minWidth: "180px" }}>
              <label style={{ display: "block", fontSize: "11px", fontWeight: "600", color: "var(--gray-500)", textTransform: "uppercase", letterSpacing: ".5px", marginBottom: "5px" }}>Search</label>
              <div className="search-inline">
                <span style={{ color: "var(--gray-400)" }}>🔍</span>
                <input
                  type="text"
                  placeholder="Product, Batch No, Test Point…"
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                />
              </div>
            </div>
            <div style={{ flex: 1, minWidth: "140px" }}>
              <label style={{ display: "block", fontSize: "11px", fontWeight: "600", color: "var(--gray-500)", textTransform: "uppercase", letterSpacing: ".5px", marginBottom: "5px" }}>From Date</label>
              <input
                type="date"
                value={filters.fromDate}
                onChange={(e) => setFilters({ ...filters, fromDate: e.target.value })}
                style={{ width: "100%", border: "1.5px solid var(--gray-200)", borderRadius: "var(--radius)", padding: "8px 10px", fontFamily: "var(--font)", fontSize: "13px", outline: "none" }}
              />
            </div>
            <div style={{ flex: 1, minWidth: "140px" }}>
              <label style={{ display: "block", fontSize: "11px", fontWeight: "600", color: "var(--gray-500)", textTransform: "uppercase", letterSpacing: ".5px", marginBottom: "5px" }}>To Date</label>
              <input
                type="date"
                value={filters.toDate}
                onChange={(e) => setFilters({ ...filters, toDate: e.target.value })}
                style={{ width: "100%", border: "1.5px solid var(--gray-200)", borderRadius: "var(--radius)", padding: "8px 10px", fontFamily: "var(--font)", fontSize: "13px", outline: "none" }}
              />
            </div>
            <div style={{ flex: 1, minWidth: "130px" }}>
              <label style={{ display: "block", fontSize: "11px", fontWeight: "600", color: "var(--gray-500)", textTransform: "uppercase", letterSpacing: ".5px", marginBottom: "5px" }}>Study Type</label>
              <CustomSelect
                options={[
                  { value: "", label: "All Types" },
                  { value: "long_term", label: "Long Study" },
                  { value: "accelerated", label: "Accelerated Study" },
                ]}
                value={filters.studyType}
                onChange={(val) => setFilters({ ...filters, studyType: val })}
                placeholder="All Types"
              />
            </div>
            <div style={{ flex: 1, minWidth: "120px" }}>
              <label style={{ display: "block", fontSize: "11px", fontWeight: "600", color: "var(--gray-500)", textTransform: "uppercase", letterSpacing: ".5px", marginBottom: "5px" }}>Status</label>
              <CustomSelect
                options={[
                  { value: "", label: "All" },
                  { value: "pending", label: "Pending" },
                  { value: "pulled", label: "Pulled" },
                  { value: "overdue", label: "Overdue" },
                  { value: "completed", label: "Completed" },
                  { value: "failed", label: "Failed" },
                ]}
                value={filters.status}
                onChange={(val) => setFilters({ ...filters, status: val })}
                placeholder="All"
              />
            </div>
            <div style={{ display: "flex", gap: "8px", paddingBottom: "1px" }}>
              <button className="btn btn-primary" onClick={() => {}}>Apply</button>
              <button className="btn btn-outline" onClick={resetFilters}>Reset</button>
            </div>
          </div>
          {/* Chips */}
          {activeChips.length > 0 && (
            <div style={{ marginTop: "10px", display: "flex", gap: "6px", flexWrap: "wrap" }}>
              {activeChips.map((chip) => (
                <span
                  key={chip.key}
                  style={{
                    background: "var(--accent-light)",
                    color: "var(--accent)",
                    border: "1px solid var(--accent)",
                    borderRadius: "99px",
                    padding: "3px 10px",
                    fontSize: "11px",
                    fontWeight: "600",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  {chip.label}
                  <span style={{ cursor: "pointer" }} onClick={() => removeChip(chip.key)}>✕</span>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Test Points Table */}
        <div className="card section-gap">
          <div className="card-header">
            <h3>📅 Test Points</h3>
            <span className={`badge ${sortedTPs.length === 0 ? "badge-gray" : "badge-primary"}`}>
              {sortedTPs.length} result{sortedTPs.length !== 1 ? "s" : ""}
            </span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Product Name</th>
                  <th>Batch No</th>
                  <th>Study Type</th>
                  <th>Test Point</th>
                  <th>Scheduled Date</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {sortedTPs.length === 0 ? (
                  <tr><td colSpan="7" className="empty-state">No test points match the filters.</td></tr>
                ) : (
                  sortedTPs.map((tp) => {
                    const batch = batches.find((b) => b.id === tp.batch);
                    const product = products.find((p) => p.id === batch?.product);
                    const label = tp.month === 0 ? "Initial" : `${tp.month}M`;
                    const status = tp.status;
                    const isCompleted = status === "completed";
                    const isFailed = status === "failed";
                    const isPulled = status === "pulled";

                    let action = "";
                    if (isCompleted || isFailed) {
                      action = <a className="action-link" onClick={() => navigate(`/schedule/${tp.batch}`)}>View Results</a>;
                    } else if (isPulled) {
                      action = <a className="action-link" onClick={() => navigate(`/test-entry/${tp.batch}/${tp.id}`)}>Enter Results</a>;
                    } else {
                      // pending or overdue
                      action = <a className="action-link" onClick={() => navigate(`/schedule/${tp.batch}`)}>📤 Pull</a>;
                    }

                    return (
                      <tr key={tp.id} className={status === "overdue" ? "overdue" : ""}>
                        <td><strong>{product?.name}</strong><span className="text-muted" style={{ display: "block", fontSize: "11px" }}>{product?.strength} · {product?.dosage_form}</span></td>
                        <td className="inline-mono">{batch?.batch_number}</td>
                        <td><span className={`badge ${batch?.study_type === "long_term" ? "badge-primary" : "badge-info"}`}>{batch?.study_type === "long_term" ? "Long Study" : "Accelerated Study"}</span></td>
                        <td><span className="badge badge-gray" style={{ fontFamily: "var(--font-mono)" }}>{label}</span></td>
                        <td>{formatDate(tp.scheduled_date)}</td>
                        <td>{statusBadge(status)}</td>
                        <td>{action}</td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Overdue Table */}
        <div className="card" style={{ marginTop: "18px" }}>
          <div className="card-header">
            <h3>🚨 Overdue Tests</h3>
            <span className={`badge ${overdueTPs.length === 0 ? "badge-success" : "badge-danger"}`}>
              {overdueTPs.length}
            </span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Product Name</th>
                  <th>Batch No</th>
                  <th>Study Type</th>
                  <th>Test Point</th>
                  <th>Due Date</th>
                  <th>Days Late</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {overdueTPs.length === 0 ? (
                  <tr><td colSpan="7" style={{ textAlign: "center", padding: "24px", color: "var(--success)" }}>✅ No overdue tests</td></tr>
                ) : (
                  overdueTPs.map((tp) => {
                    const batch = batches.find((b) => b.id === tp.batch);
                    const product = products.find((p) => p.id === batch?.product);
                    const label = tp.month === 0 ? "Initial" : `${tp.month}M`;
                    const daysLate = Math.floor((new Date() - new Date(tp.scheduled_date)) / (1000 * 60 * 60 * 24));
                    const status = tp.status;

                    let action = "";
                    if (status === "pulled") {
                      action = <a className="action-link" onClick={() => navigate(`/test-entry/${tp.batch}/${tp.id}`)}>Enter Results</a>;
                    } else {
                      action = <a className="action-link" onClick={() => navigate(`/schedule/${tp.batch}`)}>📤 Pull</a>;
                    }

                    return (
                      <tr key={tp.id} className="overdue">
                        <td><strong>{product?.name}</strong><span className="text-muted" style={{ display: "block", fontSize: "11px" }}>{product?.strength}</span></td>
                        <td className="inline-mono">{batch?.batch_number}</td>
                        <td><span className={`badge ${batch?.study_type === "long_term" ? "badge-primary" : "badge-info"}`}>{batch?.study_type === "long_term" ? "Long Study" : "Accelerated Study"}</span></td>
                        <td><span className="badge badge-gray">{label}</span></td>
                        <td>{formatDate(tp.scheduled_date)}</td>
                        <td><span className="badge badge-danger">⚠️ {daysLate}d late</span></td>
                        <td>{action}</td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;