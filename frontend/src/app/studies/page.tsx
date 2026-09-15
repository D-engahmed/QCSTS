import { ChevronRight, Filter, FlaskConical, Plus, Search, SlidersHorizontal } from "lucide-react";

const studies = [
  ["STB-2026-0042", "Amoxicillin 500 mg Capsules", "AMX-26-008", "Cairo", "Protocol v2.1", "Active", "30 Sep 2026"],
  ["STB-2026-0041", "Paracetamol 500 mg Tablets", "PCM-26-014", "Giza", "Protocol v1.4", "At Risk", "21 Sep 2026"],
  ["STB-2026-0039", "Omeprazole 20 mg Capsules", "OMP-26-005", "Cairo", "Protocol v3.0", "Active", "02 Oct 2026"],
  ["STB-2026-0037", "Azithromycin 500 mg Tablets", "AZM-26-002", "Alexandria", "Protocol v2.0", "Active", "05 Oct 2026"],
  ["STB-2026-0032", "Metformin 500 mg Tablets", "MET-26-021", "Cairo", "Protocol v1.8", "Completed", "—"],
];

export default function StudiesPage() {
  return <main className="content">
    <section className="page-heading">
      <div><div className="eyebrow">Stability</div><h1>Stability Studies</h1><p className="subtitle">Controlled study records, protocols, batches, timepoints and results.</p></div>
      <div className="actions"><button className="btn"><SlidersHorizontal size={14}/> Saved view</button><button className="btn"><Filter size={14}/> Filters</button><button className="btn primary"><Plus size={14}/> New study</button></div>
    </section>
    <div className="card">
      <div className="card-header"><div className="search" style={{width:360}}><Search size={14}/><input placeholder="Search study ID, product, batch..."/></div><div style={{fontSize:11,color:"var(--muted)"}}>24 active studies</div></div>
      <div className="table-wrap"><table><thead><tr><th>Study</th><th>Product</th><th>Batch</th><th>Site</th><th>Protocol</th><th>Status</th><th>Next timepoint</th><th></th></tr></thead><tbody>{studies.map((s) => <tr key={s[0]}><td><div style={{display:"flex",alignItems:"center",gap:8}}><div className="avatar" style={{width:28,height:28,borderRadius:7}}><FlaskConical size={13}/></div><strong>{s[0]}</strong></div></td><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td><td>{s[4]}</td><td><span className={`badge ${s[5] === "At Risk" ? "warning" : s[5] === "Completed" ? "neutral" : "active"}`}>{s[5]}</span></td><td>{s[6]}</td><td><button className="icon-button"><ChevronRight size={15}/></button></td></tr>)}</tbody></table></div>
    </div>
  </main>;
}
