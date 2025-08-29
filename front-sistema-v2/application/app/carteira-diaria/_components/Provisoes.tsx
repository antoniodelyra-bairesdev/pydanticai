import { Posicao } from "@/lib/types/leitor-carteiras-fundos/types";
import {
  Box,
  Button,
  HStack,
  Icon,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  StackProps,
  Text,
  Tooltip,
  useDisclosure,
  VStack,
} from "@chakra-ui/react";
import {
  IoCaretDown,
  IoCaretUp,
  IoCheckmark,
  IoInformationCircleOutline,
  IoListCircleOutline,
  IoWarning,
} from "react-icons/io5";
import Seta from "./Seta";
import ContagemBolinhas from "./ContagemBolinhas";
import TooltipComparativo from "./TooltipComparativo";
import { dateToStr, fmtDate, fmtNumber } from "@/lib/util/string";
import GraficoProvisoes from "./GraficoProvisoes";
import Hint from "@/app/_components/texto/Hint";
import { ICellRendererParams } from "ag-grid-community";
import { Tabela } from "@/app/_components/grid/Tabela";
import { getColorHex } from "@/app/theme";

export type ProvisoesProps = {
  posicoes: Posicao[];
  focoPosicao: number;
  setFocoPosicao: (n: number) => void;
} & StackProps;

const valoresAReceber = (p: Posicao) =>
  p.produto_investimento
    ? p.produto_investimento.financeiro.valores_a_receber.reduce(
        (soma, v) => soma + Number(v.valor),
        0,
      )
    : 0;
const valoresAPagar = (p: Posicao) =>
  p.produto_investimento
    ? p.produto_investimento.financeiro.valores_a_pagar.reduce(
        (soma, v) => soma + Number(v.valor),
        0,
      )
    : 0;
const valorPagoDespesas = (p: Posicao) =>
  p.produto_investimento
    ? p.produto_investimento.financeiro.despesas.reduce(
        (soma, v) => soma + Number(v.valor),
        0,
      )
    : 0;

const posNegRenderer = ({ value, formatValue }: ICellRendererParams) => {
  const sinal = Math.sign(forceN(value));
  return (
    <HStack>
      <Icon
        as={
          {
            [-1]: IoCaretDown,
            [0]: IoCheckmark,
            [1]: IoCaretUp,
          }[sinal]
        }
        color={
          {
            [-1]: "rosa.main",
            [0]: "cinza.main",
            [1]: "verde.main",
          }[sinal]
        }
      />
      <Text>{formatValue?.(value) ?? value}</Text>
    </HStack>
  );
};

const forceN = (n: string | number | null | undefined) =>
  n
    ? Number(
        typeof n === "number"
          ? n
          : isNaN(Number(n))
            ? Number(n.replaceAll(".", "").replaceAll(",", "."))
            : Number(n),
      )
    : 0;

const dataMenorQuePosicao = (data: Date | string, dataPos: Date | string) =>
  Number(
    typeof dataPos === "string" ? new Date(dataPos + "T00:00:00") : dataPos,
  ) -
    Number(typeof data === "string" ? new Date(data + "T00:00:00") : data) >
  0;

export default function Provisoes({
  posicoes,
  focoPosicao,
  setFocoPosicao,
  ...stackProps
}: ProvisoesProps) {
  const p = posicoes[focoPosicao];

  const { isOpen, onOpen, onClose } = useDisclosure();

  const pgtos = [
    ...(p?.produto_investimento?.financeiro.valores_a_pagar.map((p) => ({
      ...p,
      valor: `-${p.valor}`,
    })) ?? []),
    ...(p?.produto_investimento?.financeiro.valores_a_receber ?? []),
  ];

  const individual = pgtos.map(
    ({ codigo, nome, valor, data_pagamento }, i) => ({
      codigo,
      nome,
      valor: Number(valor),
      data_pagamento: new Date(data_pagamento + "T00:00:00"),
    }),
  );

  const agregado = Object.entries(
    individual.reduce(
      (mapa, p) => {
        mapa[p.nome] ??= 0;
        mapa[p.nome] += p.valor;
        return mapa;
      },
      {} as Record<string, number>,
    ),
  ).map(([nome, valor]) => ({ nome, valor }));

  return (
    <VStack {...stackProps}>
      <VStack alignItems="stretch" flex={1} gap={0}>
        <VStack
          alignItems="stretch"
          gap={0}
          m="8px 4px 0 4px"
          border="1px solid"
          borderColor="cinza.main"
          borderRadius="8px"
          p="4px 20px 0 20px"
        >
          <HStack flexWrap="nowrap">
            <Icon color="verde.main" as={IoCaretUp} />
            <TooltipComparativo
              id={focoPosicao}
              valores={posicoes.map((op, oi) => ({
                id: oi,
                nome: op.produto_investimento?.nome ?? "---",
                valor: valoresAReceber(op),
              }))}
              formatar={(n) => `R$ ${fmtNumber(n)}`}
            >
              <Text flex={1} textAlign="center" fontWeight={600} pr="24px">
                R$ {posicoes.length ? fmtNumber(valoresAReceber(p)) : "---"}
              </Text>
            </TooltipComparativo>
          </HStack>
          <Text textAlign="center" mb="8px" fontSize="xs">
            Valores a receber
          </Text>
          <HStack flexWrap="nowrap">
            <Icon color="rosa.main" as={IoCaretDown} />
            <TooltipComparativo
              id={focoPosicao}
              valores={posicoes.map((op, oi) => ({
                id: oi,
                nome: op.produto_investimento?.nome ?? "---",
                valor: valoresAPagar(op),
              }))}
              formatar={(n) => `R$ ${fmtNumber(n)}`}
            >
              <Text flex={1} textAlign="center" fontWeight={600} pr="24px">
                R$ {posicoes.length ? fmtNumber(valoresAPagar(p)) : "---"}
              </Text>
            </TooltipComparativo>
          </HStack>
          <Text textAlign="center" mb="8px" fontSize="xs">
            Valores a pagar
          </Text>
        </VStack>
        <VStack
          alignItems="stretch"
          gap={0}
          borderRadius="8px"
          border="1px solid"
          borderColor="cinza.main"
          m="4px 4px 0 4px"
          p="4px 20px 0 20px"
        >
          <HStack flexWrap="nowrap">
            <Icon color="laranja.main" as={IoListCircleOutline} />
            <TooltipComparativo
              id={focoPosicao}
              valores={posicoes.map((op, oi) => ({
                id: oi,
                nome: op.produto_investimento?.nome ?? "---",
                valor: valorPagoDespesas(op),
              }))}
              formatar={(n) => `R$ ${fmtNumber(n)}`}
            >
              <Text flex={1} textAlign="center" fontWeight={600} pr="24px">
                R$ {posicoes.length ? fmtNumber(valorPagoDespesas(p)) : "---"}
              </Text>
            </TooltipComparativo>
          </HStack>
          <Text textAlign="center" mb="8px" fontSize="xs">
            Despesas pagas no mês
          </Text>
        </VStack>
      </VStack>
      <VStack flex={1} alignItems="stretch" p="0 4px">
        <Button
          leftIcon={<Icon as={IoInformationCircleOutline} />}
          size="xs"
          onClick={onOpen}
        >
          Detalhes
        </Button>
      </VStack>
      <Box p="0 0 12px 0">
        <HStack justifyContent="center" w="100%">
          <Text flex={1} textAlign="center" fontSize="xs">
            Provisões
          </Text>
          {posicoes.length > 1 && (
            <>
              <Seta
                orientacao="ESQUERDA"
                posicao={focoPosicao}
                setPosicao={setFocoPosicao}
                tamanho={posicoes.length}
                position="absolute"
                left="4px"
              />
              <Seta
                orientacao="DIREITA"
                posicao={focoPosicao}
                setPosicao={setFocoPosicao}
                tamanho={posicoes.length}
                position="absolute"
                right="4px"
              />
              <ContagemBolinhas
                posicao={focoPosicao}
                tamanho={posicoes.length}
                position="absolute"
                bottom="4px"
              />
            </>
          )}
        </HStack>
      </Box>
      <Modal isOpen={isOpen} onClose={onClose} size="6xl">
        <ModalOverlay />
        <ModalContent m="64px" h="calc(100vh - 128px)">
          <ModalHeader>Detalhes das provisões</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack w="100%" h="100%" alignItems="stretch">
              <HStack flex={1} alignItems="stretch">
                <VStack alignItems="stretch" flex={3}>
                  <Hint>Individual</Hint>
                  <Tabela
                    boxProps={{
                      w: "100%",
                      flex: 1,
                    }}
                    gridProps={{
                      columnDefs: [
                        {
                          headerName: "Código",
                          field: "codigo",
                          width: 96,
                        },
                        {
                          headerName: "Nome",
                          field: "nome",
                          flex: 3,
                        },
                        {
                          headerName: "Valor",
                          field: "valor",
                          flex: 2,
                          filter: "agNumberColumnFilter",
                          valueGetter: ({ data }) =>
                            fmtNumber(Number(data.valor)),
                          valueFormatter: ({ value }) => `R$ ${value}`,
                          filterValueGetter: ({ data }) => Number(data.valor),
                          comparator: (vA, vB) => forceN(vA) - forceN(vB),
                          cellRenderer: posNegRenderer,
                        },
                        {
                          headerName: "Data",
                          field: "data_pagamento",
                          width: 128,
                          sort: "asc",
                          valueFormatter: ({ value }) =>
                            fmtDate(dateToStr(value)),
                          cellStyle: ({ value }) => ({
                            backgroundColor:
                              p && dataMenorQuePosicao(value, p.data)
                                ? getColorHex("rosa.50")
                                : "transparent",
                          }),
                          cellRenderer: ({
                            value,
                            valueFormatted,
                          }: ICellRendererParams) => (
                            <HStack
                              alignItems="center"
                              justifyContent="center"
                              h="100%"
                              position="relative"
                            >
                              <Text>{valueFormatted}</Text>
                              {p && dataMenorQuePosicao(value, p.data) && (
                                <Tooltip
                                  label={`Data do pagamento (${valueFormatted}) menor que data posição (${fmtDate(p.data)}).`}
                                  hasArrow
                                  bgColor="rosa.main"
                                  color="rosa.50"
                                  placement="top"
                                >
                                  <Box
                                    as="span"
                                    position="absolute"
                                    right="-8px"
                                  >
                                    <Icon as={IoWarning} color="rosa.main" />
                                  </Box>
                                </Tooltip>
                              )}
                            </HStack>
                          ),
                        },
                      ],
                      rowData: individual,
                      getRowStyle({ node }) {
                        return {
                          fontSize: "13px",
                          backgroundColor: node.group
                            ? getColorHex("cinza.200")
                            : "none",
                        };
                      },
                      headerHeight: 29,
                      rowHeight: 28,
                    }}
                  />
                </VStack>
                <VStack alignItems="stretch" flex={2}>
                  <Hint>Por categoria</Hint>
                  <Tabela
                    boxProps={{
                      w: "100%",
                      flex: 1,
                    }}
                    gridProps={{
                      columnDefs: [
                        {
                          headerName: "Nome",
                          field: "nome",
                          flex: 3,
                        },
                        {
                          headerName: "Valor",
                          field: "valor",
                          flex: 2,
                          filter: "agNumberColumnFilter",
                          sort: "asc",
                          valueGetter: ({ data }) =>
                            fmtNumber(Number(data.valor)),
                          valueFormatter: ({ value }) => `R$ ${value}`,
                          filterValueGetter: ({ data }) => Number(data.valor),
                          comparator: (vA, vB) => forceN(vA) - forceN(vB),
                          cellRenderer: posNegRenderer,
                        },
                      ],
                      rowData: agregado,
                      getRowStyle({ node }) {
                        return {
                          fontSize: "13px",
                          backgroundColor: node.group
                            ? getColorHex("cinza.200")
                            : "none",
                        };
                      },
                      headerHeight: 29,
                      rowHeight: 28,
                    }}
                  />
                </VStack>
              </HStack>
              <Box flex={1}>
                <GraficoProvisoes
                  posicoes={posicoes}
                  focoPosicao={focoPosicao}
                  detalharFluxoCaixa
                />
              </Box>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  );
}
