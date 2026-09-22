import Link from "next/link";
import { ArrowRight, CheckCircle2, FileCheck2, FlaskConical, ShieldCheck, Users, Workflow, PlayCircle } from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";
import ProductExplainer from "@/components/ProductExplainer";

const features = [
  ["Controlled stability workflows", "Studies, protocols, timepoints, samples and results in one traceable lifecycle.", FlaskConical],
  ["Tenant & role isolation", "Organization, site and membership boundaries are enforced by the platform.", Users],
  ["Audit-ready operations", "Controlled records, approvals, signatures and audit evidence stay connected.", ShieldCheck],
  ["Quality investigations", "Connect OOS/OOT, deviations and CAPA to the quality event lifecycle.", Workflow],
] as const;

const workflow = ["Organization", "Product", "Study", "Timepoint", "Result", "Review"];

/** Renders the public landing page with product features and onboarding links. */
export default function Landing() {
  return (
    <main className="landing">
      <header className="landing-nav">
        <Link className="brand" href="/">
          <div className="brand-mark">Q</div>
          <div><strong>QCSTS</strong><small>Quality & Stability</small></div>
        </Link>

        <nav>
          <a href="#platform">Platform</a>
          <a href="#workflow">Workflow</a>
          <a href="#security">Security</a>
        </nav>

        <div className="landing-actions">
          <ThemeToggle />
          <Link className="btn" href="/login">Sign in</Link>
          <Link className="btn primary" href="/register">Create workspace <ArrowRight size={15} /></Link>
        </div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <div className="hero-badge"><span className="pulse-dot" /> Pharmaceutical quality operations</div>
          <span className="eyebrow">QUALITY CONTROL · STABILITY · EVIDENCE</span>
          <h1>Control the workflow. <span>Preserve the evidence.</span></h1>
          <p>
            QCSTS is a multi-tenant quality and stability management workspace for
            pharmaceutical organizations and laboratories — from study setup to controlled review.
          </p>
          <div className="hero-actions">
            <Link className="btn primary large" href="/register">Create your organization <ArrowRight size={16} /></Link>
            <Link className="btn large" href="/login">Sign in</Link>
          </div>
          <div className="trust-row">
            <span><CheckCircle2 size={15} /> Multi-tenant SaaS</span>
            <span><CheckCircle2 size={15} /> Backend-enforced authorization</span>
            <span><CheckCircle2 size={15} /> Validation-ready architecture</span>
          </div>
          <ProductExplainer />
        </div>

        <div className="hero-visual" aria-label="QCSTS product preview">
          <div className="orb orb-a" /><div className="orb orb-b" />
          <div className="dashboard-preview">
            <div className="preview-header"><div><small>QCSTS WORKSPACE</small><strong>Stability overview</strong></div><span className="status active">Live</span></div>
            <div className="preview-stats">
              <div><span>Active studies</span><strong>24</strong><small>Across 3 sites</small></div>
              <div><span>Pending review</span><strong>08</strong><small>Awaiting action</small></div>
              <div><span>Quality events</span><strong>03</strong><small>Tracked to closure</small></div>
            </div>
            <div className="preview-card">
              <div className="preview-card-head"><span>Stability execution</span><small>Current cycle</small></div>
              <div className="preview-line"><span>AMX-250 / STB-024</span><b>On track</b></div>
              <div className="progress"><i /></div>
              <div className="preview-flow">{workflow.slice(1, 6).map((item, index) => <span key={item} className={index < 3 ? "done" : ""}>{item}</span>)}</div>
            </div>
            <div className="preview-audit"><FileCheck2 size={17} /><div><strong>Evidence trail connected</strong><span>Result → review → approval → audit event</span></div></div>
          </div>
        </div>
      </section>

      <section id="platform" className="landing-section">
        <div className="section-heading">
          <span className="eyebrow">ONE SYSTEM, ONE TRACEABLE FLOW</span>
          <h2>Designed for the work your QC team actually has to control.</h2>
          <p>Less reconstruction from spreadsheets. More connected records, ownership and review context.</p>
        </div>
        <div className="feature-grid">
          {features.map(([title, copy, Icon]) => (
            <article className="feature-card" key={title}>
              <div className="feature-icon"><Icon size={19} /></div>
              <h3>{title}</h3><p>{copy}</p><span className="feature-arrow">Explore capability <ArrowRight size={14} /></span>
            </article>
          ))}
        </div>
      </section>

      <section id="workflow" className="workflow-section">
        <div className="section-heading centered">
          <span className="eyebrow">CONTROLLED LIFECYCLE</span>
          <h2>Follow the record from setup to decision.</h2>
          <p>Each stage remains connected instead of becoming another isolated spreadsheet.</p>
        </div>
        <div className="lifecycle">
          {workflow.map((item, index) => (
            <div className="lifecycle-item" key={item}>
              <div className="lifecycle-node">{String(index + 1).padStart(2, "0")}</div>
              <strong>{item}</strong>
              {index < workflow.length - 1 && <span className="lifecycle-line" />}
            </div>
          ))}
        </div>
      </section>

      <section className="explain-band">
        <div><span className="eyebrow">SEE THE PRODUCT</span><h2>Understand the operating model before you create a workspace.</h2><p>Use the guided walkthrough to see how QCSTS connects organization, stability execution, review and evidence.</p></div>
        <ProductExplainer />
      </section>

      <section id="security" className="security-band">
        <ShieldCheck size={22} />
        <div><strong>Security is enforced by the backend, not the UI.</strong><span>Django remains the authorization authority while the frontend presents only the context the current user is allowed to access.</span></div>
      </section>

      <footer className="landing-footer">
        <div className="brand"><div className="brand-mark">Q</div><strong>QCSTS</strong></div>
        <span>Designed for GxP-regulated environments with a validation-ready architecture.</span>
        <div><Link href="/login">Sign in</Link> · <Link href="/register">Create workspace</Link></div>
      </footer>
    </main>
  );
}
