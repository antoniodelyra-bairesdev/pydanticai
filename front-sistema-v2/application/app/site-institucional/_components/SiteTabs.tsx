"use client";

import {
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  VStack,
} from "@chakra-ui/react";
import { useRef } from "react";
import TabListagemCategoriasDocumentos from "./tabs/documentos-regulatorios/TabListagemCategoriasDocumentos";
import { TabListagemProdutos } from "./tabs/produtos/TabListagemProdutos";
import { useRouter, useSearchParams } from "next/navigation";
import TabMesas from "./tabs/mesas/TabMesas";
import TabRentabilidades from "./tabs/rentabilidades/TabRentabilidades";
import {
  CategoriaRelatorio,
  Fundo,
  FundoCaracteristicaExtra,
  FundoPL,
  FundoRentabilidade,
  FundoSiteInstitucionalClassificacao,
  FundoSiteInstitucionalTipo,
  IndiceBenchmark,
  IndiceBenchmarkRentabilidade,
  Mesa,
  PlanoDeFundo,
} from "@/lib/types/api/iv/v1";
import { isSixMonthOrMoreApart } from "@/lib/util/dates";

export type SiteTabsProps = {
  categorias: CategoriaRelatorio[];
  planosDeFundo: PlanoDeFundo[];
  fundos: Fundo[];
  classificacoes: FundoSiteInstitucionalClassificacao[];
  tipos: FundoSiteInstitucionalTipo[];
  indicesBenchmark: IndiceBenchmark[];
  mesas: Mesa[];
  fundoCaracteristicasExtras: FundoCaracteristicaExtra[];
  fundosCotasRentabilidades: FundoRentabilidade[];
  fundosPLsRentabilidades: FundoPL[];
  indicesBenchmarkRentabilidades: IndiceBenchmarkRentabilidade[];
  rentabilidadesRequestsURLs: string[];
};

export default function SiteTabs({
  categorias,
  planosDeFundo,
  fundos,
  classificacoes,
  tipos,
  indicesBenchmark,
  mesas,
  fundoCaracteristicasExtras,
  fundosCotasRentabilidades,
  fundosPLsRentabilidades,
  indicesBenchmarkRentabilidades,
  rentabilidadesRequestsURLs,
}: SiteTabsProps) {
  const resizeRef = useRef<() => void>();
  const query = useSearchParams();
  const router = useRouter();

  const onTabChange = (i: number) => {
    const tab = {
      0: "documentos",
      1: "produtos",
      2: "rentabilidades",
      3: "mesas",
    }[i];

    if (!tab) return;

    const url = new URL(window.location.href);
    url.searchParams.set("tab", tab);
    router.replace(url.toString());

    if (i !== 1) return;
    resizeRef.current?.();
  };

  return (
    <VStack h="100%" alignItems="stretch" p="24px 36px">
      <Tabs
        defaultIndex={
          {
            documentos: 0,
            produtos: 1,
            rentabilidades: 2,
            mesas: 3,
          }[query.get("tab") ?? ""]
        }
        colorScheme="verde"
        flex={1}
        display="flex"
        flexDirection="column"
        onChange={onTabChange}
      >
        <TabList>
          <Tab>Documentos regulatórios</Tab>
          <Tab>Listagem de produtos</Tab>
          <Tab>Rentabilidades</Tab>
          <Tab>Mesas</Tab>
        </TabList>
        <TabPanels flex={1}>
          <TabPanel>
            <TabListagemCategoriasDocumentos
              categoriasIniciais={categorias}
              listaPlanosDeFundo={planosDeFundo}
            />
          </TabPanel>
          <TabPanel h="100%" p={0}>
            <TabListagemProdutos
              fundos={fundos}
              mesas={mesas}
              classificacoes={classificacoes}
              tipos={tipos}
              fundoCaracteristicasExtras={fundoCaracteristicasExtras}
              indicesBenchmark={indicesBenchmark}
              resizeRef={resizeRef}
            />
          </TabPanel>
          <TabPanel>
            <TabRentabilidades
              fundos={getPublicFundos(fundos)}
              indicesBenchmark={getPublicIndicesBenchmarks(indicesBenchmark)}
              fundosCotasRentabilidadesIniciais={fundosCotasRentabilidades}
              fundosPLsRentabilidadesIniciais={fundosPLsRentabilidades}
              indicesBenchmarkRentabilidadesIniciais={
                indicesBenchmarkRentabilidades
              }
              rentabilidadesRequestsURLs={rentabilidadesRequestsURLs}
            />
          </TabPanel>
          <TabPanel>
            <TabMesas mesas={mesas} fundos={fundos} />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </VStack>
  );
}

function getPublicFundos(fundos: Fundo[]): Fundo[] {
  return fundos.filter((fundo) => {
    if (!fundo.data_inicio) {
      return false;
    }

    const dataHoje: Date = new Date();
    const fundoDataInicio: Date = new Date(fundo.data_inicio);
    return (
      fundo.publicado &&
      !fundo.ticker_b3 &&
      isSixMonthOrMoreApart(fundoDataInicio, dataHoje)
    );
  });
}

function getPublicIndicesBenchmarks(
  indicesBenchmark: IndiceBenchmark[],
): IndiceBenchmark[] {
  return indicesBenchmark.filter((indiceBenchmark) => {
    return indicesBenchmarkSiteInstitucionalIds.includes(indiceBenchmark.id);
  });
}

const indicesBenchmarkSiteInstitucionalIds = [
  1, // CDI
  2, // Dólar
  5, // IMA-B 5
  6, // IMA-B 5+
  7, // IRF-M 1+
  10, // Ibovespa
  12, // IMA-B
  9, // IBX
];
