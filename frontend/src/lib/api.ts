import { authStorage } from "./auth";

export type ApiOptions = RequestInit & { token?: string; organizationId?: string; siteId?: string; skipRefresh?: boolean };
export type ApiEnvelope<T> = { success: boolean; data: T; message?: string };
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

/** Converts an API error payload into a user-facing message. */
function errorMessage(payload: unknown, status: number) {
  if (payload && typeof payload === "object") {
    const p = payload as { message?: string; errors?: Record<string,string[]|string> };
    if (p.message) return p.message;
    if (p.errors) return Object.entries(p.errors).map(([k,v]) => k + ": " + (Array.isArray(v) ? v.join(", ") : v)).join(" · ");
  }
  return "Request failed (" + status + ")";
}
/** Exchanges the stored refresh token for a new access token. */
async function refreshAccess() {
  const refresh=authStorage.refresh; if(!refresh) return null;
  const r=await fetch(API_URL+"/auth/token/refresh/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({refresh})});
  if(!r.ok) return null; const p=await r.json(); if(!p.access) return null;
  localStorage.setItem("qc_access_token",p.access); return p.access as string;
}
/** Sends an authenticated, tenant-aware request to the backend API. */
export async function api<T>(path:string, options:ApiOptions={}):Promise<T>{
  const {token,organizationId,siteId,skipRefresh,...init}=options;
  const headers=new Headers(init.headers);
  if(init.body && !headers.has("Content-Type")) headers.set("Content-Type","application/json");
  const access=token ?? authStorage.access; if(access) headers.set("Authorization","Bearer "+access);
  const org=organizationId ?? authStorage.organizationId; const site=siteId ?? authStorage.siteId;
  if(org) headers.set("X-Organization-ID",org); if(site) headers.set("X-Site-ID",site);
  const response=await fetch(API_URL+path,{...init,headers,credentials:"include",cache:"no-store"});
  if(response.status===401 && !skipRefresh && typeof window!=="undefined"){
    const renewed=await refreshAccess();
    if(renewed) return api<T>(path,{...options,token:renewed,skipRefresh:true});
    authStorage.clear(); window.location.assign("/login"); throw new Error("Your session has expired.");
  }
  const text=await response.text();
  const payload=text ? (()=>{try{return JSON.parse(text)}catch{return text}})() : null;
  if(!response.ok) throw new Error(errorMessage(payload,response.status));
  if(response.status===204 || payload===null) return undefined as T;
  return payload as T;
}
export const endpoints={
  login:"/auth/login/",logout:"/auth/logout/",me:"/auth/me/",users:"/auth/users/",
  changePassword:"/auth/change-password/",organizations:"/platform/organizations/",sites:"/platform/sites/",
  dashboard:"/reports/dashboard/",studies:"/stability/studies/",protocols:"/stability/protocols/",
  specifications:"/stability/specifications/",batches:"/batches/",testPoints:"/test-points/",
  samples:"/stability/samples/",timepoints:"/stability/timepoints/",results:"/results/",chambers:"/chamber/",
  audit:"/audit/",oos:"/quality/oos/",oot:"/quality/oot/",deviations:"/quality/deviations/",capa:"/quality/capa/",
  billing:"/billing/subscription/",plans:"/billing/plans/",usage:"/billing/usage/"
};
