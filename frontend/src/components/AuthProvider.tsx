"use client";
import {createContext,useContext,useEffect,useMemo,useState} from "react";
import {api,endpoints,type ApiEnvelope} from "@/lib/api";
import {authStorage} from "@/lib/auth";
import type {User,Organization,Site} from "@/lib/auth";

type C={
  user:User|null;
  organizations:Organization[];
  sites:Site[];
  organization:Organization|null;
  site:Site|null;
  loading:boolean;
  login:(e:string,p:string)=>Promise<void>;
  logout:()=>Promise<void>;
};

const AuthContext=createContext<C|null>(null);

export function AuthProvider({children}:{children:React.ReactNode}){
 const [user,setUser]=useState<User|null>(authStorage.user);
 const [sites,setSites]=useState<Site[]>([]);
 const [loading,setLoading]=useState(true);

 const load=async()=>{
  if(!authStorage.access){setLoading(false);return}
  try{
   const me=await api<ApiEnvelope<User>>(endpoints.me);
   setUser(me.data);authStorage.setUser(me.data);
   const ss=await api<ApiEnvelope<Site[]>>(endpoints.sites);
   setSites(ss.data||[]);
  }catch{authStorage.clear();setUser(null)}finally{setLoading(false)}
 };

 useEffect(()=>{void load()},[]);

 const login=async(email:string,password:string)=>{
  const r=await api<ApiEnvelope<{access:string;refresh:string;user:User}>>(endpoints.login,{method:"POST",body:JSON.stringify({email,password}),skipRefresh:true});
  authStorage.setSession(r.data.access,r.data.refresh,r.data.user);
  setUser(r.data.user);
  const ss=await api<ApiEnvelope<Site[]>>(endpoints.sites,{token:r.data.access});
  setSites(ss.data||[]);
 };

 const logout=async()=>{
  try{if(authStorage.refresh)await api(endpoints.logout,{method:"POST",body:JSON.stringify({refresh:authStorage.refresh}),skipRefresh:true})}
  finally{authStorage.clear();setUser(null);window.location.assign("/login")}
 };

 const organization:Organization|null=user?.organization ? {
   id:user.organization.id,name:user.organization.name,legal_name:"",slug:"",country:"",timezone:"",currency:"",status:"active"
 } : null;
 const site:Site|null=user?.site ? {
   id:user.site.id,organization:user.organization?.id||"",name:user.site.name,address:"",country:"",timezone:"",status:"active"
 } : null;

 const value=useMemo(()=>({
   user,organizations:organization?[organization]:[],sites,organization,site,loading,login,logout
 }),[user,sites,organization,site,loading]);

 return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth(){const c=useContext(AuthContext);if(!c)throw new Error("useAuth must be used inside AuthProvider");return c}
