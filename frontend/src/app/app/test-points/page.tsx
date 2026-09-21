"use client";
import EntityWorkspace from "@/components/EntityWorkspace";
import { endpoints } from "@/lib/api";
export default function TestPoints(){return <EntityWorkspace eyebrow="SCHEDULE" title="Test points" description="Server-generated stability schedule. Status and dates are authoritative backend data." endpoint={endpoints.testPoints} readonly columns={[{key:"batch_number",label:"Batch",sortable:true},{key:"product_name",label:"Product"},{key:"month",label:"Month",sortable:true},{key:"scheduled_date",label:"Scheduled date",sortable:true},{key:"status",label:"Status"}]}/>}