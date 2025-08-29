import Hint from "@/app/_components/texto/Hint";
import { QuebraRTC } from "@/lib/types/api/iv/v1";
import { fmtDatetime, fmtNumber } from "@/lib/util/string";
import {
  Box,
  HStack,
  Icon,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  VStack,
} from "@chakra-ui/react";
import {
  IoCheckmarkOutline,
  IoCloseOutline,
  IoCloudOfflineOutline,
  IoHelpCircleOutline,
  IoHelpOutline,
  IoShuffleOutline,
  IoTimeOutline,
} from "react-icons/io5";
import Image from "next/image";
import { companies } from "./fluxo/dados/companies";

export type TabelaAlocacoesProps = {
  alocacoes: QuebraRTC[];
  ladoVanguarda: "COMPRA" | "VENDA";
  precoUnitarioReais: number;
};

const th = { color: "white" };

const statusCust = (status?: number) => {
  switch (status) {
    case 0:
      return <Text color="cinza.500">Pendente análise</Text>;
    case 1:
      return <Text color="verde.main">Aprovado</Text>;
    case 2:
      return <Text color="rosa.main">Recusado</Text>;
    default:
      return <Text color="azul_4.100">Aguardando envio</Text>;
  }
};

const resumo = (
  primeiraAloc: QuebraRTC,
  ultimaAloc: QuebraRTC,
  total: number,
) => {
  const stsCustCtp = primeiraAloc.status_custodiante_contraparte;
  const ultimoStsCust = ultimaAloc.status_custodiante;
  const s = { rowSpan: total };
  if (ultimoStsCust === undefined || stsCustCtp === undefined)
    return (
      <Td {...s} bgColor="azul_4.50" color="azul_4.main">
        <HStack>
          <IoCloudOfflineOutline /> <Text>Não enviado</Text>
        </HStack>
      </Td>
    );
  if (ultimoStsCust === 0 && (stsCustCtp === 0 || stsCustCtp === 1))
    return (
      <Td {...s} bgColor="cinza.50" color="cinza.500">
        <HStack>
          <IoTimeOutline /> <Text>Aguardando Custodiante</Text>
        </HStack>
      </Td>
    );
  if ((ultimoStsCust === 0 || ultimoStsCust === 1) && stsCustCtp === 2)
    return (
      <Td {...s} bgColor="cinza.50" color="cinza.500">
        <HStack>
          <IoTimeOutline /> <Text>Aguardando Realocação Contraparte</Text>
        </HStack>
      </Td>
    );
  if (ultimoStsCust === 1 && stsCustCtp === 0)
    return (
      <Td {...s} bgColor="cinza.50" color="cinza.500">
        <HStack>
          <IoTimeOutline /> <Text>Aguardando Custodiante Contraparte</Text>
        </HStack>
      </Td>
    );
  if (ultimoStsCust === 1 && stsCustCtp === 1)
    return (
      <Td {...s} bgColor="verde.50" color="verde.main">
        <HStack>
          <IoCheckmarkOutline /> <Text>Encaminhado para liquidação</Text>
        </HStack>
      </Td>
    );
  if (ultimoStsCust === 2)
    return (
      <Td {...s} bgColor="rosa.50" color="rosa.main">
        <HStack>
          <IoCloseOutline /> <Text>Pendente realocação</Text>
        </HStack>
      </Td>
    );
  return <Td>???</Td>;
};

export default function TabelaAlocacoes({
  alocacoes,
  ladoVanguarda,
  precoUnitarioReais,
}: TabelaAlocacoesProps) {
  let qtdAprovada: number,
    qtdTotal: number,
    valorAprovado: number,
    valorTotal: number;
  qtdAprovada = qtdTotal = valorAprovado = valorTotal = 0;

  const agrupado = alocacoes.reduce(
    (map, al) => {
      const key = al.numero_controle_nome ?? "Não alocado na B3";
      map[key] ??= [];
      map[key].push(al);

      qtdTotal += Number(al.status_custodiante !== 2) * al.quantidade;
      valorTotal +=
        Number(al.status_custodiante !== 2) *
        al.quantidade *
        precoUnitarioReais;
      qtdAprovada +=
        Number(
          al.status_custodiante === 1 &&
            al.status_custodiante_contraparte === 1,
        ) * al.quantidade;
      valorAprovado +=
        Number(
          al.status_custodiante === 1 &&
            al.status_custodiante_contraparte === 1,
        ) *
        al.quantidade *
        precoUnitarioReais;

      return map;
    },
    {} as Record<string, QuebraRTC[]>,
  );

  return (
    <VStack flex={1}>
      {!alocacoes.length ? (
        <Hint m="24px">Aguardando alocações do operador.</Hint>
      ) : (
        <TableContainer w="100%">
          <Table size="xs">
            <Thead>
              <Tr bgColor="azul_1.main">
                <Th {...th}>N. Reg. NoMe</Th>
                <Th {...th}>Alocação</Th>
                <Th {...th}>Hora</Th>
                <Th {...th}>Fundo</Th>
                <Th {...th}>Lado</Th>
                <Th {...th}>Custodiante</Th>
                <Th {...th}>Status Cust.</Th>
                <Th {...th}>Status Cust. Contrp.</Th>
                <Th {...th}>Resumo</Th>
                <Th {...th}>Quantidade</Th>
                <Th {...th}>Negociado</Th>
              </Tr>
            </Thead>
            <Tbody>
              {Object.entries(agrupado)
                .sort(([n1, q1], [n2, q2]) => {
                  const n1Txt = isNaN(Number(n1));
                  const n2Txt = isNaN(Number(n2));
                  if (n1Txt && n2Txt) return 0;
                  if (n1Txt) return -1;
                  if (n2Txt) return 1;
                  return Number(n1) - Number(n2);
                })
                .flatMap(([num_nome, alocacoes]) =>
                  alocacoes.map((alocacao, indexAlocacao) => {
                    const td = {
                      padding: "2px",
                      opacity:
                        alocacao.status_custodiante === 2 ? 0.3 : undefined,
                      textDecoration:
                        alocacao.status_custodiante === 2
                          ? "line-through"
                          : undefined,
                      bgColor:
                        alocacao.status_custodiante === 2
                          ? "cinza.400"
                          : alocacao.status_custodiante === 1 &&
                              alocacao.status_custodiante_contraparte === 1
                            ? "verde.50"
                            : undefined,
                      borderBottomWidth:
                        indexAlocacao === alocacoes.length - 1 ? "1px" : 0,
                    };
                    const [primNome, segNome] = alocacao.custodiante
                      .toLocaleLowerCase()
                      .split(" ");
                    const icon =
                      companies[primNome]?.icon ?? companies[segNome]?.icon;
                    const primeiraAlocacao = alocacoes[0];
                    const ultimaAlocacao = alocacoes[alocacoes.length - 1];
                    return (
                      <Tr
                        key={
                          num_nome +
                          "|" +
                          alocacao.fundo_nome +
                          "|" +
                          indexAlocacao
                        }
                      >
                        {indexAlocacao === 0 && (
                          <>
                            <Td rowSpan={alocacoes.length}>
                              <Text as="span">{num_nome}</Text>
                            </Td>
                          </>
                        )}
                        <Td
                          {...td}
                          color={
                            alocacao.status_custodiante !== undefined
                              ? undefined
                              : "azul_4.100"
                          }
                        >
                          {alocacao.status_custodiante !== undefined
                            ? `${indexAlocacao + 1}ª alocação`
                            : "Interna"}
                        </Td>
                        <Td {...td}>
                          {fmtDatetime(alocacao.hora).split(" ").at(-1)}
                        </Td>
                        <Td {...td}>{alocacao.fundo_nome}</Td>
                        <Td {...td}>
                          <Text
                            as="span"
                            fontWeight={900}
                            color={
                              ladoVanguarda === "COMPRA"
                                ? "azul_3.main"
                                : "rosa.main"
                            }
                            fontSize="11px"
                            border="2px solid"
                            borderRadius="4px"
                            borderColor={
                              ladoVanguarda === "COMPRA"
                                ? "azul_3.main"
                                : "rosa.main"
                            }
                            p="0px 2px 0px 2px"
                            lineHeight={1}
                          >
                            {ladoVanguarda}
                          </Text>
                        </Td>
                        <Td {...td}>
                          <HStack>
                            {icon &&
                              ("src" in icon ? (
                                <Image
                                  alt="simbolo"
                                  src={icon}
                                  width={18}
                                  height={18}
                                />
                              ) : (
                                <Icon
                                  boxSize="18px"
                                  as={icon}
                                  color="cinza.500"
                                />
                              ))}{" "}
                            <Text>{alocacao.custodiante}</Text>
                          </HStack>
                        </Td>
                        <Td {...td}>
                          {statusCust(alocacao.status_custodiante)}
                        </Td>
                        {indexAlocacao === 0 && (
                          <>
                            <Td
                              bgColor={
                                ultimaAlocacao.status_custodiante === 1 &&
                                primeiraAlocacao.status_custodiante_contraparte ===
                                  1
                                  ? "verde.50"
                                  : undefined
                              }
                              rowSpan={alocacoes.length}
                            >
                              {statusCust(
                                alocacao.status_custodiante_contraparte,
                              )}
                            </Td>
                            {resumo(
                              primeiraAlocacao,
                              ultimaAlocacao,
                              alocacoes.length,
                            )}
                          </>
                        )}
                        <Td {...td} borderLeftWidth="1px">
                          {alocacao.quantidade}
                        </Td>
                        <Td {...td}>
                          R${" "}
                          {fmtNumber(alocacao.quantidade * precoUnitarioReais)}
                        </Td>
                      </Tr>
                    );
                  }),
                )}
              <Tr>
                <Td border="none" colSpan={9}></Td>
                <Th
                  bgColor="azul_1.main"
                  color="white"
                  borderLeftWidth="1px"
                  colSpan={2}
                >
                  Total aprovado
                </Th>
              </Tr>
              <Tr>
                <Td border="none" colSpan={9}></Td>
                <Td borderLeftWidth="1px" h="100%">
                  <Text>
                    {qtdAprovada} / {qtdTotal}
                  </Text>
                </Td>
                <Td h="100%">
                  <Text>
                    R$ {fmtNumber(valorAprovado)} / R$ {fmtNumber(valorTotal)}
                  </Text>
                </Td>
              </Tr>
            </Tbody>
          </Table>
        </TableContainer>
      )}
    </VStack>
  );
}
