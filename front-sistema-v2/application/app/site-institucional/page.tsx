import IVServerHTTPClient from "@/lib/util/http/vanguarda/IVServerHTTPClient";
import { pathMetadata } from "../path.metadata";
import {
  CategoriaRelatorio,
  Fundo,
  FundoCaracteristicaExtra,
  FundoPL,
  FundoRentabilidade,
  FundoSiteInstitucionalClassificacao,
  FundoSiteInstitucionalTipo,
  IndiceBenchmarkRentabilidade,
  IndiceBenchmark,
  Mesa,
  PlanoDeFundo,
} from "@/lib/types/api/iv/v1";
import SiteTabs from "./_components/SiteTabs";

export const metadata = pathMetadata["/site-institucional"];

export default async function RegulatorioPage() {
  const httpClient = new IVServerHTTPClient({ withCredentials: true });

  const requests = [
    httpClient.fetch("v1/regulatorio/publico"),
    httpClient.fetch("v1/regulatorio/categoria/plano-de-fundo"),
    httpClient.fetch("v1/fundos"),
    httpClient.fetch("v1/fundos/institucionais/classificacoes"),
    httpClient.fetch("v1/fundos/institucionais/tipos"),
    httpClient.fetch("v1/mesa"),
    httpClient.fetch("v1/fundos/caracteristicas-extras"),
    httpClient.fetch("v1/indicadores"),
  ].map((p) => p.then((resp) => (resp.ok ? resp.json() : [])));

  const [
    categorias,
    planosDeFundo,
    fundos,
    classificacoes,
    tipos,
    mesas,
    fundoCaracteristicasExtras,
    indicesBenchmark,
  ] = (await Promise.all(requests)) as [
    CategoriaRelatorio[],
    PlanoDeFundo[],
    Fundo[],
    FundoSiteInstitucionalClassificacao[],
    FundoSiteInstitucionalTipo[],
    Mesa[],
    FundoCaracteristicaExtra[],
    IndiceBenchmark[],
  ];

  fundos.sort((f1, f2) => f1.nome.localeCompare(f2.nome));
  categorias.sort((c1, c2) => c1.ordem - c2.ordem);
  planosDeFundo.sort((p1, p2) => p1.id - p2.id);
  mesas.sort((m1, m2) => m1.ordenacao - m2.ordenacao);

  const fundosIds = fundos.map((fundo) => fundo.id);
  const indicesBenchmarkIds = indicesBenchmark.map(
    (indiceBenchmark) => indiceBenchmark.id,
  );

  const rentabilidadesRequestsURLs = [
    `v1/fundos/rentabilidades/cotas?fundos_ids=${fundosIds.join(",")}`,
    `v1/fundos/rentabilidades/patrimonio_liquido?fundos_ids=${fundosIds.join(",")}`,
    `v1/indicadores/rentabilidades?indices_benchmark_ids=${indicesBenchmarkIds.join(",")}`,
  ];
  const requestsRentabilidadesPromises = rentabilidadesRequestsURLs.map(
    (url) => {
      return httpClient.fetch(url);
    },
  );
  const requestsRentabilidades = requestsRentabilidadesPromises.map((p) =>
    p.then((resp) => (resp.ok ? resp.json() : [])),
  );

  const [
    fundosCotasRentabilidades,
    fundosPLsRentabilidades,
    indicesBenchmarkRentabilidades,
  ] = (await Promise.all(requestsRentabilidades)) as [
    FundoRentabilidade[],
    FundoPL[],
    IndiceBenchmarkRentabilidade[],
  ];

  return (
    <SiteTabs
      categorias={categorias}
      planosDeFundo={planosDeFundo}
      fundos={fundos}
      classificacoes={classificacoes}
      tipos={tipos}
      mesas={mesas}
      fundoCaracteristicasExtras={fundoCaracteristicasExtras}
      indicesBenchmark={indicesBenchmark}
      fundosCotasRentabilidades={fundosCotasRentabilidades}
      fundosPLsRentabilidades={fundosPLsRentabilidades}
      indicesBenchmarkRentabilidades={indicesBenchmarkRentabilidades}
      rentabilidadesRequestsURLs={rentabilidadesRequestsURLs}
    />
  );
}
