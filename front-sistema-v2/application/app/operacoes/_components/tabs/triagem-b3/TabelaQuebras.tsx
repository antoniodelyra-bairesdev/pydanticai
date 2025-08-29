import {
  HStack,
  Icon,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tooltip,
  Tr,
} from "@chakra-ui/react";
import Image from "next/image";
import { fmtNumber } from "@/lib/util/string";
import { Alocacao } from "@/lib/types/api/iv/v1";
import { companies } from "./fluxo/dados/companies";

const txt = {
  pl: "4px",
  pr: "4px",
  overflow: "hidden",
  whiteSpace: "nowrap",
  textOverflow: "ellipsis",
} as const;
const td = { ...txt, fontSize: "13px" } as const;
const th = { ...txt, fontSize: "sm" } as const;

export type TabelaQuebrasProps = {
  alocacoes: Alocacao[];
  verificarFundos: boolean;
};

export default function TabelaQuebras({
  alocacoes,
  verificarFundos,
}: TabelaQuebrasProps) {
  return (
    <TableContainer>
      <Table layout="fixed" variant="simple" size="xs">
        <Thead>
          <Tr bgColor="white">
            <Th {...th} pl="12px" w="100px">
              Nº YMF
            </Th>
            <Th {...th} w="144px">
              CNPJ
            </Th>
            <Th {...th} w="100px">
              CETIP
            </Th>
            <Th {...th} w="300px">
              Cliente
            </Th>
            <Th {...th} w="144px">
              Custodiante
            </Th>
            <Th {...th} w="100px">
              Quant.
            </Th>
            <Th {...th} w="144px">
              Negociado
            </Th>
          </Tr>
        </Thead>
        <Tbody>
          {alocacoes.map((al, i) => {
            const custKey = al.fundo.nome_custodiante
              .split(" ")
              .find((k: string) => companies[k.toLowerCase()]?.icon)
              ?.toLowerCase();
            const icon = companies[custKey ?? ""]?.icon;
            const erro = !al.registro_fundo && verificarFundos;
            return (
              <Tr bgColor={erro ? "rosa.50" : undefined} key={i}>
                <Td {...td} pl="12px">
                  {al.fundo.ymf}
                </Td>
                <Td {...td}>{al.fundo.cnpj}</Td>
                <Td
                  {...td}
                  bgColor={erro ? "rosa.100" : undefined}
                  color={erro ? "rosa.main" : undefined}
                  fontWeight={erro ? "bold" : undefined}
                >
                  {al.fundo.conta_cetip}
                </Td>
                <Td {...td}>
                  <Tooltip
                    bgColor="azul_1.main"
                    color="white"
                    label={al.fundo.nome}
                  >
                    <Text {...txt}>{al.fundo.nome}</Text>
                  </Tooltip>
                </Td>
                <Td {...td}>
                  <HStack>
                    {icon &&
                      ("src" in icon ? (
                        <Image width={12} height={12} src={icon} alt="icone" />
                      ) : (
                        <Icon as={icon} />
                      ))}
                    <Text>{al.fundo.nome_custodiante}</Text>
                  </HStack>
                </Td>
                <Td {...td}>{al.quantidade}</Td>
                <Td {...td}>R$ {fmtNumber(al.total, 2)}</Td>
              </Tr>
            );
          })}
        </Tbody>
      </Table>
    </TableContainer>
  );
}
