"use client";

import { CheckCircle2, ChevronRight, Play, X } from "lucide-react";
import { useEffect, useState } from "react";

const steps = [
  ["01", "Create a controlled workspace", "Organization, primary site and owner membership are created as one onboarding transaction."],
  ["02", "Run the stability workflow", "Products, batches, protocols, timepoints, samples and results stay connected."],
  ["03", "Review and preserve evidence", "Approvals, signatures, quality events and audit history remain traceable."],
];

export default function ProductExplainer() {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (!open) return;
    const timer = window.setInterval(() => setStep((current) => (current + 1) % steps.length), 3600);
    return () => window.clearInterval(timer);
  }, [open]);

  return (
    <>
      <button className="explainer-card" type="button" onClick={() => { setStep(0); setOpen(true); }}>
        <span className="explainer-play"><Play size={18} fill="currentColor" /></span>
        <span>
          <strong>See QCSTS in action</strong>
          <small>2-minute product walkthrough</small>
        </span>
        <ChevronRight size={17} />
      </button>

      {open && (
        <div className="video-modal" role="dialog" aria-modal="true" aria-label="QCSTS product walkthrough">
          <button className="video-backdrop" onClick={() => setOpen(false)} aria-label="Close walkthrough" />
          <section className="video-window">
            <button className="video-close" type="button" onClick={() => setOpen(false)} aria-label="Close"><X size={18} /></button>
            <div className="video-screen">
              <div className="video-topbar"><span className="video-dot" /><span>QCSTS · Controlled workspace</span><span>Product walkthrough</span></div>
              <div className="video-content">
                <div className="video-kicker">QCSTS WORKFLOW</div>
                <h3>{steps[step][1]}</h3>
                <p>{steps[step][2]}</p>
                <div className="video-flow">
                  {["Organization", "Study", "Result", "Review"].map((item, index) => (
                    <div className={"video-node " + (index <= step ? "active" : "")} key={item}>
                      <CheckCircle2 size={15} /> {item}
                    </div>
                  ))}
                </div>
              </div>
              <div className="video-progress">
                {steps.map((_, index) => <span key={index} className={index === step ? "active" : ""} />)}
              </div>
            </div>
            <div className="video-caption"><span>{steps[step][0]}</span><span>{steps[step][1]}</span><span>Auto-playing walkthrough</span></div>
          </section>
        </div>
      )}
    </>
  );
}
