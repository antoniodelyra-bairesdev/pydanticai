import { Metadata } from "next";
import LiberacaoCotas from "./_components/LiberacaoCotas";
import { pathMetadata } from "@/app/path.metadata";

export const metadata: Metadata = pathMetadata["/liberacao-cotas"];

export default function Page() {
  return <LiberacaoCotas />;
}
