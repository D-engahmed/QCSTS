import React from "react";
import "../styles/style.css";

const PullModal = ({ showPullModal, selectedTest, product, batch, pullQuantity, pullNotes, setPullQuantity, setPullNotes, onClose, onConfirm }) => {
  if (!showPullModal || !selectedTest) return null;

  return (
    <div className="modal-overlay open">
      <div className="modal">
        <h3>📤 Mark as Pulled</h3>
        <div className="pull-qty-box" id="pull-modal-info">
          <div style={{ display: "flex", gap: "24px", flexWrap: "wrap" }}>
            <div><div className="qty-label">Product</div><div style={{ fontWeight: "600", fontSize: "13px" }}>{product.name} · {batch.batchNo}</div></div>
            <div><div className="qty-label">Test Point</div><div className="qty-val">{selectedTest.testPoint}</div></div>
            <div><div className="qty-label">Qty Remaining in Chamber</div><div className="qty-val" style={{ color: batch.qtyRemaining <= 5 ? "var(--danger)" : "var(--primary)" }}>{batch.qtyRemaining}</div></div>
            <div><div className="qty-label">Already Pulled (this TP)</div><div className="qty-val" style={{ fontSize: "18px", color: "var(--gray-600)" }}>{selectedTest.qtyPulled || 0}</div></div>
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div className="form-group">
            <label>Quantity to Pull *</label>
            <input type="number" id="pull-qty-input" value={pullQuantity} onChange={(e) => setPullQuantity(e.target.value)} placeholder="Enter quantity" min="1" max={batch.qtyRemaining} />
            {pullQuantity && parseInt(pullQuantity) > batch.qtyRemaining && (<div className="field-hint" id="hint-pull-qty">Quantity cannot exceed remaining quantity.</div>)}
          </div>
          <div className="form-group">
            <label>Notes (optional)</label>
            <input type="text" id="pull-notes" value={pullNotes} onChange={(e) => setPullNotes(e.target.value)} placeholder="e.g. Pulled for 6M stability testing" />
          </div>
        </div>
        <div className="form-actions"><button className="btn btn-success" onClick={onConfirm}>✅ Confirm Pull</button><button className="btn btn-outline" onClick={onClose}>Cancel</button></div>
      </div>
    </div>
  );
};

export default PullModal;