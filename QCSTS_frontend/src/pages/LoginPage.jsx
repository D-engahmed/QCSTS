import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../services/api";
import "../styles/style.css";

function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [shake, setShake] = useState(false);
  const [showPass, setShowPass] = useState(false);
  const navigate = useNavigate();

  const doLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Invalid username or password");
      setLoading(false);
      setShake(true);
      setTimeout(() => setShake(false), 400);
    }
  };

  return (
    <main className="container-login">
      <div className="background_login">
        <div className="container-background">
          <div className="login-logo">
            <div className="login-logo-icon">⚗️</div>
            <div className="login-logo-text">QC Stability<span>Tracking System</span></div>
          </div>
          <div className="login-discription">
            <h1><span style={{ fontSize: "45px", fontWeight: 700, color: "white" }} className="welcome">Welcome to</span> QC Stability Tracking System<span>Pharmaceutical Quality Control</span></h1>
          </div>
        </div>
      </div>
      <div className="login-card">
        <p>Sign in</p>
        <form onSubmit={doLogin}>
          <div className="form">
            <div className="form-group"><label>Username</label><input type="text" value={username} placeholder="Enter username" className={`${error ? "error" : ""} ${shake ? "shake" : ""}`} onChange={(e) => { setUsername(e.target.value); setError(""); }} /></div>
            <div className="form-group"><label>Password</label><div style={{ position: "relative" }}><input type={showPass ? "text" : "password"} value={password} placeholder="Enter password" className={`${error ? "error" : ""} ${shake ? "shake" : ""}`} style={{ paddingRight: "40px" }} onChange={(e) => { setPassword(e.target.value); setError(""); }} /><span onClick={() => setShowPass(!showPass)} style={{ position: "absolute", right: "12px", top: "50%", transform: "translateY(-50%)", cursor: "pointer", color: "var(--gray-400)" }}>{showPass ? "🙈" : "👁️"}</span></div></div>
            <button type="submit" className={`btn btn-primary btn-full ${loading ? "loading" : ""}`} disabled={loading}>{loading ? "Signing in..." : "Sign In to System"}</button>
            <div className="login-error">{error}</div>
          </div>
        </form>
      </div>
    </main>
  );
}

export default LoginPage;