import { AssetPageProvider } from "@/lib/providers/AssetPageProvider";
import {
  Emissor,
  IndicePapel,
  TipoEvento,
  TipoPapel,
} from "@/lib/types/api/iv/v1";
import IVServerHTTPClient from "@/lib/util/http/vanguarda/IVServerHTTPClient";
import { pathMetadata } from "../path.metadata";
import Ativos from "./_components/Ativos";

export const metadata = pathMetadata["/ativos"];

export default async function AtivosPage() {
  const http = new IVServerHTTPClient({ withCredentials: true });

  const listOf = <T,>(url: string): Promise<T[]> =>
    http.fetch("v1/ativos/" + url).then((r) => (r.ok ? r.json() : []));

  const [
    codigos,
    emissores,
    indices,
    tiposAtivos,
    tiposEventos,
    tiposEventosSuportados,
    totalAtivos,
    totalEventos,
  ] = await Promise.all([
    listOf<string>("codigos"),
    listOf<Emissor>("nomes_emissores"),
    listOf<IndicePapel>("indice"),
    listOf<TipoPapel>("tipo_ativos"),
    listOf<TipoEvento>("tipo_evento"),
    listOf<TipoEvento>("tipo_evento/suportados"),
    http.fetch("v1/ativos/total").then((r) => (r.ok ? r.json() : null)),
    http.fetch("v1/ativos/eventos/total").then((r) => (r.ok ? r.json() : null)),
  ] as const);

  return (
    <AssetPageProvider>
      <Ativos
        codigos={codigos}
        emissores={emissores}
        indices={indices}
        tipos_ativos={tiposAtivos}
        tipos_fluxos={tiposEventos}
        tipos_fluxos_suportados={tiposEventosSuportados}
        total_assets={totalAtivos}
        total_events={totalEventos}
      />
    </AssetPageProvider>
  );
}
