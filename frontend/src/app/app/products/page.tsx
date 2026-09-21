"use client";

import EntityWorkspace from "@/components/EntityWorkspace";
import { endpoints } from "@/lib/api";

export default function Products() {
  return (
    <EntityWorkspace
      eyebrow="MASTER DATA"
      title="Products"
      description="Maintain authorized pharmaceutical product master data. Product records are organization-scoped and validated by Django."
      endpoint={endpoints.products}
      fields={[
        { key: "name", label: "Product name", required: true },
        { key: "strength", label: "Strength", required: true, placeholder: "500 mg" },
        {
          key: "dosage_form",
          label: "Dosage form",
          type: "select",
          required: true,
          options: [
            ["tablet", "Tablet"], ["capsule", "Capsule"], ["syrup", "Syrup"],
            ["injection", "Injection"], ["cream", "Cream"], ["ointment", "Ointment"],
            ["gel", "Gel"], ["suppository", "Suppository"], ["suspension", "Suspension"],
            ["solution", "Solution"],
          ].map(([value, label]) => ({ value, label })),
        },
        {
          key: "monograph",
          label: "Approved monograph",
          type: "select",
          optionsEndpoint: endpoints.monographs,
        },
      ]}
      columns={[
        { key: "name", label: "Product", sortable: true },
        { key: "strength", label: "Strength" },
        { key: "dosage_form", label: "Dosage form" },
        { key: "monograph_name", label: "Monograph" },
        {
          key: "is_active",
          label: "Status",
          render: (row) => (
            <span className={"status " + (row.is_active ? "active" : "critical")}>
              {row.is_active ? "Active" : "Inactive"}
            </span>
          ),
        },
      ]}
    />
  );
}
