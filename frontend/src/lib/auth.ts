"use client";

export type ContextOrganization = { id: string; name: string };
export type ContextSite = { id: string; name: string };

export type User = {
  id: string; email: string; full_name: string;
  organization?: ContextOrganization | null;
  site?: ContextSite | null;
  role?: string | null;
  role_scope?: "SITE" | "ORGANIZATION" | string | null;
  is_active: boolean; created_at: string;
};
export type Organization = {
  id: string; name: string; legal_name?: string; slug: string; country: string;
  timezone: string; currency: string; status: string;
};
export type Site = {
  id: string; organization: string; name: string; address?: string;
  country: string; timezone: string; status: string;
};

const keys = { access:"qc_access_token", refresh:"qc_refresh_token", user:"qc_user" };
export const authStorage = {
  get access(){ return typeof window === "undefined" ? null : localStorage.getItem(keys.access); },
  get refresh(){ return typeof window === "undefined" ? null : localStorage.getItem(keys.refresh); },
  get user(): User | null {
    if (typeof window === "undefined") return null;
    try { const v=localStorage.getItem(keys.user); return v ? JSON.parse(v) : null; } catch { return null; }
  },
  setSession(a:string,r:string,u:User){ localStorage.setItem(keys.access,a); localStorage.setItem(keys.refresh,r); localStorage.setItem(keys.user,JSON.stringify(u)); },
  setUser(u:User){ localStorage.setItem(keys.user,JSON.stringify(u)); },
  clear(){ Object.values(keys).forEach(k=>localStorage.removeItem(k)); }
};
