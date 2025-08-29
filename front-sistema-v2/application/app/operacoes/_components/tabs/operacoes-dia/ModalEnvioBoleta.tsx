import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { useAsync, useHTTP } from "@/lib/hooks";
import {
  EstrategiaAgrupamentoOperacoes,
  OperacaoProcessada,
} from "@/lib/types/api/iv/v1";
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Button,
  Checkbox,
  Divider,
  HStack,
  Heading,
  Icon,
  Input,
  Progress,
  Radio,
  RadioGroup,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  IoCheckboxOutline,
  IoTimeOutline,
  IoWarningOutline,
} from "react-icons/io5";
import TituloOperacao from "../TituloOperacao";
import PartesNegocio from "../PartesNegocio";
import {
  SingularPluralMapping,
  fmtDatetime,
  fmtNumber,
  pluralOrSingular,
} from "@/lib/util/string";
import TabelaQuebras from "../triagem-b3/TabelaQuebras";

export type ModalEnvioBoletaProps = {
  isOpen: boolean;
  onClose: () => void;
};

const alertasEErros = (op: OperacaoProcessada) => {
  const alertas: string[] = [];
  if (!op.registro_ativo) alertas.push("Ativo não registrado");
  if (!op.voice_casado) alertas.push("Voice não encontrado");
  const erros: string[] = [];
  if (!op.registro_contraparte?.ids_b3.length)
    erros.push("Registrar identificador da B3 da contraparte");
  op.alocacoes.forEach((al: any) => {
    if (!al.registro_fundo)
      erros.push(
        `${al.fundo.nome} não possui registro com a conta CETIP informada (${al.fundo.conta_cetip})`,
      );
  });
  return { alertas, erros };
};

export default function ModalEnvioBoleta({
  isOpen,
  onClose,
}: ModalEnvioBoletaProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [stagingOperations, setStagingOperations] = useState<
    OperacaoProcessada[]
  >([]);
  const [selectedOperations, _setSelectedOperations] = useState<number[]>([]);

  const httpClient = useHTTP({ withCredentials: true });
  const [loadingSheet, loadSheet] = useAsync();
  const [enviandoOperacoes, iniciarEnvio] = useAsync();
  const [aviso, setAviso] = useState<React.ReactNode | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const [estrategia, setEstrategia] = useState<EstrategiaAgrupamentoOperacoes>(
    EstrategiaAgrupamentoOperacoes.Todas,
  );

  const selectOperation = useCallback(
    (op_tmp_id: number) => {
      const set = new Set(selectedOperations);
      set.add(op_tmp_id);
      _setSelectedOperations([...set]);
    },
    [selectedOperations],
  );

  const deselectOperation = useCallback(
    (op_tmp_id: number) => {
      const set = new Set(selectedOperations);
      set.delete(op_tmp_id);
      _setSelectedOperations([...set]);
    },
    [selectedOperations],
  );

  const limpar = () => {
    setSelectedFile(null);
    setStagingOperations([]);
    _setSelectedOperations([]);
  };

  useEffect(() => {
    if (selectedFile === null) return;
    loadSheet(async () => {
      if (selectedFile === null) return;
      const body = new FormData();
      body.append("file", selectedFile);
      const response = await httpClient.fetch(
        "v1/operacoes/boleta-resumo?estrategia=" + estrategia,
        {
          hideToast: { success: true },
          method: "POST",
          body,
          multipart: true,
        },
      );
      if (!response.ok) return;
      setStagingOperations(
        [...(await response.json())].map((j) => ({
          ...j,
          _tmp_id: Math.random(),
        })),
      );
      _setSelectedOperations([]);
    });
  }, [selectedFile, estrategia]);

  const enviarBoletas = useCallback(() => {
    if (enviandoOperacoes) return;
    iniciarEnvio(async () => {
      const body = selectedOperations.map((s) => stagingOperations[s]);
      const response = await httpClient.fetch("v1/operacoes/envio-operacoes", {
        method: "POST",
        body: JSON.stringify(body),
      });
      if (!response.ok) return;
      limpar();
      onClose();
    });
  }, [selectedOperations, stagingOperations, enviandoOperacoes]);

  return (
    <ConfirmModal
      title="Carregar boleta de operações"
      isOpen={isOpen}
      overflow="auto"
      onClose={() => {
        limpar();
        onClose();
      }}
      onConfirmAction={enviarBoletas}
      confirmEnabled={selectedOperations.length > 0 && !enviandoOperacoes}
      confirmContent={
        selectedOperations.length
          ? pluralOrSingular(
              `Inserir ${selectedOperations.length} operaç@ no fluxo`,
              { "@": { singular: "ão", plural: "ões" } },
              selectedOperations.length,
            )
          : "Aguardando seleção de operações"
      }
      size="full"
    >
      <HStack alignItems="flex-start">
        <VStack flex={1} alignItems="stretch" gap={0}>
          <Text fontSize="sm" fontWeight="bold" mb="12px">
            Carregar Arquivo
          </Text>
          <HStack>
            {stagingOperations.length > 0 && (
              <Button
                onClick={() => {
                  const semAlertasOuErros: number[] = [];
                  let totalAlertas = 0;
                  let totalErros = 0;
                  for (let i = 0; i < stagingOperations.length; i++) {
                    const op = stagingOperations[i];
                    const { alertas, erros } = alertasEErros(op);
                    if (alertas.length > 0) totalAlertas++;
                    if (erros.length > 0) totalErros++;
                    if (alertas.length + erros.length > 0) continue;
                    semAlertasOuErros.push(i);
                  }
                  const s: SingularPluralMapping = {
                    "@": { singular: "ão", plural: "ões" },
                    "!": { singular: "i", plural: "ram" },
                    $: { singular: "", plural: "s" },
                    "&": { singular: "i", plural: "em" },
                    "%": { singular: "", plural: "m" },
                  };
                  setAviso(
                    <VStack alignItems="stretch">
                      <Text>
                        {semAlertasOuErros.length > 0
                          ? pluralOrSingular(
                              `Somente ${semAlertasOuErros.length} de ${stagingOperations.length} operaç@ fo! selecionada$.`,
                              s,
                              stagingOperations.length,
                            )
                          : `Nenhuma operação entre as ${stagingOperations.length} foi selecionada.`}
                      </Text>
                      {totalAlertas > 0 && (
                        <Text fontSize="sm" color="amarelo.700">
                          <strong>{totalAlertas}</strong>{" "}
                          {pluralOrSingular(
                            "não fo! selecionada$ pois possu& alerta$ que deve% ser revisado$ e selecionado$ manualmente.",
                            s,
                            totalAlertas,
                          )}
                        </Text>
                      )}
                      {totalErros > 0 && (
                        <Text fontSize="sm" color="rosa.main">
                          <strong>{totalErros}</strong>{" "}
                          {pluralOrSingular(
                            "não fo! selecionada$ pois possu& pelo menos um erro e não pode% ser enviada$.",
                            s,
                            totalErros,
                          )}
                        </Text>
                      )}
                    </VStack>,
                  );
                  _setSelectedOperations(semAlertasOuErros);
                }}
                color="verde.main"
                leftIcon={<Icon as={IoCheckboxOutline} />}
                size="sm"
              >
                Selecionar todos
              </Button>
            )}
            <Input
              flex={1}
              size="sm"
              p="4px"
              ref={fileInputRef}
              type="file"
              accept=".xlsx"
              onChange={(ev) =>
                setSelectedFile(ev.target.files?.item(0) ?? null)
              }
            />
            <Button
              onClick={() => {
                if (fileInputRef.current) {
                  (fileInputRef.current as any).value = null;
                }
                limpar();
              }}
              size="sm"
              colorScheme="rosa"
            >
              Limpar
            </Button>
          </HStack>
        </VStack>
        <RadioGroup
          ml="24px"
          defaultValue={EstrategiaAgrupamentoOperacoes.Todas}
          size="sm"
          colorScheme="verde"
          value={estrategia}
          onChange={(valor: EstrategiaAgrupamentoOperacoes) =>
            setEstrategia(valor)
          }
        >
          <VStack alignItems="flex-start" gap={0}>
            <Text fontSize="sm" fontWeight="bold" mb="8px">
              Critério de separação de operações
            </Text>
            <Radio value={EstrategiaAgrupamentoOperacoes.Todas}>
              Agrupar todas as operações iguais, independente de posição.
            </Radio>
            <Radio value={EstrategiaAgrupamentoOperacoes.Bloco}>
              Agrupar blocos de operações separados em operações individuais.
            </Radio>
            <Radio value={EstrategiaAgrupamentoOperacoes.Linha}>
              Considerar cada linha como uma operação.
            </Radio>
          </VStack>
        </RadioGroup>
      </HStack>
      <Progress
        visibility={loadingSheet ? "visible" : "hidden"}
        isIndeterminate
        colorScheme="verde"
      />
      <Divider />
      <Box w="100%" h="100%" overflow="auto">
        <Accordion allowMultiple={true} defaultIndex={[]}>
          {stagingOperations.map((op, i) => {
            const { alertas, erros } = alertasEErros(op);
            const desativado = erros.length > 0;

            return (
              <HStack
                key={i}
                alignItems="stretch"
                gap={0}
                mb="4px"
                borderRadius="4px"
                overflow="hidden"
              >
                <HStack p="8px" bgColor={desativado ? "rosa.100" : undefined}>
                  <Checkbox
                    isDisabled={desativado}
                    isChecked={selectedOperations.includes(i)}
                    onChange={(ev) => {
                      if (ev.target.checked) {
                        selectOperation(i);
                      } else {
                        deselectOperation(i);
                      }
                    }}
                    colorScheme="verde"
                    bgColor="white"
                    visibility={desativado ? "hidden" : undefined}
                  />
                </HStack>
                <AccordionItem
                  flex={2}
                  border="1px solid"
                  borderColor="cinza.100"
                >
                  <AccordionButton p={0}>
                    <HStack alignItems="flex-start" flex={1}>
                      <HStack gap={0}>
                        <Box
                          w="8px"
                          alignSelf="stretch"
                          bgColor="azul_1.main"
                        />
                        <TituloOperacao
                          ativo={op.registro_ativo}
                          preco_unitario={op.preco_unitario}
                          quantidade={op.quantidade}
                          taxa={op.taxa ?? 0}
                          fallback_codigo_ativo={op.ativo ?? "---"}
                          fallback_indice_nome={op.indice ?? "---"}
                        />
                      </HStack>
                      <VStack alignItems="flex-start">
                        <PartesNegocio
                          contraparte_nome={op.contraparte}
                          nao_registrada={desativado}
                          vanguarda_compra={op.vanguarda_compra}
                        />
                        <Text fontSize="xs">
                          Total negociado:{" "}
                          <Text as="span" color="verde.main">
                            R$ {fmtNumber(op.total_negociado, 2)}
                          </Text>
                        </Text>
                      </VStack>
                    </HStack>
                    <HStack>
                      {erros.length > 0 && (
                        <HStack
                          fontSize="11px"
                          p="2px 4px"
                          borderRadius="4px"
                          bgColor="rosa.100"
                          color="rosa.main"
                        >
                          <Icon boxSize="14px" as={IoWarningOutline} />
                          <Text whiteSpace="nowrap">
                            {pluralOrSingular(
                              `${erros.length} erro$`,
                              { $: { plural: "s", singular: "" } },
                              erros.length,
                            )}
                          </Text>
                        </HStack>
                      )}
                      {alertas.length > 0 && (
                        <HStack
                          fontSize="11px"
                          p="2px 4px"
                          borderRadius="4px"
                          bgColor="laranja.100"
                          color="laranja.main"
                        >
                          <Icon boxSize="14px" as={IoWarningOutline} />
                          <Text whiteSpace="nowrap">
                            {pluralOrSingular(
                              `${alertas.length} alerta$`,
                              { $: { plural: "s", singular: "" } },
                              alertas.length,
                            )}
                          </Text>
                        </HStack>
                      )}
                    </HStack>
                    <AccordionIcon color="cinza.500" />
                  </AccordionButton>
                  <AccordionPanel p={0}>
                    <HStack gap={0} w="100%">
                      <Box w="8px" alignSelf="stretch" bgColor="azul_1.main" />
                      <Tabs
                        flex={1}
                        borderTop="1px solid"
                        borderColor="cinza.100"
                      >
                        <TabList bgColor="white">
                          <Tab>ALOCAÇÕES</Tab>
                          <Tab>CASAMENTO VOICE</Tab>
                          <Tab
                            color={
                              alertas.length > 0 ? "laranja.700" : undefined
                            }
                          >
                            ALERTAS{" "}
                            {alertas.length > 0 && (
                              <HStack
                                ml="4px"
                                w="16px"
                                h="16px"
                                borderRadius="full"
                                overflow="hidden"
                                bgColor="laranja.700"
                              >
                                <Text w="100%" fontSize="10px" color="white">
                                  {alertas.length}
                                </Text>
                              </HStack>
                            )}
                          </Tab>
                          <Tab
                            color={erros.length > 0 ? "rosa.main" : undefined}
                          >
                            ERROS{" "}
                            {erros.length > 0 && (
                              <HStack
                                ml="4px"
                                w="16px"
                                h="16px"
                                borderRadius="full"
                                overflow="hidden"
                                bgColor="rosa.main"
                              >
                                <Text w="100%" fontSize="10px" color="white">
                                  {erros.length}
                                </Text>
                              </HStack>
                            )}
                          </Tab>
                        </TabList>
                        <TabPanels bgColor="cinza.50">
                          <TabPanel p={0}>
                            <TabelaQuebras
                              alocacoes={op.alocacoes}
                              verificarFundos={true}
                            />
                          </TabPanel>
                          <TabPanel p={0}>
                            {!op.voices_candidatos.length ? (
                              <Text fontSize="xs" color="cinza.500" p="12px">
                                Nenhum voice{" "}
                                {op.vanguarda_compra ? "comprando" : "vendendo"}
                                <Text as="span" fontWeight="bold">
                                  {" "}
                                  {fmtNumber(op.quantidade, 0)}{" "}
                                </Text>
                                unidades de
                                <Text as="span" fontWeight={900}>
                                  {" "}
                                  {op.ativo}{" "}
                                </Text>
                                da
                                <Text as="span" fontWeight="bold">
                                  {" "}
                                  {op.contraparte}{" "}
                                </Text>
                                a
                                <Text as="span" fontWeight="bold">
                                  {" "}
                                  R${fmtNumber(op.preco_unitario, 6)}{" "}
                                </Text>
                                ({op.indice ?? "---"} {fmtNumber(op.taxa, 3)}%)
                                foi encontrado
                              </Text>
                            ) : (
                              <VStack w="100%" h="100%" alignItems="stretch">
                                {op.voices_candidatos.map(
                                  (voice: any, i: number) => (
                                    <HStack
                                      key={i}
                                      bgColor={
                                        op.voice_casado?.id_trader ===
                                        voice.id_trader
                                          ? "verde.100"
                                          : undefined
                                      }
                                      p="8px"
                                      borderBottom="1px solid"
                                      borderColor="cinza.main"
                                    >
                                      <HStack p="8px">
                                        <Radio
                                          isChecked={
                                            op.voice_casado?.id_trader ===
                                            voice.id_trader
                                          }
                                          bgColor="white"
                                          colorScheme="verde"
                                        />
                                      </HStack>
                                      <HStack gap="4px" p="0px 8px 0px 4px">
                                        <Icon
                                          color="cinza.500"
                                          as={IoTimeOutline}
                                        />
                                        <Text color="cinza.600" fontSize="sm">
                                          {fmtDatetime(voice.criado_em)
                                            .split(" ")
                                            .at(-1)}
                                        </Text>
                                      </HStack>
                                      <VStack
                                        alignItems="flex-start"
                                        fontSize="xs"
                                        gap={0}
                                      >
                                        <Text>
                                          ID Trader: {voice.id_trader}
                                        </Text>
                                        <Text>
                                          ID Contraparte:{" "}
                                          {voice.nome_contraparte}
                                        </Text>
                                      </VStack>
                                    </HStack>
                                  ),
                                )}
                              </VStack>
                            )}
                          </TabPanel>
                          <TabPanel p={0}>
                            {alertas.length > 0 ? (
                              <VStack p="12px" alignItems="flex-start">
                                {alertas.map((alerta, i) => (
                                  <HStack
                                    key={i}
                                    fontSize="xs"
                                    color="laranja.700"
                                    bgColor="laranja.50"
                                    p="4px"
                                    borderRadius="4px"
                                  >
                                    <Icon as={IoWarningOutline} />
                                    <Text>{alerta}</Text>
                                  </HStack>
                                ))}
                              </VStack>
                            ) : (
                              <Text fontSize="xs" color="cinza.500" p="12px">
                                Nenhum alerta
                              </Text>
                            )}
                          </TabPanel>
                          <TabPanel p={0}>
                            {erros.length > 0 ? (
                              <VStack p="12px" alignItems="flex-start">
                                {erros.map((erro, i) => (
                                  <HStack
                                    key={i}
                                    fontSize="xs"
                                    color="rosa.main"
                                    bgColor="rosa.50"
                                    p="4px"
                                    borderRadius="4px"
                                  >
                                    <Icon as={IoWarningOutline} />
                                    <Text>{erro}</Text>
                                  </HStack>
                                ))}
                              </VStack>
                            ) : (
                              <Text fontSize="xs" color="cinza.500" p="12px">
                                Nenhum erro
                              </Text>
                            )}
                          </TabPanel>
                        </TabPanels>
                      </Tabs>
                    </HStack>
                  </AccordionPanel>
                </AccordionItem>
              </HStack>
            );
          })}
        </Accordion>
      </Box>
      <ConfirmModal
        title="Aviso"
        isOpen={!!aviso}
        onClose={() => setAviso(null)}
        size="3xl"
        hideCancelButton={true}
        confirmContent="OK"
      >
        {aviso}
      </ConfirmModal>
    </ConfirmModal>
  );
}
