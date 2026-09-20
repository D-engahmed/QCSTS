import Link from "next/link";
import { ArrowRight, CheckCircle2, FileCheck2, FlaskConical, ShieldCheck, Users, Workflow } from "lucide-react";

const features = [
  ["Controlled stability workflows", "Studies, protocols, timepoints, samples and results in one traceable lifecycle.", FlaskConical],
  ["Tenant & role isolation", "Separate organizations, sites and user memberships without exposing tenant boundaries.", Users],
  ["Audit-ready operations", "Controlled records, approvals, signatures and audit evidence are built into the workflow.", ShieldCheck],
  ["Quality investigations", "Connect OOS/OOT, deviations and CAPA to the quality event lifecycle.", Workflow],
] as const;

export default function Landing() {
  return (
    <main className="landing">
      <header className="landing-nav">
        <Link className="brand" href="/">
          <div className="brand-mark">Q</div>
          <div>
            <strong>QCSTS</strong>
            <small>Quality & Stability</small>
          </div>
        </Link>

        <nav>
          <a href="#platform">Platform</a>
          <a href="#quality">Quality</a>
          <a href="#security">Security</a>
        </nav>

        <div className="landing-actions">
          <Link className="btn" href="/login">Sign in</Link>
          <Link className="btn primary" href="/register">
            Start free workspace <ArrowRight size={15} />
          </Link>
        </div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">PHARMACEUTICAL QUALITY OPERATIONS</span>
          <h1>One controlled workspace for stability and quality data.</h1>
          <p>
            QCSTS gives pharmaceutical teams a structured system for stability
            studies, controlled results, quality investigations, auditability
            and organization-level access control.
          </p>

          <div className="hero-actions">
            <Link className="btn primary large" href="/register">
              Create organization <ArrowRight size={16} />
            </Link>
            <Link className="btn large" href="/login">Sign in</Link>
          </div>

          <div className="trust-row">
            <span><CheckCircle2 size={15} /> Multi-tenant SaaS</span>
            <span><CheckCircle2 size={15} /> Role-based access</span>
            <span><CheckCircle2 size={15} /> Validation-ready architecture</span>
          </div>
        </div>

        <div className="hero-panel">
          <div className="panel-head">
            <span>CONTROLLED WORKSPACE</span>
            <b>Operating model</b>
          </div>
          <div className="mini-metrics">
            {["Studies", "Results", "Quality", "Audit"].map((label) => (
              <div key={label}>
                <strong>{label}</strong>
                <b>{label === "Audit" ? "Evidence" : "Workflow"}</b>
                <span>Traceable activity</span>
              </div>
            ))}
          </div>
          <div className="panel-footer">
            <FileCheck2 size={18} />
            <div>
              <strong>Designed for regulated environments</strong>
              <span>Validation, procedures and qualification remain part of the complete compliance lifecycle.</span>
            </div>
          </div>
        </div>
      </section>

      <section id="platform" className="landing-section">
        <div className="section-heading">
          <span className="eyebrow">PLATFORM</span>
          <h2>Built around controlled QC workflows.</h2>
        </div>
        <div className="feature-grid">
          {features.map(([title, copy, Icon]) => (
            <article className="feature-card" key={title}>
              <Icon size={20} />
              <h3>{title}</h3>
              <p>{copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="quality" className="split-section">
        <div>
          <span className="eyebrow">QUALITY CONTROL</span>
          <h2>From planned study to controlled decision.</h2>
          <p>
            Connect master data, stability execution, results, review and
            quality events so teams do not reconstruct batch history from spreadsheets.
          </p>
        </div>
        <div className="workflow">
          <span>Organization</span><i>→</i><span>Study</span><i>→</i>
          <span>Timepoint</span><i>→</i><span>Result</span><i>→</i><span>Review</span>
        </div>
      </section>

      <section id="security" className="security-band">
        <ShieldCheck size={22} />
        <div>
          <strong>Security is enforced by the backend, not the UI.</strong>
          <span>The frontend presents authorized context; Django remains the authorization authority.</span>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="brand">
          <div className="brand-mark">Q</div>
          <strong>QCSTS</strong>
        </div>
        <span>Designed for GxP-regulated environments with a validation-ready architecture.</span>
      </footer>
    </main>
  );
}
