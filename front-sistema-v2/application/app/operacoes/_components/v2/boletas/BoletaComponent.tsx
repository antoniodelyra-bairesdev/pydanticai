import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "ag-grid-enterprise";
import "@/app/_components/grid/Grid.css";

import { AgGridReact } from "ag-grid-react";
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Button,
  HStack,
  Icon,
  Input,
  keyframes,
  Select,
  Text,
  Tooltip,
} from "@chakra-ui/react";
import {
  SugestaoBoleta,
  TipoOperacaoEnum,
  TipoOperacaoMap,
  MercadoEnum,
  TipoTituloPrivadoEnum,
  SugestaoAlocacao,
  MercadoMap,
  TipoTituloPrivadoMap,
  ResultadoBuscaBoleta_Alocacao,
  ResultadoBuscaBoleta,
} from "@/lib/types/api/iv/operacoes/processamento";
import {
  ColDef,
  GridApi,
  ICellRendererParams,
  IRowNode,
} from "ag-grid-enterprise";
import {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  IoCashOutline,
  IoCubeOutline,
  IoPeopleCircleOutline,
  IoShapesOutline,
  IoSwapHorizontal,
  IoSwapVertical,
} from "react-icons/io5";
import { getColorHex } from "@/app/theme";
import Image from "next/image";

import IconeB3 from "@/public/b3.png";
import { useAsync, useHTTP } from "@/lib/hooks";
import {
  AlocacoesContext,
  BoletaClient,
} from "@/lib/providers/AlocacoesProvider";
import { dateToStr, fmtDate, fmtCNPJ, fmtCETIP } from "@/lib/util/string";
import { companies } from "../../tabs/triagem-b3/fluxo/dados/companies";
import { ehFluxoII } from "@/lib/util/operacoes";
import CarregamentoBoleta from "../Carregamento";

const frames = () => keyframes`
    0% { opacity: 60%; }
    50% { opacity: 100%; }
    100% { opacity: 60%; }
`;
const animation = () => `${frames()} 1s ease-in-out infinite`;

export type PassoBoleta =
  | "IMPORTACAO"
  | "SIMULACAO"
  | "TRIAGEM"
  | "ACOMPANHAMENTO";

export type BoletaComponentProps = {
  boleta: BoletaClient;
  selecionavel?: boolean;
  onAlocacaoSelecionada?: (
    selecionada: boolean,
    alocacao: ResultadoBuscaBoleta_Alocacao,
  ) => void;
  onBoletaChange?: (boleta: BoletaClient) => void;
  passo?: PassoBoleta;
};

const defaultColDef: ColDef = {
  resizable: true,
  sortable: true,
  filter: true,
};

export type StatusAlocacao =
  | "CONCLUIDO"
  | "PENDENTE_EXTERNO_CADASTRADO"
  | "PENDENTE_EXTERNO_NAO_CADASTRADO"
  | "PENDENTE_VANGUARDA"
  | "CANCELADO_OU_ERRO";
export type DetalhesStatusAlocacao = { status: StatusAlocacao; texto: string };
type CoresStatus = {
  txt: string;
  bg: string;
  anim?: boolean;
};

export const coresStatus = (status: StatusAlocacao) => {
  const mapaStatus: Record<StatusAlocacao, CoresStatus> = {
    CANCELADO_OU_ERRO: { bg: "rosa.100", txt: "rosa.main" },
    CONCLUIDO: { bg: "verde.50", txt: "verde.500" },
    PENDENTE_EXTERNO_CADASTRADO: { bg: "cinza.100", txt: "cinza.500" },
    PENDENTE_EXTERNO_NAO_CADASTRADO: { bg: "amarelo.100", txt: "laranja.main" },
    PENDENTE_VANGUARDA: { bg: "azul_3.100", txt: "azul_3.main", anim: true },
  };
  return mapaStatus[status];
};

const statusAlocacaoTriagem = (
  alocacao: ResultadoBuscaBoleta_Alocacao,
): DetalhesStatusAlocacao => {
  if (alocacao.cancelamento) {
    return {
      status: "CANCELADO_OU_ERRO",
      texto: "Não aprovado",
    };
  }
  return {
    status: "PENDENTE_VANGUARDA",
    texto: "Aguardando aprovação",
  };
};

const statusAlocacaoAcompanhamentoFluxoAntigo = (
  alocacao: ResultadoBuscaBoleta_Alocacao,
): DetalhesStatusAlocacao => {
  if (alocacao.alocacao_administrador?.cancelamento) {
    return {
      status: "CANCELADO_OU_ERRO",
      texto: "Operação cancelada no administrador",
    };
  }

  if (alocacao.cancelamento) {
    if (!alocacao.alocacao_administrador) {
      return {
        status: "CANCELADO_OU_ERRO",
        texto: "Operação cancelada",
      };
    } else {
      return {
        status: "PENDENTE_VANGUARDA",
        texto: "Sinalizar cancelamento no administrador",
      };
    }
  } else {
    if (!alocacao.alocacao_administrador)
      return {
        status: "PENDENTE_VANGUARDA",
        texto: "Sinalizar alocação no administrador",
      };
    return {
      status: "PENDENTE_EXTERNO_CADASTRADO",
      texto: "Alocado",
    };
  }
};

const statusAlocacaoAcompanhamentoFluxoII = (
  alocacao: ResultadoBuscaBoleta_Alocacao,
): DetalhesStatusAlocacao => {
  const { registro_NoMe: rn, casamento } = alocacao;
  if (alocacao.cancelamento) {
    if (!alocacao.alocacao_administrador) {
      return {
        status: "CANCELADO_OU_ERRO",
        texto: "Operação cancelada",
      };
    } else if (alocacao.alocacao_administrador.cancelamento) {
      return {
        status: "CANCELADO_OU_ERRO",
        texto: "Operação cancelada no administrador",
      };
    }
    return {
      status: "PENDENTE_VANGUARDA",
      texto: "Sinalizar cancelamento no administrador",
    };
  }

  // Registro NoMe emitido
  if (rn) {
    // Ainda não foi alocado no administrador
    if (!alocacao.alocacao_administrador) {
      return {
        status: "PENDENTE_VANGUARDA",
        texto: "Sinalizar alocação no administrador",
      };
    }
    // Uma das custódias rejeitou a operação
    if (
      rn.posicao_custodia === false ||
      rn.posicao_custodia_contraparte === false
    ) {
      return {
        status: "CANCELADO_OU_ERRO",
        texto: `Rejeição custódia${rn.posicao_custodia_contraparte === false ? " da contraparte" : ""}`,
      };
    }
    // Informar status da alocação normalmente
    const ambosAcatados =
      rn.posicao_custodia && rn.posicao_custodia_contraparte;
    return {
      status: ambosAcatados ? "CONCLUIDO" : "PENDENTE_EXTERNO_CADASTRADO",
      texto: rn.posicao_custodia
        ? rn.posicao_custodia_contraparte
          ? "Encaminhado para liquidação"
          : "Aguardando custódia contraparte"
        : "Aguardando custódia",
    };
  }
  if (casamento) {
    // Já sabemos quais alocações internas enviar para a [B]³
    if (casamento.voice.horario_recebimento_post_trade) {
      // Já temos os dados disponíveis em Post Trade para enviar as alocações
      const envios = casamento.voice.envios_post_trade.sort((a, b) =>
        a.enviado_em.localeCompare(b.enviado_em),
      );
      if (envios.length === 0) {
        return {
          status: "PENDENTE_VANGUARDA",
          texto: "Aguardando envio Post Trade",
        };
      } else if (envios.some((e) => e.sucesso_em)) {
        return {
          status: "PENDENTE_EXTERNO_CADASTRADO",
          texto: "Aguardando alocação contraparte",
        };
      } else if (envios.some((e) => e.erro)) {
        return {
          status: "CANCELADO_OU_ERRO",
          texto: "Falha ao alocar operações",
        };
      }
      return {
        status: "PENDENTE_EXTERNO_CADASTRADO",
        texto: "Aguardando confirmação da [B]³",
      };
    }
    const envios = casamento.voice.envios_pre_trade.sort((a, b) =>
      a.enviado_em.localeCompare(b.enviado_em),
    );
    if (envios.some((e) => e.erro)) {
      return {
        status: "CANCELADO_OU_ERRO",
        texto: "Falha ao acatar voice",
      };
    }
    return {
      status: "PENDENTE_EXTERNO_CADASTRADO",
      texto: "Aguardando confirmação de acato",
    };
  }

  return {
    status: "PENDENTE_EXTERNO_NAO_CADASTRADO",
    texto: "Aguardando casamento de voice",
  };
};

export const statusAlocacao = (
  boleta: ResultadoBuscaBoleta,
  alocacao: ResultadoBuscaBoleta_Alocacao,
): DetalhesStatusAlocacao => {
  if (alocacao.alocacao_administrador?.liquidacao) {
    return {
      status: "CONCLUIDO",
      texto: "Liquidado",
    };
  }
  if (!alocacao.aprovado_em) {
    return statusAlocacaoTriagem(alocacao);
  }
  if (ehFluxoII(boleta.tipo_ativo_id, boleta.mercado_negociado_id)) {
    return statusAlocacaoAcompanhamentoFluxoII(alocacao);
  }
  return statusAlocacaoAcompanhamentoFluxoAntigo(alocacao);
};

export default function BoletaComponent({
  boleta,
  selecionavel,
  onBoletaChange,
  onAlocacaoSelecionada,
  passo = "IMPORTACAO",
}: BoletaComponentProps) {
  const [acao, setAcao] = useState("criar");
  const [isLoading, load] = useAsync();
  const httpClient = useHTTP({ withCredentials: true });

  const { setAlocacaoDetalhes } = useContext(AlocacoesContext);

  const enviar = () => {
    if (isLoading) return;
    load(async () => {
      const alocacoes: SugestaoAlocacao[] = boleta.boleta.alocacoes.map(
        (a) => ({
          id: -1,
          data_liquidacao: a.data_liquidacao,
          horario: dateToStr(new Date()) + "T00:00:00",
          id_ativo: {
            tipo_ativo: TipoTituloPrivadoMap[boleta.boleta.tipo_ativo_id],
            tipo_codigo: "TICKER",
            codigo: a.codigo_ativo,
          },
          id_corretora: {
            tipo: "APELIDO_VANGUARDA",
            valor: boleta.boleta.corretora.nome,
          },
          id_fundo: {
            tipo: "CETIP",
            valor: a.fundo.conta_cetip,
          },
          lado_operacao: a.vanguarda_compra ? "C" : "V",
          preco: Number(a.preco_unitario),
          quantidade: Number(a.quantidade),
        }),
      );
      const body: SugestaoBoleta = {
        id: -1,
        client_id: boleta.client_id,
        alocacoes,
        corretora: boleta.boleta.corretora.nome,
        horario: dateToStr(new Date()) + "T00:00:00",
        mercado: MercadoMap[boleta.boleta.mercado_negociado_id],
        tipo: TipoOperacaoMap[boleta.boleta.natureza_operacao_id],
        tipo_ativo: TipoTituloPrivadoMap[boleta.boleta.tipo_ativo_id],
        data_liquidacao: boleta.boleta.data_liquidacao,
      };
      const response = await httpClient.fetch("v1/operacoes/alocacoes/boleta", {
        method: "POST",
        body: JSON.stringify(body),
      });
      if (!response.ok) return;
    });
  };

  useEffect(() => {
    if (acao === "criar") {
      boleta.boleta.id = -1;
    } else {
      boleta.boleta.id = 0;
    }
    onBoletaChange?.({ ...boleta });
  }, [acao]);

  const temVendas = useMemo(
    () => Boolean(boleta.boleta.alocacoes.find((a) => !a.vanguarda_compra)),
    [boleta],
  );

  const possiveisAlocacoes = useCallback(
    (passo: PassoBoleta): ResultadoBuscaBoleta_Alocacao[] =>
      ({
        IMPORTACAO: () => boleta.boleta.alocacoes,
        SIMULACAO: () => boleta.boleta.alocacoes,
        TRIAGEM: () => boleta.boleta.alocacoes.filter((a) => !a.aprovado_em),
        ACOMPANHAMENTO: () =>
          boleta.boleta.alocacoes.filter((a) => a.aprovado_em),
      })[passo](),
    [boleta],
  );
  const alocacoes = possiveisAlocacoes(passo);
  const tamAlocacoesEQuebras = alocacoes.flatMap((a) => [
    a,
    ...a.quebras,
  ]).length;

  const passoEdicao = (["IMPORTACAO", "SIMULACAO"] as PassoBoleta[]).includes(
    passo,
  );
  const passoStatus = (["TRIAGEM", "ACOMPANHAMENTO"] as PassoBoleta[]).includes(
    passo,
  );

  const idParaAlocacao = useMemo(
    () =>
      boleta.boleta.alocacoes.reduce(
        (map, a) => {
          map[a.id] = a;
          return map;
        },
        {} as Record<number, ResultadoBuscaBoleta_Alocacao>,
      ),
    [boleta],
  );

  const colDefs = useMemo(
    () =>
      [
        {
          showRowGroup: false,
          rowGroup: true,
          field: "grouping",
          hide: true,
        },
        {
          lockPinned: true,
          pinned: "left",
          width: 48,
          checkboxSelection: ({ node }) => {
            return !node.group && passoStatus && selecionavel;
          },
          headerCheckboxSelection: passoStatus && selecionavel,
        },
        {
          headerName: "ID Alocação",
          field: "id",
          width: 84,
          hide: true,
          sortable: false,
        },
        {
          headerName: "Fundo",
          field: "fundo.nome",
          width: 256,
          cellRenderer: ({ value, node }: ICellRendererParams) => {
            if (node.group) {
              value = idParaAlocacao[Number(node.key)]?.fundo.nome;
            }
            return (
              <Tooltip label={value} hasArrow>
                <Text
                  w="100%"
                  overflow="hidden"
                  whiteSpace="nowrap"
                  textOverflow="ellipsis"
                >
                  {value}
                </Text>
              </Tooltip>
            );
          },
        },
        {
          headerName: "Side",
          width: 76,
          field: "vanguarda_compra",
          cellRenderer({ value, node }: ICellRendererParams) {
            if (node.group) {
              value = idParaAlocacao[Number(node.key)]?.vanguarda_compra;
            }
            return (
              <Text textAlign="center" fontWeight="bold">
                {/* Não fiz um ternário pq o valor também pode ser undefined */}
                {value == true && (
                  <Text as="span" color="azul_2.main">
                    C
                  </Text>
                )}
                {value == false && (
                  <Text as="span" color="rosa.main">
                    V
                  </Text>
                )}
              </Text>
            );
          },
        },
        {
          headerName: "Ativo",
          width: 128,
          field: "codigo_ativo",
          cellRenderer({ value, node }: ICellRendererParams) {
            if (node.group) {
              value = idParaAlocacao[Number(node.key)]?.codigo_ativo;
            }
            return (
              <Text fontWeight="bold" textAlign="center">
                {value}
              </Text>
            );
          },
        },
        {
          headerName: "Preço",
          width: 128,
          field: "preco_unitario",
          cellRenderer({ value, node }: ICellRendererParams) {
            if (node.group) {
              value = idParaAlocacao[Number(node.key)]?.preco_unitario;
            }
            return (
              <Text>
                <Text as="span" color="verde.main" mr="4px">
                  R$
                </Text>
                {Number(value).toLocaleString("pt-BR", {
                  maximumFractionDigits: 8,
                  minimumFractionDigits: 8,
                })}
              </Text>
            );
          },
        },
        {
          headerName: "Quantidade",
          width: 128,
          field: "quantidade",
          type: "number",
          cellRenderer({ value, node }: ICellRendererParams) {
            if (node.group) {
              value = idParaAlocacao[Number(node.key)]?.quantidade;
            }
            return (
              <HStack justifyContent="space-between" m="0 4px">
                <Icon color="verde.main" as={IoCubeOutline} />
                <Text>
                  {Number(value).toLocaleString("pt-BR", {
                    maximumFractionDigits: 8,
                    minimumFractionDigits: 0,
                  })}
                </Text>
              </HStack>
            );
          },
        },
        {
          headerName: "Liquidação",
          field: "data_liquidacao",
          width: 128,
          cellRenderer: ({ value, node }: ICellRendererParams) => {
            if (node.group) {
              value = idParaAlocacao[Number(node.key)]?.data_liquidacao;
            }
            return <Text textAlign="center">{value && fmtDate(value)}</Text>;
          },
        },
        {
          headerName: "CETIP",
          field: "fundo.conta_cetip",
          width: 90,
          cellRenderer: ({ value, node }: ICellRendererParams) => {
            if (node.group) {
              value = idParaAlocacao[Number(node.key)]?.fundo.conta_cetip;
            }
            return (
              <Text textAlign="center">
                {(value && fmtCETIP(value)) || (node.expanded ? "" : "...")}
              </Text>
            );
          },
        },
        {
          headerName: "CNPJ",
          field: "fundo.cnpj",
          width: 128,
          cellRenderer: ({ value, node }: ICellRendererParams) => {
            if (node.group) {
              value = idParaAlocacao[Number(node.key)]?.fundo.cnpj;
            }
            return value && fmtCNPJ(value);
          },
        },
        {
          headerName: "Administrador",
          field: "fundo.administrador.nome",
          width: 144,
          cellRenderer: ({ value, node }: ICellRendererParams) => {
            if (node.group) {
              value =
                idParaAlocacao[Number(node.key)]?.fundo.administrador?.nome;
            }
            const txt = value ?? "";
            const custKey = txt
              .split(" ")
              .find((k: string) => companies[k.toLowerCase()]?.icon)
              ?.toLowerCase();
            const icon = companies[custKey ?? ""]?.icon;
            return (
              <HStack w="100%" justifyContent="center">
                {icon &&
                  ("src" in icon ? (
                    <Image width={12} height={12} src={icon} alt="icone" />
                  ) : (
                    <Icon as={icon} />
                  ))}
                <Text>{txt}</Text>
              </HStack>
            );
          },
        },
        ...(passoStatus
          ? [
              {
                headerName: "Status",
                lockPinned: true,
                pinned: "right",
                width: 240,
                cellRenderer: ({
                  data,
                  node,
                }: ICellRendererParams<ResultadoBuscaBoleta_Alocacao>) => {
                  if (node.group) {
                    data = idParaAlocacao[Number(node.key)];
                  }
                  if (!data) return;
                  const { status, texto } = !node.group
                    ? statusAlocacao(boleta.boleta, data)
                    : ({
                        status: "CANCELADO_OU_ERRO",
                        texto: "Quebra de alocações",
                      } as DetalhesStatusAlocacao);
                  const { bg, txt } = coresStatus(status);
                  return (
                    <Text
                      pl="4px"
                      fontSize="xs"
                      bgColor={bg}
                      color={txt}
                      animation={
                        status === "PENDENTE_VANGUARDA"
                          ? animation()
                          : undefined
                      }
                    >
                      {texto}
                    </Text>
                  );
                },
              },
              {
                headerName: "",
                lockPinned: true,
                pinned: "right",
                width: 70,
                cellRenderer: ({
                  data,
                  node,
                }: ICellRendererParams<ResultadoBuscaBoleta_Alocacao>) => {
                  if (node.group) {
                    data = idParaAlocacao[Number(node.key)];
                  }
                  if (!data) return;
                  return (
                    <HStack w="100%" alignItems="stretch">
                      <Button
                        w="100%"
                        colorScheme="azul_1"
                        size="xs"
                        onClick={() =>
                          setAlocacaoDetalhes(
                            data
                              ? {
                                  ...data,
                                  tipo_ativo_id: boleta.boleta.tipo_ativo_id,
                                  mercado_negociado_id:
                                    boleta.boleta.mercado_negociado_id,
                                  natureza_operacao_id:
                                    boleta.boleta.natureza_operacao_id,
                                }
                              : null,
                          )
                        }
                      >
                        Detalhes
                      </Button>
                    </HStack>
                  );
                },
              } as ColDef,
            ]
          : []),
      ] as ColDef[],
    [boleta, selecionavel],
  );

  const gridRef = useRef<GridApi | null>(null);

  useEffect(() => {
    if (!gridRef.current) return;
    gridRef.current.refreshCells();
  }, [alocacoes]);

  useEffect(() => {
    if (selecionavel || !gridRef.current) return;
    const nodes: IRowNode[] = [];
    gridRef.current.forEachNode((node) => nodes.push(node));
    gridRef.current.setNodesSelected({ nodes, newValue: false });
  }, [selecionavel]);

  const dadosGrid = alocacoes
    .flatMap((a) => (a.quebras.length ? a.quebras : [a]))
    .map((a) => ({ grouping: a.alocacao_anterior_id, ...a }));

  return (
    <Accordion allowToggle>
      <AccordionItem
        bgColor="cinza.200"
        border="1px solid"
        borderColor="cinza.main"
      >
        <AccordionButton
          position="sticky"
          top={0}
          zIndex={999}
          cursor="pointer"
          as="div"
          _expanded={{ bgColor: "azul_1.50", borderBottomRadius: 0 }}
          _hover={{ bgColor: "white" }}
        >
          <Box
            w="9px"
            h="9px"
            bgColor="white"
            position="absolute"
            top="-1px"
            left="-1px"
          >
            <Box
              bgColor="cinza.400"
              w="100%"
              h="100%"
              clipPath="polygon(0 100%, 100% 0, 100% 100%)"
            />
          </Box>
          <HStack w="100%" justifyContent="space-between">
            <HStack flex={1}>
              <AccordionIcon />
              {passoEdicao && (
                <Select
                  isDisabled={isLoading}
                  minW="160px"
                  maxW="160px"
                  bgColor="white"
                  size="xs"
                  onClick={(ev) => ev.stopPropagation()}
                  value={acao}
                  onChange={(ev) => setAcao(ev.target.value)}
                >
                  <option value="criar">➕ Criar boleta</option>
                  <option value="alterar">✏️ Alterar existente</option>
                </Select>
              )}
              {acao === "criar" ? (
                <>
                  <HStack
                    gap={0}
                    pl="4px"
                    w="144px"
                    h="22px"
                    bgColor="white"
                    onClick={(ev) => ev.stopPropagation()}
                  >
                    <Icon
                      as={IoCashOutline}
                      color="verde.main"
                      w="16px"
                      h="16px"
                    />
                    <Input
                      size="xs"
                      type="date"
                      value={boleta.boleta.data_liquidacao ?? ""}
                      isDisabled={!passoEdicao || isLoading}
                      isInvalid={!boleta.boleta.data_liquidacao}
                      onChange={(ev) =>
                        onBoletaChange?.({
                          client_id: boleta.client_id,
                          boleta: {
                            ...boleta.boleta,
                            data_liquidacao: ev.target.value,
                            alocacoes: boleta.boleta.alocacoes.map((a) => ({
                              ...a,
                              data_liquidacao: ev.target.value,
                            })),
                          },
                        })
                      }
                    />
                  </HStack>
                  <HStack
                    h="22px"
                    mt="1px"
                    p="0 4px"
                    bgColor="white"
                    minW="92px"
                  >
                    <Icon color="azul_2.main" as={IoShapesOutline} />
                    <Text fontSize="xs">
                      {TipoTituloPrivadoMap[boleta.boleta.tipo_ativo_id] ??
                        "???"}
                    </Text>
                  </HStack>
                  <HStack
                    minW="70px"
                    maxW="70px"
                    mt="1px"
                    h="22px"
                    bgColor="white"
                    gap="4px"
                    p="0 4px"
                  >
                    <Icon
                      color={
                        boleta.boleta.natureza_operacao_id ===
                        TipoOperacaoEnum.INTERNA
                          ? "roxo.main"
                          : "laranja.main"
                      }
                      as={
                        boleta.boleta.natureza_operacao_id ===
                        TipoOperacaoEnum.INTERNA
                          ? IoSwapHorizontal
                          : IoSwapVertical
                      }
                    />
                    <Text fontSize="xs">
                      {TipoOperacaoMap[boleta.boleta.natureza_operacao_id][0] +
                        TipoOperacaoMap[boleta.boleta.natureza_operacao_id]
                          .slice(1)
                          .toLocaleLowerCase()}
                    </Text>
                  </HStack>
                  <Select
                    minW="156px"
                    maxW="156px"
                    bgColor="white"
                    size="xs"
                    value={boleta.boleta.mercado_negociado_id ?? "0"}
                    isInvalid={!Number(boleta.boleta.mercado_negociado_id)}
                    isDisabled={
                      !passoEdicao ||
                      isLoading ||
                      boleta.boleta.natureza_operacao_id ===
                        TipoOperacaoEnum.INTERNA ||
                      (boleta.boleta.natureza_operacao_id ===
                        TipoOperacaoEnum.EXTERNA &&
                        temVendas)
                    }
                    onChange={(ev) =>
                      onBoletaChange?.({
                        client_id: boleta.client_id,
                        boleta: {
                          ...boleta.boleta,
                          mercado_negociado_id: Number(
                            ev.target.value,
                          ) as MercadoEnum,
                        },
                      })
                    }
                    onClick={(ev) => ev.stopPropagation()}
                    color={
                      {
                        [MercadoEnum.INDEFINIDO]: getColorHex("cinza.500"),
                        [MercadoEnum.PRIMARIO]: getColorHex("verde.main"),
                        [MercadoEnum.SECUNDARIO]: getColorHex("azul_3.main"),
                      }[boleta.boleta.mercado_negociado_id]
                    }
                  >
                    <option
                      value="0"
                      style={{ color: getColorHex("cinza.main") }}
                    >
                      Selecionar mercado...
                    </option>
                    <option
                      value="1"
                      style={{ color: getColorHex("verde.main") }}
                    >
                      Primário
                    </option>
                    <option
                      value="2"
                      style={{ color: getColorHex("azul_3.main") }}
                    >
                      Secundário
                    </option>
                  </Select>
                  <HStack
                    minW="256px"
                    maxW="256px"
                    h="22px"
                    mt="1px"
                    p="0 4px"
                    bgColor="white"
                  >
                    <Icon as={IoPeopleCircleOutline} />
                    <Text fontSize="xs">{boleta.boleta.corretora.nome}</Text>
                  </HStack>
                  {ehFluxoII(
                    boleta.boleta.tipo_ativo_id,
                    boleta.boleta.mercado_negociado_id,
                  ) && (
                    <HStack
                      borderRadius="4px"
                      h="22px"
                      minW="74px"
                      maxW="74px"
                      p="0 4px"
                      bgColor="azul_3.main"
                    >
                      <Image
                        style={{ filter: "brightness(0) invert(1)" }}
                        width={16}
                        height={16}
                        src={IconeB3}
                        alt="[B]³"
                      />
                      <Text fontSize="xs" color="white" fontWeight="bold">
                        Fluxo II
                      </Text>
                    </HStack>
                  )}
                  {passo === "ACOMPANHAMENTO" && (
                    <HStack flex={1} justifyContent="flex-end">
                      <CarregamentoBoleta
                        detalhes={boleta.boleta.alocacoes
                          .flatMap((a) => (a.quebras.length ? a.quebras : [a]))
                          .map((a) => statusAlocacao(boleta.boleta, a))}
                      />
                    </HStack>
                  )}
                </>
              ) : (
                <Select
                  w="160px"
                  bgColor="white"
                  size="xs"
                  onClick={(ev) => ev.stopPropagation()}
                  value={String(boleta.boleta.id)}
                  isInvalid={boleta.boleta.id === 0}
                  onChange={(ev) => {
                    const id = Number(ev.target.value);
                    if (isNaN(id)) return;
                    onBoletaChange?.({
                      client_id: boleta.client_id,
                      boleta: { ...boleta.boleta, id },
                    });
                  }}
                >
                  <option value="0">Selecionar boleta...</option>
                </Select>
              )}
            </HStack>
            {passo === "SIMULACAO" && (
              <Button
                isLoading={isLoading}
                isDisabled={
                  !(
                    (boleta.boleta.id < 0 &&
                      boleta.boleta.mercado_negociado_id !==
                        MercadoEnum.INDEFINIDO) ||
                    boleta.boleta.id > 0
                  )
                }
                size="xs"
                colorScheme="verde"
                onClick={(ev) => {
                  ev.preventDefault();
                  enviar();
                }}
              >
                Enviar para triagem
              </Button>
            )}
          </HStack>
        </AccordionButton>
        <AccordionPanel p={0}>
          <Box
            className="ag-theme-alpine"
            w="100%"
            h={tamAlocacoesEQuebras * 28 + 62}
          >
            <AgGridReact
              suppressRowClickSelection
              defaultColDef={defaultColDef}
              rowData={dadosGrid}
              columnDefs={colDefs}
              rowHeight={28}
              overlayNoRowsTemplate="Nenhum dado para mostrar"
              postSortRows={({ columnApi }) => {
                // Sempre ordenar por ID no final
                const states = columnApi.getColumnState();
                const idCol = states.find((s) => s.colId === "id");
                if (!idCol) return;
                idCol.sort = "asc";
                idCol.sortIndex = Infinity;
                columnApi.applyColumnState({ state: states });
              }}
              rowSelection="multiple"
              getRowId={({ data }) => data.id}
              onGridReady={({ api }) => (gridRef.current = api)}
              getRowStyle={({ node }) => {
                if (node.group) {
                  return {
                    backgroundColor: getColorHex("cinza.300"),
                  };
                } else if (node.parent?.key) {
                  return {
                    backgroundColor: getColorHex("cinza.100"),
                  };
                }
                return {
                  backgroundColor: "white",
                };
              }}
              onRowSelected={({ node }) => {
                let data = node.data;
                if (node.group) {
                  data = idParaAlocacao[Number(node.key)];
                  if (!data) return;
                }
                if (!node.group) {
                  console.log({ selected: node.isSelected() ?? false, data });
                  onAlocacaoSelecionada?.(node.isSelected() ?? false, data);
                }
              }}
              enableRangeSelection
              groupAllowUnbalanced
              autoGroupColumnDef={{
                headerName: "Quebras",
                width: 128,
                valueFormatter: () => "",
                pinned: "left",
                cellRendererParams: {
                  value: "Quebras: ",
                },
              }}
            />
          </Box>
        </AccordionPanel>
      </AccordionItem>
    </Accordion>
  );
}
