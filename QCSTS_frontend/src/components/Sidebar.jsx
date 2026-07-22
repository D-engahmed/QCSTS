import React, { useState, useEffect } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { getCurrentUser, logout } from "../services/api";
import "../styles/style.css";

function Sidebar() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    setUser(getCurrentUser());
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  if (!user) return null;

  const isAdmin = user.role === "admin";
  const isQAManager = user.role === "qa_manager";

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">⚗️</div>
        <div className="sidebar-brand-text">
          QC Stability
          <span>Tracking System</span>
          <div className="sidebar-version">v2.1</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-label">Main</div>
        <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <span className="nav-icon">📊</span>Dashboard
        </NavLink>

        <div className="nav-label">Management</div>
        <NavLink to="/products" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <span className="nav-icon">💊</span>Products
        </NavLink>
        <NavLink to="/batches" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <span className="nav-icon">🧪</span>Batches
        </NavLink>
        <NavLink to="/monographs" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <span className="nav-icon">📋</span>Monographs
        </NavLink>

        <div className="nav-label">Chamber</div>
        <NavLink to="/chamber" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <span className="nav-icon">🏛️</span>Chamber Inventory
        </NavLink>
        <NavLink to="/pulllist" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <span className="nav-icon">📤</span>Pull List
        </NavLink>

        <div className="nav-label">Analysis</div>
        <NavLink to="/reports" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
          <span className="nav-icon">📈</span>Reports
        </NavLink>

        {(isQAManager || isAdmin) && (
          <>
            <div className="nav-label">Compliance</div>
            <NavLink to="/audit" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
              <span className="nav-icon">📜</span>Audit Trail
            </NavLink>
          </>
        )}

        {isAdmin && (
          <>
            <div className="nav-label">Admin</div>
            <NavLink to="/users" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
              <span className="nav-icon">👥</span>User Management
            </NavLink>
          </>
        )}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="user-avatar">{user.full_name?.charAt(0) || "U"}</div>
          <div className="user-info">
            <strong>{user.full_name}</strong>
            {user.role === "admin"
              ? "Administrator"
              : user.role === "qa_manager"
              ? "QA Manager"
              : user.role === "supervisor"
              ? "Supervisor"
              : "Analyst"}
          </div>
        </div>
        <button
          className="btn btn-outline btn-sm btn-full"
          style={{ background: "rgba(255,255,255,.08)", color: "rgba(255,255,255,.7)", borderColor: "rgba(255,255,255,.15)" }}
          onClick={handleLogout}
        >
          🚪 Logout
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;