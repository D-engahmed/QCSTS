"use client";

import { useState } from "react";

export function SignaturePanel({
  action,
  onCancel,
  onConfirm,
  requiresReason = true,
  requiresValue = false,
  pending = false,
}: {
  action: string;
  onCancel: () => void;
  onConfirm: (reason: string, password: string, value?: string) => void;
  requiresReason?: boolean;
  requiresValue?: boolean;
  pending?: boolean;
}) {
  const [password, setPassword] = useState("");
  const [reason, setReason] = useState("");
  const [value, setValue] = useState("");

  const canSubmit =
    password.trim().length > 0 &&
    (!requiresReason || reason.trim().length > 0) &&
    (!requiresValue || value.trim().length > 0);

  return (
    <div className="modal-backdrop">
      <section
        className="signature-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="signature-title"
      >
        <span className="eyebrow">CONTROLLED ACTION</span>
        <h2 id="signature-title">{action}</h2>
        <p>Re-confirm your identity before recording this controlled action.</p>

        {requiresValue && (
          <label className="field">
            <span>Corrected result value</span>
            <input
              autoFocus
              value={value}
              onChange={(event) => setValue(event.target.value)}
              placeholder="Enter the corrected value"
            />
          </label>
        )}

        <label className="field">
          <span>Password</span>
          <input
            autoFocus={!requiresValue}
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>

        {requiresReason && (
          <label className="field">
            <span>Reason / comments</span>
            <textarea
              required
              value={reason}
              onChange={(event) => setReason(event.target.value)}
              placeholder="Enter the reason for this action"
            />
          </label>
        )}

        <div className="modal-actions">
          <button className="btn" onClick={onCancel} disabled={pending}>
            Cancel
          </button>
          <button
            className="btn primary"
            disabled={!canSubmit || pending}
            onClick={() => onConfirm(reason, password, value)}
          >
            {pending ? "Recording…" : action}
          </button>
        </div>
      </section>
    </div>
  );
}
