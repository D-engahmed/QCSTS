import { useState, useEffect } from "react";
import React from "react";
import { useNavigate } from "react-router-dom";
import CustomSelect from "../components/CustomSelect";
import LocationChangeModal from "../components/LocationChangeModal";
import LocationHistoryModal from "../components/LocationHistoryModal";
import { getChamberInventory, moveBatch as moveBatchAPI, getLocationHistory, getCurrentUser } from "../services/api";
import { formatDate } from "../utils/locationUtils.js";

function ChamberPage() {
  const navigate = useNavigate();
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState({ study: "" });
  const [chamberExpandState, setChamberExpandState] = useState({});
  const [locationTargetBatch, setLocationTargetBatch] = useState(null);
  const [historyTargetBatch, setHistoryTargetBatch] = useState(null);
  const [moveForm, setMoveForm] = useState({ shelf: "", rack: "", position: "", reason: "" });
  const user = getCurrentUser();

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await getChamberInventory();
        const list = data || [];
        setBatches(list);
        const productNames = [...new Set(list.map(b => b.product_name))];
        const initState = {};
        productNames.forEach(name => { initState[name] = true; });
        setChamberExpandState(initState);
      } catch (err) { console.error(err); } finally { setLoading(false); }
    };
    load();
  }, []);

  const getFilteredBatches = () => {
    let active = batches.filter(b => b.status === "active");
    if (filters.study) {
      const apiStudy = filters.study === "Long Study" ? "long_term" : "accelerated";
      active = active.filter(b => b.study_type === apiStudy);
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      active = active.filter(b => (b.product_name + " " + b.batch_number).toLowerCase().includes(q));
    }
    return active;
  };

  const getFilteredBatchesByProduct = () => {
    const active = getFilteredBatches();
    const productNames = [...new Set(active.map(b => b.product_name))];
    return productNames.map(name => ({ productName: name, batches: active.filter(b => b.product_name === name) }));
  };

  const filteredBatchesByProduct = getFilteredBatchesByProduct();
  const totalBatches = getFilteredBatches().length;

  const toggleChamber = (productName) => setChamberExpandState(prev => ({ ...prev, [productName]: !prev[productName] }));
  const expandAllChamber = () => { const newState = {}; filteredBatchesByProduct.forEach(({ productName }) => newState[productName] = true); setChamberExpandState(newState); };
  const collapseAllChamber = () => { const newState = {}; filteredBatchesByProduct.forEach(({ productName }) => newState[productName] = false); setChamberExpandState(newState); };

  const handleShowChangeLocation = (batch) => { setLocationTargetBatch(batch); setMoveForm({ shelf: "", rack: "", position: "", reason: "" }); };
  const handleConfirmLocationChange = async () => {
    if (!locationTargetBatch) return;
    const { shelf, rack, position, reason } = moveForm;
    if (!shelf || !rack || !position || !reason) { alert("Fill all fields"); return; }
    try {
      await moveBatchAPI({ batch: locationTargetBatch.id, new_shelf: shelf, new_rack: rack, new_position: position, reason });
      const updated = await getChamberInventory();
      setBatches(updated);
      alert(`✅ Batch moved to ${shelf}/${rack}/${position}`);
      setLocationTargetBatch(null);
    } catch (err) { alert("Error: " + err.message); }
  };
  const handleCloseLocationModal = () => setLocationTargetBatch(null);
  const handleShowHistory = async (batch) => {
    try {
      const history = await getLocationHistory(batch.id);
      setHistoryTargetBatch({ ...batch, productName: batch.product_name, batchNo: batch.batch_number, locationHistory: history || [] });
    } catch { setHistoryTargetBatch({ ...batch, productName: batch.product_name, batchNo: batch.batch_number, locationHistory: [] }); }
  };
  const handleCloseHistoryModal = () => setHistoryTargetBatch(null);

  const studyLabel = (st) => st === "long_term" ? "Long Study" : "Accelerated Study";
  const studyBadge = (st) => st === "long_term" ? "badge-primary" : "badge-info";

  if (loading) return <div className="page active"><div className="page-header"><h2>🏛️ Chamber Inventory</h2></div><div className="page-body"><div className="empty-state"><p>Loading...</p></div></div></div>;

  return (
    <div className="page active">
      <div className="page-header"><h2>🏛️ Chamber Inventory</h2><div className="page-header-actions"><span className="badge badge-purple" style={{ fontSize: "13px", padding: "5px 12px" }}>{totalBatches} batch{totalBatches !== 1 ? "es" : ""}</span></div></div>
      <div className="page-body">
        <div className="filter-bar mb-4"><div className="input_filter"><div className="search-inline"><span>🔍</span><input type="text" placeholder="Search product or batch…" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} style={{ width: "330px" }} /></div><CustomSelect options={[{ value: "", label: "All Study Types" }, { value: "Long Study", label: "Long Study" }, { value: "Accelerated Study", label: "Accelerated Study" }]} value={filters.study} onChange={(val) => setFilters(prev => ({ ...prev, study: val }))} placeholder="All Types" /><button className="btn btn-outline_2 btn-lg" onClick={expandAllChamber}>⊞ Expand All</button><button className="btn btn-outline_2 btn-lg" onClick={collapseAllChamber}>⊟ Collapse All</button></div></div>
        <div className="card"><div className="card-header"><h3>🏛️ Active Chamber Contents</h3></div><div className="table-wrap"><table><thead><tr><th style={{ width: "32px" }}></th><th>Product / Batch No</th><th>Study Type</th><th>Shelf</th><th>Rack</th><th>Position</th><th>Incubation Date</th><th>Qty Remaining</th><th>Status</th><th>Actions</th></tr></thead><tbody>
          {filteredBatchesByProduct.map(({ productName, batches: pBatches }) => {
            const isExpanded = chamberExpandState[productName] !== false;
            return (
              <React.Fragment key={productName}>
                <tr className={`hier-parent-row ${!isExpanded ? "collapsed" : ""}`} onClick={() => toggleChamber(productName)} style={{ cursor: "pointer" }}><td><span className="toggle-icon">{isExpanded ? "▼" : "▶"}</span></td><td colSpan="9"><div className="product-summary"><div><strong style={{ fontSize: "14px" }}>💊 {productName}</strong></div><div className="product-meta"><span className="badge badge-purple">{pBatches.length} batch{pBatches.length !== 1 ? "es" : ""} in chamber</span></div></div></td></tr>
                {pBatches.map(batch => {
                  const [shelf, rack, position] = (batch.location || "").split("/");
                  const pct = batch.qty_placed > 0 ? Math.round((batch.qty_remaining / batch.qty_placed) * 100) : 0;
                  const barColor = pct > 50 ? "var(--success)" : pct > 20 ? "var(--warning)" : "var(--danger)";
                  return (<tr key={batch.id} className={`hier-child-row ${!isExpanded ? "hidden" : ""}`}><td></td><td><span className="inline-mono">{batch.batch_number}</span></td><td><span className={`badge ${studyBadge(batch.study_type)}`}>{studyLabel(batch.study_type)}</span></td><td><span className="badge badge-gray">{shelf || batch.shelf}</span></td><td><span className="badge badge-gray">{rack || batch.rack}</span></td><td><span className="badge badge-gray">{position || batch.position}</span></td><td>{formatDate(batch.incubation_date)}</td><td><span style={{ fontWeight: "600" }}>{batch.qty_remaining}</span> / {batch.qty_placed}<div className="qty-bar-wrap"><div className="qty-bar" style={{ width: `${pct}%`, background: barColor }} /></div></td><td><span className="badge badge-success">Active</span></td><td><div style={{ display: "flex", gap: "15px" }}><div><span className="action-link" onClick={() => handleShowHistory(batch)}>History</span><span className="action-link" onClick={() => navigate(`/schedule/${batch.id}`)}>Schedule</span></div>{(user?.role === "admin" || user?.role === "qa_manager" || user?.role === "supervisor") && <span className="action-link warn" onClick={() => handleShowChangeLocation(batch)}>📍 Move</span>}</div></td></tr>);
                })}
              </React.Fragment>
            );
          })}
        </tbody></table></div></div>
      </div>
      <LocationChangeModal moveBatch={locationTargetBatch} moveForm={moveForm} setMoveForm={setMoveForm} onClose={handleCloseLocationModal} onConfirm={handleConfirmLocationChange} />
      <LocationHistoryModal historyBatch={historyTargetBatch} onClose={handleCloseHistoryModal} />
    </div>
  );
}

export default ChamberPage;