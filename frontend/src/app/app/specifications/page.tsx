"use client";
import EntityWorkspace from "@/components/EntityWorkspace";
import { endpoints } from "@/lib/api";
export default function Specifications(){return <EntityWorkspace eyebrow="STABILITY" title="Specifications" description="Controlled product specification identities. Versioned limits remain separate and traceable." endpoint={endpoints.specifications} fields={[{key:"code",label:"Specification code",required:true},{key:"name",label:"Specification name",required:true},{key:"product",label:"Product",type:"select",required:true,optionsEndpoint: endpoints.products},{key:"description",label:"Description",type:"textarea"}]} columns={[{key:"code",label:"Code",sortable:true},{key:"name",label:"Name"},{key:"product",label:"Product"},{key:"status",label:"Status"}]}/>}
