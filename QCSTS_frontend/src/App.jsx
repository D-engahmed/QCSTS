import React from "react";
import { Routes, Route, useLocation, Navigate } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardPage from "./pages/DashboardPage";
import ProductsPage from "./pages/ProductsPage";
import AddProductPage from "./pages/AddProductPage";
import BatchesPage from "./pages/BatchesPage";
import AddBatchPage from "./pages/AddBatchPage";
import ReportsPage from "./pages/ReportsPage";
import BatchStabilityReportPage from "./pages/BatchStabilityReportPage";
import LoginPage from "./pages/LoginPage";
import MonographsPage from "./pages/MonographsPage";
import MonographDetailPage from "./pages/MonographDetailPage";
import ChamberPage from "./pages/ChamberPage";
import PullListPage from "./pages/PullListPage";
import SchedulePage from "./pages/SchedulePage";
import TestEntryPage from "./pages/TestEntryPage";
import UsersPage from "./pages/UsersPage";
import AuditLogPage from "./pages/AuditLogPage";

import "./styles/style.css";

function App() {
  const isLoggedIn = localStorage.getItem("qc_logged_in") === "true";
  const location = useLocation();
  const showSidebar = isLoggedIn && location.pathname !== "/";

  return (
    <>
      {showSidebar && <Sidebar />}
      <div className={showSidebar ? "main-content" : "main-content full"}>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/products" element={<ProtectedRoute><ProductsPage /></ProtectedRoute>} />
          <Route path="/add-product" element={<ProtectedRoute><AddProductPage /></ProtectedRoute>} />
          <Route path="/batches" element={<ProtectedRoute><BatchesPage /></ProtectedRoute>} />
          <Route path="/add-batch" element={<ProtectedRoute><AddBatchPage /></ProtectedRoute>} />
          <Route path="/monographs" element={<ProtectedRoute><MonographsPage /></ProtectedRoute>} />
          <Route path="/monograph/:id" element={<ProtectedRoute><MonographDetailPage /></ProtectedRoute>} />
          <Route path="/chamber" element={<ProtectedRoute><ChamberPage /></ProtectedRoute>} />
          <Route path="/pulllist" element={<ProtectedRoute><PullListPage /></ProtectedRoute>} />
          <Route path="/schedule/:batchId" element={<ProtectedRoute><SchedulePage /></ProtectedRoute>} />
          <Route path="/test-entry/:batchId/:testPointId" element={<ProtectedRoute><TestEntryPage /></ProtectedRoute>} />
          <Route path="/reports" element={<ProtectedRoute><ReportsPage /></ProtectedRoute>} />
          <Route path="/reports/batch-stability" element={<ProtectedRoute><BatchStabilityReportPage /></ProtectedRoute>} />
          <Route path="/users" element={<ProtectedRoute allowedRoles={["admin"]}><UsersPage /></ProtectedRoute>} />
          <Route path="/audit" element={<ProtectedRoute allowedRoles={["qa_manager", "admin"]}><AuditLogPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to={isLoggedIn ? "/dashboard" : "/"} replace />} />
        </Routes>
      </div>
    </>
  );
}

export default App;