"use client";
import { useState } from "react"; import { CreateStudyWizard } from "@/components/DataWorkspace";
export default function NewStudy(){const [open]=useState(true);return <div className="content"><div className="page-header"><div><div className="eyebrow">Stability</div><h1>New stability study</h1><p>Build a controlled study from effective protocol and specification versions.</p></div></div>{open&&<CreateStudyWizard onClose={()=>window.location.href="/studies"}/>}</div>}
