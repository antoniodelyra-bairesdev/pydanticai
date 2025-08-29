import { AlocacoesProvider } from "@/lib/providers/AlocacoesProvider";
import { pathMetadata } from "../path.metadata";
import Operacoes from "./_components/v2/Operacoes";

export const metadata = pathMetadata["/operacoes"];

export default async function ComprasVendasPage() {
  return (
    <AlocacoesProvider>
      <Operacoes />
    </AlocacoesProvider>
  );
}
