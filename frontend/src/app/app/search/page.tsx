"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import { ErrorBanner } from "@/components/ui/ErrorBanner";

type Hit = { type:string; id:string; title:string; meta:string; href:string };

function list(payload:any): any[] {
  const data = payload?.data ?? payload;
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.items)) return data.items;
  return [];
}

export default function SearchPage() {
  const [hits,setHits] = useState<Hit[]>([]);
  const [loading,setLoading] = useState(true);
  const [error,setError] = useState("");

  useEffect(() => {
    const query = new URLSearchParams(window.location.search).get("q")?.trim().toLowerCase() ?? "";
    if (!query) { setLoading(false); return; }

    const source = [
      { type:"Product", endpoint:endpoints.products, href:"/app/products" },
      { type:"Batch", endpoint:endpoints.batches, href:"/app/batches" },
      { type:"Study", endpoint:endpoints.studies, href:"/app/studies" },
      { type:"Result", endpoint:endpoints.results, href:"/app/results" },
    ];

    Promise.all(source.map(async item => {
      const response = await api<ApiEnvelope<any>>(item.endpoint);
      return list(response)
        .filter(row => Object.values(row).some(value => String(value ?? "").toLowerCase().includes(query)))
        .slice(0, 10)
        .map(row => ({
          type: item.type,
          id: String(row.id),
          title: String(row.name ?? row.batch_number ?? row.test_name ?? row.code ?? "Record"),
          meta: String(row.status ?? row.workflow_state ?? row.product_name ?? ""),
          href: item.type === "Result" ? "/app/results/" + row.id : item.href,
        }));
    })).then(groups => setHits(groups.flat())).catch(value => {
      setError(value instanceof Error ? value.message : "Search failed.");
    }).finally(() => setLoading(false));
  }, []);

  return (
    <div className="content">
      <div className="page-header"><div><span className="eyebrow">SEARCH</span><h1>Workspace search</h1><p>Search only records returned by the current authorized workspace.</p></div></div>
      {error && <ErrorBanner message={error} />}
      <section className="card">
        {loading ? <div className="empty">Searching authorized data…</div> : hits.length ? (
          <div className="list">{hits.map(hit => <Link className="list-row" href={hit.href} key={hit.type + hit.id}><div><b>{hit.title}</b><span>{hit.type} · {hit.meta}</span></div><span className="btn">Open</span></Link>)}</div>
        ) : <div className="empty"><b>No matches</b><span>No authorized record matched your query.</span></div>}
      </section>
    </div>
  );
}
