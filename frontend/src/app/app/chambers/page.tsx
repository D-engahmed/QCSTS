"use client";
import EntityWorkspace from "@/components/EntityWorkspace";
import { endpoints } from "@/lib/api";
export default function Chambers(){return <EntityWorkspace eyebrow="CHAMBER" title="Chamber inventory" description="View authorized batch locations and current quantities. Movement remains a controlled backend operation." endpoint={endpoints.chambers} readonly columns={[{key:"batch_number",label:"Batch",sortable:true},{key:"product_name",label:"Product"},{key:"location",label:"Location"},{key:"qty_remaining",label:"Remaining"},{key:"status",label:"Status"}]}/>}