import type { Metadata } from "next";
import "./globals.css";
import AppShell from "@/components/AppShell";
import { AuthProvider } from "@/components/AuthProvider";
export const metadata:Metadata={title:"QCSTS | Pharmaceutical Quality & Stability",description:"Multi-tenant pharmaceutical quality and stability management platform."};
/** Provides the shared authentication and application shell for every route. */
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><AuthProvider><AppShell>{children}</AppShell></AuthProvider></body></html>}
