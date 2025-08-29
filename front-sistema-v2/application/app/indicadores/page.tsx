import { Metadata } from "next";
import Indicadores from "./_components/Indicadores";
import { pathMetadata } from "@/app/path.metadata";

export const metadata: Metadata = pathMetadata["/indicadores"];

export default function Page() {
  return <Indicadores />;
}
