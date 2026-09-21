"use client";

import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { api, type ApiEnvelope } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { ErrorBanner } from "@/components/ui/ErrorBanner";

export type WorkspaceField = {
  key: string;
  label: string;
  type?: "text" | "date" | "number" | "textarea" | "select";
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
  optionsEndpoint?: string;
  optionLabel?: string;
};

export type WorkspaceColumn = {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (row: any) => ReactNode;
};

function unwrap<T>(payload: any): T {
  if (payload && typeof payload === "object" && "data" in payload) return payload.data as T;
  return payload as T;
}

function asRows(value: any): any[] {
  if (Array.isArray(value)) return value;
  if (value && Array.isArray(value.results)) return value.results;
  if (value && Array.isArray(value.items)) return value.items;
  return [];
}

export default function EntityWorkspace({
  eyebrow = "WORKSPACE",
  title,
  description,
  endpoint,
  columns,
  fields = [],
  createLabel = "Create record",
  emptyTitle = "No records",
  readonly = false,
  headerAction,
  transformCreate,
}: {
  eyebrow?: string;
  title: string;
  description: string;
  endpoint: string;
  columns: WorkspaceColumn[];
  fields?: WorkspaceField[];
  createLabel?: string;
  emptyTitle?: string;
  readonly?: boolean;
  headerAction?: ReactNode;
  transformCreate?: (data: Record<string, string>) => Record<string, unknown>;
}) {
  const [rows, setRows] = useState<any[]>([]);
  const [values, setValues] = useState<Record<string, string>>({});
  const [options, setOptions] = useState<Record<string, { value: string; label: string }[]>>({});
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = await api<ApiEnvelope<unknown>>(endpoint);
      setRows(asRows(unwrap(payload)));
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to load records.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, [endpoint]);

  const lookupSpec = fields.filter((field) => field.optionsEndpoint).map((field) => `${field.key}:${field.optionsEndpoint}:${field.optionLabel ?? ""}`).join("|");

  useEffect(() => {
    const lookupFields = fields.filter((field) => field.optionsEndpoint);
    if (!lookupFields.length) return;

    let cancelled = false;
    void Promise.all(
      lookupFields.map(async (field) => {
        try {
          const payload = await api<ApiEnvelope<unknown>>(field.optionsEndpoint!);
          const data = asRows(unwrap(payload));
          const result = data.map((item) => ({
            value: String(item.id ?? item.value ?? ""),
            label: String(
              item[field.optionLabel ?? "name"] ??
              item.title ??
              item.code ??
              item.id ??
              "Option",
            ),
          })).filter((item) => item.value);
          if (!cancelled) setOptions((current) => ({ ...current, [field.key]: result }));
        } catch {
          if (!cancelled) setOptions((current) => ({ ...current, [field.key]: [] }));
        }
      }),
    );
    return () => {
      cancelled = true;
    };
  }, [lookupSpec]);

  const filteredRows = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return rows;
    return rows.filter((row) =>
      Object.values(row).some((value) => String(value ?? "").toLowerCase().includes(needle)),
    );
  }, [rows, query]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const payload = transformCreate ? transformCreate(values) : Object.fromEntries(
        Object.entries(values).filter(([, value]) => value !== ""),
      );
      await api(endpoint, { method: "POST", body: JSON.stringify(payload) });
      setValues({});
      setOpen(false);
      await load();
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to create record.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="content">
      <div className="page-header">
        <div>
          <span className="eyebrow">{eyebrow}</span>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>
        <div className="action-row">
          {headerAction}
          {!readonly && fields.length > 0 && (
            <button className="btn primary" onClick={() => setOpen((value) => !value)}>
              {open ? "Close" : createLabel}
            </button>
          )}
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={load} />}

      {open && !readonly && (
        <section className="card form-card" style={{ maxWidth: 760, marginBottom: 14 }}>
          <div className="card-header" style={{ margin: "-20px -20px 8px" }}>
            <div>
              <strong>New {title.replace(/s$/, "")}</strong>
              <span>Server-side validation remains authoritative.</span>
            </div>
          </div>
          <form onSubmit={submit}>
            <div className="form-grid">
              {fields.map((field) => {
                const fieldOptions = field.options ?? options[field.key] ?? [];
                if (field.type === "textarea") {
                  return (
                    <label className="field" key={field.key} style={{ gridColumn: "1 / -1" }}>
                      <span>{field.label}</span>
                      <textarea
                        value={values[field.key] ?? ""}
                        onChange={(event) => setValues((current) => ({ ...current, [field.key]: event.target.value }))}
                        placeholder={field.placeholder}
                        required={field.required}
                      />
                    </label>
                  );
                }

                if (field.type === "select") {
                  return (
                    <label className="field" key={field.key}>
                      <span>{field.label}</span>
                      <select
                        value={values[field.key] ?? ""}
                        onChange={(event) => setValues((current) => ({ ...current, [field.key]: event.target.value }))}
                        required={field.required}
                      >
                        <option value="">Select…</option>
                        {fieldOptions.map((option) => (
                          <option key={option.value} value={option.value}>{option.label}</option>
                        ))}
                      </select>
                    </label>
                  );
                }

                return (
                  <label className="field" key={field.key}>
                    <span>{field.label}</span>
                    <input
                      value={values[field.key] ?? ""}
                      onChange={(event) => setValues((current) => ({ ...current, [field.key]: event.target.value }))}
                      type={field.type ?? "text"}
                      placeholder={field.placeholder}
                      required={field.required}
                    />
                  </label>
                );
              })}
            </div>
            <button className="btn primary" disabled={busy}>
              {busy ? "Saving…" : createLabel}
            </button>
          </form>
        </section>
      )}

      <section className="card table-card">
        <div className="card-header">
          <div>
            <strong>{rows.length} records</strong>
            <span>{loading ? "Loading authorized data…" : "Live API data for the current organization"}</span>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              aria-label="Filter records"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Filter records"
              style={{ border: "1px solid var(--line)", borderRadius: 7, padding: "8px 10px", fontSize: 11 }}
            />
            <button className="btn" onClick={() => void load()}>Refresh</button>
          </div>
        </div>
        <DataTable
          rows={filteredRows}
          columns={columns}
          emptyTitle={loading ? "Loading…" : emptyTitle}
          emptyText={loading ? "":"No authorized records were returned for this workspace."}
        />
      </section>
    </div>
  );
}
