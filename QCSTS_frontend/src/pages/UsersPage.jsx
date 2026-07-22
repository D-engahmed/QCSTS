import React, { useState, useEffect } from "react";
import { getUsers, createUser, updateUser, deactivateUser, getCurrentUser } from "../services/api";
import CustomSelect from "../components/CustomSelect";

// Fixed Role Options (No API call needed)
const ROLE_OPTIONS = [
  { value: "admin", label: "Admin" },
  { value: "qa_manager", label: "QA Manager" },
  { value: "supervisor", label: "Supervisor" },
  { value: "analyst", label: "Analyst" },
  { value: "system", label: "System" }, // Future use for configs
];

function UsersPage() {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    email: "", full_name: "", role: "analyst", password: "", confirmPassword: ""
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const currentUser = getCurrentUser();
  const isAdmin = currentUser?.role === "admin";

  const loadData = async () => {
    setLoading(true);
    try {
      const usersData = await getUsers();
      setUsers(usersData || []);
    } catch (err) {
      console.error("Failed to load users:", err);
      setError("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  useEffect(() => {
    let filtered = [...users];
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(u => u.full_name.toLowerCase().includes(term) || u.email.toLowerCase().includes(term));
    }
    if (roleFilter) filtered = filtered.filter(u => u.role === roleFilter);
    if (statusFilter) filtered = filtered.filter(u => u.is_active === (statusFilter === "active"));
    setFilteredUsers(filtered);
  }, [users, searchTerm, roleFilter, statusFilter]);

  const openCreateModal = () => {
    setEditingUser(null);
    setFormData({ email: "", full_name: "", role: "analyst", password: "", confirmPassword: "" });
    setShowModal(true);
    setError("");
  };

  const handleSubmit = async () => {
    if (!formData.email || !formData.full_name || !formData.role) {
      setError("Please fill all required fields.");
      return;
    }
    if (formData.password && formData.password !== formData.confirmPassword) {
      setError("Passwords do not match."); return;
    }
    try {
      if (editingUser) {
        await updateUser(editingUser.id, { full_name: formData.full_name, role: formData.role, password: formData.password || undefined });
        setSuccess("User updated successfully.");
      } else {
        await createUser({ email: formData.email, full_name: formData.full_name, role: formData.role, password: formData.password });
        setSuccess("User created successfully.");
      }
      setShowModal(false); loadData(); setTimeout(() => setSuccess(""), 3000);
    } catch (err) { setError(err.message || "Operation failed"); }
  };

  const roleOptions = [{ value: "", label: "All roles" }, ...ROLE_OPTIONS];
  const statusOptions = [{ value: "", label: "All statuses" }, { value: "active", label: "Active" }, { value: "inactive", label: "Inactive" }];

  if (!isAdmin) return <div className="page active"><div className="page-header"><h2>Access Denied</h2></div><div className="page-body"><p>You do not have permission to view this page.</p></div></div>;

  return (
    <div className="page active">
      <div className="page-header">
        <h2>👥 User Management</h2>
        <p className="text-muted">Manage system accounts and access roles</p>
      </div>
      <div className="page-body">
        {/* Stats */}
        <div className="stats-grid" style={{ marginBottom: "24px" }}>
          <div className="stat-card"><div className="stat-icon">👥</div><div className="stat-info"><div className="stat-value">{users.length}</div><div className="stat-label">Total Users</div></div></div>
          <div className="stat-card"><div className="stat-icon">✅</div><div className="stat-info"><div className="stat-value">{users.filter(u=>u.is_active).length}</div><div className="stat-label">Active</div></div></div>
          <div className="stat-card"><div className="stat-icon">👑</div><div className="stat-info"><div className="stat-value">{ROLE_OPTIONS.length}</div><div className="stat-label">Defined Roles</div></div></div>
        </div>

        {/* Filters */}
        <div className="filter-bar" style={{ marginBottom: "24px", justifyContent: "space-between" }}>
          <div className="input_filter" style={{ flex: 1, gap: "12px" }}>
            <div className="search-inline" style={{ flex: 1 }}>
              <span>🔍</span>
              <input type="text" placeholder="Search by name or email..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} style={{ width: "100%" }} />
            </div>
            <CustomSelect options={roleOptions} value={roleFilter} onChange={setRoleFilter} placeholder="All roles" />
            <CustomSelect options={statusOptions} value={statusFilter} onChange={setStatusFilter} placeholder="All statuses" />
          </div>
          <div className="page-header-actions">
            <button className="btn btn-primary" onClick={openCreateModal}>+ Add User</button>
          </div>
        </div>

        {/* Table */}
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead><tr><th>User</th><th>Email</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
              <tbody>
                {loading ? <tr><td colSpan="5" className="empty-state">Loading...</td></tr> : filteredUsers.map(user => {
                  const roleName = ROLE_OPTIONS.find(r => r.value === user.role)?.label || user.role;
                  return <tr key={user.id}>
                    <td><strong>{user.full_name}</strong></td><td>{user.email}</td>
                    <td><span className="badge badge-info">{roleName}</span></td>
                    <td><span className={`badge ${user.is_active ? "badge-success" : "badge-gray"}`}>{user.is_active ? "Active" : "Inactive"}</span></td>
                    <td>
                      <button className="btn-link" onClick={() => { setEditingUser(user); setFormData({...user, password: "", confirmPassword: ""}); setShowModal(true); }}>Edit</button>
                      {user.is_active && <button className="btn-link" style={{ color: "#dc3545", marginLeft: "10px" }} onClick={() => { if(window.confirm("Deactivate user?")) deactivateUser(user.id).then(loadData); }}>Deactivate</button>}
                    </td>
                  </tr>
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Create/Edit User Modal */}
      {showModal && <div className="modal-overlay open">
        <div className="modal">
          <h3>{editingUser ? "Edit User" : "Create New User"}</h3>
          <div className="form-group"><label>Full Name *</label><input type="text" value={formData.full_name} onChange={e => setFormData({...formData, full_name: e.target.value})} /></div>
          <div className="form-group"><label>Email *</label><input type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} disabled={!!editingUser} /></div>
          
          <div className="form-group"><label>Role *</label>
            <CustomSelect options={ROLE_OPTIONS} value={formData.role} onChange={val => setFormData({...formData, role: val})} placeholder="Select Role" />
          </div>
          
          <div className="form-group"><label>Password {!editingUser && "*"}</label><input type={showPassword ? "text" : "password"} value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} /></div>
          <div className="form-group"><label>Confirm Password *</label><input type={showPassword ? "text" : "password"} value={formData.confirmPassword} onChange={e => setFormData({...formData, confirmPassword: e.target.value})} /></div>
          {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
          <div className="form-actions">
            <button className="btn btn-primary" onClick={handleSubmit}>{editingUser ? "Update" : "Create"}</button>
            <button className="btn btn-outline" onClick={() => setShowModal(false)}>Cancel</button>
          </div>
        </div>
      </div>}
    </div>
  );
}

export default UsersPage; 