"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { StatusBadge } from "@/components/ui/StatusBadge";

type ResultRow = {
  id: string;
  test_name?: string;
  value?: string;
  unit?: string;
  pass_fail?: string;
  workflow_state?: string;
  test_point?: string;
  analyst_name?: string;
  submitted_at?: string;
};

function workflowLabel(value?: string) {
  return String(value || "unknown")
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default function Results() {
  const router = useRouter();
  const [rows, setRows] = useState<ResultRow[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api<ApiEnvelope<ResultRow[]>>(endpoints.results);
      setRows(Array.isArray(response.data) ? response.data : []);
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to load results.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="content">
      <div className="page-header">
        <div>
          <span className="eyebrow">RESULTS</span>
          <h1>Results & Review</h1>
          <p>Live controlled test results returned by the QCSTS API for your authorized workspace.</p>
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={load} />}

      <section className="card">
        <DataTable
          rows={rows}
          columns={[
            {
              key: "test_name",
              label: "Test",
              sortable: true,
              render: (row) => <b>{row.test_name || "Test result"}</b>,
            },
            {
              key: "value",
              label: "Value",
              sortable: true,
              render: (row) => row.value ? row.value + (row.unit ? " " + row.unit : "") : "—",
            },
            {
              key: "pass_fail",
              label: "Outcome",
              sortable: true,
              render: (row) => row.pass_fail || "—",
            },
            {
              key: "workflow_state",
              label: "Workflow",
              sortable: true,
              render: (row) => <StatusBadge status={workflowLabel(row.workflow_state)} />,
            },
            {
              key: "analyst_name",
              label: "Analyst",
              sortable: true,
              render: (row) => row.analyst_name || "—",
            },
            {
              key: "submitted_at",
              label: "Submitted",
              sortable: true,
              render: (row) =>
                row.submitted_at ? new Date(row.submitted_at).toLocaleString() : "—",
            },
          ]}
          onRowClick={(row) => router.push("/app/results/" + row.id)}
          emptyTitle={loading ? "Loading results…" : "No results yet"}
          emptyText={
            loading
              ? ""
              : "No authorized test results were returned by the backend."
          }
        />
      </section>
    </div>
  );
}
