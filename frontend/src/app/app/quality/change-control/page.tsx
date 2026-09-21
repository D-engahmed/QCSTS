"use client";

import EntityWorkspace from "@/components/EntityWorkspace";
import { endpoints } from "@/lib/api";

export default function ChangeControl() {
  return (
    <EntityWorkspace
      eyebrow="QUALITY"
      title="Change control"
      description="Record proposed controlled changes, their risk assessment and implementation plan."
      endpoint={endpoints.changeControls}
      fields={[
        { key: "reference", label: "Reference", required: true },
        { key: "title", label: "Title", required: true },
        { key: "description", label: "Description", type: "textarea", required: true },
        {
          key: "severity",
          label: "Severity",
          type: "select",
          required: true,
          options: [
            { value: "low", label: "Low" },
            { value: "medium", label: "Medium" },
            { value: "high", label: "High" },
            { value: "critical", label: "Critical" },
          ],
        },
        { key: "change_type", label: "Change type", required: true },
        { key: "current_state", label: "Current state", type: "textarea", required: true },
        { key: "proposed_state", label: "Proposed state", type: "textarea", required: true },
        { key: "risk_assessment", label: "Risk assessment", type: "textarea", required: true },
        { key: "implementation_plan", label: "Implementation plan", type: "textarea" },
        { key: "due_at", label: "Due date", type: "date" },
      ]}
      columns={[
        { key: "reference", label: "Reference", sortable: true },
        { key: "title", label: "Title" },
        { key: "change_type", label: "Type" },
        { key: "status", label: "Status" },
        { key: "due_at", label: "Due" },
      ]}
      transitionStatuses={(row) =>
        row.status === "open"
          ? [{ value: "investigation", label: "Start investigation" }, { value: "canceled", label: "Cancel" }]
          : row.status === "investigation"
            ? [{ value: "pending_approval", label: "Submit for approval" }, { value: "canceled", label: "Cancel" }]
            : row.status === "pending_approval"
              ? [{ value: "approved", label: "Approve" }, { value: "investigation", label: "Return to investigation" }]
              : row.status === "approved"
                ? [{ value: "closed", label: "Close" }]
                : []
      }
    />
  );
}
