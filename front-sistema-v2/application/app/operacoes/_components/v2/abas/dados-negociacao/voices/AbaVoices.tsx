import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "ag-grid-enterprise";
import "@/app/_components/grid/Grid.css";

import {
  Box,
  Button,
  Divider,
  HStack,
  Icon,
  Table,
  TableContainer,
  Tbody,
  Text,
  Th,
  Thead,
  Tr,
  useToast,
  VStack,
} from "@chakra-ui/react";
import VoiceComponent, { VoiceOrderEntry } from "./VoiceComponent";
import { useCallback, useEffect, useState } from "react";
import {
  IoCalendarOutline,
  IoCubeOutline,
  IoGitBranchOutline,
  IoIdCardOutline,
  IoMailOutline,
  IoReload,
  IoSendOutline,
  IoTimeOutline,
  IoWarningOutline,
} from "react-icons/io5";
import { useHTTP } from "@/lib/hooks";
import { AgGridReact } from "ag-grid-react";

import { ICellRendererParams } from "ag-grid-enterprise";
import { fmtDate, fmtDatetime } from "@/lib/util/string";

export default function AbaVoices() {
  const [voices, setVoices] = useState<VoiceOrderEntry[]>([]);

  const httpClient = useHTTP({ withCredentials: true });

  const buscarVoices = useCallback(async () => {
    const response = await httpClient.fetch("v1/b3/voices", {
      hideToast: { success: true },
    });
    if (!response.ok) return;
    setVoices(await response.json());
  }, []);

  useEffect(() => {
    buscarVoices();
  }, []);

  return (
    <VStack flex={1} h="100%" gap={0} alignItems="stretch">
      <HStack p="16px">
        <Button
          size="xs"
          colorScheme="azul_4"
          leftIcon={<Icon as={IoReload} />}
          onClick={buscarVoices}
        >
          Atualizar
        </Button>
      </HStack>
      <Divider />
      <Box flex={1} className="ag-theme-alpine">
        <AgGridReact
          overlayNoRowsTemplate="Nenhum voice encontrado"
          defaultColDef={{
            resizable: true,
            sortable: true,
            filter: true,
          }}
          enableRangeSelection
          columnDefs={[
            {
              headerName: "ID Voice",
              field: "id_trader",
              flex: 1,
              minWidth: 128,
              cellRenderer({ value }: ICellRendererParams) {
                return (
                  <HStack p="0 8px">
                    <Icon as={IoSendOutline} color="azul_2.main" />
                    <Text textAlign="right">{value}</Text>
                  </HStack>
                );
              },
            },
            {
              headerName: "Ativo",
              field: "codigo_ativo",
              flex: 1,
              minWidth: 128,
              cellRenderer({ value }: ICellRendererParams) {
                return (
                  <Text textAlign="center" fontWeight="bold">
                    {value}
                  </Text>
                );
              },
            },
            {
              headerName: "Lado",
              field: "vanguarda_compra",
              flex: 1,
              minWidth: 80,
              valueGetter: ({ data }) => (data?.vanguarda_compra ? "C" : "V"),
              cellRenderer({ value }: ICellRendererParams) {
                return (
                  <Text
                    textAlign="center"
                    color={value == "C" ? "azul_3.main" : "rosa.main"}
                    fontWeight="bold"
                  >
                    {value}
                  </Text>
                );
              },
            },
            {
              headerName: "P.U.",
              field: "preco_unitario",
              valueGetter: ({ data }) => Number(data?.preco_unitario),
              valueFormatter: ({ value }) =>
                Number(value).toLocaleString("pt-BR", {
                  maximumFractionDigits: 8,
                  minimumFractionDigits: 8,
                }),
              useValueFormatterForExport: true,
              cellRenderer({ value }: ICellRendererParams) {
                return (
                  <HStack
                    alignItems="center"
                    justifyContent="space-between"
                    p="0 8px"
                  >
                    <HStack
                      h="24px"
                      borderRadius="4px"
                      p="0 8px"
                      bgColor="verde.50"
                      color="verde.main"
                    >
                      <Text>R$</Text>
                    </HStack>
                    <Text textAlign="right">
                      {value.toLocaleString("pt-BR", {
                        maximumFractionDigits: 8,
                        minimumFractionDigits: 8,
                      })}
                    </Text>
                  </HStack>
                );
              },
            },
            {
              headerName: "Qtd.",
              field: "quantidade",
              valueGetter: ({ data }) => Number(data?.quantidade),
              valueFormatter: ({ value }) =>
                Number(value).toLocaleString("pt-BR", {
                  maximumFractionDigits: 8,
                  minimumFractionDigits: 8,
                }),
              useValueFormatterForExport: true,
              cellRenderer({ value }: ICellRendererParams) {
                return (
                  <HStack justifyContent="space-between" p="0 8px">
                    <Icon as={IoCubeOutline} color="verde.main" />
                    <Text textAlign="right">
                      {value.toLocaleString("pt-BR", {
                        maximumFractionDigits:
                          Math.floor(value) === value ? 0 : 8,
                        minimumFractionDigits:
                          Math.floor(value) === value ? 0 : 8,
                      })}
                    </Text>
                  </HStack>
                );
              },
            },
            {
              headerName: "Data Liquidação",
              field: "data_liquidacao",
              valueGetter: ({ data }) =>
                data?.data_liquidacao ? fmtDate(data.data_liquidacao) : "---",
              cellRenderer({ value }: ICellRendererParams) {
                return (
                  <HStack p="0 8px">
                    <Icon as={IoCalendarOutline} color="azul_1.500" />
                    <Text textAlign="right">{value}</Text>
                  </HStack>
                );
              },
            },
            {
              headerName: "Contraparte",
              field: "nome_contraparte_cadastrada",
              valueGetter: ({ data }) =>
                data?.nome_contraparte_cadastrada
                  ? data.nome_contraparte_cadastrada
                  : String(
                      data?.contraparte_b3_mesa_id ??
                        data?.contraparte_b3_mesa_id ??
                        "---",
                    ),
              cellRenderer({ data }: ICellRendererParams) {
                if (data?.nome_contraparte_cadastrada)
                  return (
                    <HStack>
                      <Icon as={IoIdCardOutline} color="verde.main" />
                      <Text fontWeight={600}>
                        {data.nome_contraparte_cadastrada}
                      </Text>
                    </HStack>
                  );

                const labelDadoFornecido = String(
                  data?.nome_contraparte_cadastrada
                    ? "[B]³ Nome corretora:"
                    : data?.contraparte_b3_mesa_id
                      ? "[B]³ ID Mesa:"
                      : "---",
                );
                const dadoFornecido = String(
                  data?.nome_contraparte_cadastrada
                    ? data.nome_contraparte_cadastrada
                    : data?.contraparte_b3_mesa_id
                      ? data.contraparte_b3_mesa_id
                      : "---",
                );
                return (
                  <VStack
                    h="100%"
                    fontSize="11px"
                    alignItems="stretch"
                    p="0 8px"
                    bgColor="rosa.50"
                    color="rosa.main"
                    gap={0}
                  >
                    <HStack h="20px">
                      <Icon as={IoWarningOutline} />
                      <Text textAlign="right">Cadastrar contraparte!</Text>
                    </HStack>
                    <HStack
                      h="20px"
                      justifyContent="space-between"
                      fontWeight="bold"
                    >
                      <Text>{labelDadoFornecido}</Text>
                      <Text>{dadoFornecido}</Text>
                    </HStack>
                  </VStack>
                );
              },
            },
            {
              headerName: "Recebido Pré Trade",
              field: "horario_recebimento_order_entry",
              valueGetter: ({ data }) =>
                data?.horario_recebimento_order_entry
                  ? fmtDatetime(data.horario_recebimento_order_entry)
                  : "---",
              cellRenderer({ value }: ICellRendererParams) {
                return (
                  <HStack p="0 8px">
                    <Icon as={IoTimeOutline} color="azul_3.main" />
                    <Text textAlign="right">{value}</Text>
                  </HStack>
                );
              },
            },
            {
              headerName: "Casamento",
              field: "casamento",
              valueGetter: ({ data }) =>
                data?.casamento
                  ? `Casado com ${data.casamento.length} alocações`
                  : "Não há alocações casadas",
              cellRenderer({ value }: ICellRendererParams) {
                return (
                  <HStack p="0 8px">
                    <Icon as={IoGitBranchOutline} color="azul_4.main" />
                    <Text textAlign="right">{value}</Text>
                  </HStack>
                );
              },
            },
            {
              headerName: "Envio acato",
              field: "envios_pre_trade",
              valueGetter: ({ data }) =>
                (data?.envios_pre_trade.length
                  ? data.envios_pre_trade.length
                  : "Não há") + " envios",
              cellRenderer({ value }: ICellRendererParams) {
                return (
                  <HStack p="0 8px">
                    <Icon as={IoMailOutline} color="cinza.500" />
                    <Text textAlign="right">{value}</Text>
                  </HStack>
                );
              },
            },
            {
              headerName: "Recebido Pós Trade",
              field: "horario_recebimento_post_trade",
              valueGetter: ({ data }) =>
                data?.horario_recebimento_post_trade
                  ? fmtDatetime(data.horario_recebimento_post_trade)
                  : "---",
              cellRenderer({ value }: ICellRendererParams) {
                return (
                  <HStack p="0 8px">
                    <Icon as={IoTimeOutline} color="azul_3.main" />
                    <Text textAlign="right">{value}</Text>
                  </HStack>
                );
              },
            },
            {
              headerName: "Envio Alocação",
              field: "envios_post_trade",
              valueGetter: ({ data }) =>
                (data?.envios_post_trade.length
                  ? data.envios_post_trade.length
                  : "Não há") + " envios",
              cellRenderer({ value }: ICellRendererParams) {
                return (
                  <HStack p="0 8px">
                    <Icon as={IoMailOutline} color="cinza.500" />
                    <Text textAlign="right">{value}</Text>
                  </HStack>
                );
              },
            },
          ]}
          rowData={voices}
          animateRows={true}
        />
      </Box>
    </VStack>
  );
}
