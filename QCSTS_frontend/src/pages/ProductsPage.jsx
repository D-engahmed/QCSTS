import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import LocationChangeModal from "../components/LocationChangeModal";
import LocationHistoryModal from "../components/LocationHistoryModal";
import { getProducts, getBatches, getCurrentUser, moveBatch as moveBatchAPI, getLocationHistory } from "../services/api";
import { formatDate } from "../utils/locationUtils.js";

function ProductsPage() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState("");
  const [expanded, setExpanded] = useState({});
  const [moveBatch, setMoveBatch] = useState(null);
  const [historyBatch, setHistoryBatch] = useState(null);
  const [moveForm, setMoveForm] = useState({ shelf: "", rack: "", position: "", reason: "" });

  const user = getCurrentUser();
  const canAddProduct = user && ["admin", "qa_manager", "supervisor", "analyst"].includes(user.role);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [productData, batchData] = await Promise.all([getProducts(), getBatches()]);
        setProducts(productData || []);
        setBatches(batchData || []);
        if (productData?.length) setExpanded({ [productData[0].id]: true });
      } catch (err) { console.error(err); } finally { setLoading(false); }
    };
    load();
  }, []);

  const filteredProducts = products.filter(p => p.name.toLowerCase().includes(searchText.toLowerCase()));
  const toggleRow = (id) => setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  const expandAll = () => { const all = {}; products.forEach(p => all[p.id] = true); setExpanded(all); };
  const collapseAll = () => setExpanded({});
  const getBatchesForProduct = (productId) => batches.filter(b => b.product === productId);
  const getLocation = (batch) => batch.location || `${batch.shelf}/${batch.rack}/${batch.position}`;

  const handleShowChangeLocation = (batch) => { setMoveBatch(batch); setMoveForm({ shelf: "", rack: "", position: "", reason: "" }); };
  const handleConfirmLocationChange = async () => {
    if (!moveBatch) return;
    const { shelf, rack, position, reason } = moveForm;
    if (!shelf || !rack || !position || !reason) { alert("Fill all fields"); return; }
    try {
      await moveBatchAPI({ batch: moveBatch.id, new_shelf: shelf, new_rack: rack, new_position: position, reason });
      const updated = await getBatches();
      setBatches(updated);
      alert(`✅ Batch moved to ${shelf}/${rack}/${position}`);
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

  if (loading) return <div className="page active"><div className="page-header"><h2>💊 Products</h2></div><div className="page-body"><div className="empty-state"><p>Loading...</p></div></div></div>;

  return (
    <div className="page active">
      <div className="page-header"><h2>💊 Products</h2></div>
      <div className="page-body">
        <div className="filter-bar">
          <div className="input_filter">
            <div className="search-inline"><span>🔍</span><input type="text" placeholder="Search products…" value={searchText} onChange={(e) => setSearchText(e.target.value)} style={{ width: "330px" }} /></div>
            <button className="btn btn-outline_2 btn-lg" onClick={expandAll}>⊞ Expand All</button>
            <button className="btn btn-outline_2 btn-lg" onClick={collapseAll}>⊟ Collapse All</button>
          </div>
          <div className="page-header-actions">
            {canAddProduct && <button className="btn btn-primary" onClick={() => navigate("/add-product")}>+ Add New Product</button>}
          </div>
        </div>
        <div className="card">
          <div className="table-wrap">
            <table style={{ borderCollapse: "collapse", width: "100%" }}>
              <thead><tr><th style={{ width: "32px" }}></th><th>PRODUCT NAME</th><th>STRENGTH</th><th>DOSAGE FORM</th><th>MONOGRAPH</th><th>BATCHES</th><th>ACTIVE</th><th>ACTIONS</th></tr></thead>
              <tbody>
                {filteredProducts.map(product => {
                  const productBatches = getBatchesForProduct(product.id);
                  const activeCount = productBatches.filter(b => b.status === "active").length;
                  const isExpanded = expanded[product.id];
                  return (
                    <React.Fragment key={product.id}>
                      <tr style={{ cursor: "pointer" }} onClick={() => toggleRow(product.id)}>
                        <td><span style={{ display: "inline-flex", width: "20px", height: "20px", background: "#0a3d7c", color: "white", borderRadius: "4px", alignItems: "center", justifyContent: "center", transform: isExpanded ? "rotate(0deg)" : "rotate(-90deg)" }}>▾</span></td>
                        <td><strong>{product.name}</strong></td>
                        <td>{product.strength}</td>
                        <td>{product.dosage_form}</td>
                        <td><span className="badge badge-info">{product.monograph_name}</span></td>
                        <td><span className="badge badge-purple">{productBatches.length} batch{productBatches.length !== 1 ? "es" : ""}</span></td>
                        <td><span className="badge badge-success">{activeCount} active</span></td>
                        <td><span className="action-link" onClick={() => navigate("/add-batch")}>+ Add Batch</span></td>
                      </tr>
                      {productBatches.map(batch => (
                        <tr key={batch.id} style={{ display: isExpanded ? "table-row" : "none", background: "#f3f6f8" }}>
                          <td></td>
                          <td colSpan="7">
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 20px", margin: "8px", background: "#fff", borderRadius: "8px", border: "1px solid #e9ecef" }}>
                              <div style={{ display: "flex", gap: "32px", alignItems: "center" }}>
                                <div><div style={{ fontFamily: "monospace", fontWeight: "bold" }}>{batch.batch_number}</div><div style={{ fontSize: "12px" }}>{batch.study_type === "long_term" ? "Long Study" : "Accelerated Study"}</div></div>
                                <div>{formatDate(batch.incubation_date)} → {formatDate(batch.expiry_date)}</div>
                                <div className="badge badge-purple">📍 {getLocation(batch)}</div>
                                <div><span className="badge badge-success">Active</span></div>
                              </div>
                              <div style={{ display: "flex", gap: "15px" }}>
                                <span className="action-link" onClick={() => handleShowHistory(batch)}>History</span>
                                <span className="action-link" onClick={() => navigate(`/schedule/${batch.id}`)}>Schedule</span>
                                {(user?.role === "admin" || user?.role === "qa_manager" || user?.role === "supervisor") && <span className="action-link warn" onClick={() => handleShowChangeLocation(batch)}>📍 Move</span>}
                              </div>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <LocationChangeModal moveBatch={moveBatch} moveForm={moveForm} setMoveForm={setMoveForm} onClose={handleCloseLocationModal} onConfirm={handleConfirmLocationChange} />
      <LocationHistoryModal historyBatch={historyBatch} onClose={handleCloseHistoryModal} />
    </div>
  );
}

export default ProductsPage;