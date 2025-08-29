import {
  Divider,
  HStack,
  Icon,
  Table,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tooltip,
  Tr,
  VStack,
} from "@chakra-ui/react";
import { IoCaretDown, IoCaretUp, IoCheckmark } from "react-icons/io5";

export type TooltipComparativoProps = {
  id: string | number;
  valores: { id: string | number; nome: string; valor: number }[];
  formatar?: (valor: number) => React.ReactNode;
  detalhes?: React.ReactNode;
  children?: React.ReactNode;
};

export default function TooltipComparativo({
  id,
  valores,
  formatar = (valor) => valor,
  detalhes,
  children,
}: TooltipComparativoProps) {
  const mapaValores = valores.reduce(
    (mapa, v) => ((mapa[v.id] ??= v), mapa),
    {} as Record<string, { id: string | number; nome: string; valor: number }>,
  );
  const valor = mapaValores[id];
  if (!valor) {
    return children;
  }

  const temMaisDeUmValor = valores.length > 1;
  const temDetalhes = !!detalhes;

  return (
    <Tooltip
      hasArrow
      bgColor="blackAlpha.800"
      p="4px"
      borderRadius="4px"
      label={
        !temDetalhes && !temMaisDeUmValor ? (
          ""
        ) : temDetalhes && !temMaisDeUmValor ? (
          detalhes
        ) : (
          <VStack>
            <Text fontWeight={600} textAlign="center">
              {mapaValores[id]?.nome ?? "---"}
            </Text>
            {temDetalhes ? (
              <>
                <Divider />
                {detalhes}
                <Divider />
              </>
            ) : (
              <></>
            )}
            <Table>
              <Thead>
                <Tr>
                  <Td p="2px">
                    <Text color="cinza.main" fontSize="xs">
                      Comparando com
                    </Text>
                  </Td>
                  <Td p="2px">
                    <Text textAlign="center" color="cinza.main" fontSize="xs">
                      Diferença
                    </Text>
                  </Td>
                </Tr>
              </Thead>
              <Tbody>
                {valores.map((v) => {
                  const diff = v.valor - valor.valor;
                  const sinal = Math.sign(diff);
                  return v.id === id ? (
                    <></>
                  ) : (
                    <Tr fontSize="xs">
                      <Td p="0 2px">{v.nome}</Td>
                      <Td p="0 2px">
                        <HStack gap="2px">
                          <Icon
                            color={
                              {
                                [1]: "verde.main",
                                [0]: "cinza.main",
                                [-1]: "rosa.main",
                              }[sinal]
                            }
                            as={
                              {
                                [1]: IoCaretUp,
                                [0]: IoCheckmark,
                                [-1]: IoCaretDown,
                              }[sinal]
                            }
                          />
                          <Text whiteSpace="nowrap">{formatar(diff)}</Text>
                        </HStack>
                      </Td>
                    </Tr>
                  );
                })}
              </Tbody>
            </Table>
          </VStack>
        )
      }
    >
      {children}
    </Tooltip>
  );
}
