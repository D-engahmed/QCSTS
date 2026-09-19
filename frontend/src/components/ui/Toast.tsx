"use client";import {createContext,useContext,useMemo,useState} from "react";
type T={message:string;kind:"success"|"error"};const C=createContext<{show:(message:string,kind?:T["kind"])=>void}>({show:()=>{}});
export function ToastProvider({children}:{children:React.ReactNode}){const [toast,setToast]=useState<T|null>(null);const value=useMemo(()=>({show:(message:string,kind:T["kind"]="success")=>{setToast({message,kind});setTimeout(()=>setToast(null),2800)}}),[]);return <C.Provider value={value}>{children}{toast&&<div className={"toast toast-"+toast.kind} role="status">{toast.message}</div>}</C.Provider>}
export const useToast=()=>useContext(C);
