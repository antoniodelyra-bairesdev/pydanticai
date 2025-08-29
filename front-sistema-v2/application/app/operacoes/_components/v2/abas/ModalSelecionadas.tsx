import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { ResultadoBuscaBoleta_Alocacao } from "@/lib/types/api/iv/operacoes/processamento";
import {
  Icon,
  ListItem,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tooltip,
  Tr,
  UnorderedList,
} from "@chakra-ui/react";
import {
  IoCheckmarkCircle,
  IoCloseCircle,
  IoCubeOutline,
} from "react-icons/io5";

export type ModalSelecionadasProps<Intencao extends string> = {
  selecionadas: Record<number, ResultadoBuscaBoleta_Alocacao>;
  problemasIntencao: Record<
    Intencao,
    (alocacao: ResultadoBuscaBoleta_Alocacao) => string[]
  >;
  intencao: Intencao | null;
  titulos: Record<Intencao, string>;
  acao: (i: Intencao) => void;
  setIntencao: (i: Intencao | null) => void;
  children?: React.ReactNode;
};

export default function ModalSelecionadas<Intencao extends string>({
  selecionadas,
  problemasIntencao,
  intencao,
  titulos,
  acao,
  setIntencao,
  children,
}: ModalSelecionadasProps<Intencao>) {
  return (
    <ConfirmModal
      isOpen={!!intencao}
      onClose={() => setIntencao(null)}
      title={intencao ? titulos[intencao] : ""}
      size="5xl"
      confirmEnabled={
        !!Object.keys(selecionadas).length &&
        Object.values(selecionadas).every(
          (a) => intencao && problemasIntencao[intencao]?.(a).length === 0,
        )
      }
      onConfirmAction={() => {
        if (intencao) {
          acao(intencao);
        }
      }}
    >
      {children}
      {Object.keys(selecionadas).length ? (
        <TableContainer mt="16px" borderTopRadius="8px" overflowY="auto">
          <Table size="sm">
            <Thead position="sticky" top={0}>
              <Tr bgColor="azul_1.500">
                <Th p="8px" color="white"></Th>
                <Th p="8px" color="white">
                  ID
                </Th>
                <Th p="8px" color="white">
                  Fundo
                </Th>
                <Th p="8px" color="white">
                  Lado
                </Th>
                <Th p="8px" color="white">
                  Código
                </Th>
                <Th p="8px" color="white">
                  P.U.
                </Th>
                <Th p="8px" color="white">
                  Quantidade
                </Th>
              </Tr>
            </Thead>
            <Tbody>
              {Object.values(selecionadas)
                .sort((a, b) => a.id - b.id)
                .map((a) => {
                  const ps = intencao ? problemasIntencao[intencao](a) : [];
                  return (
                    <Tr>
                      <Tooltip
                        hasArrow
                        borderRadius="4px"
                        fontSize="xs"
                        label={
                          ps.length ? (
                            <UnorderedList>
                              {ps.map((p) => (
                                <ListItem>{p}</ListItem>
                              ))}
                            </UnorderedList>
                          ) : (
                            "OK"
                          )
                        }
                      >
                        <Td>
                          {ps.length ? (
                            <Icon as={IoCloseCircle} color="rosa.main" />
                          ) : (
                            <Icon as={IoCheckmarkCircle} color="verde.main" />
                          )}
                        </Td>
                      </Tooltip>
                      <Td fontSize="xs" p="0 8px">
                        {a.id}
                      </Td>
                      <Td fontSize="xs" p="0 8px">
                        {a.fundo.nome}
                      </Td>
                      <Td
                        fontSize="xs"
                        p="0 8px"
                        fontWeight="bold"
                        color={a.vanguarda_compra ? "azul_2.main" : "rosa.main"}
                      >
                        {a.vanguarda_compra ? "C" : "V"}
                      </Td>
                      <Td fontSize="xs" p="0 8px" fontWeight="bold">
                        {a.codigo_ativo}
                      </Td>
                      <Td fontSize="xs" p="0 8px">
                        <Text as="span" color="verde.main" mr="4px">
                          R$
                        </Text>
                        {Number(a.preco_unitario).toLocaleString("pt-BR", {
                          minimumFractionDigits: 8,
                          maximumFractionDigits: 8,
                        })}
                      </Td>
                      <Td fontSize="xs" p="0 8px">
                        <Icon as={IoCubeOutline} mr="12px" color="verde.main" />
                        {Number(a.quantidade).toLocaleString("pt-BR", {
                          minimumFractionDigits: 8,
                          maximumFractionDigits: 8,
                        })}
                      </Td>
                    </Tr>
                  );
                })}
            </Tbody>
          </Table>
        </TableContainer>
      ) : (
        <Text
          p="32px"
          textAlign="center"
          borderRadius="8px"
          bgColor="cinza.100"
          color="cinza.500"
          fontSize="sm"
        >
          Não há alocações selecionadas
        </Text>
      )}
    </ConfirmModal>
  );
}
