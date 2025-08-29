import { pathMetadata } from "@/app/path.metadata";
import VisualizacaoCarteirasSandbox from "./_components/VisualizacaoCarteirasSandbox";

export const metadata = pathMetadata["/ferramentas/relatorio-carteira"];

export default function VisualizacaoCarteirasPage() {
  return <VisualizacaoCarteirasSandbox />;
}
