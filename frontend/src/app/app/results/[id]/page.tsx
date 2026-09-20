"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import { authStorage } from "@/lib/auth";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { SignaturePanel } from "@/components/ui/SignaturePanel";
import { useToast } from "@/components/ui/Toast";
import { ErrorBanner } from "@/components/ui/ErrorBanner";

type Result = {
  id: string;
  test_point?: string;
  monograph_test?: string;
  test_name?: string;
  value?: string;
  unit?: string;
  specification_snapshot?: string;
  pass_fail?: string;
  analyst?: string;
  analyst_name?: string;
  submitted_at?: string;
  created_at?: string;
  notes?: string;
  workflow_state?: string;
};

function displayWorkflow(value?: string) {
  return String(value || "unknown")
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default function ResultDetail() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { show } = useToast();

  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [action, setAction] = useState<"Review" | "Approve" | "Reject" | "Request Correction" | null>(null);
  const [pending, setPending] = useState(false);

  const user = authStorage.user;
  const role = String(user?.role || user?.organization_role || "").toLowerCase();

  const load = async () => {
    try {
      setError("");
      const response = await api<ApiEnvelope<Result[]>>(endpoints.results);
      const rows = Array.isArray(response.data) ? response.data : [];
      const found = rows.find((item) => String(item.id) === String(id));

      if (!found) {
        setError("The requested result could not be found in your authorized workspace.");
        return;
      }

      setResult(found);
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to load the result.");
    }
  };

  useEffect(() => {
    void load();
  }, [id]);

  if (error) {
    return (
      <div className="content">
        <ErrorBanner message={error} onRetry={load} />
      </div>
    );
  }

  if (!result) {
    return <div className="content"><div className="empty">Loading result…</div></div>;
  }

  const state = String(result.workflow_state || "").toLowerCase();

  const canReview =
    state === "submitted" &&
    ["supervisor", "qa_manager", "admin"].includes(role) &&
    result.analyst !== user?.id;

  const canApproveOrReject =
    state === "under_review" &&
    ["qa_manager", "admin"].includes(role) &&
    result.analyst !== user?.id;

  const canCorrect =
    ["approved", "rejected", "under_review"].includes(state) &&
    ["analyst", "supervisor", "qa_manager", "admin"].includes(role);

  async function transition(reason: string, password: string, correctedValue?: string) {
    if (!action) return;

    setPending(true);
    setError("");

    try {
      const signature = await api<ApiEnvelope<{ signature_token: string }>>(
        endpoints.results + "/signature/verify/",
        {
          method: "POST",
          body: JSON.stringify({ password }),
        },
      );

      const signatureToken = signature.data.signature_token;

      if (!signatureToken) {
        throw new Error("The server did not issue a signature token.");
      }

      const path =
        action === "Review"
          ? "review"
          : action === "Approve"
            ? "approve"
            : action === "Reject"
              ? "reject"
              : "correct";

      const body =
        action === "Review"
          ? { comments: reason }
          : action === "Approve"
            ? { comments: reason }
            : action === "Reject"
              ? { comments: reason }
              : {
                  reason,
                  value: correctedValue,
                  unit: result.unit || "",
                  notes: result.notes || "",
                };

      const response = await api<ApiEnvelope<any>>(
        endpoints.results + "/" + id + "/" + path + "/",
        {
          method: "POST",
          headers: { "X-Signature-Token": signatureToken },
          body: JSON.stringify(body),
        },
      );

      if (action === "Request Correction") {
        const corrected = response.data?.corrected_result;
        if (corrected) setResult(corrected);
      }

      show(
        action === "Review"
          ? "Supervisor review recorded."
          : action === "Approve"
            ? "Result approved."
            : action === "Reject"
              ? "Result rejected."
              : "Correction recorded.",
      );

      setAction(null);
      await load();

      if (action === "Request Correction") {
        router.refresh();
      }
    } catch (value) {
      setError(
        value instanceof Error
          ? value.message
          : "The controlled action could not be completed.",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="content">
      <div className="breadcrumb">
        <Link href="/app/results">Results & Review</Link>
        <span>/</span>
        <span>{result.id}</span>
      </div>

      <header className="detail-header">
        <div>
          <span className="eyebrow">TEST RESULT</span>
          <h1>{result.test_name || "Test result"}</h1>
          <div className="detail-meta">
            {result.id} · {result.analyst_name || "Unknown analyst"}
          </div>
        </div>
        <StatusBadge status={displayWorkflow(result.workflow_state)} />
      </header>

      <div className="action-row">
        {canReview && (
          <button className="btn" onClick={() => setAction("Review")}>
            Review
          </button>
        )}

        {canApproveOrReject && (
          <>
            <button className="btn approve" onClick={() => setAction("Approve")}>
              Approve
            </button>
            <button className="btn reject" onClick={() => setAction("Reject")}>
              Reject
            </button>
          </>
        )}

        {canCorrect && (
          <button className="btn correction" onClick={() => setAction("Request Correction")}>
            Request Correction
          </button>
        )}
      </div>

      <div className="detail-grid">
        <section className="card detail-card">
          <h2>Overview</h2>
          <dl>
            <dt>Result</dt>
            <dd>{result.value ?? "—"} {result.unit || ""}</dd>
            <dt>Specification</dt>
            <dd>{result.specification_snapshot || "—"}</dd>
            <dt>Pass / Fail</dt>
            <dd>{result.pass_fail || "—"}</dd>
            <dt>Test point</dt>
            <dd>{result.test_point || "—"}</dd>
            <dt>Submitted</dt>
            <dd>{result.submitted_at ? new Date(result.submitted_at).toLocaleString() : "—"}</dd>
          </dl>
        </section>

        <section className="card detail-card">
          <h2>Controlled state</h2>
          <dl>
            <dt>Workflow</dt>
            <dd>{displayWorkflow(result.workflow_state)}</dd>
            <dt>Analyst</dt>
            <dd>{result.analyst_name || "—"}</dd>
            <dt>Notes</dt>
            <dd>{result.notes || "—"}</dd>
          </dl>
          <p className="muted">
            Workflow transitions are authorized and recorded by Django. The frontend only
            exposes actions applicable to the authenticated role and current state.
          </p>
        </section>
      </div>

      {error && <div className="inline-error">{error}</div>}

      <section className="card detail-card">
        <div className="tabs">
          <button className="active">Overview</button>
          <button disabled>Audit Trail</button>
          <button disabled>Attachments</button>
        </div>
        <div className="empty">
          Audit and attachment views require their dedicated backend read APIs before the
          frontend can display them without inventing records.
        </div>
      </section>

      {action && (
        <SignaturePanel
          action={action}
          onCancel={() => setAction(null)}
          onConfirm={(reason, password, value) => transition(reason, password, value)}
          pending={pending}
          requiresReason={action !== "Review" || true}
          requiresValue={action === "Request Correction"}
        />
      )}
    </div>
  );
}
