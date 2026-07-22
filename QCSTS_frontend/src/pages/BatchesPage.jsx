import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CustomSelect from "../components/CustomSelect";
import LocationChangeModal from "../components/LocationChangeModal";
import LocationHistoryModal from "../components/LocationHistoryModal";
import { getBatches, getProducts, moveBatch as moveBatchAPI, getLocationHistory, getCurrentUser } from "../services/api";
import { formatDate } from "../utils/locationUtils.js";

function BatchesPage() {
  const navigate = useNavigate();
  const [batches, setBatches] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [moveBatch, setMoveBatch] = useState(null);
  const [historyBatch, setHistoryBatch] = useState(null);
  const [moveForm, setMoveForm] = useState({ shelf: "", rack: "", position: "", reason: "" });
  const [filters, setFilters] = useState({ product: "", study: "", status: "" });
  const user = getCurrentUser();

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [batchData, productData] = await Promise.all([getBatches(), getProducts()]);
        setBatches(batchData || []);
        setProducts(productData || []);
      } catch (err) { console.error(err); } finally { setLoading(false); }
    };
    load();
  }, []);

  const filteredBatches = batches.filter(b => {
    if (filters.product && b.product !== filters.product) return false;
    if (filters.study) { const apiStudy = filters.study === "Long Study" ? "long_term" : "accelerated"; if (b.study_type !== apiStudy) return false; }
    if (filters.status && b.status !== filters.status.toLowerCase()) return false;
    return true;
  });

  const handleShowChangeLocation = (batch) => { setMoveBatch(batch); setMoveForm({ shelf: "", rack: "", position: "", reason: "" }); };
  const handleConfirmLocationChange = async () => {
    if (!moveBatch) return;
    const { shelf, rack, position, reason } = moveForm;
    if (!shelf || !rack || !position || !reason) { alert("Fill all fields"); return; }
    try {
      await moveBatchAPI({ batch: moveBatch.id, new_shelf: shelf, new_rack: rack, new_position: position, reason });
      const updated = await getBatches();
      setBatches(updated);
      alert(`✅ Batch ${moveBatch.batch_number} moved to ${shelf}/${rack}/${position}`);
      setMoveBatch(null);
    } catch (err) { alert("Error: " + err.message); }
  };
  const handleCloseLocationModal = () => setMoveBatch(null);
  const handleShowHistory = async (batch) => {
    try {
      const history = await getLocationHistory(batch.id);
      setHistoryBatch({ ...batch, productName: batch.product_name, batchNo: batch.batch_number, locationHistory: history || [] });
    } catch { setHistoryBatch({ ...batch, productName: batch.product_name, batchNo: batch.batch_number, locationHistory: [] }); }
  };
  const handleCloseHistoryModal = () => setHistoryBatch(null);

  const studyLabel = (st) => st === "long_term" ? "Long Study" : "Accelerated Study";
  const studyBadge = (st) => st === "long_term" ? "badge-primary" : "badge-info";
  const statusBadge = (status) => status === "active" ? "badge-success" : status === "complete" ? "badge-gray" : status === "failed" ? "badge-danger" : "badge-warning";
  const statusLabel = (status) => status === "active" ? "Active" : status === "complete" ? "Completed" : status === "failed" ? "Failed" : "Inactive";

  if (loading) return <div className="page active"><div className="page-header"><h2>🧪 Batches</h2></div><div className="page-body"><div className="empty-state"><p>Loading...</p></div></div></div>;

  return (
    <div className="page active">
      <div className="page-header"><h2>🧪 Batches</h2></div>
      <div className="page-body">
        <div className="filter-bar">
          <div className="input_filter">
            <CustomSelect options={[{ value: "", label: "All Products" }, ...products.map(p => ({ value: p.id, label: p.name }))]} value={filters.product} onChange={(val) => setFilters({ ...filters, product: val })} placeholder="All Products" />
            <CustomSelect options={[{ value: "", label: "All Study Types" }, { value: "Long Study", label: "Long Study" }, { value: "Accelerated Study", label: "Accelerated Study" }]} value={filters.study} onChange={(val) => setFilters({ ...filters, study: val })} placeholder="All Study Types" />
            <CustomSelect options={[{ value: "", label: "All Statuses" }, { value: "Active", label: "Active" }, { value: "Complete", label: "Completed" }, { value: "Failed", label: "Failed" }]} value={filters.status} onChange={(val) => setFilters({ ...filters, status: val })} placeholder="All Statuses" />
          </div>
          <div className="page-header-actions"><button className="btn btn-primary" onClick={() => navigate("/add-batch")}>+ Add New Batch</button></div>
        </div>
        <div className="card">
          <div className="table-wrap">
            <table><thead><tr><th>Product</th><th>Batch No</th><th>Mfg Date</th><th>Incubation Date</th><th>Expiry</th><th>Study Type</th><th>Chamber Location</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>{filteredBatches.map(b => (
              <tr key={b.id}>
                <td><strong>{b.product_name}</strong></td>
                <td className="inline-mono">{b.batch_number}</td>
                <td>{formatDate(b.mfg_date)}</td>
                <td>{formatDate(b.incubation_date)}</td>
                <td>{formatDate(b.expiry_date)}</td>
                <td><span className={`badge ${studyBadge(b.study_type)}`}>{studyLabel(b.study_type)}</span></td>
                <td><span className="location-badge"><span>📍</span><span>{b.location || `${b.shelf}/${b.rack}/${b.position}`}</span></span></td>
                <td><span className={`badge ${statusBadge(b.status)}`}>{statusLabel(b.status)}</span></td>
                <td><div style={{ display: "flex", gap: "15px" }}><div style={{ display: "flex", flexDirection: "column", gap: "5px" }}><span className="action-link" onClick={() => handleShowHistory(b)}>History</span><span className="action-link" onClick={() => navigate(`/schedule/${b.id}`)}>Schedule</span></div>{(user?.role === "admin" || user?.role === "qa_manager" || user?.role === "supervisor") && <span className="action-link warn" onClick={() => handleShowChangeLocation(b)}>📍 Move</span>}</div></td>
              </tr>
            ))}</tbody></table>
          </div>
        </div>
      </div>
      <LocationChangeModal moveBatch={moveBatch} moveForm={moveForm} setMoveForm={setMoveForm} onClose={handleCloseLocationModal} onConfirm={handleConfirmLocationChange} />
      <LocationHistoryModal historyBatch={historyBatch} onClose={handleCloseHistoryModal} />
    </div>
  );
}

export default BatchesPage;