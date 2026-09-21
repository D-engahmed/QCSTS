"use client";
import EntityWorkspace from "@/components/EntityWorkspace";
import { endpoints } from "@/lib/api";
export default function Audit(){return <EntityWorkspace eyebrow="AUDIT TRAIL" title="Audit evidence" description="Read-only organization-scoped audit history. Audit records are not editable from the customer UI." endpoint={endpoints.audit} readonly columns={[{key:"performed_by",label:"User"},{key:"action",label:"Action",sortable:true},{key:"model_name",label:"Object type"},{key:"object_id",label:"Object ID"},{key:"created_at",label:"When",sortable:true} ]}/>}