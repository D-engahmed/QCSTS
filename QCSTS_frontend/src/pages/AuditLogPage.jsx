import React, { useState, useEffect } from "react";
import { getAuditLog, getCurrentUser, getUsers } from "../services/api";
import CustomSelect from "../components/CustomSelect";
import "../styles/audit.css";

function AuditLogPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    model_name: "",
    action: "",
    performed_by: "",
    date_from: "",
    date_to: "",
  });
  const [users, setUsers] = useState([]);
  const user = getCurrentUser();
  const isAuthorized = user?.role === "qa_manager" || user?.role === "admin";

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.model_name) params.model_name = filters.model_name;
      if (filters.action) params.action = filters.action;
      if (filters.performed_by) params.performed_by = filters.performed_by;
      if (filters.date_from) params.date_from = filters.date_from;
      if (filters.date_to) params.date_to = filters.date_to;
      const data = await getAuditLog(params);
      setLogs(data || []);
      setCurrentPage(1);
    } catch (err) {
      console.error("Failed to load audit log:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      if (user?.role === "admin") {
        const usersData = await getUsers();
        setUsers(usersData || []);
      }
    } catch (err) {
      console.error("Failed to load users for filter:", err);
    }
  };

  useEffect(() => {
    if (isAuthorized) {
      loadLogs();
      loadUsers();
    }
  }, [filters]);

  // ─── Helper: Convert Technical Log to Human-Readable English ───
  const formatHumanReadableActivity = (log) => {
    const action = log.action;
    const model = log.model_name;
    const object = log.object_repr || "";
    const newVal = log.new_value || {};
    const oldVal = log.old_value || {};

    if (action === "CREATE") {
      return (
        <span className="audit-activity-text">
          Created a new <strong>{model}</strong> record: <span className="highlight-added">{object}</span>.
        </span>
      );
    }

    if (action === "APPROVE") {
      return (
        <span className="audit-activity-text">
          ✅ Approved the <strong>{model}</strong>: <span className="highlight-changed">{object}</span>.
        </span>
      );
    }

    if (action === "UPDATE") {
      const changes = [];
      if (newVal && typeof newVal === 'object') {
        Object.keys(newVal).forEach((key) => {
          const newValue = newVal[key];
          const oldValue = oldVal ? oldVal[key] : undefined;
          
          if (newValue !== oldValue) {
            const friendlyKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            if (oldValue === undefined || oldValue === null) {
              changes.push(
                <div key={key}>→ Added <span className="highlight-added">{friendlyKey}</span>: <strong>{newValue}</strong></div>
              );
            } else if (newValue === undefined || newValue === null) {
              changes.push(
                <div key={key}>→ Removed <span className="highlight-removed">{friendlyKey}</span>: <strong>{oldValue}</strong></div>
              );
            } else {
              changes.push(
                <div key={key}>→ Changed <span className="highlight-changed">{friendlyKey}</span> from <strong>{oldValue}</strong> to <strong>{newValue}</strong></div>
              );
            }
          }
        });
      }

      if (changes.length === 0) {
        return <span className="audit-activity-text">Updated <strong>{model}</strong> {object}.</span>;
      }

      return (
        <div className="audit-activity-text">
          <div>Updated <strong>{model}</strong> {object}:</div>
          <div style={{ paddingLeft: "16px", marginTop: "4px", fontSize: "13px", color: "var(--gray-700)" }}>
            {changes}
          </div>
        </div>
      );
    }

    if (action === "LOGIN") return <span className="audit-activity-text">🔑 Logged in to the system.</span>;
    if (action === "LOGOUT") return <span className="audit-activity-text">🚪 Logged out of the system.</span>;
    if (action === "DELETE") return <span className="audit-activity-text">🗑️ Deleted <strong>{model}</strong>: {object}.</span>;
    if (action === "SIGN") return <span className="audit-activity-text">📝 Electronically signed a result for <strong>{model}</strong>.</span>;

    return <span className="audit-activity-text">Performed <strong>{action}</strong> on {model}: {object}.</span>;
  };

  // ─── Pagination Logic ───
  const totalItems = logs.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentLogs = logs.slice(indexOfFirstItem, indexOfLastItem);

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) setCurrentPage(page);
  };

  if (!isAuthorized) {
    return (
      <div className="page active">
        <div className="page-header"><h2>Access Denied</h2></div>
        <div className="page-body"><p>You do not have permission to view the audit trail.</p></div>
      </div>
    );
  }

  const modelOptions = [
    { value: "", label: "All Models" },
    { value: "Batch", label: "Batch" },
    { value: "Product", label: "Product" },
    { value: "Monograph", label: "Monograph" },
    { value: "MonographTest", label: "Monograph Test" },
    { value: "TestResult", label: "Test Result" },
    { value: "SamplePull", label: "Sample Pull" },
    { value: "LocationHistory", label: "Location History" },
    { value: "CustomUser", label: "User" },
  ];

  const actionOptions = [
    { value: "", label: "All Actions" },
    { value: "CREATE", label: "Created" },
    { value: "UPDATE", label: "Updated" },
    { value: "DELETE", label: "Deleted" },
    { value: "APPROVE", label: "Approved" },
    { value: "SIGN", label: "Electronic Signature" },
    { value: "LOGIN", label: "Login" },
    { value: "LOGOUT", label: "Logout" },
  ];

  const formatDate = (dateString) => {
    if (!dateString) return "—";
    return new Date(dateString).toLocaleString("en-US", {
      year: "numeric", month: "short", day: "2-digit",
      hour: "2-digit", minute: "2-digit"
    });
  };

  const handleFilterChange = (key, value) =>
    setFilters((prev) => ({ ...prev, [key]: value }));

  const clearFilters = () => {
    setFilters({
      model_name: "",
      action: "",
      performed_by: "",
      date_from: "",
      date_to: "",
    });
    setCurrentPage(1);
  };

  const getActionBadgeClass = (action) => {
    switch (action) {
      case "CREATE": return "badge-success";
      case "UPDATE": return "badge-info";
      case "DELETE": return "badge-danger";
      case "APPROVE": return "badge-primary";
      case "SIGN": return "badge-warning";
      default: return "badge-gray";
    }
  };

  // Helper to truncate the Object ID (UUID) to just the first 8 chars
  const truncateId = (id) => {
    if (!id) return "—";
    return id.length > 8 ? `${id.substring(0, 8)}...` : id;
  };

  return (
    <div className="page active">
      <div className="page-header">
        <h2>📜 Audit Trail</h2>
        <span className="text-muted">Complete history of all system changes</span>
      </div>
      <div className="page-body">
        
        {/* ─── Filters (Compact & Professional) ─── */}
        <div className="audit-filters">
          <div className="filter-group">
            <label>Category</label>
            <CustomSelect options={modelOptions} value={filters.model_name} onChange={(val) => handleFilterChange("model_name", val)} placeholder="All Models" />
          </div>
          <div className="filter-group">
            <label>Activity Type</label>
            <CustomSelect options={actionOptions} value={filters.action} onChange={(val) => handleFilterChange("action", val)} placeholder="All Actions" />
          </div>
          {user?.role === "admin" && users.length > 0 && (
            <div className="filter-group">
              <label>User</label>
              <CustomSelect options={[{ value: "", label: "All Users" }, ...users.map((u) => ({ value: u.id, label: u.full_name }))]} value={filters.performed_by} onChange={(val) => handleFilterChange("performed_by", val)} placeholder="All Users" />
            </div>
          )}
          <div className="filter-group" style={{ maxWidth: "280px" }}>
            <label>Date Range</label>
            <div className="date-range-wrapper">
              <input type="date" value={filters.date_from} onChange={(e) => handleFilterChange("date_from", e.target.value)} placeholder="From" />
              <span style={{ color: "var(--gray-400)", fontSize: "12px" }}>to</span>
              <input type="date" value={filters.date_to} onChange={(e) => handleFilterChange("date_to", e.target.value)} placeholder="To" />
            </div>
          </div>
          <div className="filter-actions">
            <button className="btn btn-outline btn-sm" onClick={clearFilters}>Clear</button>
            <button className="btn btn-primary btn-sm" onClick={loadLogs}>Apply Filters</button>
          </div>
        </div>

        {/* ─── Table ─── */}
        <div className="card">
          <div className="card-header">
            <h3>Activity Log</h3>
            <span className="badge badge-primary">{totalItems} records</span>
          </div>
          <div className="audit-table-wrap">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Date & Time</th>
                  <th>User</th>
                  <th>Activity</th>
                  <th>Object / ID</th>
                  <th style={{ minWidth: "350px" }}>Details (Changes)</th>
                  <th className="audit-ip">IP Address</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan="6" className="empty-state">Loading...</td></tr>
                ) : currentLogs.length === 0 ? (
                  <tr><td colSpan="6" className="empty-state"><div className="empty-icon">🔍</div><p>No audit records found for the selected filters.</p></td></tr>
                ) : (
                  currentLogs.map((log) => {
                    // User initials
                    const initials = log.performed_by_name ? 
                      log.performed_by_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : "SYS";
                    
                    return (
                      <tr key={log.id}>
                        <td className="audit-timestamp">{formatDate(log.timestamp)}</td>
                        <td className="audit-user">
                          <div className="user-avatar-small">{initials}</div>
                          {log.performed_by_name || "System"}
                        </td>
                        <td>
                          <span className={`badge ${getActionBadgeClass(log.action)}`} style={{ textTransform: "capitalize" }}>
                            {log.action}
                          </span>
                        </td>
                        <td>
                          <strong>{log.model_name}</strong>
                          <span className="audit-object-id">{truncateId(log.object_id)}</span>
                        </td>
                        <td>
                          {/* Human Readable Sentence */}
                          <div>{formatHumanReadableActivity(log)}</div>

                          {/* Expandable Raw JSON for Technical Auditors */}
                          {(log.old_value || log.new_value) && (
                            <details className="audit-json-details">
                              <summary>View raw audit data</summary>
                              <pre>
                                {log.old_value && (
                                  <div className="audit-old">
                                    <strong>Before:</strong> {JSON.stringify(log.old_value, null, 2)}
                                  </div>
                                )}
                                {log.new_value && (
                                  <div className="audit-new">
                                    <strong>After:</strong> {JSON.stringify(log.new_value, null, 2)}
                                  </div>
                                )}
                              </pre>
                            </details>
                          )}
                        </td>
                        <td className="audit-ip">{log.ip_address || "—"}</td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* ─── Pagination ─── */}
          {!loading && totalItems > itemsPerPage && (
            <div className="audit-pagination">
              <div className="records-info">
                Showing {indexOfFirstItem + 1}–{Math.min(indexOfLastItem, totalItems)} of {totalItems}
              </div>
              <div className="page-controls">
                <button className="page-btn" onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>‹ Prev</button>
                {[...Array(Math.min(totalPages, 7))].map((_, i) => {
                  let pageNum = i + 1;
                  if (totalPages > 7 && currentPage > 4) {
                    if (currentPage + 3 > totalPages) pageNum = totalPages - 6 + i;
                    else pageNum = currentPage - 3 + i;
                  }
                  return <button key={pageNum} className={`page-btn ${currentPage === pageNum ? "active" : ""}`} onClick={() => handlePageChange(pageNum)}>{pageNum}</button>;
                })}
                <button className="page-btn" onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === totalPages}>Next ›</button>
                <select value={itemsPerPage} onChange={(e) => { setItemsPerPage(Number(e.target.value)); setCurrentPage(1); }} style={{ padding: "4px 8px", borderRadius: "var(--radius)", border: "1px solid var(--gray-200)", fontSize: "13px", outline: "none", marginLeft: "8px" }}>
                  <option value="25">25 / page</option>
                  <option value="50">50 / page</option>
                  <option value="100">100 / page</option>
                </select>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AuditLogPage;