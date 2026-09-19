"use client";
import {createContext,useContext,useEffect,useMemo,useState} from "react";
import {api,endpoints,type ApiEnvelope} from "@/lib/api";
import {authStorage} from "@/lib/auth";
import type {User,Organization,Site} from "@/lib/auth";
type C={user:User|null;organizations:Organization[];sites:Site[];organization:Organization|null;site:Site|null;loading:boolean;login:(e:string,p:string)=>Promise<void>;logout:()=>Promise<void>;selectOrganization:(id:string)=>Promise<void>;selectSite:(id:string|null)=>void};
const AuthContext=createContext<C|null>(null);
export function AuthProvider({children}:{children:React.ReactNode}){
 const [user,setUser]=useState<User|null>(authStorage.user),[organizations,setOrganizations]=useState<Organization[]>([]),[sites,setSites]=useState<Site[]>([]),[loading,setLoading]=useState(true);
 const load=async()=>{if(!authStorage.access){setLoading(false);return}try{
  const me=await api<ApiEnvelope<User>>(endpoints.me);setUser(me.data);authStorage.setUser(me.data);
  const orgs=await api<ApiEnvelope<Organization[]>>(endpoints.organizations);setOrganizations(orgs.data||[]);
  const org=orgs.data?.find(x=>x.id===authStorage.organizationId)||orgs.data?.[0];
  if(org){authStorage.setOrganization(org.id);const ss=await api<ApiEnvelope<Site[]>>(endpoints.sites,{organizationId:org.id});setSites(ss.data||[]);if(!ss.data?.some(x=>x.id===authStorage.siteId))authStorage.setSite(ss.data?.[0]?.id||null)}
 }catch{authStorage.clear();setUser(null)}finally{setLoading(false)}};
 useEffect(()=>{void load()},[]);
 const login=async(email:string,password:string)=>{const r=await api<ApiEnvelope<{access:string;refresh:string;user:User}>>(endpoints.login,{method:"POST",body:JSON.stringify({email,password}),skipRefresh:true});authStorage.setSession(r.data.access,r.data.refresh,r.data.user);setUser(r.data.user);const os=await api<ApiEnvelope<Organization[]>>(endpoints.organizations,{token:r.data.access});setOrganizations(os.data||[]);if(os.data?.[0]){authStorage.setOrganization(os.data[0].id);const ss=await api<ApiEnvelope<Site[]>>(endpoints.sites,{token:r.data.access,organizationId:os.data[0].id});setSites(ss.data||[]);authStorage.setSite(ss.data?.[0]?.id||null)}};
 const logout=async()=>{try{if(authStorage.refresh)await api(endpoints.logout,{method:"POST",body:JSON.stringify({refresh:authStorage.refresh}),skipRefresh:true})}finally{authStorage.clear();setUser(null);window.location.assign("/login")}};
 const selectOrganization=async(id:string)=>{authStorage.setOrganization(id);authStorage.setSite(null);const r=await api<ApiEnvelope<Site[]>>(endpoints.sites,{organizationId:id});setSites(r.data||[]);authStorage.setSite(r.data?.[0]?.id||null)};
 const value=useMemo(()=>({user,organizations,sites,organization:organizations.find(x=>x.id===authStorage.organizationId)||null,site:sites.find(x=>x.id===authStorage.siteId)||null,loading,login,logout,selectOrganization,selectSite:(id:string|null)=>authStorage.setSite(id)}),[user,organizations,sites,loading]);
 return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth(){const c=useContext(AuthContext);if(!c)throw new Error("useAuth must be used inside AuthProvider");return c}
