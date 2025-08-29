import type {
  Fundo,
  FundoPL,
  FundoRentabilidade,
  IndiceBenchmark,
  IndiceBenchmarkRentabilidade,
  ProcessamentoBdFolder,
} from "@/lib/types/api/iv/v1";
import type { ColDef, ICellRendererParams } from "ag-grid-community";
import type { Dispatch, SetStateAction } from "react";
import type {
  FundoRowData,
  IndiceBenchmarkRowData,
} from "../_table/rowDataGetters";

import { useCallback, useEffect, useRef, useState } from "react";
import { AgGridReact } from "ag-grid-react";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { useAsync, useHTTP } from "@/lib/hooks";
import {
  VStack,
  Text,
  Input,
  Divider,
  Progress,
  Button,
  HStack,
  Box,
} from "@chakra-ui/react";
import { cnpjFormatter, dateFormatter } from "@/app/_ag-grid/formatters/index";
import {
  plCellRenderer,
  precoCotaCellRenderer,
  rentabilidadeCellRenderer,
} from "@/app/_ag-grid/cell-renderers/index";
import {
  getFundosRowData,
  getLinhasIndicesBenchmarkRowData,
} from "../_table/rowDataGetters";

type RentabilidadesPreviewModalProps = {
  fundos: Fundo[];
  indicesBenchmark: IndiceBenchmark[];
  setFundosCotasRentabilidades: Dispatch<SetStateAction<FundoRentabilidade[]>>;
  setFundosPLsRentabilidades: Dispatch<SetStateAction<FundoPL[]>>;
  setIndicesBenchmarkRentabilidades: Dispatch<
    SetStateAction<IndiceBenchmarkRentabilidade[]>
  >;
  isFetchUpdateLoading: boolean;
  fetchUpdate: (callback: () => Promise<void>) => Promise<void>;
  rentabilidadesRequestsURLs: string[];
  isOpen: boolean;
  onClose: () => void;
};

export default function RentabilidadesPreviewModal({
  fundos,
  indicesBenchmark,
  setFundosCotasRentabilidades,
  setFundosPLsRentabilidades,
  setIndicesBenchmarkRentabilidades,
  isFetchUpdateLoading,
  fetchUpdate,
  rentabilidadesRequestsURLs,
  isOpen,
  onClose,
}: RentabilidadesPreviewModalProps) {
  const httpClient = useHTTP({ withCredentials: true });
  const [isFetchPreviewLoading, fetchPreview] = useAsync();

  const [file, setFile] = useState<File | null>(null);
  const isConfirmButtonEnabled = file && !isFetchPreviewLoading ? true : false;

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [fundosRowDataPreviewModal, setFundosRowDataPreviewModal] = useState<
    FundoRowData[]
  >([]);
  const [
    indicesBenchmarkRowDataPreviewModal,
    setIndicesBenchmarkRowDataPreviewModal,
  ] = useState<IndiceBenchmarkRowData[]>([]);

  const resetPreviewState = useCallback(() => {
    setFundosRowDataPreviewModal([]);
    setIndicesBenchmarkRowDataPreviewModal([]);
    setFile(null);

    if (!fileInputRef.current) {
      return;
    }
    fileInputRef.current.value = "";
  }, []);

  const previewRentabilidades = async (file: File) => {
    if (isFetchPreviewLoading) {
      return;
    }

    await fetchPreview(async () => {
      const body = new FormData();
      body.append("rentabilidades", file);

      const response = await httpClient.fetch(
        "sistema/arquivos/bd-folder?persist=false",
        {
          method: "POST",
          body,
          hideToast: { success: true },
          multipart: true,
        },
      );
      if (!response.ok) {
        return;
      }
      const responseJSON = (await response.json()) as ProcessamentoBdFolder;
      if (responseJSON.persist === true) {
        return;
      }

      const fundosCotasRentabilidadesPreview: FundoRentabilidade[] =
        responseJSON.fundos.rentabilidades;
      const fundosPLsRentabilidadesPreview: FundoPL[] = responseJSON.fundos.pls;
      const indicesBenchmarkRentabilidadesPreview: IndiceBenchmarkRentabilidade[] =
        responseJSON.indicadores;

      const _linhasFundosPreviewModal = getFundosRowData({
        fundos: fundos,
        fundosCotasRentabilidades: fundosCotasRentabilidadesPreview,
        fundosPLsRentabilidades: fundosPLsRentabilidadesPreview,
      });
      const _linhasIndicesBenchmarkPreviewModal =
        getLinhasIndicesBenchmarkRowData({
          indicesBenchmark: indicesBenchmark,
          indicesBenchmarkRentabilidades: indicesBenchmarkRentabilidadesPreview,
        });

      setFundosRowDataPreviewModal(_linhasFundosPreviewModal);
      setIndicesBenchmarkRowDataPreviewModal(
        _linhasIndicesBenchmarkPreviewModal,
      );
    });
  };

  const updateRentabilidades = async (file: File) => {
    if (isFetchUpdateLoading) {
      return;
    }

    await fetchUpdate(async () => {
      const body = new FormData();
      body.append("rentabilidades", file);

      const response = await httpClient.fetch(
        "sistema/arquivos/bd-folder?persist=true",
        {
          method: "POST",
          body,
          hideToast: { success: false },
          multipart: true,
        },
      );
      if (!response.ok) {
        return;
      }

      const requestsPromises = rentabilidadesRequestsURLs.map((url) =>
        httpClient.fetch(url, { hideToast: { success: true } }),
      );
      const requests = requestsPromises.map((promise) =>
        promise.then((resp) => (resp.ok ? resp.json() : [])),
      );

      const [
        uptodateCotasRentabilidades,
        uptodateFundosPLsRentabilidades,
        uptodateIndicesBenchmarkRentabilidades,
      ] = (await Promise.all(requests)) as [
        FundoRentabilidade[],
        FundoPL[],
        IndiceBenchmarkRentabilidade[],
      ];

      setFundosCotasRentabilidades(uptodateCotasRentabilidades);
      setFundosPLsRentabilidades(uptodateFundosPLsRentabilidades);
      setIndicesBenchmarkRentabilidades(uptodateIndicesBenchmarkRentabilidades);
    });
  };

  const defaultColumnDef = {
    resizable: true,
    sortable: true,
  };

  const fundosTableColDefsArr = [
    {
      field: "fundo.nome",
      headerName: "Fundo",
      filter: true,
      width: 550,
      cellRenderer: ({ value }: ICellRendererParams) => {
        return <Text paddingLeft="10px">{value}</Text>;
      },
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
      width: 100,
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

  useEffect(() => {
    return () => {
      resetPreviewState();
    };
  }, []);

  return (
    <ConfirmModal
      confirmEnabled={isConfirmButtonEnabled}
      isOpen={isOpen}
      onClose={onClose}
      onCancelAction={() => resetPreviewState()}
      onConfirmAction={async () => {
        if (!file) {
          return;
        }
        await updateRentabilidades(file);
        resetPreviewState();
      }}
      size="6xl"
    >
      <VStack alignItems="stretch">
        <VStack alignItems="stretch" gap={1}>
          <Text>Carregue uma planilha com o formato da "BdFolder.xlsb"</Text>
          <HStack gap={2}>
            <Input
              ref={fileInputRef}
              p="4px"
              size="md"
              type="file"
              accept=".xlsb"
              onChange={async (ev) => {
                if (!ev.currentTarget.files) {
                  return;
                }
                const file = ev.currentTarget.files[0];
                setFile(file);
                await previewRentabilidades(file);
              }}
            />
            <Button
              isDisabled={!file || isFetchPreviewLoading ? true : false}
              size="sm"
              width="90px"
              variant="outline"
              colorScheme="azul_1"
              onClick={() => {
                resetPreviewState();
              }}
            >
              Limpar
            </Button>
          </HStack>
          {isFetchPreviewLoading && (
            <Progress isIndeterminate colorScheme="verde" />
          )}
        </VStack>
        <Divider />
        <Box
          className="ag-theme-alpine"
          h="40vh"
          border="1px solid"
          borderColor="cinza.main"
          borderRadius="8px"
        >
          <AgGridReact
            headerHeight={32}
            defaultColDef={defaultColumnDef}
            columnDefs={fundosTableColDefs}
            rowData={fundosRowDataPreviewModal}
            animateRows={true}
            suppressNoRowsOverlay={true}
          />
        </Box>
        <Divider />
        <Box
          className="ag-theme-alpine"
          h="20vh"
          border="1px solid"
          borderColor="cinza.main"
          borderRadius="8px"
          overflowY="auto"
        >
          <AgGridReact
            headerHeight={32}
            defaultColDef={defaultColumnDef}
            columnDefs={indicesBenchmarkTableColDefs}
            rowData={indicesBenchmarkRowDataPreviewModal}
            animateRows={true}
            suppressNoRowsOverlay={true}
          />
        </Box>
      </VStack>
    </ConfirmModal>
  );
}
