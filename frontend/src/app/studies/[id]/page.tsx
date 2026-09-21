import { redirect } from "next/navigation";
export default async function LegacyStudyDetail({params}:{params:Promise<{id:string}>}){const {id}=await params;redirect("/app/studies/"+id);}
