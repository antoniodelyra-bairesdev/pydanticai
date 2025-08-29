import {
  Box,
  Divider,
  HStack,
  Icon,
  StackProps,
  Text,
  VStack,
  keyframes,
} from "@chakra-ui/react";
import { IoTimeOutline, IoWarningOutline } from "react-icons/io5";
import {
  AlocacaoStatus,
  EventoAlocacaoOperador,
  EventoOperacao,
  OperacaoType,
} from "@/lib/types/api/iv/v1";
import TituloOperacao from "../TituloOperacao";
import PartesNegocio from "../PartesNegocio";
import { fmtDatetime } from "@/lib/util/string";
import { companies } from "./fluxo/dados/companies";

export type PendenciaType = { nome: string; ator: "Operador" | "Backoffice" };

export type OperacaoItemColunaProps = {
  operacao: OperacaoType;
} & StackProps;

export const quebras = (eventos: EventoOperacao[]) => {
  let encaminhadas_liquidacao = 0;
  let total = 0;
  for (const evento of eventos) {
    if (evento.informacoes.tipo === "emissao-numeros-controle") {
      total = evento.informacoes.quebras.length;
      continue;
    } else if (evento.informacoes.tipo !== "atualizacao-custodiante") continue;

    if (evento.informacoes.status === AlocacaoStatus.Disponível_para_Registro) {
      encaminhadas_liquidacao++;
    }
  }
  return { encaminhadas_liquidacao, total };
};

export const pendencias = (eventos: EventoOperacao[]): PendenciaType[] => {
  let acato = 1;
  let aloc = 1;
  let ap = 0;
  for (const evento of eventos) {
    switch (evento.informacoes.tipo) {
      case "acato-voice":
        acato--;
        break;
      case "alocacao-operador":
        aloc--;
        ap++;
        break;
      case "aprovacao-backoffice":
        ap--;
        break;
    }
  }
  const pendencias: PendenciaType[] = [];
  if (aloc)
    pendencias.push({
      ator: "Operador",
      nome: "Pendente alocação",
    });
  if (ap)
    pendencias.push({
      ator: "Backoffice",
      nome: "Pendente revisão",
    });
  if (acato)
    pendencias.push({
      ator: "Operador",
      nome: "Pendente acato voice",
    });
  return pendencias;
};

const frames = () => keyframes`
    0% { outline-width: 0px; }
    50% { outline-width: 5px; }
    100% { outline-width: 0px; }
`;

const animation = () => `${frames()} 1s ease-in-out infinite`;

export default function OperacaoItemColuna({
  operacao,
  ...props
}: OperacaoItemColunaProps) {
  const { encaminhadas_liquidacao, total } = quebras(operacao.eventos);
  const pendenciasOperacao = pendencias(operacao.eventos);

  const alocacaoFinal = operacao.eventos
    .filter((e) => e.informacoes.tipo === "alocacao-operador")
    .sort((e1, e2) =>
      (
        e1.informacoes as EventoAlocacaoOperador
      ).operacao.criado_em.localeCompare(
        (e2.informacoes as EventoAlocacaoOperador).operacao.criado_em,
      ),
    )
    .at(-1)?.informacoes as EventoAlocacaoOperador | undefined;

  return (
    <HStack
      border="1px solid"
      alignItems="strech"
      borderColor="cinza.200"
      borderRadius="8px"
      overflow="hidden"
      gap={0}
      cursor="pointer"
      {...props}
    >
      <div
        style={{
          width: "8px",
          backgroundColor: "green",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {companies.vanguarda.detail}
      </div>
      <HStack flex={1} gap={0} alignItems="stretch">
        <TituloOperacao
          ativo={operacao.cadastro_ativo}
          preco_unitario={operacao.preco_unitario}
          quantidade={operacao.quantidade}
          fallback_codigo_ativo={operacao.codigo_ativo}
          fallback_indice_nome="---"
          taxa={operacao.taxa}
        />
        <VStack alignItems="stretch" flex={1}>
          <HStack
            justifyContent="space-between"
            p="2px 6px 0px 4px"
            wrap="wrap"
          >
            <PartesNegocio
              contraparte_nome={operacao.contraparte_nome}
              vanguarda_compra={operacao.vanguarda_compra}
            />
            <HStack
              flex={1}
              justifyContent="flex-end"
              fontSize="14px"
              gap="2px"
            >
              <Icon as={IoTimeOutline} mr="2px" color="cinza.400" />
              <Text color="cinza.700">
                {fmtDatetime(operacao.criado_em).split(" ").at(-1)}
              </Text>
            </HStack>
          </HStack>
          <Divider />
          <HStack justifyContent="flex-end" alignItems="center">
            <HStack
              p="4px"
              fontSize="11px"
              flexWrap="wrap"
              justifyContent="flex-start"
              gap="4px"
            >
              {pendenciasOperacao.map((a, i) => (
                <HStack
                  key={i}
                  p="2px 4px"
                  borderRadius="4px"
                  bgColor="cinza.50"
                  color="azul_2.main"
                  outline="2px solid"
                  outlineColor="azul_4.main"
                  animation={animation()}
                >
                  <Icon boxSize="14px" as={IoWarningOutline} />
                  <Text whiteSpace="nowrap">{a.nome}</Text>
                </HStack>
              ))}
            </HStack>
            {total !== 0 && (
              <Text
                textAlign="center"
                fontSize="10px"
                w="128px"
                color={
                  alocacaoFinal
                    ? alocacaoFinal?.operacao.alocacoes.length === total
                      ? "verde.main"
                      : "laranja.main"
                    : "cinza.400"
                }
              >
                {alocacaoFinal
                  ? alocacaoFinal.operacao.alocacoes.length === total
                    ? "Não há quebras"
                    : "Há quebras de alocações"
                  : "Aguardando contraparte"}
              </Text>
            )}
            {total ? (
              <VStack alignItems="flex-start" gap={0} mr="8px" mt="-4px">
                <Text fontSize="10px" h="14px" color="cinza.500">
                  {total ? "Progresso enc. liquidação:" : ""}
                </Text>
                <VStack
                  w="144px"
                  h="18px"
                  bgColor={total ? "cinza.main" : undefined}
                  position="relative"
                  borderRadius="4px"
                  overflow="hidden"
                >
                  <Box
                    zIndex={0}
                    w={(encaminhadas_liquidacao / total) * 100 + "%"}
                    h="100%"
                    position="absolute"
                    top={0}
                    left={0}
                    bgColor={
                      encaminhadas_liquidacao === total
                        ? "verde.main"
                        : "verde.200"
                    }
                  />
                  <Text
                    zIndex={1}
                    fontSize="xs"
                    color={
                      total && encaminhadas_liquidacao === total
                        ? "white"
                        : "black"
                    }
                    fontWeight={
                      total && encaminhadas_liquidacao === total
                        ? "bold"
                        : "normal"
                    }
                  >
                    {encaminhadas_liquidacao}/{total}
                  </Text>
                </VStack>
              </VStack>
            ) : (
              <Text fontSize="10px" mr="8px">
                Registros não emitidos
              </Text>
            )}
          </HStack>
        </VStack>
      </HStack>
    </HStack>
  );
}
