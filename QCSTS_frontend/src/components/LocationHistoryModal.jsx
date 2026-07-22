import React from "react";
import "../styles/style.css";

const LocationHistoryModal = ({ historyBatch, onClose }) => {
  if (!historyBatch) return null;
  const { productName, batchNo, shelf, rack, position, locationHistory } = historyBatch;

  return (
    <div className="modal-overlay open">
      <div className="modal modal-wide">
        <h3>📍 Location Movement History</h3>
        <div>
          <div style={{ fontWeight: "600", color: "var(--primary)", marginBottom: "14px" }}>
            {productName} · {batchNo}
          </div>
          <div style={{ background: "var(--accent-light)", border: "1px solid var(--accent)", borderRadius: "var(--radius)", padding: "10px 14px", marginBottom: "14px", fontSize: "13px" }}>
            <strong>Current Location:</strong>
            <span className="location-badge" style={{ marginLeft: "8px" }}>📍 {shelf}/{rack}/{position}</span>
          </div>
          {locationHistory && locationHistory.length > 0 ? (
            <div className="movement-log">
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: "left", padding: "8px 10px", fontSize: "11px", textTransform: "uppercase", color: "var(--gray-500)", borderBottom: "1px solid var(--gray-200)" }}>Date</th>
                    <th style={{ textAlign: "left", padding: "8px 10px", fontSize: "11px", textTransform: "uppercase", color: "var(--gray-500)", borderBottom: "1px solid var(--gray-200)" }}>From</th>
                    <th style={{ textAlign: "left", padding: "8px 10px", fontSize: "11px", textTransform: "uppercase", color: "var(--gray-500)", borderBottom: "1px solid var(--gray-200)" }}>To</th>
                    <th style={{ textAlign: "left", padding: "8px 10px", fontSize: "11px", textTransform: "uppercase", color: "var(--gray-500)", borderBottom: "1px solid var(--gray-200)" }}>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {locationHistory.map((h, idx) => (
                    <tr key={idx}>
                      <td style={{ padding: "8px 10px", borderBottom: "1px solid var(--gray-100)", fontSize: "12px" }}>{new Date(h.created_at).toLocaleDateString()}</td>
                      <td style={{ padding: "8px 10px", borderBottom: "1px solid var(--gray-100)" }}>
                        <span className="location-badge" style={{ marginLeft: "8px" }}>📍 {h.old_shelf}/{h.old_rack}/{h.old_position}</span>
                      </td>
                      <td style={{ padding: "8px 10px", borderBottom: "1px solid var(--gray-100)" }}>
                        <span className="location-badge" style={{ background: "#e6f4ed", color: "var(--success)", borderColor: "var(--success)", marginLeft: "8px" }}>📍 {h.new_shelf}/{h.new_rack}/{h.new_position}</span>
                      </td>
                      <td style={{ padding: "8px 10px", borderBottom: "1px solid var(--gray-100)", fontSize: "12px", color: "var(--gray-600)" }}>{h.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state"><div className="empty-icon">📍</div><p>No location changes recorded for this batch.</p></div>
          )}
        </div>
        <div className="form-actions"><button className="btn btn-outline" onClick={onClose}>Close</button></div>
      </div>
    </div>
  );
};

export default LocationHistoryModal;