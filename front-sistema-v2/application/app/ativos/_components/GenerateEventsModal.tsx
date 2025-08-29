import { ValidationGridMethods } from "@/app/_components/grid/ValidationGrid";
import {
  dateColDef,
  listColDef,
  percentageColDef,
} from "@/app/_components/grid/colDefs";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import Hint from "@/app/_components/texto/Hint";
import { useAsync, useHTTP } from "@/lib/hooks";
import { Ativo, Evento } from "@/lib/types/api/iv/v1";
import { dateFilter, listFilter } from "@/lib/util/grid";
import { distribuir } from "@/lib/util/math";
import { wait } from "@/lib/util/misc";
import {
  SingularPluralMapping,
  fmtDate,
  pluralOrSingular,
  ptDateToYYYYMMDD,
  strCSSColor,
} from "@/lib/util/string";
import { validYYYYMMDD } from "@/lib/util/validation";
import { AddIcon, ArrowForwardIcon, CalendarIcon } from "@chakra-ui/icons";
import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  Box,
  Button,
  Card,
  CardBody,
  Divider,
  HStack,
  LightMode,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  Progress,
  Radio,
  RadioGroup,
  StackDivider,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import { ColumnApi, GridApi } from "ag-grid-community";
import {
  MutableRefObject,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import GenerateEventsGrid, { StagedEvent } from "./GenerateEventsGrid";
import GenerateEventsModalConfirmContents from "./GenerateEventsModalConfirmContents";
import InserirLinhasModal from "./InserirLinhasModal";

export type GenerateEventsModalProps = {
  ativo: Ativo;
  tipoEventos: string[];
  isOpen: boolean;
  eventsGridMethodsRef: MutableRefObject<
    ValidationGridMethods<Evento> | undefined
  >;
  onClose(): void;
};

const getNum = (setter: (n: number) => void) => (_: unknown, num: number) =>
  setter(isNaN(num) ? 1 : num);

const sm: SingularPluralMapping = {
  "€": { singular: "ê", plural: "e" },
  $: { singular: "s", plural: "ses" },
};

const ehAmortizacaoOuVencimento = (f: { tipo_evento?: string }) =>
  Boolean(f.tipo_evento && !f.tipo_evento.toLowerCase().includes("juros"));

export default function GenerateEventsModal({
  ativo,
  isOpen,
  eventsGridMethodsRef,
  onClose,
  tipoEventos,
}: GenerateEventsModalProps) {
  const cancelRef = useRef<HTMLButtonElement>(null);

  const [cellErrors, setCellErrors] = useState(0);
  const [juros, setJuros] = useState("bullet");
  const [jurosPeriodicos, setJurosPeriodicos] = useState(0);
  const [amortizacao, setAmortizacao] = useState("bullet");
  const [amortizacaoPeriodica, setAmortizacaoPeriodica] = useState(0);
  const [fluxos, setFluxos] = useState<
    { uuid: number; data: string; tipo_evento: string; percentual: number }[]
  >([]);
  const [accPercentage, setAccPercentage] = useState(0);
  const [dueCount, setDueCount] = useState(0);
  const [correctLastEvent, setCorrectLastEvent] = useState(false);
  const [percentageType, setPercentageType] = useState<
    "Base100" | "RelativoVNA"
  >("Base100");
  const [dueDateIs100, setDuePays100] = useState(false);
  const methodsRef = useRef<ValidationGridMethods<Evento & { uuid: number }>>();
  const colApiRef = useRef<ColumnApi | null>(null);
  const apiRef = useRef<GridApi | null>(null);

  const updatePercentageHeaderName = useCallback(() => {
    if (!apiRef.current || !colApiRef.current) return;
    const coldef = colApiRef.current.getColumn("percentual")?.getColDef();
    if (!coldef) return;
    coldef.headerName =
      percentageType === "Base100" ? "(%) Base 100" : "(%) Saldo devedor";
    apiRef.current.refreshHeader();
  }, [percentageType]);

  const {
    isOpen: newRowsIsOpen,
    onOpen: newRowsOnOpen,
    onClose: newRowsOnClose,
  } = useDisclosure();

  const {
    isOpen: confirmIsOpen,
    onOpen: confirmOnOpen,
    onClose: confirmOnClose,
  } = useDisclosure();

  useEffect(() => {
    setCellErrors(0);
    setJuros("bullet");
    setJurosPeriodicos(0);
    setAmortizacao("bullet");
    setAmortizacaoPeriodica(0);
    setFluxos([]);
    setAccPercentage(0);
    setDueCount(0);
    setCorrectLastEvent(false);
    setPercentageType("Base100");
    setDuePays100(false);
  }, [ativo, isOpen]);

  useEffect(() => {
    updatePercentageHeaderName();
  }, [percentageType]);

  const [loading, load] = useAsync();
  const [relativesReady, setRelativesReady] = useState<
    (StagedEvent & { percentual_relativoVNA: number })[]
  >([]);

  const httpClient = useHTTP({ withCredentials: true });

  const gerarFluxos = (ptype: typeof percentageType) =>
    load(async () => {
      methodsRef.current?.resetClientSideData();
      setFluxos([]);

      const atLeast = wait(500);

      const q = new URLSearchParams("");

      q.append("data_inicio_rentabilidade", ativo.inicio_rentabilidade);
      q.append("data_vencimento", ativo.data_vencimento);
      q.append("periodicidade_meses", String(jurosPeriodicos));
      const fluxosJuros = await httpClient.fetch(
        `v1/calculos/data/gerar-intervalos?${q.toString()}`,
        { hideToast: { success: true } },
      );
      if (!fluxosJuros.ok) return;
      const fluxosJurosData = (await fluxosJuros.json()) as string[];

      q.delete("periodicidade_meses");
      q.append("periodicidade_meses", String(amortizacaoPeriodica));
      const fluxosAmortizacao = await httpClient.fetch(
        `v1/calculos/data/gerar-intervalos?${q.toString()}`,
        { hideToast: { success: true } },
      );
      if (!fluxosAmortizacao.ok) return;
      const fluxosAmortizacaoData =
        (await fluxosAmortizacao.json()) as string[];

      await atLeast;

      const percentuais =
        ptype === "Base100"
          ? distribuir(1, fluxosAmortizacaoData.length, 8)
          : Array(fluxosAmortizacaoData.length)
              .fill(1)
              .map((inteiro, partes) => inteiro / (partes + 1))
              .reverse();

      const fluxosFinais = [
        ...fluxosJurosData.map((data) => ({
          uuid: Math.random(),
          data,
          tipo_evento: "Juros",
          percentual: 0,
        })),
        ...fluxosAmortizacaoData.map((data, i) => ({
          uuid: Math.random(),
          data,
          tipo_evento: "Amortização",
          percentual: percentuais[percentuais.length - 1 - i],
        })),
      ];
      fluxosFinais.sort((f1, f2) => f1.data.localeCompare(f2.data));
      if (fluxosFinais.length) {
        const ultimo = fluxosFinais.findLast(
          (e) => e.tipo_evento === "Amortização",
        );
        if (ultimo) {
          ultimo.tipo_evento = "Vencimento";
          setDueCount(1);
        } else {
          setDueCount(0);
        }
      } else {
        setDueCount(0);
      }
      setFluxos(fluxosFinais);
      const accumulated = fluxosFinais.reduce(
        (acc, fluxo) => fluxo.percentual + acc,
        0,
      );
      setCellErrors(0);
      setCorrectLastEvent(true);
      setAccPercentage(accumulated * 100);
      setDuePays100(true);
      return;
    });

  const redistribute = useCallback(async () => {
    const data = methodsRef.current?.getRowData() ?? [];
    let amortizacoesEVencimento = 0;
    data.forEach((f) => {
      if (ehAmortizacaoOuVencimento(f as any)) {
        amortizacoesEVencimento++;
      }
    });
    if (amortizacoesEVencimento === 0) return;
    const percentuais =
      percentageType === "Base100"
        ? distribuir(1, amortizacoesEVencimento, 8)
        : Array(amortizacoesEVencimento)
            .fill(1)
            .map((inteiro, partes) => inteiro / (partes + 1))
            .reverse();

    amortizacoesEVencimento = 0;
    const ajustados = data.map((f) => ({
      ...f,
      percentual: ehAmortizacaoOuVencimento(f as any)
        ? percentuais[amortizacoesEVencimento++]
        : 0,
    }));
    methodsRef.current?.updateRows(ajustados);
  }, [percentageType]);

  const convert = useCallback(
    () =>
      load(async () => {
        setPercentageType(
          percentageType === "Base100" ? "RelativoVNA" : "Base100",
        );

        const rows = methodsRef.current?.getRowData() ?? [];
        methodsRef.current?.resetClientSideData();
        setFluxos([]);

        const atLeast = wait(500);

        const q = new URLSearchParams("");
        rows.forEach((row) => {
          if (ehAmortizacaoOuVencimento(row as any)) {
            q.append(
              percentageType === "Base100" ? "absolutas" : "relativas",
              String(row.percentual ?? 0),
            );
          }
        });
        const response = await httpClient.fetch(
          `v1/calculos/porcentagem/${percentageType === "Base100" ? "absoluta-para-relativa" : "relativa-para-absoluta"}?${q.toString()}`,
        );
        if (!response.ok) return;
        const converted = (await response.json()) as number[];
        await atLeast;

        let pIndex = 0;
        setFluxos(
          rows.map(
            (row) =>
              ({
                ...row,
                percentual: ehAmortizacaoOuVencimento(row as any)
                  ? converted[pIndex++]
                  : row.percentual,
              }) as any,
          ),
        );
      }),
    [percentageType],
  );

  const errorValidStart = useMemo(
    () => validYYYYMMDD(ativo.inicio_rentabilidade),
    [isOpen],
  );
  const errorValidEnd = useMemo(
    () => validYYYYMMDD(ativo.data_vencimento),
    [isOpen],
  );

  const reorder = async () => {
    colApiRef.current?.applyColumnState({
      state: [{ colId: "data", sort: null, sortIndex: 0 }],
    });
    colApiRef.current?.applyColumnState({
      state: [{ colId: "data", sort: "asc", sortIndex: 0 }],
    });
  };

  const insertRows = useCallback(
    (rowCount: number) => {
      const rows: { uuid: number }[] = [];
      for (let i = 0; i < rowCount; i++) {
        rows.push({ uuid: Math.random() });
      }
      methodsRef.current?.insertRows(rows);
    },
    [fluxos],
  );

  const colDefs = useMemo(
    () => [
      {
        field: "data",
        ...dateColDef,
        ...dateFilter,
        sortable: false,
        comparator: (vA: string, vB: string) =>
          Number(new Date(ptDateToYYYYMMDD(vA))) -
          Number(new Date(ptDateToYYYYMMDD(vB))),
      },
      {
        field: "tipo_evento",
        headerName: "Tipo Evento",
        sortable: false,
        ...listColDef(tipoEventos),
        ...listFilter(tipoEventos),
      },
      {
        field: "percentual",
        headerName:
          percentageType === "Base100" ? "(%) Base 100" : "(%) Saldo devedor",
        sortable: false,
        ...percentageColDef,
      },
    ],
    [percentageType],
  );

  const grid = useMemo(() => {
    return (
      <GenerateEventsGrid
        methodsRef={methodsRef}
        apiRef={apiRef}
        colApiRef={colApiRef}
        colDefs={colDefs}
        eventos={fluxos}
        tipoEventos={tipoEventos}
        onPercentageChange={setAccPercentage}
        onLastEventChange={setCorrectLastEvent}
        onDueCountChange={setDueCount}
        onError={setCellErrors}
        onDuePays100={setDuePays100}
      />
    );
  }, [fluxos, tipoEventos]);

  const confirmWithProportionalsModal = useMemo(() => {
    return (
      <GenerateEventsModalConfirmContents
        ativo={ativo}
        tipoPorcentagem={percentageType}
        fluxos={(methodsRef.current?.getRowData() as any[]) ?? []}
        onRelativesReady={setRelativesReady}
      />
    );
  }, [ativo, confirmIsOpen]);

  return (
    <AlertDialog
      isOpen={isOpen}
      onClose={onClose}
      leastDestructiveRef={cancelRef}
      scrollBehavior="inside"
      size="3xl"
    >
      <AlertDialogOverlay>
        <AlertDialogContent
          overflow="hidden"
          m="16px"
          minH="calc(100vh - 32px)"
        >
          <AlertDialogHeader bgColor="azul_1.600" color="white">
            <Text
              as="span"
              color={ativo.fluxos.length ? "laranja.main" : "verde.main"}
            >
              {ativo.fluxos.length ? "Recriar" : "Gerar"}
            </Text>{" "}
            novos eventos para{" "}
            <Text as="span" color={strCSSColor(ativo.codigo)}>
              {ativo.codigo}
            </Text>
          </AlertDialogHeader>
          <AlertDialogBody>
            <VStack alignItems="stretch" gap="4px" pt="12px">
              <Box>
                <Card variant="outline">
                  <CardBody p="12px">
                    <HStack w="100%" align="flex-start">
                      <Text flexGrow={1} fontSize="sm">
                        Início rentabilidade:{" "}
                        {errorValidStart ? (
                          <Text color="rosa.main" as="span">
                            {errorValidStart}
                          </Text>
                        ) : (
                          <Text color="verde.main" as="span">
                            {fmtDate(ativo.inicio_rentabilidade)}
                          </Text>
                        )}
                      </Text>
                      <Text flexGrow={1} fontSize="sm">
                        Vencimento:{" "}
                        {errorValidEnd ? (
                          <Text color="rosa.main" as="span">
                            {errorValidEnd}
                          </Text>
                        ) : (
                          <Text color="verde.main" as="span">
                            {fmtDate(ativo.data_vencimento)}
                          </Text>
                        )}
                      </Text>
                    </HStack>
                  </CardBody>
                </Card>
              </Box>
              <Box>
                <Hint>Repetição</Hint>
                <Card variant="outline">
                  <CardBody p={0}>
                    <HStack
                      p="12px"
                      gap="16px"
                      alignItems="flex-start"
                      pt="12px"
                    >
                      <VStack minH="110px" alignItems="flex-start" w="50%">
                        <Hint>
                          {juros === "bullet"
                            ? "Pagamento de juros único"
                            : pluralOrSingular(
                                `Pagamento de juros a cada ${jurosPeriodicos} m€$`,
                                sm,
                                jurosPeriodicos,
                              )}
                        </Hint>
                        <RadioGroup
                          defaultValue="bullet"
                          onChange={(value) => {
                            setJuros(value);
                            setJurosPeriodicos(value === "bullet" ? 0 : 1);
                          }}
                        >
                          <VStack alignItems="flex-start" gap="2px">
                            <Radio size="sm" value="bullet">
                              Bullet
                            </Radio>
                            <Radio size="sm" value="periodico">
                              Periódico
                            </Radio>
                          </VStack>
                        </RadioGroup>
                        <NumberInput
                          focusBorderColor="verde.main"
                          size="sm"
                          defaultValue={0}
                          min={juros === "bullet" ? 0 : 1}
                          max={juros === "bullet" ? 0 : Infinity}
                          step={1}
                          keepWithinRange={true}
                          clampValueOnBlur={true}
                          w="100%"
                          onChange={getNum(setJurosPeriodicos)}
                          isDisabled={juros === "bullet"}
                          value={jurosPeriodicos}
                        >
                          <NumberInputField />
                          <NumberInputStepper>
                            <NumberIncrementStepper />
                            <NumberDecrementStepper />
                          </NumberInputStepper>
                        </NumberInput>
                      </VStack>
                      <VStack minH="110px" alignItems="flex-start" w="50%">
                        <Hint>
                          {amortizacao === "bullet"
                            ? "Amortização única"
                            : pluralOrSingular(
                                `Amortização a cada ${amortizacaoPeriodica} m€$`,
                                sm,
                                amortizacaoPeriodica,
                              )}
                        </Hint>
                        <RadioGroup
                          defaultValue="bullet"
                          onChange={(value) => {
                            setAmortizacao(value);
                            setAmortizacaoPeriodica(value === "bullet" ? 0 : 1);
                          }}
                        >
                          <VStack alignItems="flex-start" gap="2px">
                            <Radio size="sm" value="bullet">
                              No vencimento
                            </Radio>
                            <Radio size="sm" value="periodico">
                              Periódica
                            </Radio>
                          </VStack>
                        </RadioGroup>
                        <NumberInput
                          focusBorderColor="verde.main"
                          size="sm"
                          defaultValue={0}
                          min={amortizacao === "bullet" ? 0 : 1}
                          max={amortizacao === "bullet" ? 0 : Infinity}
                          step={1}
                          keepWithinRange={true}
                          clampValueOnBlur={true}
                          w="100%"
                          onChange={getNum(setAmortizacaoPeriodica)}
                          isDisabled={amortizacao === "bullet"}
                          value={amortizacaoPeriodica}
                        >
                          <NumberInputField />
                          <NumberInputStepper>
                            <NumberIncrementStepper />
                            <NumberDecrementStepper />
                          </NumberInputStepper>
                        </NumberInput>
                      </VStack>
                    </HStack>
                    <Divider />
                    <HStack p="12px">
                      <LightMode>
                        <Button
                          isDisabled={
                            loading ||
                            Boolean(errorValidStart) ||
                            Boolean(errorValidEnd)
                          }
                          rightIcon={<ArrowForwardIcon />}
                          size="xs"
                          alignSelf="start"
                          colorScheme="azul_2"
                          onClick={() => gerarFluxos(percentageType)}
                        >
                          {fluxos.length > 0 ? "Recriar" : "Gerar"} eventos
                        </Button>
                      </LightMode>
                      {loading && (
                        <Progress
                          borderRadius="full"
                          isIndeterminate
                          colorScheme="verde"
                          size="sm"
                          flexGrow={1}
                        />
                      )}
                    </HStack>
                  </CardBody>
                </Card>
              </Box>
              <Box>
                <Hint>Eventos</Hint>
                <Card variant="outline">
                  <CardBody p={0}>
                    <HStack m="12px" justifyContent="space-between">
                      {errorValidStart || errorValidEnd ? (
                        <Text color="rosa.main" fontSize="xs">
                          Uma ou mais datas informadas são inválidas!
                        </Text>
                      ) : (
                        <HStack w="100%" justifyContent="space-between">
                          {
                            <LightMode>
                              <HStack>
                                <Button
                                  size="xs"
                                  isDisabled={loading}
                                  leftIcon={<AddIcon />}
                                  colorScheme="verde"
                                  onClick={newRowsOnOpen}
                                >
                                  Adicionar
                                </Button>
                                <Button
                                  size="xs"
                                  isDisabled={loading}
                                  leftIcon={<CalendarIcon />}
                                  colorScheme="gray"
                                  onClick={reorder}
                                >
                                  Reordenar
                                </Button>
                              </HStack>
                              <HStack>
                                <Button
                                  size="xs"
                                  isDisabled={loading}
                                  leftIcon={<Text fontWeight="bolder">%</Text>}
                                  colorScheme="azul_1"
                                  onClick={convert}
                                >
                                  Converter para{" "}
                                  {percentageType === "Base100"
                                    ? "saldo devedor"
                                    : "base 100"}
                                </Button>
                                <Button
                                  size="xs"
                                  isDisabled={loading}
                                  leftIcon={<Text fontWeight="bolder">%</Text>}
                                  colorScheme="azul_1"
                                  onClick={redistribute}
                                >
                                  Redistribuir igualmente
                                </Button>
                              </HStack>
                            </LightMode>
                          }
                        </HStack>
                      )}
                    </HStack>
                    <Divider />
                    <Box h="350px">{grid}</Box>
                    <Divider />
                    <HStack
                      p={0}
                      m={0}
                      justifyContent="space-around"
                      divider={<StackDivider />}
                    >
                      <Text ml="8px" fontSize="xs">
                        {percentageType === "Base100" ? (
                          <>
                            Percentual absoluto:{" "}
                            <Text
                              as="span"
                              fontWeight="bold"
                              color={
                                accPercentage.toFixed(6) === "100.000000"
                                  ? "verde.main"
                                  : "rosa.main"
                              }
                            >
                              {Math.floor(+accPercentage.toFixed(6)) -
                                +accPercentage.toFixed(6) ===
                              0
                                ? Math.round(accPercentage)
                                : accPercentage.toFixed(6)}
                              % / 100%
                            </Text>
                          </>
                        ) : (
                          <Text
                            as="span"
                            fontWeight="bold"
                            color={dueDateIs100 ? "verde.main" : "rosa.main"}
                          >
                            Vencimento {dueDateIs100 ? "" : "não"} paga 100% do
                            saldo devedor
                          </Text>
                        )}
                      </Text>
                      <Text
                        fontSize="xs"
                        as="span"
                        fontWeight="bold"
                        color={cellErrors === 0 ? "verde.main" : "rosa.main"}
                      >
                        {(cellErrors || "Nenhuma") +
                          pluralOrSingular(
                            " célula$ com erro",
                            { $: { plural: "s", singular: "" } },
                            cellErrors,
                          )}
                      </Text>
                      <Text
                        fontSize="xs"
                        as="span"
                        fontWeight="bold"
                        color={correctLastEvent ? "verde.main" : "rosa.main"}
                      >
                        Última data {correctLastEvent ? "" : "não"} é um
                        vencimento
                      </Text>
                      <Text mr="8px" fontSize="xs">
                        Vencimentos contabilizados:{" "}
                        <Text
                          as="span"
                          fontWeight="bold"
                          color={dueCount === 1 ? "verde.main" : "rosa.main"}
                        >
                          {dueCount}
                        </Text>
                      </Text>
                    </HStack>
                  </CardBody>
                </Card>
              </Box>
            </VStack>
            <InserirLinhasModal
              isOpen={newRowsIsOpen}
              onClose={newRowsOnClose}
              insertAction={insertRows}
            />
          </AlertDialogBody>
          <AlertDialogFooter gap={2}>
            <Button ref={cancelRef} size="sm" onClick={onClose}>
              Voltar
            </Button>
            <Button
              isDisabled={
                loading ||
                !fluxos.length ||
                (percentageType === "Base100" &&
                  accPercentage.toFixed(6) !== "100.000000") ||
                (percentageType === "RelativoVNA" && !dueDateIs100) ||
                dueCount !== 1 ||
                cellErrors > 0 ||
                !correctLastEvent
              }
              colorScheme="azul_2"
              size="sm"
              onClick={confirmOnOpen}
              rightIcon={<ArrowForwardIcon />}
            >
              Calcular
            </Button>
            <ConfirmModal
              isOpen={confirmIsOpen}
              onClose={() => {
                confirmOnClose();
                setRelativesReady([]);
              }}
              title={`Confirmar criação de eventos?`}
              onConfirmAction={() => {
                if (!eventsGridMethodsRef.current) return;

                const newEvents = relativesReady.map((r) => ({
                  id: r.uuid ?? Math.random(),
                  data_pagamento: r.data,
                  ativo_codigo: ativo.codigo,
                  tipo_evento: r.tipo_evento,
                  percentual: r.percentual_relativoVNA,
                }));
                eventsGridMethodsRef.current.deleteRows(
                  ativo.fluxos.map((a) => a.id as any),
                );
                eventsGridMethodsRef.current.insertRows(newEvents);
                ativo.fluxos = newEvents as any[];

                confirmOnClose();
                onClose();
              }}
              size="2xl"
              confirmEnabled={relativesReady.length > 0}
            >
              {confirmWithProportionalsModal}
            </ConfirmModal>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialogOverlay>
    </AlertDialog>
  );
}
