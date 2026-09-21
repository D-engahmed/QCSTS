"use client";

import EntityWorkspace from "@/components/EntityWorkspace";
import { endpoints } from "@/lib/api";

export default function CAPA() {
  return (
    <EntityWorkspace
      eyebrow="QUALITY"
      title="CAPA"
      description="Create corrective and preventive actions with effectiveness-check fields."
      endpoint={endpoints.capa}
      fields={[
        { key:"reference", label:"Reference", required:true },
        { key:"title", label:"Title", required:true },
        { key:"description", label:"Description", type:"textarea", required:true },
        { key:"severity", label:"Severity", type:"select", required:true, options:[
          {value:"low",label:"Low"},{value:"medium",label:"Medium"},{value:"high",label:"High"},{value:"critical",label:"Critical"}
        ]},
        { key:"source_deviation", label:"Source deviation", type:"select", optionsEndpoint:endpoints.deviations },
        { key:"corrective_action", label:"Corrective action", type:"textarea", required:true },
        { key:"preventive_action", label:"Preventive action", type:"textarea" },
        { key:"effectiveness_check", label:"Effectiveness check", type:"textarea" },
        { key:"effectiveness_due_at", label:"Effectiveness due", type:"date" },
      ]}
      columns={[
        {key:"reference",label:"Reference",sortable:true},
        {key:"title",label:"Title"},
        {key:"severity",label:"Severity"},
        {key:"status",label:"Status"},
        {key:"effectiveness_due_at",label:"Effectiveness due"},
      ]}
      transitionStatuses={(row) =>
        row.status==="open"
          ? [{value:"investigation",label:"Start investigation"},{value:"canceled",label:"Cancel"}]
          : row.status==="investigation"
            ? [{value:"pending_approval",label:"Submit for approval"},{value:"canceled",label:"Cancel"}]
            : row.status==="pending_approval"
              ? [{value:"approved",label:"Approve"},{value:"investigation",label:"Return to investigation"}]
              : row.status==="approved"
                ? [{value:"closed",label:"Close"}]
                : []
      }
    />
  );
}
