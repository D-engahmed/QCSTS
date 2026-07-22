import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import PullModal from "../components/PullModal";
import { getBatch, getSamplePulls, recordPull } from "../services/api";
import { formatDate } from "../utils/locationUtils";

function SchedulePage() {
  const navigate = useNavigate();
  const { batchId } = useParams();
  const [batch, setBatch] = useState(null);
  const [testPoints, setTestPoints] = useState([]);
  const [pulls, setPulls] = useState({}); // testPointId -> total pulled
  const [loading, setLoading] = useState(true);

  const [showPullModal, setShowPullModal] = useState(false);
  const [pullQuantity, setPullQuantity] = useState("");
  const [pullNotes, setPullNotes] = useState("");
  const [selectedTest, setSelectedTest] = useState(null);

  useEffect(() => {
    if (!batchId) return;
    const load = async () => {
      try {
        setLoading(true);
        const batchData = await getBatch(batchId);
        setBatch(batchData);
        setTestPoints(batchData.test_points || []);

        const pullsData = await getSamplePulls(batchId);
        const pullsMap = {};
        (pullsData || []).forEach((pull) => {
          const tpId = pull.test_point;
          if (!pullsMap[tpId]) pullsMap[tpId] = 0;
          pullsMap[tpId] += pull.qty_pulled;
        });
        setPulls(pullsMap);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [batchId]);

  const openPullModal = (tp) => {
    setSelectedTest(tp);
    setShowPullModal(true);
    setPullQuantity("");
    setPullNotes("");
  };

  const confirmPull = async () => {
    const qty = parseInt(pullQuantity) || 0;
    if (qty <= 0 || qty > (batch?.qty_remaining || 0)) {
      alert("Invalid quantity.");
      return;
    }
    try {
      await recordPull({
        batch: batchId,
        test_point: selectedTest.id,
        qty_pulled: qty,
        notes: pullNotes,
      });
      const updatedBatch = await getBatch(batchId);
      setBatch(updatedBatch);
      setTestPoints(updatedBatch.test_points || []);
      const updatedPulls = await getSamplePulls(batchId);
      const pullsMap = {};
      (updatedPulls || []).forEach((pull) => {
        const tpId = pull.test_point;
        if (!pullsMap[tpId]) pullsMap[tpId] = 0;
        pullsMap[tpId] += pull.qty_pulled;
      });
      setPulls(pullsMap);
      setShowPullModal(false);
      setSelectedTest(null);
      alert(`✅ ${qty} units pulled`);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  const handleClosePullModal = () => {
    setShowPullModal(false);
    setSelectedTest(null);
    setPullQuantity("");
    setPullNotes("");
  };

  if (loading || !batch) {
    return (
      <div className="page active">
        <div className="page-header">
          <h2>📅 Stability Schedule</h2>
          <div className="page-header-actions">
            <span className="back-link" onClick={() => navigate("/batches")}>← Back to Batches</span>
          </div>
        </div>
        <div className="page-body"><div style={{ textAlign: "center", padding: "50px" }}>Loading schedule data...</div></div>
      </div>
    );
  }

  const studyLabel = batch.study_type === "long_term" ? "Long Study" : "Accelerated Study";

  // Prototype-compliant Status Badge
  const getStatusBadge = (status) => {
    switch (status) {
      case "completed": return <span className="badge badge-success">✅ Completed</span>;
      case "failed": return <span className="badge badge-danger">❌ Failed</span>;
      case "overdue": return <span className="badge badge-danger">🚨 Overdue</span>;
      case "pulled": return <span className="badge badge-purple">📤 Pulled</span>;
      default: return <span className="badge badge-warning">⏳ Pending</span>;
    }
  };

  return (
    <div className="page active">
      <div className="page-header">
        <h2>📅 Stability Schedule</h2>
        <div className="page-header-actions">
          <span className="back-link" onClick={() => navigate("/batches")}>← Back to Batches</span>
        </div>
      </div>

      <div className="page-body">
        {/* Prototype-style Info Grid (8 items in one row) */}
        <div className="info-grid mb-6" style={{ gridTemplateColumns: "repeat(8, 1fr)" }}>
          <div className="info-item"><label>Product</label><span>{batch.product_name}</span></div>
          <div className="info-item"><label>Batch Number</label><span className="inline-mono">{batch.batch_number}</span></div>
          <div className="info-item"><label>Study Type</label><span>{studyLabel}</span></div>
          <div className="info-item"><label>Manufacturing Date</label><span>{formatDate(batch.mfg_date)}</span></div>
          <div className="info-item"><label>Incubation Date</label><span>{formatDate(batch.incubation_date)}</span></div>
          <div className="info-item"><label>Expiry Date</label><span>{formatDate(batch.expiry_date)}</span></div>
          <div className="info-item"><label>Location</label><span className="location-badge">📍 {batch.location || `${batch.shelf}/${batch.rack}/${batch.position}`}</span></div>
          <div className="info-item"><label>Qty Remaining</label><span>{batch.qty_remaining} / {batch.qty_placed}</span></div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>📅 Test Schedule</h3>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Test Point</th>
                  <th>Scheduled Date</th>
                  <th>Status</th>
                  <th>Qty Pulled</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {testPoints.map((tp) => {
                  const label = tp.month === 0 ? "Initial" : `${tp.month}M`;
                  const totalPulled = pulls[tp.id] || 0;
                  const status = tp.status;
                  const isTested = status === "completed" || status === "failed";
                  const isPulled = status === "pulled";

                  let actions = "";
                  if (isTested) {
                    actions = <a className="action-link" onClick={() => navigate(`/test-entry/${batchId}/${tp.id}`)}>View Results</a>;
                  } else {
                    // Prototype layout: Always show Enter Results, and show appropriate Pull button
                    actions = (
                      <>
                        {isPulled ? (
                          <a className="action-link" onClick={() => openPullModal(tp)}>📤 More Pull</a>
                        ) : (
                          <a className="action-link" onClick={() => openPullModal(tp)}>📤 Mark as Pulled</a>
                        )}
                        <a className="action-link" onClick={() => navigate(`/test-entry/${batchId}/${tp.id}`)}>Enter Results</a>
                      </>
                    );
                  }

                  return (
                    <tr key={tp.id} className={status === "overdue" ? "overdue" : ""}>
                      <td><span className="badge badge-gray" style={{ fontFamily: "var(--font-mono)" }}>{label}</span></td>
                      <td>{formatDate(tp.scheduled_date)}</td>
                      <td>{getStatusBadge(status)}</td>
                      <td>{totalPulled > 0 ? <span className="badge badge-purple">{totalPulled} pulled</span> : "—"}</td>
                      <td>{actions}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <PullModal
        showPullModal={showPullModal}
        selectedTest={selectedTest ? { ...selectedTest, testPoint: selectedTest.month === 0 ? "Initial" : `${selectedTest.month}M` } : null}
        product={{ name: batch.product_name }}
        batch={{ ...batch, batchNo: batch.batch_number }}
        pullQuantity={pullQuantity}
        pullNotes={pullNotes}
        setPullQuantity={setPullQuantity}
        setPullNotes={setPullNotes}
        onClose={handleClosePullModal}
        onConfirm={confirmPull}
      />
    </div>
  );
}

export default SchedulePage;