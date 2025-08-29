import { useAsync } from "@/lib/hooks";
import { useState } from "react";
import {
  IoCloudUploadOutline,
  IoEyeOffOutline,
  IoGlobeOutline,
} from "react-icons/io5";
import {
  Fundo,
  FundoPL,
  FundoRentabilidade,
  IndiceBenchmarkRentabilidade,
  IndiceBenchmark,
} from "@/lib/types/api/iv/v1";
import {
  Box,
  Button,
  Divider,
  HStack,
  Icon,
  Progress,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import { ColDef, ICellRendererParams } from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";
import RentabilidadesPreviewModal from "./_components/RentabilidadesPreviewModal";
import { cnpjFormatter, dateFormatter } from "@/app/_ag-grid/formatters";
import {
  plCellRenderer,
  precoCotaCellRenderer,
  rentabilidadeCellRenderer,
} from "@/app/_ag-grid/cell-renderers";
import {
  getFundosRowData,
  getLinhasIndicesBenchmarkRowData,
} from "./_table/rowDataGetters";

export type TabRentabilidadesProps = {
  fundos: Fundo[];
  indicesBenchmark: IndiceBenchmark[];
  fundosCotasRentabilidadesIniciais: FundoRentabilidade[];
  fundosPLsRentabilidadesIniciais: FundoPL[];
  indicesBenchmarkRentabilidadesIniciais: IndiceBenchmarkRentabilidade[];
  rentabilidadesRequestsURLs: string[];
};

export default function TabRentabilidades({
  fundos,
  indicesBenchmark,
  fundosCotasRentabilidadesIniciais,
  fundosPLsRentabilidadesIniciais,
  indicesBenchmarkRentabilidadesIniciais,
  rentabilidadesRequestsURLs,
}: TabRentabilidadesProps) {
  const { isOpen, onClose, onOpen } = useDisclosure();

  const [isFetchUpdateRentabilidadesLoading, fetchUpdateRentabilidades] =
    useAsync();

  const [fundosCotasRentabilidades, setFundosCotasRentabilidades] = useState<
    FundoRentabilidade[]
  >(fundosCotasRentabilidadesIniciais);
  const [fundosPLsRentabilidades, setFundosPLsRentabilidades] = useState<
    FundoPL[]
  >(fundosPLsRentabilidadesIniciais);
  const [indicesBenchmarkRentabilidades, setIndicesBenchmarkRentabilidades] =
    useState<IndiceBenchmarkRentabilidade[]>(
      indicesBenchmarkRentabilidadesIniciais,
    );

  const fundosRowData = getFundosRowData({
    fundos: fundos,
    fundosCotasRentabilidades: fundosCotasRentabilidades,
    fundosPLsRentabilidades: fundosPLsRentabilidades,
  });
  const indicesBenchmarkRowData = getLinhasIndicesBenchmarkRowData({
    indicesBenchmark: indicesBenchmark,
    indicesBenchmarkRentabilidades: indicesBenchmarkRentabilidades,
  });

  const defaultColumnDef = {
    resizable: true,
    sortable: true,
  };

  const fundosTableColDefsArr = [
    {
      field: "fundo.publicado",
      headerName: "Status",
      cellRenderer: ({ value }: ICellRendererParams) => {
        if (value === true) {
          return (
            <Text color="verde.main" textAlign="center">
              <Icon as={IoGlobeOutline} /> Publicado
            </Text>
          );
        }
        return (
          <Text color="rosa.main" textAlign="center">
            <Icon as={IoEyeOffOutline} /> Oculto
          </Text>
        );
      },
      width: 100,
    },
    {
      field: "fundo.nome",
      headerName: "Fundo",
      filter: true,
      width: 550,
    },
    {
      field: "fundo.cnpj",
      headerName: "CNPJ",
      filter: true,
      valueFormatter: cnpjFormatter,
      width: 140,
    },
    {
      field: "rentabilidade.data_posicao",
      headerName: "Data da Cota",
      filter: true,
      valueFormatter: dateFormatter,
      width: 135,
    },
    {
      field: "rentabilidade.preco_cota",
      headerName: "Valor da Cota",
      width: 128,
      cellRenderer: precoCotaCellRenderer,
    },
    {
      field: "rentabilidade.rentabilidade_mes",
      headerName: "% Mês",
      width: 90,
      cellRenderer: rentabilidadeCellRenderer,
    },
    {
      field: "rentabilidade.rentabilidade_ano",
      headerName: "% Ano",
      width: 90,
      cellRenderer: rentabilidadeCellRenderer,
    },
    {
      field: "rentabilidade.rentabilidade_12meses",
      headerName: "% 12 Meses",
      width: 120,
      cellRenderer: rentabilidadeCellRenderer,
    },
    {
      field: "rentabilidade.rentabilidade_24meses",
      headerName: "% 24 Meses",
      width: 120,
      cellRenderer: rentabilidadeCellRenderer,
    },
    {
      field: "rentabilidade.rentabilidade_36meses",
      headerName: "% 36 Meses",
      width: 120,
      cellRenderer: rentabilidadeCellRenderer,
    },
    {
      field: "pl.patrimonio_liquido",
      headerName: "PL",
      width: 100,
      cellRenderer: plCellRenderer,
    },
    {
      field: "pl.media_12meses",
      headerName: "PL Médio 12M",
      width: 135,
      cellRenderer: plCellRenderer,
    },
    {
      field: "fundo.data_inicio",
      headerName: "Início",
      width: 84,
      filter: true,
      valueFormatter: dateFormatter,
    },
  ];
  const [fundosTableColDefs] = useState<ColDef[]>(fundosTableColDefsArr);

  const indicesBenchmarkTableColDefsArr = [
    {
      field: "indiceBenchmark.nome",
      headerName: "Índice",
      filter: true,
      flex: 1,
      cellRenderer: ({ value }: ICellRendererParams) => {
        return <Text paddingLeft="10px">{value}</Text>;
      },
    },
    {
      field: "rentabilidade.data_posicao",
      headerName: "Data da Cota",
      filter: true,
      valueFormatter: dateFormatter,
    },
    {
      field: "rentabilidade.rentabilidade_mes",
      headerName: "% Mês",
      cellRenderer: rentabilidadeCellRenderer,
    },
    {
      field: "rentabilidade.rentabilidade_ano",
      headerName: "% Ano",
      cellRenderer: rentabilidadeCellRenderer,
    },
    {
      field: "rentabilidade.rentabilidade_12meses",
      headerName: "% 12 Meses",
      cellRenderer: rentabilidadeCellRenderer,
    },
    {
      field: "rentabilidade.rentabilidade_24meses",
      headerName: "% 24 Meses",
      cellRenderer: rentabilidadeCellRenderer,
    },
    {
      field: "rentabilidade.rentabilidade_36meses",
      headerName: "% 36 Meses",
      cellRenderer: rentabilidadeCellRenderer,
    },
  ];
  const [indicesBenchmarkTableColDefs] = useState<ColDef[]>(
    indicesBenchmarkTableColDefsArr,
  );

  return (
    <>
      {isFetchUpdateRentabilidadesLoading ? (
        <Progress isIndeterminate colorScheme="verde" />
      ) : (
        <VStack w="100%" alignItems="stretch">
          <HStack>
            <Button
              onClick={onOpen}
              colorScheme="azul_3"
              alignSelf="flex-start"
              size="xs"
              leftIcon={<Icon as={IoCloudUploadOutline} />}
            >
              Carregar planilha de rentabilidades
            </Button>
          </HStack>
          <Box
            className="ag-theme-alpine"
            h="60vh"
            overflowX="auto"
            overflowY="auto"
            border="1px solid"
            borderColor="cinza.main"
            borderRadius="8px"
          >
            <AgGridReact
              headerHeight={32}
              defaultColDef={defaultColumnDef}
              columnDefs={fundosTableColDefs}
              rowData={fundosRowData}
              animateRows={true}
            />
          </Box>
          <Divider />
          <Box
            className="ag-theme-alpine"
            h="40vh"
            border="1px solid"
            borderColor="cinza.main"
            borderRadius="8px"
            overflowY="auto"
          >
            <AgGridReact
              headerHeight={32}
              defaultColDef={defaultColumnDef}
              columnDefs={indicesBenchmarkTableColDefs}
              rowData={indicesBenchmarkRowData}
              animateRows={true}
            />
          </Box>
        </VStack>
      )}

      <RentabilidadesPreviewModal
        fundos={fundos}
        indicesBenchmark={indicesBenchmark}
        setFundosCotasRentabilidades={setFundosCotasRentabilidades}
        setFundosPLsRentabilidades={setFundosPLsRentabilidades}
        setIndicesBenchmarkRentabilidades={setIndicesBenchmarkRentabilidades}
        isFetchUpdateLoading={isFetchUpdateRentabilidadesLoading}
        fetchUpdate={fetchUpdateRentabilidades}
        rentabilidadesRequestsURLs={rentabilidadesRequestsURLs}
        isOpen={isOpen}
        onClose={onClose}
      />
    </>
  );
}

export const indicesBenchmarkSiteInstitucionalIds = [
  1, // CDI
  2, // Dólar
  5, // IMA-B 5
  6, // IMA-B 5+
  7, // IRF-M 1+
  10, // Ibovespa
  12, // IMA-B
  9, // IBX
];
