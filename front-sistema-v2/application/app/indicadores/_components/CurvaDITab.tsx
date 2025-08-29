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
import {
  IoAnalytics,
  IoBriefcaseOutline,
  IoSaveOutline,
  IoSquare,
  IoSquareOutline,
} from "react-icons/io5";

import { getColorHex } from "@/app/theme";

import { Chart, Line } from "react-chartjs-2";
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
import { dateToStr, fmtDate } from "@/lib/util/string";
import Hint from "@/app/_components/texto/Hint";
import { CurvaDIResponse } from "@/lib/types/api/iv/v1";
import { required } from "@/lib/util/validation";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import DiffSummary from "@/app/_components/modal/DiffSummary";
import { ChartDataset, ChartOptions } from "chart.js";
import { ChartJSOrUndefined } from "react-chartjs-2/dist/types";
import GridEditBar from "./GridEditBar";
import Legenda from "./Legenda";
import HResize from "@/app/_components/misc/HResize";

export default function CurvaDITab() {
  const httpClient = useHTTP({ withCredentials: true });

  const [date, setDate] = useState(dateToStr(new Date()));
  const [loading, load] = useAsync();

  const [data, setData] = useState<CurvaDIResponse>();

  const [editing, setEditing] = useState(false);

  const [selectedDay, setSelectedDay] = useState(1);

  const max = useMemo(
    () => Math.max(data?.curva.at(-1)?.dias_uteis ?? 1, 1),
    [data],
  );

  const atualizadoEm = data?.atualizacao ?? data?.dia ?? "";

  const colDefs: ValidationGridColDef[] = useMemo(
    () => [
      {
        width: 144,
        headerName: "Detalhes",
        editable: false,
        cellRenderer: (params: ICellRendererParams) => (
          <HStack
            bgColor={editing ? getColorHex("cinza.main") + "4f" : "none"}
            cursor={editing ? "not-allowed" : "auto"}
            p="4px"
            borderRadius="8px"
            fontSize="xs"
            alignItems="stretch"
            justifyContent="center"
            w="100%"
            h="100%"
            divider={<StackDivider />}
          >
            <VStack alignItems="flex-start" gap="4px" justifyContent="center">
              <HStack h="14px" justifyContent="space-between" w="100%">
                <Text>Dias corridos:</Text>
                <Text>{params.data.dias_corridos}</Text>
              </HStack>
              <HStack h="14px" justifyContent="space-between" w="100%">
                <Text>Data ref.:</Text>
                <Text>{fmtDate(params.data.data_referencia)}</Text>
              </HStack>
            </VStack>
          </HStack>
        ),
      },
      {
        width: 84,
        field: "dias_uteis",
        headerName: "D.U.",
        editable: false,
        cellRenderer: (params: ICellRendererParams) => (
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
            <Icon as={IoBriefcaseOutline} color="verde.main" />
            <Text>{params.data.dias_uteis}</Text>
          </HStack>
        ),
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
          <HStack w="100%" h="100%" p="4px">
            <Icon as={IoAnalytics} color="verde.main" />
            <Text>{params.valueFormatted ?? params.value}</Text>
          </HStack>
        ),
      },
    ],
    [editing],
  );

  const options = {
    scales: {
      x: {
        title: {
          display: true,
          text: "Dias úteis",
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
            return getColorHex(tick.value === 0 ? "cinza.500" : "cinza.main");
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
          title(tooltipItems) {
            const du = `Dias úteis: ${tooltipItems[0].parsed.x}`;
            const data = tooltipItems.at(-1)?.raw as
              | {
                  dc: number;
                  dr: string;
                }
              | undefined;
            return `${du}\n${
              data
                ? `Dias corridos: ${data.dc}\nData referência: ${fmtDate(data.dr)}`
                : ""
            }`;
          },
        },
      },
    },
  } as ChartOptions;

  const datasets = data
    ? ([
        {
          label: "Taxa na curva",
          data: data.curva
            .filter((p) => !p.interpolado)
            .map((p) => ({ x: p.dias_uteis, y: p.taxa })),
          pointRadius: 4,
          pointBackgroundColor: getColorHex("verde.main"),
          pointBorderColor: getColorHex("verde.900"),
          showLine: false,
        },
        {
          label: "Taxa interpolada",
          data: data.curva.map((p) => ({
            x: p.dias_uteis,
            y: p.taxa,
            dc: p.dias_corridos,
            dr: p.data_referencia,
          })),
          pointRadius: 0,
          pointBackgroundColor: getColorHex("azul_2.main"),
          borderWidth: 1,
          borderColor: getColorHex("azul_2.main"),
          backgroundColor: getColorHex("azul_3.main") + "2f",
          fill: "origin",
        },
      ] as ChartDataset[])
    : [];

  const fetchData = useCallback(async () => {
    setEditing(false);
    setEdited({});
    setData(undefined);
    const response = await httpClient.fetch(
      "v1/indicadores/curva-di?data=" + date,
      { hideToast: { success: true } },
    );
    if (!response.ok) return;
    const body = (await response.json()) as CurvaDIResponse;
    setData(body);
  }, [date]);

  useEffect(() => {
    if (!date) return;
    load(fetchData);
  }, [date]);

  const diaSelecionadoInterpolado =
    data?.curva[selectedDay - 1]?.interpolado === true;
  const diaSelecionadoNaCurva =
    data?.curva[selectedDay - 1]?.interpolado === false;

  const grid = useMemo(
    () => (
      <ValidationGrid
        data={structuredClone(
          (data?.curva ?? []).filter((p) => p.interpolado === false),
        )}
        colDefs={colDefs}
        editable={editing}
        identifier="dias_uteis"
        rowHeight={64}
        cellValidators={{
          taxa: [required],
        }}
        onClientDataChanged={({ modified }) => setEdited(modified)}
      />
    ),
    [data, editing],
  );

  const [edited, setEdited] = useState<
    ModificationMap<CurvaDIResponse["curva"][number]>
  >({});

  const { isOpen, onClose, onOpen } = useDisclosure();

  const [saving, save] = useAsync();

  const onConfirm = () =>
    save(async () => {
      if (!data) return;
      const body = data.curva
        .filter((p) => !p.interpolado)
        .map(({ dias_uteis, dias_corridos, taxa }) => {
          const modified = edited[dias_uteis]?.data.new;
          if (modified) {
            dias_corridos = modified.dias_corridos;
            taxa = modified.taxa;
          }
          return { dias_corridos, taxa };
        });
      const response = await httpClient.fetch(
        `v1/indicadores/curva-di?data=${data.dia}`,
        {
          method: "PUT",
          body: JSON.stringify(body),
        },
      );
      if (!response.ok) return;
      await fetchData();
    });

  const chartRef = useRef<ChartJSOrUndefined<"line">>();

  const { user } = useUser();

  return (
    <HResize
      w="100%"
      h="100%"
      startingLeftWidth={330}
      leftElement={
        <VStack alignItems="flex-start" minW="330px" h="100%" gap={0}>
          <Hint>Listagem de pontos na curva</Hint>
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
                editedCount={Object.keys(edited).length}
                editing={editing}
                setEditing={setEditing}
                onSave={onOpen}
              />
            )}
            <Box flex={1} w="100%">
              {grid}
            </Box>
          </VStack>
        </VStack>
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
                      Dia útil {max !== 1 ? `(1 a ${max})` : ""}
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
                      onChange={(_, n) => setSelectedDay(isNaN(n) ? 1 : n)}
                      value={selectedDay}
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
                      <Text>{data?.curva[selectedDay - 1]?.taxa ?? "---"}</Text>
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
                    <Text
                      fontSize="xs"
                      color={
                        diaSelecionadoNaCurva ? "verde.main" : "cinza.main"
                      }
                    >
                      <Icon
                        strokeWidth={2}
                        mr="4px"
                        as={diaSelecionadoNaCurva ? IoSquare : IoSquareOutline}
                      />
                      Ponto na curva
                    </Text>
                    <Text
                      fontSize="xs"
                      color={
                        diaSelecionadoInterpolado ? "azul_2.main" : "cinza.main"
                      }
                    >
                      <Icon
                        mr="4px"
                        as={
                          diaSelecionadoInterpolado ? IoSquare : IoSquareOutline
                        }
                      />
                      Ponto interpolado
                    </Text>
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
                overflow="none"
                borderRadius="8px"
                p="12px"
              >
                <HStack
                  w="100%"
                  alignItems="flex-start"
                  justifyContent="space-between"
                  overflow="auto"
                  wrap="nowrap"
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
                      {data?.dia ? (
                        <Text h="32px" fontSize="sm" pt="6px">
                          <CalendarIcon
                            fontSize="13px"
                            verticalAlign="center"
                            mr="8px"
                          />
                          {fmtDate(data.dia)}
                        </Text>
                      ) : (
                        <Text>---</Text>
                      )}
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
                    ref={chartRef}
                    type="line"
                    data={{ datasets }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      ...options,
                    }}
                  />
                </Box>

                <HStack w="100%" justifyContent="space-between">
                  <Hint>
                    Última atualização: {atualizadoEm && fmtDate(atualizadoEm)}
                  </Hint>
                  <HStack>
                    <Legenda text="Taxa na curva" colorScheme="verde" />
                  </HStack>
                </HStack>
              </VStack>
            </VStack>
          </VStack>
          <ConfirmModal
            isOpen={saving ? true : isOpen}
            onClose={onClose}
            onConfirmAction={onConfirm}
            confirmEnabled={!saving}
            size="3xl"
          >
            <Box w="100%" h="60vh" minH="480px">
              <DiffSummary
                added={[]}
                deleted={[]}
                modified={edited}
                colDefs={colDefs.slice(1)}
                identifier="dias_uteis"
                showDeleted={false}
                showAdded={false}
              />
            </Box>
            <Progress
              isIndeterminate
              colorScheme="verde"
              visibility={saving ? "visible" : "hidden"}
            />
          </ConfirmModal>
        </>
      }
    />
  );
}
