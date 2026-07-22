import React from "react";
import "../styles/style.css";

const LocationChangeModal = ({ moveBatch, moveForm, setMoveForm, onClose, onConfirm }) => {
  if (!moveBatch) return null;

  // FIX: API returns `product_name` and `batch_number`, not `productName`/`batchNo`
  // Both naming conventions are handled so this component works from any parent.
  const productName = moveBatch.product_name || moveBatch.productName || "Product";
  const batchNumber = moveBatch.batch_number || moveBatch.batchNo || "—";
  const currentLocation =
    moveBatch.location ||
    `${moveBatch.shelf}/${moveBatch.rack}/${moveBatch.position}`;

  return (
    <div className="modal-overlay open">
      <div className="modal">
        <h3>📍 Change Chamber Location</h3>
        <div className="move-modal-current">
          <div className="text-muted" style={{ marginBottom: "6px" }}>
            Current Location for{" "}
            <strong>
              {productName} · {batchNumber}
            </strong>
          </div>
          <div className="location-badge">
            <span>📍</span>
            <span>{currentLocation}</span>
          </div>
        </div>
        <div className="move-modal-grid">
          <div className="form-group">
            <label>New Shelf *</label>
            <input
              type="text"
              placeholder="e.g. S2"
              value={moveForm.shelf}
              onChange={(e) =>
                setMoveForm({ ...moveForm, shelf: e.target.value.toUpperCase() })
              }
            />
          </div>
          <div className="form-group">
            <label>New Rack *</label>
            <input
              type="text"
              placeholder="e.g. R1"
              value={moveForm.rack}
              onChange={(e) =>
                setMoveForm({ ...moveForm, rack: e.target.value.toUpperCase() })
              }
            />
          </div>
          <div className="form-group">
            <label>New Position *</label>
            <input
              type="text"
              placeholder="e.g. P4"
              value={moveForm.position}
              onChange={(e) =>
                setMoveForm({ ...moveForm, position: e.target.value.toUpperCase() })
              }
            />
          </div>
        </div>
        <div className="form-group">
          <label>Reason for move *</label>
          <textarea
            rows="3"
            placeholder="e.g. Equipment maintenance, space optimization"
            value={moveForm.reason}
            onChange={(e) =>
              setMoveForm({ ...moveForm, reason: e.target.value })
            }
          />
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "flex-start",
            gap: "8px",
            marginTop: "16px",
          }}
        >
          <button className="btn btn-primary btn-sm" onClick={onConfirm}>
            📍 Confirm Move
          </button>
          <button className="btn btn-outline btn-sm" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default LocationChangeModal;