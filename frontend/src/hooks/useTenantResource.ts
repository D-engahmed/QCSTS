"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export function useTenantResource<T>(path: string, fallback: T, enabled=true) {
  const [data,setData]=useState<T>(fallback); const [loading,setLoading]=useState(enabled); const [error,setError]=useState<string | null>(null);
  useEffect(()=>{if(!enabled)return;let cancelled=false;setLoading(true);api<T>(path).then(value=>{if(!cancelled)setData(value)}).catch(e=>{if(!cancelled)setError(e instanceof Error?e.message:"Request failed")}).finally(()=>{if(!cancelled)setLoading(false)});return()=>{cancelled=true}},[path,enabled]);
  return {data,setData,loading,error,refresh:()=>{setLoading(true);api<T>(path).then(setData).catch(e=>setError(e instanceof Error?e.message:"Request failed")).finally(()=>setLoading(false))}};
}
