import Link from "next/link";
import { ArrowDownRight, ArrowRight, CheckCircle2, FileCheck2, FlaskConical, ShieldCheck } from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";
import ProductExplainer from "@/components/ProductExplainer";

const capabilities = [
  ["01", "Stability, without the spreadsheet maze.", "Products, batches, protocols, timepoints, samples and results stay connected through one controlled workflow."],
  ["02", "Quality evidence, where the work happens.", "Review, approvals, audit events and quality investigations remain attached to the records that created them."],
  ["03", "One organization. Clear boundaries.", "Sites, memberships, roles and entitlements are isolated by the backend—not by assumptions in the UI."],
];

const lifecycle = ["Organization", "Product", "Study", "Timepoint", "Result", "Review"];

export default function Landing() {
  return (
    <main className="landing qcsts-editorial">
      <header className="landing-nav">
        <Link className="brand" href="/">
          <div className="brand-mark">Q</div>
          <div><strong>QCSTS</strong><small>Quality & Stability</small></div>
        </Link>

        <nav aria-label="Primary">
          <a href="#watch">Product</a>
          <a href="#workflow">How it works</a>
          <a href="#security">Control</a>
        </nav>

        <div className="landing-actions">
          <ThemeToggle />
          <Link className="landing-signin" href="/login">Sign in</Link>
          <Link className="btn primary" href="/register">Create workspace <ArrowRight size={15} /></Link>
        </div>
      </header>

      <section className="hero anytime-hero">
        <div className="hero-copy">
          <span className="hero-kicker"><span className="pulse-dot" /> PHARMACEUTICAL QUALITY OPERATIONS</span>
          <h1>Quality work.<br /><span>Controlled end to end.</span></h1>
          <p className="hero-lede">
            QCSTS gives pharmaceutical organizations and laboratories one connected workspace for quality control and stability testing—from setup to review, with the evidence preserved along the way.
          </p>
          <div className="hero-actions">
            <Link className="btn primary large" href="/register">Create your organization <ArrowRight size={16} /></Link>
            <a className="watch-link" href="#watch"><span className="watch-play">▶</span> See how QCSTS works</a>
          </div>
          <div className="hero-proof">
            <span><CheckCircle2 size={14} /> Multi-tenant by design</span>
            <span><CheckCircle2 size={14} /> Backend-enforced access</span>
            <span><CheckCircle2 size={14} /> Validation-ready architecture</span>
          </div>
        </div>

        <div className="hero-visual" aria-label="QCSTS stability workspace preview">
          <div className="hero-visual-label">A LOOK AT WHAT COMES NEXT</div>
          <div className="product-window">
            <div className="product-window-top">
              <span>QCSTS</span><span className="window-status">● LIVE WORKSPACE</span>
            </div>
            <div className="product-window-title">
              <div><small>STABILITY OVERVIEW</small><strong>Current studies</strong></div>
              <span>3 sites · 24 active</span>
            </div>
            <div className="preview-calendar">
              {["MON", "TUE", "WED", "THU", "FRI"].map((day) => <span key={day}>{day}</span>)}
              <div className="calendar-line"><b>AMX-250</b><i>Timepoint 06M</i><em>Under review</em></div>
              <div className="calendar-line"><b>PAR-100</b><i>Timepoint 03M</i><em>On track</em></div>
              <div className="calendar-line"><b>MET-500</b><i>Timepoint 12M</i><em>Approved</em></div>
            </div>
            <div className="product-evidence"><FileCheck2 size={16} /><div><strong>Evidence trail connected</strong><span>Result → review → approval → audit event</span></div><ArrowRight size={15} /></div>
          </div>
        </div>
      </section>

      <section id="watch" className="watch-section">
        <div className="section-heading centered">
          <span className="eyebrow">FROM FIRST RECORD TO CONTROLLED DECISION</span>
          <h2>One workflow. No reconstruction later.</h2>
          <p>QCSTS is built around the actual chain of work, so context does not disappear between systems, spreadsheets and approvals.</p>
        </div>
        <ProductExplainer />
      </section>

      <section className="so-section"><div className="so-mark">SO</div><div><span className="eyebrow">ONE SYSTEM · EVERY RECORD CONNECTED</span><h2>From first record to controlled decision.</h2><p>Products, studies, results, review and evidence stay in the same operational thread.</p></div></section>

      <section id="workflow" className="capability-section">
        <div className="section-heading">
          <span className="eyebrow">THE OPERATING MODEL</span>
          <h2>We run the record.<br /><span>You keep the decision.</span></h2>
        </div>
        <div className="capability-list">
          {capabilities.map(([number, title, copy]) => (
            <article className="capability-row" key={number}>
              <span className="capability-number">{number}</span>
              <div><h3>{title}</h3><p>{copy}</p></div>
              <ArrowDownRight size={20} />
            </article>
          ))}
        </div>
      </section>

      <section className="lifecycle-section">
        <div className="section-heading centered">
          <span className="eyebrow">CONTROLLED LIFECYCLE</span>
          <h2>Every handoff stays visible.</h2>
        </div>
        <div className="lifecycle">
          {lifecycle.map((item, index) => (
            <div className="lifecycle-item" key={item}>
              <div className="lifecycle-node">{String(index + 1).padStart(2, "0")}</div>
              <strong>{item}</strong>
              {index < lifecycle.length - 1 && <span className="lifecycle-line" />}
            </div>
          ))}
        </div>
      </section>

      <section className="process-section">
        <div className="section-heading centered">
          <span className="eyebrow">HOW QCSTS WORKS</span>
          <h2>One team. Every quality handoff covered.</h2>
          <p>The platform follows the work in the same sequence your team does—without forcing the record into disconnected tools.</p>
        </div>
        <div className="process-grid">
          <article><span>01</span><h3>Set up the foundation.</h3><p>Create the organization, site, memberships and controlled workspace.</p><div className="mock-panel"><b>ABC Pharma</b><small>CAIRO QC LAB · OWNER</small><i>Workspace ready</i></div></article>
          <article><span>02</span><h3>Run the study.</h3><p>Connect product, batch, protocol, timepoints, samples and chamber activity.</p><div className="mock-panel"><b>AMX-250 / STB-024</b><small>06M · 25°C / 60% RH</small><i>On track</i></div></article>
          <article><span>03</span><h3>Review the result.</h3><p>Move records through controlled review, approval and correction states.</p><div className="mock-panel"><b>Result #02491</b><small>SUBMITTED · QA REVIEW</small><i>Awaiting review</i></div></article>
          <article><span>04</span><h3>Preserve the evidence.</h3><p>Keep audit events, signatures and quality investigations attached to the work.</p><div className="mock-panel"><b>Evidence trail</b><small>RESULT → REVIEW → APPROVAL</small><i>Traceable</i></div></article>
        </div>
      </section>

      <section id="security" className="control-section">
        <div className="control-icon"><ShieldCheck size={24} /></div>
        <div>
          <span className="eyebrow">CONTROL IS A SYSTEM PROPERTY</span>
          <h2>Security is enforced by the backend—not painted onto the interface.</h2>
          <p>Organization isolation, site boundaries, roles, entitlements and controlled records are authoritative in Django. The frontend only exposes the context the current user is allowed to access.</p>
        </div>
        <div className="control-points">
          <span><FlaskConical size={15} /> Stability workflows</span>
          <span><ShieldCheck size={15} /> Tenant isolation</span>
          <span><FileCheck2 size={15} /> Audit evidence</span>
        </div>
      </section>

      <section className="faq-section">
        <div className="section-heading"><span className="eyebrow">GOOD QUESTIONS</span><h2>What should a quality platform make obvious?</h2></div>
        <div className="faq-list">
          <details open><summary>Who owns the authorization decision?</summary><p>Django is authoritative for authentication, tenant isolation, roles and entitlements. The frontend does not decide whether a user is allowed to access a record.</p></details>
          <details><summary>Can one organization see another organization's records?</summary><p>The tenant model is designed around organization boundaries, site-scoped memberships and backend-enforced access checks.</p></details>
          <details><summary>Is QCSTS a GxP certification?</summary><p>No. QCSTS is designed for GxP-regulated environments with a validation-ready architecture; deployment, validation and procedural controls remain the customer's responsibility.</p></details>
          <details><summary>What happens when a result needs correction?</summary><p>The workflow keeps review and correction context attached to the controlled record rather than silently overwriting the history.</p></details>
        </div>
      </section>

      <section className="final-cta">
        <span className="eyebrow">READY WHEN YOUR QC TEAM IS</span>
        <h2>Bring quality work into one controlled flow.</h2>
        <p>Create an organization workspace and start building the operating record your team can actually trust.</p>
        <div className="hero-actions">
          <Link className="btn primary large" href="/register">Create your organization <ArrowRight size={16} /></Link>
          <Link className="btn large" href="/login">Sign in</Link>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="brand"><div className="brand-mark">Q</div><strong>QCSTS</strong></div>
        <span>Designed for GxP-regulated environments with a validation-ready architecture.</span>
        <div><Link href="/login">Sign in</Link> · <Link href="/register">Create workspace</Link></div>
      </footer>
    </main>
  );
}
