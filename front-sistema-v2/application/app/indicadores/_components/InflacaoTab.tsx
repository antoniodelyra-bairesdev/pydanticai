import ValidationGrid, {
  ModificationMap,
} from "@/app/_components/grid/ValidationGrid";
import Hint from "@/app/_components/texto/Hint";
import { getColorHex } from "@/app/theme";
import { useAsync, useHTTP, useUser } from "@/lib/hooks";
import { IPCA, IPCAProj } from "@/lib/types/api/iv/v1";
import { dateToStr, fmtDate } from "@/lib/util/string";
import { CalendarIcon } from "@chakra-ui/icons";
import {
  Box,
  Button,
  Checkbox,
  HStack,
  Icon,
  Input,
  Progress,
  StackDivider,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import { ICellRendererParams, ValueSetterParams } from "ag-grid-community";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Line } from "react-chartjs-2";
import { IoAnalytics, IoBarChart, IoTimeOutline } from "react-icons/io5";
import GridEditBar from "./GridEditBar";
import Legenda from "./Legenda";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import DiffSummary from "@/app/_components/modal/DiffSummary";
import HResize from "@/app/_components/misc/HResize";
import VResize from "@/app/_components/misc/VResize";

type IGPM = IPCA;
type IGPMProj = IPCAProj;

const maxDate = (dates: Date[]) =>
  new Date(Math.max(...dates.map((d) => Number(d))));

const numSetter = (field: string) => (params: ValueSetterParams) => {
  const num = params.newValue !== null ? Number(params.newValue) : 0;
  params.data[field] = isNaN(num) ? 0 : num;
  return true;
};

const projRenderer = (params: ICellRendererParams) => {
  return String(params.value) === "false" ? (
    <Text fontSize="xs">
      <Icon color="verde.main" as={IoBarChart} /> Fechado
    </Text>
  ) : (
    <Text fontSize="xs">
      <Icon color="cinza.500" as={IoTimeOutline} /> Projetado
    </Text>
  );
};

const dateRenderer = (params: ICellRendererParams) => {
  return (
    <Text fontSize="xs">
      <CalendarIcon color="cinza.400" /> {fmtDate(params.value)}
    </Text>
  );
};

const taxaRenderer = (params: ICellRendererParams) => {
  return <Text fontSize="xs">{params.value}</Text>;
};

const projColDefs = [
  {
    width: 100,
    field: "data",
    headerName: "Data",
    editable: false,
    cellRenderer: dateRenderer,
  },
  {
    width: 80,
    field: "projetado",
    headerName: "Projetado",
    editable: false,
    cellRenderer: projRenderer,
  },
  {
    width: 120,
    field: "projecao",
    headerName: "Projeção",
    valueSetter: numSetter("projecao"),
    cellRenderer: taxaRenderer,
  },
];

const indiceColDefs = [
  {
    width: 110,
    field: "data",
    headerName: "Data",
    editable: false,
    cellRenderer: dateRenderer,
  },
  {
    width: 190,
    field: "indice_acumulado",
    headerName: "Acumulado",
    valueSetter: numSetter("indice_acumulado"),
    cellRenderer: taxaRenderer,
  },
];

export default function InflacaoTab() {
  const [ipca, setIpca] = useState<IPCA[]>([]);
  const [igpm, setIgpm] = useState<IGPM[]>([]);

  const [showIpca, setShowIpca] = useState(true);
  const [showIpcaClosed, setShowIpcaClosed] = useState(true);
  const [showIpcaProjected, setShowIpcaProjected] = useState(true);

  const [showIgpm, setShowIgpm] = useState(true);
  const [showIgpmClosed, setShowIgpmClosed] = useState(true);
  const [showIgpmProjected, setShowIgpmProjected] = useState(true);

  const [ipcaProj, setIpcaProj] = useState<IPCAProj[]>([]);
  const [igpmProj, setIgpmProj] = useState<IGPMProj[]>([]);

  const [editingIpca, setEditingIpca] = useState(false);
  const [editingIgpm, setEditingIgpm] = useState(false);
  const [editingIpcaProj, setEditingIpcaProj] = useState(false);
  const [editingIgpmProj, setEditingIgpmProj] = useState(false);

  const [editedIpca, setEditedIpca] = useState<ModificationMap<IPCA>>({});
  const [editedIgpm, setEditedIgpm] = useState<ModificationMap<IGPM>>({});
  const [editedIpcaProj, setEditedIpcaProj] = useState<
    ModificationMap<IPCAProj>
  >({});
  const [editedIgpmProj, setEditedIgpmProj] = useState<
    ModificationMap<IGPMProj>
  >({});

  const {
    isOpen: isSaveIpcaOpen,
    onClose: onSaveIpcaClose,
    onOpen: onSaveIpcaOpen,
  } = useDisclosure();
  const {
    isOpen: isSaveIpcaProjOpen,
    onClose: onSaveIpcaProjClose,
    onOpen: onSaveIpcaProjOpen,
  } = useDisclosure();
  const {
    isOpen: isSaveIgpmOpen,
    onClose: onSaveIgpmClose,
    onOpen: onSaveIgpmOpen,
  } = useDisclosure();
  const {
    isOpen: isSaveIgpmProjOpen,
    onClose: onSaveIgpmProjClose,
    onOpen: onSaveIgpmProjOpen,
  } = useDisclosure();

  const [dataInicio, setDataInicio] = useState(
    `${new Date().getFullYear() - 1}-01-01`,
  );
  const [dataFim, setDataFim] = useState(dateToStr(new Date()));

  const { user } = useUser();
  const httpClient = useHTTP({ withCredentials: true });
  const [savingIpca, saveIpca] = useAsync();
  const [savingIgpm, saveIgpm] = useAsync();
  const [savingIpcaProj, saveIpcaProj] = useAsync();
  const [savingIgpmProj, saveIgpmProj] = useAsync();

  const getIpca = useCallback(async () => {
    setIpca([]);
    setEditingIpca(false);
    setEditedIpca({});
    const response = await httpClient.fetch(
      `v1/indicadores/inflacao/ipca?inicio=${dataInicio}&fim=${dataFim}`,
      { hideToast: { success: true } },
    );
    if (!response.ok) return;
    setIpca((await response.json()) as IPCA[]);
  }, [dataInicio, dataFim]);

  const getIgpm = useCallback(async () => {
    setIgpm([]);
    setEditingIgpm(false);
    setEditedIgpm({});
    const response = await httpClient.fetch(
      `v1/indicadores/inflacao/igpm?inicio=${dataInicio}&fim=${dataFim}`,
      { hideToast: { success: true } },
    );
    if (!response.ok) return;
    setIgpm((await response.json()) as IPCA[]);
  }, [dataInicio, dataFim]);

  const getIpcaProj = useCallback(async () => {
    setIpcaProj([]);
    setEditingIpcaProj(false);
    setEditedIpcaProj({});
    const response = await httpClient.fetch(
      `v1/indicadores/inflacao/ipca/projecao?inicio=${dataInicio}&fim=${dataFim}`,
      { hideToast: { success: true } },
    );
    if (!response.ok) return;
    setIpcaProj((await response.json()) as IPCAProj[]);
  }, [dataInicio, dataFim]);

  const getIgpmProj = useCallback(async () => {
    setIgpmProj([]);
    setEditingIgpmProj(false);
    setEditedIgpmProj({});
    const response = await httpClient.fetch(
      `v1/indicadores/inflacao/igpm/projecao?inicio=${dataInicio}&fim=${dataFim}`,
      { hideToast: { success: true } },
    );
    if (!response.ok) return;
    setIgpmProj((await response.json()) as IGPMProj[]);
  }, [dataInicio, dataFim]);

  useEffect(() => {
    getIpca();
    getIgpm();
    getIpcaProj();
    getIgpmProj();
  }, [dataInicio, dataFim]);

  const ultimaAtualizacaoIpca =
    ipca.length > 0
      ? fmtDate(dateToStr(maxDate(ipca.map((i) => new Date(i.atualizacao)))))
      : "";

  const ultimaAtualizacaoIgpm =
    igpm.length > 0
      ? fmtDate(dateToStr(maxDate(igpm.map((i) => new Date(i.atualizacao)))))
      : "";

  const gridIpca = useMemo(
    () => (
      <ValidationGrid
        colDefs={indiceColDefs}
        data={structuredClone(ipca)}
        editable={editingIpca}
        identifier="data"
        onClientDataChanged={({ modified }) => setEditedIpca(modified)}
      />
    ),
    [ipca, editingIpca],
  );

  const gridIgpm = useMemo(
    () => (
      <ValidationGrid
        colDefs={indiceColDefs}
        data={structuredClone(igpm)}
        editable={editingIgpm}
        identifier="data"
        onClientDataChanged={({ modified }) => setEditedIgpm(modified)}
      />
    ),
    [igpm, editingIgpm],
  );

  const gridIpcaProj = useMemo(
    () => (
      <ValidationGrid
        colDefs={projColDefs}
        data={structuredClone(ipcaProj)}
        editable={editingIpcaProj}
        identifier="data"
        onClientDataChanged={({ modified }) => setEditedIpcaProj(modified)}
      />
    ),
    [ipcaProj, editingIpcaProj],
  );

  const gridIgpmProj = useMemo(
    () => (
      <ValidationGrid
        colDefs={projColDefs}
        data={structuredClone(igpmProj)}
        editable={editingIgpmProj}
        identifier="data"
        onClientDataChanged={({ modified }) => setEditedIgpmProj(modified)}
      />
    ),
    [igpmProj, editingIgpmProj],
  );

  const updateIpca = () =>
    saveIpca(async () => {
      const body = JSON.stringify(
        ipca.map(({ data, indice_acumulado }) => {
          const modified = editedIpca[data]?.data.new;
          if (modified) {
            indice_acumulado = Number(modified.indice_acumulado);
          }
          return { data, indice_acumulado };
        }),
      );
      const response = await httpClient.fetch("v1/indicadores/inflacao/ipca", {
        method: "PUT",
        body,
      });
      if (!response.ok) return;
      await getIpca();
    });

  const updateIgpm = () =>
    saveIgpm(async () => {
      const body = JSON.stringify(
        igpm.map(({ data, indice_acumulado }) => {
          const modified = editedIgpm[data]?.data.new;
          if (modified) {
            indice_acumulado = Number(modified.indice_acumulado);
          }
          return { data, indice_acumulado };
        }),
      );
      const response = await httpClient.fetch("v1/indicadores/inflacao/igpm", {
        method: "PUT",
        body,
      });
      if (!response.ok) return;
      await getIgpm();
    });

  const updateIpcaProj = () =>
    saveIpcaProj(async () => {
      const body = JSON.stringify(
        ipcaProj.map(({ data, projecao, projetado }) => {
          const modified = editedIpcaProj[data]?.data.new;
          if (modified) {
            projecao = Number(modified.projecao);
          }
          return { data, projetado, taxa: projecao };
        }),
      );
      const response = await httpClient.fetch(
        "v1/indicadores/inflacao/ipca/projecao",
        { method: "PUT", body },
      );
      if (!response.ok) return;
      await getIpcaProj();
    });

  const updateIgpmProj = () =>
    saveIgpmProj(async () => {
      const body = JSON.stringify(
        igpmProj.map(({ data, projecao, projetado }) => {
          const modified = editedIgpmProj[data]?.data.new;
          if (modified) {
            projecao = Number(modified.projecao);
          }
          return { data, projetado, taxa: projecao };
        }),
      );
      const response = await httpClient.fetch(
        "v1/indicadores/inflacao/igpm/projecao",
        { method: "PUT", body },
      );
      if (!response.ok) return;
      await getIgpmProj();
    });

  return (
    <VStack w="100%" h="100%" alignItems="stretch">
      <VStack alignItems="flex-start" gap={0}>
        <Hint>Controles</Hint>
        <HStack
          justifyContent="flex-end"
          w="100%"
          border="1px solid"
          borderColor="cinza.main"
          borderRadius="8px"
          p="6px"
          gap="24px"
        >
          <HStack
            divider={<StackDivider />}
            justifyContent="space-between"
            alignItems="center"
            border="1px solid"
            borderColor="cinza.main"
            overflow="hidden"
            borderRadius="8px"
            p="6px"
          >
            <Text fontSize="xs" flex={1}>
              Período da consulta
            </Text>
            <HStack>
              <Input
                size="xs"
                type="date"
                value={dataInicio}
                onChange={(ev) => setDataInicio(ev.target.value)}
              />
              <Input
                size="xs"
                type="date"
                value={dataFim}
                onChange={(ev) => setDataFim(ev.target.value)}
              />
            </HStack>
          </HStack>
          <HStack
            divider={<StackDivider />}
            justifyContent="space-between"
            alignItems="center"
            border="1px solid"
            borderColor="cinza.main"
            overflow="hidden"
            borderRadius="8px"
            p="6px"
          >
            <Text fontSize="xs" flex={1}>
              Exibir
            </Text>
            <HStack>
              <HStack>
                <Checkbox
                  colorScheme="verde"
                  isChecked={showIpca}
                  onChange={(ev) => setShowIpca(ev.target.checked)}
                />
                <Text fontSize="sm">IPCA</Text>
              </HStack>
              <HStack>
                <Checkbox
                  colorScheme="azul_1"
                  isChecked={showIgpm}
                  onChange={(ev) => setShowIgpm(ev.target.checked)}
                />
                <Text fontSize="sm">IGPM</Text>
              </HStack>
            </HStack>
          </HStack>
          {/* <HStack>
                    <Input size='sm' maxW='180px' type="date" />
                    <Input size='sm' maxW='180px' type="date" />
                </HStack> */}
        </HStack>
      </VStack>
      <HResize
        flex={1}
        w="100%"
        startingLeftWidth={650}
        leftElement={
          <VResize
            w="100%"
            h="100%"
            startingProportion={0.4}
            topElement={
              <HStack w="100%" h="100%" alignItems="stretch">
                <VStack alignItems="flex-start" gap={0} minW="320px" flex={1}>
                  <Hint>Histórico - IPCA</Hint>
                  <HStack
                    w="100%"
                    flex={1}
                    border="1px solid"
                    borderColor="cinza.main"
                    borderRadius="8px"
                    gap="24px"
                    overflow="hidden"
                  >
                    <VStack w="100%" h="100%">
                      {user?.roles
                        .map((r) => r.nome)
                        .includes("Indicadores - Editar") && (
                        <GridEditBar
                          editing={editingIpca}
                          setEditing={setEditingIpca}
                          editedCount={Object.keys(editedIpca).length}
                          onSave={onSaveIpcaOpen}
                        />
                      )}
                      <Box flex={1} w="100%">
                        {gridIpca}
                      </Box>
                    </VStack>
                  </HStack>
                </VStack>
                <VStack alignItems="flex-start" gap={0} minW="320px" flex={1}>
                  <Hint>Histórico - IGPM</Hint>
                  <HStack
                    w="100%"
                    flex={1}
                    border="1px solid"
                    borderColor="cinza.main"
                    borderRadius="8px"
                    gap="24px"
                    overflow="hidden"
                  >
                    <VStack w="100%" h="100%">
                      {user?.roles
                        .map((r) => r.nome)
                        .includes("Indicadores - Editar") && (
                        <GridEditBar
                          editing={editingIgpm}
                          setEditing={setEditingIgpm}
                          editedCount={Object.keys(editedIgpm).length}
                          onSave={onSaveIgpmOpen}
                        />
                      )}
                      <Box flex={1} w="100%">
                        {gridIgpm}
                      </Box>
                    </VStack>
                  </HStack>
                </VStack>
              </HStack>
            }
            bottomElement={
              <HStack w="100%" h="100%" alignItems="stretch">
                <VStack alignItems="flex-start" gap={0} minW="320px" flex={1}>
                  <Hint>Projeção - IPCA</Hint>
                  <HStack
                    w="100%"
                    flex={1}
                    border="1px solid"
                    borderColor="cinza.main"
                    borderRadius="8px"
                    gap="24px"
                    overflow="hidden"
                  >
                    <VStack w="100%" h="100%">
                      {user?.roles
                        .map((r) => r.nome)
                        .includes("Indicadores - Editar") && (
                        <GridEditBar
                          editing={editingIpcaProj}
                          setEditing={setEditingIpcaProj}
                          editedCount={Object.keys(editedIpcaProj).length}
                          onSave={onSaveIpcaProjOpen}
                        />
                      )}
                      <Box flex={1} w="100%">
                        {gridIpcaProj}
                      </Box>
                    </VStack>
                  </HStack>
                </VStack>
                <VStack alignItems="flex-start" gap={0} minW="320px" flex={1}>
                  <Hint>Projeção - IGPM</Hint>
                  <HStack
                    w="100%"
                    flex={1}
                    border="1px solid"
                    borderColor="cinza.main"
                    borderRadius="8px"
                    gap="24px"
                    overflow="hidden"
                  >
                    <VStack w="100%" h="100%">
                      {user?.roles
                        .map((r) => r.nome)
                        .includes("Indicadores - Editar") && (
                        <GridEditBar
                          editing={editingIgpmProj}
                          setEditing={setEditingIgpmProj}
                          editedCount={Object.keys(editedIgpmProj).length}
                          onSave={onSaveIgpmProjOpen}
                        />
                      )}
                      <Box flex={1} w="100%">
                        {gridIgpmProj}
                      </Box>
                    </VStack>
                  </HStack>
                </VStack>
              </HStack>
            }
          />
        }
        rightElement={
          <VStack w="100%" h="100%" alignItems="stretch">
            <HStack flex={2} alignItems="stretch">
              <VStack alignItems="flex-start" gap={0} flex={1}>
                <Hint>Histórico</Hint>
                <VStack
                  flex={1}
                  w="100%"
                  border="1px solid"
                  borderColor="cinza.main"
                  borderRadius="8px"
                  p="12px"
                  alignItems="stretch"
                >
                  <Box flex={1}>
                    <Line
                      data={{
                        labels: ipca.map((p) => fmtDate(p.data)),
                        datasets: [
                          ...(showIpca
                            ? [
                                {
                                  data: ipca.map(
                                    (p) => (p.indice_acumulado - 1) * 100,
                                  ),
                                  pointRadius: 4,
                                  pointBackgroundColor:
                                    getColorHex("verde.main"),
                                  pointBorderColor: getColorHex("verde.900"),
                                  borderWidth: 1,
                                  spanGaps: true,
                                  borderColor: getColorHex("verde.main"),
                                  backgroundColor:
                                    getColorHex("verde.main") + "2f",
                                  fill: "origin",
                                },
                              ]
                            : []),
                          ...(showIgpm
                            ? [
                                {
                                  data: igpm.map(
                                    (p) => (p.indice_acumulado - 1) * 100,
                                  ),
                                  pointRadius: 4,
                                  pointBackgroundColor:
                                    getColorHex("azul_2.main"),
                                  pointBorderColor: getColorHex("azul_1.900"),
                                  borderWidth: 1,
                                  spanGaps: true,
                                  borderColor: getColorHex("azul_2.main"),
                                  backgroundColor:
                                    getColorHex("azul_2.main") + "2f",
                                  fill: "origin",
                                },
                              ]
                            : []),
                        ],
                      }}
                      options={{
                        maintainAspectRatio: false,
                        responsive: true,
                        animation: false,
                        scales: {
                          y: {
                            grid: {
                              color({ tick }) {
                                return getColorHex(
                                  tick.value === 0 ? "cinza.500" : "cinza.main",
                                );
                              },
                            },
                          },
                        },
                        plugins: {
                          tooltip: {
                            intersect: false,
                          },
                          zoom: {
                            pan: {
                              enabled: true,
                              mode: "x",
                            },
                            zoom: {
                              wheel: {
                                enabled: true,
                              },
                              pinch: {
                                enabled: true,
                              },
                              mode: "x",
                            },
                          },
                        },
                      }}
                    />
                  </Box>
                  <HStack w="100%" justifyContent="space-between">
                    <HStack>
                      {ultimaAtualizacaoIpca && (
                        <Hint mr="12px">
                          Última atualização (IPCA): {ultimaAtualizacaoIpca}
                        </Hint>
                      )}
                      {ultimaAtualizacaoIgpm && (
                        <Hint>
                          Última atualização (IGPM): {ultimaAtualizacaoIgpm}
                        </Hint>
                      )}
                    </HStack>
                    <HStack>
                      <Legenda text="IPCA" colorScheme="verde" />
                      <Legenda
                        text="IGPM"
                        background="azul_2.main"
                        border="azul_1.900"
                      />
                    </HStack>
                  </HStack>
                </VStack>
              </VStack>
            </HStack>
            <HStack flex={3} alignItems="stretch">
              <VStack alignItems="flex-start" gap={0} flex={1}>
                <Hint>Projeção</Hint>
                <VStack
                  flex={1}
                  w="100%"
                  border="1px solid"
                  borderColor="cinza.main"
                  borderRadius="8px"
                  p="12px"
                  alignItems="stretch"
                >
                  <HStack>
                    <HStack
                      color={showIpca ? undefined : "cinza.main"}
                      border="1px solid"
                      borderColor="cinza.main"
                      borderRadius="8px"
                      p="6px"
                      alignItems="stretch"
                      divider={<StackDivider />}
                    >
                      <Text>
                        <Icon
                          verticalAlign="center"
                          color={showIpca ? "verde.main" : undefined}
                          as={IoAnalytics}
                        />{" "}
                        IPCA
                      </Text>
                      <HStack>
                        <HStack>
                          <Checkbox
                            colorScheme="verde"
                            isDisabled={!showIpca}
                            isChecked={showIpcaProjected}
                            onChange={(ev) =>
                              setShowIpcaProjected(ev.target.checked)
                            }
                          />
                          <Text fontSize="sm">Projeções</Text>
                        </HStack>
                        <HStack>
                          <Checkbox
                            colorScheme="verde"
                            isDisabled={!showIpca}
                            isChecked={showIpcaClosed}
                            onChange={(ev) =>
                              setShowIpcaClosed(ev.target.checked)
                            }
                          />
                          <Text fontSize="sm">Valores fechados</Text>
                        </HStack>
                      </HStack>
                    </HStack>
                    <HStack
                      color={showIgpm ? undefined : "cinza.main"}
                      border="1px solid"
                      borderColor="cinza.main"
                      borderRadius="8px"
                      p="6px"
                      alignItems="stretch"
                      divider={<StackDivider />}
                    >
                      <Text>
                        <Icon
                          verticalAlign="center"
                          color={showIgpm ? "azul_2.main" : undefined}
                          as={IoAnalytics}
                        />{" "}
                        IGPM
                      </Text>
                      <HStack>
                        <HStack>
                          <Checkbox
                            colorScheme="azul_1"
                            isDisabled={!showIgpm}
                            isChecked={showIgpmProjected}
                            onChange={(ev) =>
                              setShowIgpmProjected(ev.target.checked)
                            }
                          />
                          <Text fontSize="sm">Projeções</Text>
                        </HStack>
                        <HStack>
                          <Checkbox
                            colorScheme="azul_1"
                            isDisabled={!showIgpm}
                            isChecked={showIgpmClosed}
                            onChange={(ev) =>
                              setShowIgpmClosed(ev.target.checked)
                            }
                          />
                          <Text fontSize="sm">Valores fechados</Text>
                        </HStack>
                      </HStack>
                    </HStack>
                  </HStack>
                  <Box flex={1}>
                    <Line
                      data={{
                        labels: ipcaProj.map((p) => fmtDate(p.data)),
                        datasets: [
                          ...(showIpca && showIpcaClosed
                            ? [
                                {
                                  data: ipcaProj.map((p) =>
                                    p.projetado ? NaN : p.projecao,
                                  ),
                                  pointRadius: 4,
                                  pointBackgroundColor:
                                    getColorHex("verde.main"),
                                  pointBorderColor: getColorHex("verde.900"),
                                  borderWidth: 1,
                                  spanGaps: true,
                                  showLine: !showIpcaProjected,
                                  borderColor: getColorHex("verde.main"),
                                  backgroundColor:
                                    getColorHex("verde.main") + "2f",
                                  fill: !showIpcaProjected ? "origin" : false,
                                },
                              ]
                            : []),
                          ...(showIgpm && showIgpmClosed
                            ? [
                                {
                                  data: igpmProj.map((p) =>
                                    p.projetado ? NaN : p.projecao,
                                  ),
                                  pointRadius: 4,
                                  pointBackgroundColor:
                                    getColorHex("azul_2.main"),
                                  pointBorderColor: getColorHex("azul_1.900"),
                                  borderWidth: 1,
                                  spanGaps: true,
                                  showLine: !showIgpmProjected,
                                  borderColor: getColorHex("azul_2.main"),
                                  backgroundColor:
                                    getColorHex("azul_2.main") + "2f",
                                  fill: !showIgpmProjected ? "origin" : false,
                                },
                              ]
                            : []),
                          ...(showIpca && showIpcaProjected
                            ? [
                                {
                                  data: ipcaProj.map((p) => p.projecao),
                                  pointRadius: 1,
                                  pointBackgroundColor:
                                    getColorHex("verde.main"),
                                  pointBorderColor: getColorHex("verde.900"),
                                  borderWidth: 1,
                                  spanGaps: true,
                                  borderColor: getColorHex("verde.main"),
                                  backgroundColor:
                                    getColorHex("verde.main") + "2f",
                                  fill: "origin",
                                },
                              ]
                            : []),
                          ...(showIgpm && showIgpmProjected
                            ? [
                                {
                                  data: igpmProj.map((p) => p.projecao),
                                  pointRadius: 1,
                                  pointBackgroundColor:
                                    getColorHex("azul_2.main"),
                                  pointBorderColor: getColorHex("azul_1.900"),
                                  borderWidth: 1,
                                  spanGaps: true,
                                  borderColor: getColorHex("azul_2.main"),
                                  backgroundColor:
                                    getColorHex("azul_2.main") + "2f",
                                  fill: "origin",
                                },
                              ]
                            : []),
                        ],
                      }}
                      options={{
                        maintainAspectRatio: false,
                        responsive: true,
                        animation: false,
                        scales: {
                          y: {
                            grid: {
                              color({ tick }) {
                                return getColorHex(
                                  tick.value === 0 ? "cinza.500" : "cinza.main",
                                );
                              },
                            },
                          },
                        },
                        plugins: {
                          tooltip: {
                            intersect: false,
                          },
                          zoom: {
                            pan: {
                              enabled: true,
                              mode: "x",
                            },
                            zoom: {
                              wheel: {
                                enabled: true,
                              },
                              pinch: {
                                enabled: true,
                              },
                              mode: "x",
                            },
                          },
                        },
                      }}
                    />
                  </Box>
                  <HStack w="100%" justifyContent="space-between">
                    <HStack></HStack>
                    <HStack>
                      <Legenda
                        text="IPCA (Índice fechado)"
                        colorScheme="verde"
                      />
                      <Legenda
                        text="IGPM (Índice fechado)"
                        background="azul_2.main"
                        border="azul_1.900"
                      />
                      <Legenda
                        text="IPCA (Projeção)"
                        size="3px"
                        colorScheme="verde"
                      />
                      <Legenda
                        text="IGPM (Projeção)"
                        size="3px"
                        background="azul_2.main"
                        border="azul_1.900"
                      />
                    </HStack>
                  </HStack>
                </VStack>
              </VStack>
            </HStack>
            <ConfirmModal
              isOpen={savingIpca || isSaveIpcaOpen}
              onClose={onSaveIpcaClose}
              onConfirmAction={updateIpca}
              confirmEnabled={!savingIpca}
              size="3xl"
            >
              <Box w="100%" h="60vh" minH="480px">
                <DiffSummary
                  added={[]}
                  deleted={[]}
                  modified={editedIpca}
                  colDefs={indiceColDefs}
                  identifier="data"
                  showDeleted={false}
                  showAdded={false}
                />
              </Box>
              <Progress
                isIndeterminate
                colorScheme="verde"
                visibility={savingIpca ? "visible" : "hidden"}
              />
            </ConfirmModal>
            <ConfirmModal
              isOpen={savingIgpm || isSaveIgpmOpen}
              onClose={onSaveIgpmClose}
              onConfirmAction={updateIgpm}
              confirmEnabled={!savingIgpm}
              size="3xl"
            >
              <Box w="100%" h="60vh" minH="480px">
                <DiffSummary
                  added={[]}
                  deleted={[]}
                  modified={editedIgpm}
                  colDefs={indiceColDefs}
                  identifier="data"
                  showDeleted={false}
                  showAdded={false}
                />
              </Box>
              <Progress
                isIndeterminate
                colorScheme="verde"
                visibility={savingIgpm ? "visible" : "hidden"}
              />
            </ConfirmModal>
            <ConfirmModal
              isOpen={savingIpcaProj || isSaveIpcaProjOpen}
              onClose={onSaveIpcaProjClose}
              onConfirmAction={updateIpcaProj}
              confirmEnabled={!savingIpcaProj}
              size="3xl"
            >
              <Box w="100%" h="60vh" minH="480px">
                <DiffSummary
                  added={[]}
                  deleted={[]}
                  modified={editedIpcaProj}
                  colDefs={projColDefs}
                  identifier="data"
                  showDeleted={false}
                  showAdded={false}
                />
              </Box>
              <Progress
                isIndeterminate
                colorScheme="verde"
                visibility={savingIpcaProj ? "visible" : "hidden"}
              />
            </ConfirmModal>
            <ConfirmModal
              isOpen={savingIgpmProj || isSaveIgpmProjOpen}
              onClose={onSaveIgpmProjClose}
              onConfirmAction={updateIgpmProj}
              confirmEnabled={!savingIgpmProj}
              size="3xl"
            >
              <Box w="100%" h="60vh" minH="480px">
                <DiffSummary
                  added={[]}
                  deleted={[]}
                  modified={editedIgpmProj}
                  colDefs={projColDefs}
                  identifier="data"
                  showDeleted={false}
                  showAdded={false}
                />
              </Box>
              <Progress
                isIndeterminate
                colorScheme="verde"
                visibility={savingIgpmProj ? "visible" : "hidden"}
              />
            </ConfirmModal>
          </VStack>
        }
      />
    </VStack>
  );
}
