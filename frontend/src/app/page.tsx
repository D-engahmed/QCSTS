import { Activity, AlertTriangle, BarChart3, Bell, BookOpen, Building2, CalendarClock, CheckCircle2, ClipboardCheck, Database, FileCheck2, FlaskConical, LayoutDashboard, Menu, Package, Search, Settings2, ShieldCheck, Users, WalletCards } from "lucide-react";

const nav = [
  { label: "Command Center", icon: LayoutDashboard, active: true },
  { label: "Stability", icon: FlaskConical },
  { label: "Studies", icon: ClipboardCheck },
  { label: "Samples", icon: Package },
  { label: "Results", icon: FileCheck2 },
  { label: "Chambers", icon: Activity },
  { label: "Master Data", icon: Database },
  { label: "Reports & Analytics", icon: BarChart3 },
  { label: "Audit & Compliance", icon: ShieldCheck },
];

const admin = [
  { label: "Organization", icon: Building2 },
  { label: "Users & Roles", icon: Users },
  { label: "Billing", icon: WalletCards },
  { label: "Settings", icon: Settings2 },
];

const studies = [
  { id: "STB-2026-0042", name: "Amoxicillin 500 mg Capsules", site: "Cairo Manufacturing Site", status: "Active", tone: "active", progress: 78, next: "30 Sep 2026" },
  { id: "STB-2026-0041", name: "Paracetamol 500 mg Tablets", site: "Giza Quality Site", status: "At Risk", tone: "warning", progress: 54, next: "21 Sep 2026" },
  { id: "STB-2026-0039", name: "Omeprazole 20 mg Capsules", site: "Cairo Manufacturing Site", status: "Active", tone: "active", progress: 66, next: "02 Oct 2026" },
  { id: "STB-2026-0037", name: "Azithromycin 500 mg Tablets", site: "Alexandria Site", status: "Active", tone: "active", progress: 91, next: "05 Oct 2026" },
];

export default function Dashboard() {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">Q</div><span>QCSTS</span></div>
        <nav className="nav-group">
          {nav.map((item) => <a className={`nav-item ${item.active ? "active" : ""}`} href="#" key={item.label}><item.icon size={16} />{item.label}</a>)}
        </nav>
        <div className="nav-group">
          <div className="nav-label">Administration</div>
          {admin.map((item) => <a className="nav-item" href="#" key={item.label}><item.icon size={16} />{item.label}</a>)}
        </div>
        <div className="sidebar-footer"><a className="nav-item" href="#"><BookOpen size={16} />Documentation</a></div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="search"><Search size={15} /><input aria-label="Search QCSTS" placeholder="Search studies, batches, products..." /><span style={{fontSize:10}}>⌘ K</span></div>
          <div className="top-actions"><button className="icon-button" aria-label="Notifications"><Bell size={16} /></button><button className="icon-button" aria-label="Menu"><Menu size={16} /></button><div className="user"><div><strong style={{fontSize:12}}>Ahmed Hassan</strong><div style={{fontSize:10,color:"var(--muted)"}}>QA Manager</div></div><div className="avatar">AH</div></div></div>
        </header>

        <div className="content">
          <section className="page-heading">
            <div><div className="eyebrow">Cairo Pharmaceutical Group · Cairo Site</div><h1>Command Center</h1><p className="subtitle">A controlled operational view of stability, quality and compliance activity.</p></div>
            <div className="actions"><button className="btn">Export report</button><button className="btn primary"><ClipboardCheck size={14} /> New study</button></div>
          </section>

          <section className="stats">
            <div className="card stat"><div className="stat-top"><span>Active studies</span><FlaskConical size={15}/></div><div className="stat-value">24</div><div className="stat-meta good">+3 this month</div></div>
            <div className="card stat"><div className="stat-top"><span>Due timepoints</span><CalendarClock size={15}/></div><div className="stat-value">7</div><div className="stat-meta warn">3 due within 48 hours</div></div>
            <div className="card stat"><div className="stat-top"><span>Pending QA review</span><ShieldCheck size={15}/></div><div className="stat-value">12</div><div className="stat-meta">4 require action today</div></div>
            <div className="card stat"><div className="stat-top"><span>Quality events</span><AlertTriangle size={15}/></div><div className="stat-value">3</div><div className="stat-meta">1 critical · 2 monitoring</div></div>
          </section>

          <section className="grid">
            <div className="card">
              <div className="card-header"><div><div className="card-title">Stability portfolio</div><div className="card-subtitle">Current study health and next scheduled activity</div></div><button className="btn">View all</button></div>
              <div className="card-body study-list">{studies.map((study) => <div className="study" key={study.id}><div><div className="study-id">{study.id}</div><div className="study-name">{study.name}</div><div className="study-site">{study.site} · Next timepoint {study.next}</div><div className="progress"><span style={{width:`${study.progress}%`}} /></div></div><div><span className={`badge ${study.tone}`}>{study.status}</span><div style={{fontSize:10,color:"var(--muted)",marginTop:7,textAlign:"right"}}>{study.progress}% complete</div></div></div>)}</div>
            </div>

            <div className="card">
              <div className="card-header"><div><div className="card-title">Critical actions</div><div className="card-subtitle">Items requiring controlled attention</div></div><button className="btn">Open queue</button></div>
              <div className="card-body alert-list">
                <div className="alert"><div className="alert-icon"><AlertTriangle size={15}/></div><div><div className="alert-title">Chamber excursion detected</div><div className="alert-detail">CH-04 · 14 minutes outside qualified range</div></div><span className="badge critical">Critical</span></div>
                <div className="alert"><div className="alert-icon"><ShieldCheck size={15}/></div><div><div className="alert-title">QA review pending</div><div className="alert-detail">8 stability results awaiting review</div></div><span className="badge warning">Due</span></div>
                <div className="alert"><div className="alert-icon"><CalendarClock size={15}/></div><div><div className="alert-title">Timepoints due today</div><div className="alert-detail">4 samples across 2 active studies</div></div><span className="badge neutral">Today</span></div>
                <div className="alert"><div className="alert-icon"><CheckCircle2 size={15}/></div><div><div className="alert-title">Protocol approval completed</div><div className="alert-detail">STB-PRO-003 v2.1 is now effective</div></div><span className="badge active">Complete</span></div>
              </div>
            </div>
          </section>

          <section className="card" style={{marginTop:18}}>
            <div className="card-header"><div><div className="card-title">Upcoming timepoints</div><div className="card-subtitle">Operational queue for the next seven days</div></div><button className="btn">Calendar view</button></div>
            <div className="table-wrap"><table><thead><tr><th>Study</th><th>Product / Batch</th><th>Site</th><th>Timepoint</th><th>Samples</th><th>Status</th></tr></thead><tbody>
              <tr><td><strong>STB-2026-0042</strong></td><td>Amoxicillin 500 mg · AMX-26-008</td><td>Cairo</td><td>30 Sep 2026 · 09:00</td><td>24</td><td><span className="badge active">Scheduled</span></td></tr>
              <tr><td><strong>STB-2026-0041</strong></td><td>Paracetamol 500 mg · PCM-26-014</td><td>Giza</td><td>21 Sep 2026 · 08:30</td><td>18</td><td><span className="badge warning">Due soon</span></td></tr>
              <tr><td><strong>STB-2026-0039</strong></td><td>Omeprazole 20 mg · OMP-26-005</td><td>Cairo</td><td>02 Oct 2026 · 10:00</td><td>16</td><td><span className="badge active">Scheduled</span></td></tr>
            </tbody></table></div>
          </section>
        </div>
      </main>
    </div>
  );
}
