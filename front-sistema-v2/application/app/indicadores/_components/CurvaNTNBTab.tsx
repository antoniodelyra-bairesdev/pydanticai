import {
  Box,
  Button,
  HStack,
  Icon,
  Input,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  Progress,
  StackDivider,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { IoAnalytics, IoEllipse, IoSaveOutline } from "react-icons/io5";

import { getColorHex } from "@/app/theme";

import { Chart } from "react-chartjs-2";
import { useAsync, useHTTP, useUser } from "@/lib/hooks";
import {
  CalendarIcon,
  DownloadIcon,
  EditIcon,
  SmallCloseIcon,
} from "@chakra-ui/icons";
import ValidationGrid, {
  ModificationMap,
  ValidationGridColDef,
} from "@/app/_components/grid/ValidationGrid";
import { ICellRendererParams, ValueSetterParams } from "ag-grid-community";
import { dateToStr, fmtDate, fmtNumber } from "@/lib/util/string";
import Hint from "@/app/_components/texto/Hint";
import { CurvaNTNBResponse, PontoCurvaNTNB } from "@/lib/types/api/iv/v1";
import VResize from "@/app/_components/misc/VResize";
import { required } from "@/lib/util/validation";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import DiffSummary from "@/app/_components/modal/DiffSummary";

import { ChartJSOrUndefined } from "react-chartjs-2/dist/types";
import { ChartOptions } from "chart.js";
import { ChartDataset } from "chart.js";
import GridEditBar from "./GridEditBar";
import Legenda from "./Legenda";
import HResize from "@/app/_components/misc/HResize";

const months = [
  "Jan",
  "Fev",
  "Mar",
  "Abr",
  "Mai",
  "Jun",
  "Jul",
  "Ago",
  "Set",
  "Out",
  "Nov",
  "Dez",
];
const letters = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"];

const durationRenderer =
  (editing: boolean) => (params: ICellRendererParams) => (
    <HStack
      w="100%"
      h="100%"
      gap="4px"
      p="4px"
      borderRadius="8px"
      fontSize="xs"
      alignItems="center"
      justifyContent="center"
      bgColor={editing ? getColorHex("cinza.main") + "4f" : "none"}
      cursor={editing ? "not-allowed" : "auto"}
    >
      <Text>{fmtNumber(params.data.duration, 3)}</Text>
    </HStack>
  );

export default function CurvaNTNBTab() {
  const httpClient = useHTTP({ withCredentials: true });

  const [loading, load] = useAsync();
  const [date, setDate] = useState(dateToStr(new Date()));

  const [data, setData] = useState<CurvaNTNBResponse>();

  const [editingTaxas, setEditingTaxas] = useState(false);
  const [editingDaps, setEditingDaps] = useState(false);

  const [editedTaxas, setEditedTaxas] = useState<
    ModificationMap<CurvaNTNBResponse["taxas_indicativas"]["dados"][number]>
  >({});
  const [editedDaps, setEditedDaps] = useState<
    ModificationMap<CurvaNTNBResponse["ajustes_dap"]["dados"][number]>
  >({});

  const [selectedDuration, setSelectedDuration] = useState(1);

  const max = Math.max(data?.curva.at(-1)?.duration ?? 1, 1);
  const dapAtualizadoEm =
    data?.ajustes_dap.atualizacao ?? data?.ajustes_dap.data_referencia ?? "";
  const taxaAtualizadaEm =
    data?.taxas_indicativas.atualizacao ??
    data?.taxas_indicativas.data_referencia ??
    "";

  const fetchData = useCallback(async () => {
    setData(undefined);
    const response = await httpClient.fetch(
      "v1/indicadores/curva-ntnb?data=" + date,
      { hideToast: { success: true } },
    );
    if (!response.ok) return;
    const body = (await response.json()) as CurvaNTNBResponse;
    setData(body);
  }, [date]);

  useEffect(() => {
    if (!date) return;
    load(fetchData);
  }, [date]);

  const colDefsTaxas: ValidationGridColDef[] = [
    {
      width: 144,
      headerName: "Detalhes",
      cellRenderer: (params: ICellRendererParams) => (
        <HStack
          bgColor={editingTaxas ? getColorHex("cinza.main") + "4f" : "none"}
          cursor={editingTaxas ? "not-allowed" : "auto"}
          p="4px"
          borderRadius="8px"
          fontSize="xs"
          alignItems="stretch"
          justifyContent="center"
          w="100%"
          h="100%"
          divider={<StackDivider />}
        >
          <VStack
            fontSize="xs"
            alignItems="stretch"
            gap="4px"
            justifyContent="center"
          >
            <HStack fontSize="xs">
              <Text>NTN-B</Text>
              <Text>{fmtDate(params.data.data_vencimento as string)}</Text>
            </HStack>
          </VStack>
        </HStack>
      ),
      editable: false,
    },
    {
      width: 84,
      field: "duration",
      headerName: "Duration",
      cellRenderer: durationRenderer(editingTaxas),
      editable: false,
    },
    {
      width: 82,
      field: "taxa",
      headerName: "Taxa",
      valueSetter(params: ValueSetterParams) {
        const num = params.newValue !== null ? Number(params.newValue) : 0;
        params.data.taxa = isNaN(num) ? 0 : num;
        return true;
      },
      cellRenderer: (params: ICellRendererParams) => (
        <HStack>
          <Icon as={IoAnalytics} color="verde.main" />
          <Text>{params.valueFormatted ?? params.value}</Text>
        </HStack>
      ),
    },
  ];

  const colDefsDaps: ValidationGridColDef[] = useMemo(
    () => [
      {
        width: 144,
        headerName: "Detalhes",
        cellRenderer: (params: ICellRendererParams) => {
          const [ano, mes] = (params.data.data_vencimento as string).split("-");
          const utilizado = params.data.utilizado as boolean;
          return (
            <HStack
              bgColor={editingDaps ? getColorHex("cinza.main") + "4f" : "none"}
              cursor={editingDaps ? "not-allowed" : "auto"}
              p="12px"
              borderRadius="8px"
              fontSize="xs"
              alignItems="stretch"
              justifyContent="center"
              w="100%"
              h="100%"
              divider={<StackDivider />}
            >
              <VStack
                w="100%"
                fontSize="xs"
                alignItems="stretch"
                gap="4px"
                justifyContent="center"
              >
                <HStack h="14px" justifyContent="space-between">
                  <Text>
                    DAP {letters[Number(mes) - 1]}
                    {ano.substring(2)}
                  </Text>
                  <Text>
                    {months[Number(mes) - 1]}/{ano}
                  </Text>
                </HStack>
                <HStack
                  justifyContent="space-between"
                  h="14px"
                  w="100%"
                  gap="4px"
                >
                  <Icon
                    boxSize="16px"
                    strokeWidth={32}
                    stroke={utilizado ? "amarelo.900" : "rosa.900"}
                    color={utilizado ? "amarelo.main" : "rosa.main"}
                    as={IoEllipse}
                  />
                  <Text>
                    {utilizado ? "Utilizado" : "Inutilizado"} na curva
                  </Text>
                </HStack>
              </VStack>
            </HStack>
          );
        },
        editable: false,
      },
      {
        width: 84,
        field: "duration",
        headerName: "Duration",
        cellRenderer: durationRenderer(editingDaps),
        editable: false,
      },
      {
        width: 82,
        valueSetter(params: ValueSetterParams) {
          const num = params.newValue !== null ? Number(params.newValue) : 0;
          params.data.taxa = isNaN(num) ? 0 : num;
          return true;
        },
        field: "taxa",
        headerName: "Taxa",
        cellRenderer: (params: ICellRendererParams) => (
          <HStack>
            <Icon as={IoAnalytics} color="verde.main" />
            <Text>{params.valueFormatted ?? params.value}</Text>
          </HStack>
        ),
      },
    ],
    [editingDaps],
  );

  const dapMaisProximo: number | null =
    data?.ajustes_dap.dados
      .filter((d) => d.utilizado)
      .map((d) => d.duration - selectedDuration)
      .reduce((min, d) => (Math.abs(d) < Math.abs(min) ? d : min), Infinity) ??
    null;

  const taxaMaisProxima: number | null =
    data?.taxas_indicativas.dados
      .map((d) => d.duration - selectedDuration)
      .reduce((min, d) => (Math.abs(d) < Math.abs(min) ? d : min), Infinity) ??
    null;

  const pontoMaisProximo: (PontoCurvaNTNB & { tipo: "dap" | "taxa" }) | null =
    data && taxaMaisProxima !== null && dapMaisProximo !== null
      ? Math.abs(taxaMaisProxima) <= Math.abs(dapMaisProximo)
        ? {
            tipo: "taxa",
            ...(data.taxas_indicativas.dados.find(
              (d) => d.duration === taxaMaisProxima + selectedDuration,
            ) as PontoCurvaNTNB),
          }
        : {
            tipo: "dap",
            ...(data.ajustes_dap.dados.find(
              (d) => d.duration === dapMaisProximo + selectedDuration,
            ) as PontoCurvaNTNB),
          }
      : null;

  const taxa = data?.curva.find((p) => p.duration === selectedDuration)?.taxa;

  const gridNTNB = useMemo(
    () => (
      <ValidationGrid
        data={structuredClone(data?.taxas_indicativas.dados ?? [])}
        colDefs={colDefsTaxas}
        editable={editingTaxas}
        identifier="data_vencimento"
        cellValidators={{
          taxa: [required],
        }}
        onClientDataChanged={({ modified }) => setEditedTaxas(modified)}
      />
    ),
    [data, editingTaxas],
  );

  const gridDAP = useMemo(
    () => (
      <ValidationGrid
        data={structuredClone(data?.ajustes_dap.dados ?? [])}
        colDefs={colDefsDaps}
        editable={editingDaps}
        identifier="data_vencimento"
        onClientDataChanged={({ modified }) => setEditedDaps(modified)}
        rowHeight={64}
      />
    ),
    [data, editingDaps],
  );

  const {
    isOpen: isSaveTaxasOpen,
    onClose: onSaveTaxasClose,
    onOpen: onSaveTaxasOpen,
  } = useDisclosure();
  const {
    isOpen: isSaveDapsOpen,
    onClose: onSaveDapsClose,
    onOpen: onSaveDapsOpen,
  } = useDisclosure();

  const [savingTaxas, saveTaxas] = useAsync();
  const [savingDaps, saveDaps] = useAsync();

  const onConfirmTaxas = () =>
    saveTaxas(async () => {
      if (!data) return;
      const { data_referencia } = data.taxas_indicativas;
      const body = data.taxas_indicativas.dados.map(
        ({ data_vencimento, duration, taxa }) => {
          const modified = editedTaxas[data_vencimento]?.data.new;
          if (modified) {
            taxa = modified.taxa;
          }
          return { data_vencimento, taxa, duration };
        },
      );
      const response = await httpClient.fetch(
        `v1/indicadores/curva-ntnb/taxas_indicativas?data_referencia=${data_referencia}`,
        {
          method: "PUT",
          body: JSON.stringify(body),
        },
      );
      if (!response.ok) return;
      await fetchData();
      setEditingTaxas(false);
    });

  const onConfirmDaps = () =>
    saveDaps(async () => {
      if (!data) return;
      const { data_referencia } = data.ajustes_dap;
      const body = data.ajustes_dap.dados.map(
        ({ data_vencimento, duration, taxa }) => {
          const modified = editedDaps[data_vencimento]?.data.new;
          if (modified) {
            taxa = modified.taxa;
          }
          return { data_vencimento, taxa, duration };
        },
      );
      const response = await httpClient.fetch(
        `v1/indicadores/curva-ntnb/ajuste-dap?data_referencia=${data_referencia}`,
        {
          method: "PUT",
          body: JSON.stringify(body),
        },
      );
      if (!response.ok) return;
      await fetchData();
      setEditingDaps(false);
    });

  const chartRef = useRef<ChartJSOrUndefined<"line">>();

  const options = data
    ? ({
        scales: {
          x: {
            title: {
              display: true,
              text: "Duration",
              color: getColorHex("azul_1.main"),
            },
            type: "linear",
            min: 1,
            max,
          },
          y: {
            title: {
              display: true,
              text: "Taxa (%)",
              color: getColorHex("azul_1.main"),
            },
            type: "linear",
            grid: {
              color({ tick }) {
                return getColorHex(
                  tick.value === 0 ? "cinza.500" : "cinza.main",
                );
              },
            },
          },
        },
        animation: false,
        plugins: {
          zoom: {
            pan: {
              enabled: true,
              mode: "x",
            },
            limits: {
              x: { min: 1, max },
            },
            zoom: {
              wheel: {
                enabled: true,
              },
              mode: "x",
            },
          },
          tooltip: {
            enabled: true,
            intersect: false,
            callbacks: {
              title: ([
                {
                  parsed: { x },
                },
              ]) => `Duration: ${fmtNumber(x, 3)}`,
              label({ raw, formattedValue, dataset }) {
                const values = [dataset.label ?? ""];
                const data = raw as Record<string, string>;
                if ("ntnb" in data) {
                  values[0] = `NTN-B: ${fmtDate(data["ntnb"])}`;
                }
                if ("dap" in data) {
                  const [ano, mes] = data["dap"].split("-");
                  values[0] = `DAP ${letters[Number(mes) - 1]}${ano.substring(2)}: ${months[Number(mes) - 1]}/${ano}`;
                }
                values.push(`Taxa: ${formattedValue}`);
                return values;
              },
            },
          },
        },
      } as ChartOptions)
    : {};
  const datasets = data
    ? ([
        {
          label: "Derivativo utilizado",
          data: data.ajustes_dap.dados
            .filter((p) => p.utilizado)
            .map((p) => ({ x: p.duration, y: p.taxa, dap: p.data_vencimento })),
          pointRadius: 4,
          pointBackgroundColor: getColorHex("amarelo.main"),
          pointBorderColor: getColorHex("amarelo.900"),
          borderWidth: 1,
          borderColor: getColorHex("amarelo.main"),
          showLine: false,
        },
        {
          label: "Taxa Indicativa",
          data: data.taxas_indicativas.dados.map((p) => ({
            x: p.duration,
            y: p.taxa,
            ntnb: p.data_vencimento,
          })),
          pointRadius: 4,
          pointBackgroundColor: getColorHex("verde.main"),
          pointBorderColor: getColorHex("verde.900"),
          borderWidth: 1,
          borderColor: getColorHex("verde.main"),
          showLine: false,
        },
        {
          label: "Derivativo inutilizado",
          data: data.ajustes_dap.dados
            .filter((p) => !p.utilizado)
            .map((p) => ({ x: p.duration, y: p.taxa, dap: p.data_vencimento })),
          pointRadius: 4,
          pointBackgroundColor: getColorHex("rosa.main"),
          pointBorderColor: getColorHex("rosa.900"),
          borderWidth: 1,
          borderColor: getColorHex("rosa.main"),
          showLine: false,
        },
        {
          label: "Ponto interpolado",
          data: data.curva.map((p) => ({ x: p.duration, y: p.taxa })),
          pointRadius: 1,
          pointBackgroundColor: getColorHex("azul_2.main"),
          pointBorderColor: getColorHex("azul_2.900"),
          borderWidth: 1,
          spanGaps: true,
          borderColor: getColorHex("azul_4.main"),
          backgroundColor: getColorHex("azul_3.main") + "2f",
          fill: "origin",
        },
      ] as ChartDataset[])
    : [];

  const { user } = useUser();

  return (
    <HResize
      w="100%"
      h="100%"
      startingLeftWidth={330}
      leftElement={
        <VResize
          minW="330px"
          h="100%"
          gap={0}
          topElement={
            <VStack w="100%" h="100%" alignItems="flex-start" gap={0}>
              <Hint>NTN-Bs</Hint>
              <VStack
                w="100%"
                h="100%"
                alignItems="flex-start"
                border="1px solid"
                borderColor="cinza.main"
                overflow="hidden"
                borderRadius="8px"
                gap={0}
              >
                {user?.roles
                  .map((r) => r.nome)
                  .includes("Indicadores - Editar") && (
                  <GridEditBar
                    editedCount={Object.keys(editedTaxas).length}
                    editing={editingTaxas}
                    setEditing={setEditingTaxas}
                    onSave={onSaveTaxasOpen}
                  />
                )}
                <Box flex={1} w="100%">
                  {gridNTNB}
                </Box>
              </VStack>
            </VStack>
          }
          bottomElement={
            <VStack w="100%" h="100%" alignItems="flex-start" gap={0}>
              <Hint>Derivativos</Hint>
              <VStack
                w="100%"
                h="100%"
                alignItems="flex-start"
                border="1px solid"
                borderColor="cinza.main"
                overflow="hidden"
                borderRadius="8px"
                gap={0}
              >
                {user?.roles
                  .map((r) => r.nome)
                  .includes("Indicadores - Editar") && (
                  <GridEditBar
                    editedCount={Object.keys(editedDaps).length}
                    editing={editingDaps}
                    setEditing={setEditingDaps}
                    onSave={onSaveDapsOpen}
                  />
                )}
                <Box flex={1} w="100%">
                  {gridDAP}
                </Box>
              </VStack>
            </VStack>
          }
        />
      }
      rightElement={
        <>
          <VStack w="100%" minW="720px" h="100%" alignItems="flex-start">
            <VStack w="100%" gap={0} alignItems="flex-start">
              <Hint>Consultar ponto</Hint>
              <VStack
                w="100%"
                border="1px solid"
                borderColor="cinza.main"
                overflow="hidden"
                borderRadius="8px"
                p="12px"
                alignItems="flex-start"
              >
                <HStack alignItems="stretch" gap="12px">
                  <VStack
                    gap={0}
                    justifyContent="space-between"
                    alignItems="flex-start"
                    border="1px solid"
                    borderColor="cinza.main"
                    overflow="hidden"
                    borderRadius="8px"
                    p="12px"
                  >
                    <Text fontSize="xs">
                      Duration {max !== 1 ? `(1 a ${max})` : ""}
                    </Text>
                    <NumberInput
                      allowMouseWheel
                      isDisabled={max === 1}
                      focusBorderColor="verde.main"
                      size="sm"
                      defaultValue={1}
                      min={1}
                      max={Math.max(max, 1)}
                      step={1}
                      keepWithinRange={true}
                      clampValueOnBlur={true}
                      onChange={(_, n) => setSelectedDuration(isNaN(n) ? 1 : n)}
                      value={selectedDuration}
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </VStack>
                  <VStack
                    alignItems="flex-start"
                    minW="96px"
                    gap={0}
                    justifyContent="space-between"
                    border="1px solid"
                    borderColor="cinza.main"
                    overflow="hidden"
                    borderRadius="8px"
                    p="12px"
                  >
                    <Text fontSize="xs">Taxa</Text>
                    <Box h="32px">
                      <Text>{taxa ? fmtNumber(taxa, 2) : "---"}</Text>
                    </Box>
                  </VStack>
                  <VStack
                    alignItems="stretch"
                    border="1px solid"
                    borderColor="cinza.main"
                    overflow="hidden"
                    borderRadius="8px"
                    p="12px"
                    justifyContent="center"
                  >
                    <Text fontSize="xs">Ponto na curva mais próximo</Text>
                    {pontoMaisProximo ? (
                      <HStack h="32px" divider={<StackDivider />}>
                        {pontoMaisProximo.tipo === "dap" ? (
                          <Text color="amarelo.main">Derivativo</Text>
                        ) : (
                          <Text color="verde.main">Taxa</Text>
                        )}
                        <VStack gap={0} alignItems="flex-start">
                          <Text fontSize="xs">
                            Taxa: {fmtNumber(pontoMaisProximo.taxa, 2)}
                          </Text>
                          <Text fontSize="xs">
                            Duration: {fmtNumber(pontoMaisProximo.duration, 2)}
                          </Text>
                        </VStack>
                      </HStack>
                    ) : (
                      <Text h="32px">---</Text>
                    )}
                  </VStack>
                </HStack>
              </VStack>
            </VStack>
            <VStack flex={1} w="100%" gap={0} alignItems="flex-start">
              <Hint>Visualização da curva</Hint>
              <VStack
                w="100%"
                h="100%"
                alignItems="flex-start"
                border="1px solid"
                borderColor="cinza.main"
                overflow="hidden"
                borderRadius="8px"
                p="12px"
              >
                <HStack
                  w="100%"
                  alignItems="flex-start"
                  justifyContent="space-between"
                  overflow="auto"
                >
                  <HStack gap="24px">
                    <VStack
                      gap={0}
                      justifyContent="space-between"
                      alignItems="flex-start"
                      border="1px solid"
                      borderColor="cinza.main"
                      overflow="hidden"
                      borderRadius="8px"
                      p="12px"
                    >
                      <Text fontSize="xs" flex={1}>
                        Consultar dia
                      </Text>
                      <Input
                        size="sm"
                        type="date"
                        value={date}
                        onChange={(ev) => setDate(ev.target.value)}
                      />
                    </VStack>
                    <VStack
                      gap={0}
                      justifyContent="space-between"
                      alignItems="flex-start"
                      border="1px solid"
                      borderColor="cinza.main"
                      overflow="hidden"
                      borderRadius="8px"
                      p="12px"
                    >
                      <Text fontSize="xs">Data referência</Text>
                      <VStack gap={0} alignItems="flex-start" h="32px">
                        <Text fontSize="xs">
                          <CalendarIcon
                            fontSize="8px"
                            verticalAlign="center"
                            mr="4px"
                          />
                          {data?.ajustes_dap.data_referencia ? (
                            <Text h="32px" pt="6px" as="span">
                              {" "}
                              {fmtDate(data.ajustes_dap.data_referencia)}
                            </Text>
                          ) : (
                            <Text as="span"> ---</Text>
                          )}
                          <Text as="span" color="amarelo.main" ml="4px">
                            {" "}
                            Derivativos
                          </Text>
                        </Text>
                        <Text fontSize="xs">
                          <CalendarIcon
                            fontSize="8px"
                            verticalAlign="center"
                            mr="4px"
                          />
                          {data?.taxas_indicativas.data_referencia ? (
                            <Text as="span">
                              {" "}
                              {fmtDate(data.taxas_indicativas.data_referencia)}
                            </Text>
                          ) : (
                            <Text as="span"> ---</Text>
                          )}
                          <Text as="span" color="verde.main" ml="4px">
                            {" "}
                            Taxas Ind.
                          </Text>
                        </Text>
                      </VStack>
                    </VStack>
                    <VStack
                      gap={0}
                      justifyContent="space-between"
                      alignItems="flex-start"
                      border="1px solid"
                      borderColor="cinza.main"
                      overflow="hidden"
                      borderRadius="8px"
                      p="12px"
                    >
                      <Hint color="black">Zoom</Hint>
                      <HStack h="32px">
                        <Button
                          colorScheme="azul_4"
                          size="xs"
                          onClick={() => {
                            chartRef.current?.resetZoom();
                          }}
                        >
                          Redefinir
                        </Button>
                      </HStack>
                    </VStack>
                  </HStack>
                  <Button
                    size="sm"
                    minW="144px"
                    isDisabled={true /*labels.length === 0*/}
                    colorScheme="verde"
                    leftIcon={<DownloadIcon />}
                  >
                    Baixar planilha
                  </Button>
                </HStack>
                <Progress
                  w="100%"
                  colorScheme="verde"
                  isIndeterminate
                  visibility={loading ? "visible" : "hidden"}
                />
                <Box w="100%" flex={1}>
                  <Chart
                    type="line"
                    ref={chartRef}
                    data={{ datasets }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      ...options,
                    }}
                  />
                </Box>
                <HStack w="100%" justifyContent="space-between">
                  <HStack>
                    <Hint mr="12px">
                      Última atualização (Derivativos):{" "}
                      {dapAtualizadoEm && fmtDate(dapAtualizadoEm)}
                    </Hint>
                    <Hint>
                      Última atualização (Taxas indicativas):{" "}
                      {taxaAtualizadaEm && fmtDate(taxaAtualizadaEm)}
                    </Hint>
                  </HStack>
                  <HStack>
                    <Legenda text="NTN-B" colorScheme="verde" />
                    <Legenda text="DAP utilizado" colorScheme="amarelo" />
                    <Legenda text="Ponto Interpolado" colorScheme="azul_2" />
                    <Legenda text="DAP inutilizado" colorScheme="rosa" />
                  </HStack>
                </HStack>
              </VStack>
            </VStack>
          </VStack>
          <ConfirmModal
            isOpen={savingTaxas ? true : isSaveTaxasOpen}
            onClose={onSaveTaxasClose}
            onConfirmAction={onConfirmTaxas}
            confirmEnabled={!savingTaxas}
            size="3xl"
          >
            <Box w="100%" h="60vh" minH="480px">
              <DiffSummary
                added={[]}
                deleted={[]}
                modified={editedTaxas}
                colDefs={colDefsTaxas.slice(1)}
                identifier="data_vencimento"
                showDeleted={false}
                showAdded={false}
              />
            </Box>
            <Progress
              isIndeterminate
              colorScheme="verde"
              visibility={savingTaxas ? "visible" : "hidden"}
            />
          </ConfirmModal>
          <ConfirmModal
            isOpen={savingDaps ? true : isSaveDapsOpen}
            onClose={onSaveDapsClose}
            onConfirmAction={onConfirmDaps}
            confirmEnabled={!savingDaps}
            size="3xl"
          >
            <Box w="100%" h="60vh" minH="480px">
              <DiffSummary
                added={[]}
                deleted={[]}
                modified={editedDaps}
                colDefs={colDefsDaps.slice(1)}
                identifier="data_vencimento"
                showDeleted={false}
                showAdded={false}
              />
            </Box>
            <Progress
              isIndeterminate
              colorScheme="verde"
              visibility={savingDaps ? "visible" : "hidden"}
            />
          </ConfirmModal>
        </>
      }
    />
  );
}
