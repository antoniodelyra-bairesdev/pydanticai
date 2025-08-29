"use client";

import Hint from "@/app/_components/texto/Hint";
import { useAsync, useHTTP } from "@/lib/hooks";
import { wait } from "@/lib/util/misc";
import { AddIcon } from "@chakra-ui/icons";
import {
  Box,
  Button,
  Divider,
  HStack,
  Heading,
  Icon,
  Input,
  Stat,
  StatLabel,
  StatNumber,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
  VStack,
  keyframes,
  useDisclosure,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import {
  IoCalendarClearOutline,
  IoCalendarNumberOutline,
  IoCalendarOutline,
  IoCashOutline,
  IoCheckboxOutline,
  IoCloudDownloadOutline,
  IoLocationOutline,
  IoReload,
  IoSquareOutline,
  IoTrendingDownOutline,
} from "react-icons/io5";
import ModalCarregarFluxo from "./ModalCarregarFluxo";
import { Ativo, Evento } from "@/lib/types/api/iv/v1";
import { dateToStr, fmtDate, fmtNumber } from "@/lib/util/string";

const keys = keyframes`
    0% { transform: rotate(0deg); }
    50% { transform: rotate(180deg); }
    100% { transform: rotate(360deg); }
`;

const rodando = `${keys} 1s linear infinite`;

type FluxoUI = {
  id: number;
  nome: string;
};

export default function Calculadora() {
  const http = useHTTP({ withCredentials: true });

  const [fluxos, setFluxos] = useState<FluxoUI[]>(
    ["AEGPA0", "CBAN22", "ENAT21"].map((nome) => ({ id: Math.random(), nome })),
  );

  const [calculando, iniciarCalculo] = useAsync();

  const [marcar, setMarcar] = useState(false);
  const [fluxoSelecionado, setFluxoSelecionado] = useState<FluxoUI | null>(
    null,
  );
  const [fluxosMarcados, setFluxosMarcados] = useState<number[]>([]);

  const [dados, setDados] = useState<Ativo | null>(null);

  const { isOpen, onOpen, onClose } = useDisclosure();

  const calcular = () => {
    if (calculando) return;
    iniciarCalculo(async () => {
      await wait(1000);
    });
  };

  const busca = async () => {
    const response = await http.fetch(
      "v1/ativos/" + fluxoSelecionado?.nome ?? "",
      { hideToast: { success: true } },
    );
    setDados(!response.ok ? null : ((await response.json()) as Ativo));
  };

  useEffect(() => {
    if (!fluxoSelecionado) return;
    busca();
  }, [fluxoSelecionado]);

  return (
    <>
      <HStack flex={1} alignItems="stretch" p="12px 24px">
        <VStack
          flex={1}
          border="1px solid"
          borderColor="cinza.main"
          borderRadius="8px"
          alignItems="stretch"
        >
          <VStack alignItems="stretch">
            <Button
              onClick={onOpen}
              borderBottomRadius={0}
              size="sm"
              colorScheme="azul_1"
              leftIcon={<AddIcon />}
            >
              Novo cálculo
            </Button>
            <HStack p="0px 8px">
              <Button
                colorScheme={marcar ? "azul_1" : "verde"}
                onClick={() => {
                  if (marcar) {
                    setFluxosMarcados([]);
                  }
                  setMarcar(!marcar);
                }}
                size="xs"
              >
                {marcar ? "Cancelar" : "Editar"}
              </Button>
              {marcar && (
                <Button
                  onClick={() => {
                    if (fluxosMarcados.includes(fluxoSelecionado?.id ?? -1)) {
                      setFluxoSelecionado(null);
                    }
                    setFluxos(
                      fluxos.filter((f) => !fluxosMarcados.includes(f.id)),
                    );
                    setFluxosMarcados([]);
                  }}
                  colorScheme="rosa"
                  isDisabled={!fluxosMarcados.length}
                  flex={1}
                  size="xs"
                >
                  Apagar selecionados
                </Button>
              )}
            </HStack>
          </VStack>
          <Divider />
          <VStack alignItems="stretch" gap="1px" p="8px" pt={0}>
            {fluxos.map((fluxo) => (
              <Button
                key={fluxo.id}
                onClick={() => {
                  if (marcar) {
                    const s = new Set(fluxosMarcados);
                    if (s.has(fluxo.id)) {
                      s.delete(fluxo.id);
                    } else {
                      s.add(fluxo.id);
                    }
                    setFluxosMarcados([...s]);
                  } else {
                    setFluxoSelecionado(
                      fluxo.id === fluxoSelecionado?.id ? null : fluxo,
                    );
                  }
                }}
                colorScheme={
                  fluxo.id === fluxoSelecionado?.id ? "azul_2" : undefined
                }
                size="xs"
              >
                <HStack justifyContent="space-between" w="100%">
                  <Icon
                    visibility={marcar ? "visible" : "hidden"}
                    as={
                      fluxosMarcados.includes(fluxo.id)
                        ? IoCheckboxOutline
                        : IoSquareOutline
                    }
                  />
                  <Text flex={1}>{fluxo.nome}</Text>
                </HStack>
              </Button>
            ))}
          </VStack>
        </VStack>
        <VStack
          flex={5}
          alignItems="stretch"
          justifyContent="center"
          h="calc(100vh - 80px)"
        >
          {fluxoSelecionado ? (
            <>
              <VStack gap={0} alignItems="stretch">
                <Hint>Barra de ferramentas</Hint>
                <HStack
                  p="8px 16px"
                  justifyContent="space-between"
                  border="1px solid"
                  borderColor="cinza.main"
                  borderRadius="8px"
                >
                  <Input size="sm" value={fluxoSelecionado.nome} />
                  <Button
                    onClick={calcular}
                    isDisabled={calculando}
                    right={0}
                    top={0}
                    size="sm"
                    borderRadius="full"
                    p={0}
                  >
                    <Icon
                      animation={calculando ? rodando : "none"}
                      as={IoReload}
                      color="verde.main"
                    />
                  </Button>
                </HStack>
              </VStack>
              <VStack gap={0} alignItems="stretch">
                <Hint>Resultados do cálculo</Hint>
                <HStack
                  p="8px 16px"
                  border="1px solid"
                  borderColor="cinza.main"
                  borderRadius="8px"
                >
                  <Stat>
                    <StatLabel>VNA</StatLabel>
                    <StatNumber>R$ 0,00</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>PU Par</StatLabel>
                    <StatNumber>R$ 0,00</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Preço</StatLabel>
                    <StatNumber>R$ 0,00</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Duration (Anos)</StatLabel>
                    <StatNumber>0,00</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Taxa</StatLabel>
                    <StatNumber>0,00%</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>% do PAR</StatLabel>
                    <StatNumber>0,00%</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Spread</StatLabel>
                    <StatNumber>0,00%</StatNumber>
                  </Stat>
                </HStack>
              </VStack>
              <VStack flex={1} gap={0} alignItems="stretch" overflow="hidden">
                <Hint>Detalhes</Hint>
                <HStack
                  flex={1}
                  alignItems="stretch"
                  gap={0}
                  overflow="hidden"
                  border="1px solid"
                  borderColor="cinza.main"
                  borderRadius="8px"
                >
                  <VStack flex={1} gap={0} alignItems="stretch">
                    <HStack
                      minH="32px"
                      bgColor="azul_1.50"
                      p="4px 8px"
                      justifyContent="space-between"
                    >
                      <Text fontSize="sm">Regras</Text>
                    </HStack>
                    <VStack
                      p="4px"
                      alignItems="stretch"
                      gap="2px"
                      overflow="auto"
                    >
                      <HStack bgColor="verde.50" p="4px" borderRadius="4px">
                        <Icon color="verde.main" as={IoCloudDownloadOutline} />
                        <Text fontSize="xs">
                          Carregar características do ativo{" "}
                          {fluxoSelecionado.nome}
                        </Text>
                      </HStack>
                      <HStack bgColor="azul_4.50" p="4px" borderRadius="4px">
                        <Icon color="azul_4.main" as={IoCloudDownloadOutline} />
                        <Text fontSize="xs">
                          Carregar fluxo do ativo {fluxoSelecionado.nome}
                        </Text>
                      </HStack>
                    </VStack>
                  </VStack>
                  <Box w="1px" bgColor="cinza.main" />
                  <Tabs
                    flex={4}
                    size="sm"
                    fontSize="sm"
                    colorScheme="verde"
                    overflow="auto"
                  >
                    <TabList position="sticky" top={0} left={0} bgColor="white">
                      <Tab>Características iniciais</Tab>
                      <Tab>Fluxo de eventos</Tab>
                      <Tab>Memória de cálculo</Tab>
                      <Tab>Gráficos</Tab>
                    </TabList>
                    <TabPanels overflow="auto">
                      <TabPanel>
                        <VStack alignItems="stretch" mb="4px">
                          <Text>
                            <strong>Ativo:</strong> {dados?.codigo}
                          </Text>
                          <Text>
                            <strong>Tipo:</strong> {dados?.tipo.nome}
                          </Text>
                          <Text>
                            <strong>Taxa:</strong> {dados?.indice.nome}{" "}
                            {fmtNumber((dados?.taxa ?? 0) * 100)}% (a.a.)
                          </Text>
                          <Text>
                            <strong>Preço Unitário:</strong> R${" "}
                            {dados ? fmtNumber(dados.valor_emissao) : "---"}
                          </Text>
                          <Text>
                            <strong>Início da rentabilidade:</strong>{" "}
                            {dados
                              ? fmtDate(dados.inicio_rentabilidade)
                              : "---"}
                          </Text>
                          <Text>
                            <strong>Data de vencimento:</strong>{" "}
                            {dados ? fmtDate(dados.data_vencimento) : "---"}
                          </Text>
                        </VStack>
                      </TabPanel>
                      <TabPanel overflow="auto">
                        <VStack alignItems="stretch" fontSize="xs" gap="2px">
                          {[
                            ...(dados?.fluxos ?? []),
                            {
                              id: -2,
                              ativo_codigo: fluxoSelecionado.nome,
                              data_pagamento: dateToStr(new Date()),
                              tipo: {
                                id: -1,
                                nome: "Hoje",
                                tokens: [],
                              },
                            } as Evento,
                          ]
                            .sort((e1, e2) =>
                              e1.data_pagamento.localeCompare(
                                e2.data_pagamento,
                              ),
                            )
                            .map((dado) =>
                              dado.tipo.nome === "Hoje" ? (
                                <HStack
                                  bgColor="verde.50"
                                  color="verde.main"
                                  p="4px"
                                  borderRadius="4px"
                                  key={dado.id}
                                >
                                  <Icon as={IoLocationOutline} />
                                  <Text>{fmtDate(dado.data_pagamento)}</Text>
                                  <Text>Hoje</Text>
                                </HStack>
                              ) : (
                                <HStack
                                  color={
                                    {
                                      Juros: "azul_3.main",
                                      Amortização: "azul_1.main",
                                      Vencimento: "laranja.main",
                                    }[dado.tipo.nome] ?? "cinza.500"
                                  }
                                  p="4px"
                                  borderRadius="4px"
                                  key={dado.id}
                                >
                                  <Icon as={IoCashOutline} />
                                  <Text>{fmtDate(dado.data_pagamento)}</Text>
                                  <Text>{dado.tipo.nome}</Text>
                                </HStack>
                              ),
                            )}
                        </VStack>
                      </TabPanel>
                      <TabPanel>
                        <Text>---</Text>
                      </TabPanel>
                      <TabPanel>
                        <Text>---</Text>
                      </TabPanel>
                    </TabPanels>
                  </Tabs>
                </HStack>
              </VStack>
            </>
          ) : (
            <Heading size="md" color="cinza.main" textAlign="center">
              Nenhum fluxo selecionado
            </Heading>
          )}
        </VStack>
      </HStack>
      <ModalCarregarFluxo isOpen={isOpen} onClose={onClose} />
    </>
  );
}
