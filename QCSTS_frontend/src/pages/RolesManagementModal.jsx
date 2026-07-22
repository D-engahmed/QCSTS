import React, { useState, useEffect } from "react";
import { getPermissions, createRole } from "../services/api";

function RolesManagementModal({ isOpen, onClose, onRoleCreated }) {
  const [form, setForm] = useState({ name: "", description: "", permissions: [] });
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      getPermissions().then(setPermissions).catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const togglePermission = (permId) => {
    setForm(prev => ({
      ...prev,
      permissions: prev.permissions.includes(permId)
        ? prev.permissions.filter(id => id !== permId)
        : [...prev.permissions, permId]
    }));
  };

  const handleSave = async () => {
    if (!form.name) return alert("Role name is required");
    setLoading(true);
    try {
      const newRole = await createRole({ name: form.name, description: form.description, permission_ids: form.permissions });
      onRoleCreated(newRole);
      setForm({ name: "", description: "", permissions: [] });
      onClose();
    } catch (err) {
      alert("Error creating role: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay open">
      <div className="modal" style={{ width: "640px", maxWidth: "96%" }}>
        <h3>👑 Create New Role</h3>
        
        <div className="form-group">
          <label>Role Name *</label>
          <input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g. Lab Technician" />
        </div>
        <div className="form-group">
          <label>Description</label>
          <input type="text" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="e.g. Can only view and submit results" />
        </div>
        
        <div style={{ margin: "16px 0", borderTop: "1px solid var(--gray-200)", paddingTop: "16px" }}>
          <label style={{ display: "block", fontSize: "11px", fontWeight: "600", color: "var(--gray-500)", marginBottom: "10px" }}>GRANT PERMISSIONS (Check all that apply)</label>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", maxHeight: "220px", overflowY: "auto", paddingRight: "4px" }}>
            {permissions.map(p => (
              <label key={p.id} style={{ display: "flex", alignItems: "center", gap: "10px", padding: "6px 12px", borderRadius: "var(--radius)", background: "var(--gray-50)", cursor: "pointer", border: form.permissions.includes(p.id) ? "1.5px solid var(--accent)" : "1px solid transparent" }}>
                <input type="checkbox" checked={form.permissions.includes(p.id)} onChange={() => togglePermission(p.id)} style={{ accentColor: "var(--accent)" }} />
                <span style={{ fontSize: "13px", fontWeight: "500" }}>{p.label || p.name}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="form-actions">
          <button className="btn btn-primary" onClick={handleSave} disabled={loading}>
            {loading ? "Saving..." : "✅ Create Role"}
          </button>
          <button className="btn btn-outline" onClick={onClose}>Cancel</button>
        </div>
      </div>
    </div>
  );
}

export default RolesManagementModal;