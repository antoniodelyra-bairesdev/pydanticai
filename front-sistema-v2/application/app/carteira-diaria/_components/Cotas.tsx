"use client";

import { Posicao } from "@/lib/types/leitor-carteiras-fundos/types";
import {
  Card,
  CardBody,
  CardFooter,
  CardProps,
  HStack,
  Icon,
  Text,
  VStack,
} from "@chakra-ui/react";
import {
  IoAnalyticsOutline,
  IoCubeOutline,
  IoPersonAddOutline,
  IoPersonRemoveOutline,
} from "react-icons/io5";
import TooltipComparativo from "./TooltipComparativo";
import { fmtNumber } from "@/lib/util/string";
import Seta from "./Seta";
import ContagemBolinhas from "./ContagemBolinhas";

export type CotasProps = {
  posicoes: Posicao[];
  focoPosicao: number;
  setFocoPosicao: (n: number) => void;
} & CardProps;

const valorCota = (pos: Posicao) =>
  pos.produto_investimento && "cotas" in pos.produto_investimento
    ? Number(pos.produto_investimento.cotas.valor_unitario)
    : 0;

const quantidadeCotas = (pos: Posicao) =>
  pos.produto_investimento && "cotas" in pos.produto_investimento
    ? Number(pos.produto_investimento.cotas.quantidade)
    : 0;

const valorCotasAEmitir = (pos: Posicao) =>
  pos.produto_investimento && "cotas" in pos.produto_investimento
    ? Number(pos.produto_investimento.cotas.valor_cotas_a_emitir)
    : 0;

const valorCotasAReceber = (pos: Posicao) =>
  pos.produto_investimento && "cotas" in pos.produto_investimento
    ? Number(pos.produto_investimento.cotas.valor_cotas_a_resgatar)
    : 0;

export default function Cotas({
  posicoes,
  focoPosicao,
  setFocoPosicao,
  ...cardProps
}: CotasProps) {
  const p = posicoes[focoPosicao];
  return (
    <Card {...cardProps}>
      <CardBody p="12px 24px">
        <VStack alignItems="stretch" w="100%" h="100%" gap={0}>
          <HStack justifyContent="center" flexWrap="nowrap">
            <Icon
              w="16px"
              h="16px"
              color="azul_4.main"
              as={IoAnalyticsOutline}
            />
            <TooltipComparativo
              id={focoPosicao}
              valores={posicoes.map((op, oi) => ({
                id: oi,
                nome: op.produto_investimento?.nome ?? "---",
                valor: valorCota(op),
              }))}
              formatar={fmtNumber}
            >
              <Text flex={1} textAlign="center" fontWeight={600} pr="24px">
                {posicoes.length ? fmtNumber(valorCota(p), 8) : "---"}
              </Text>
            </TooltipComparativo>
          </HStack>

          <Text textAlign="center" mb="8px" fontSize="xs">
            Valor da cota
          </Text>

          <HStack flexWrap="nowrap">
            <Icon w="16px" h="16px" color="verde.main" as={IoCubeOutline} />
            <TooltipComparativo
              id={focoPosicao}
              valores={posicoes.map((op, oi) => ({
                id: oi,
                nome: op.produto_investimento?.nome ?? "---",
                valor: quantidadeCotas(op),
              }))}
              formatar={fmtNumber}
            >
              <Text flex={1} textAlign="center" fontWeight={600} pr="24px">
                {posicoes.length ? fmtNumber(quantidadeCotas(p), 8) : "---"}
              </Text>
            </TooltipComparativo>
          </HStack>

          <Text textAlign="center" mb="8px" fontSize="xs">
            Qtd. de cotas
          </Text>

          <HStack flexWrap="nowrap">
            <Icon color="cinza.500" w="16px" h="16px" as={IoPersonAddOutline} />
            <TooltipComparativo
              id={focoPosicao}
              valores={posicoes.map((op, oi) => ({
                id: oi,
                nome: op.produto_investimento?.nome ?? "---",
                valor: valorCotasAEmitir(op),
              }))}
              formatar={(v) => `R$ ${fmtNumber(v)}`}
            >
              <Text flex={1} textAlign="center" fontWeight={600} pr="24px">
                R${" "}
                {posicoes.length ? fmtNumber(valorCotasAEmitir(p), 2) : "---"}
              </Text>
            </TooltipComparativo>
          </HStack>

          <Text textAlign="center" mb="8px" fontSize="xs">
            Cotas a emitir
          </Text>

          <HStack flexWrap="nowrap">
            <Icon
              w="16px"
              h="16px"
              color="cinza.500"
              as={IoPersonRemoveOutline}
            />
            <TooltipComparativo
              id={focoPosicao}
              valores={posicoes.map((op, oi) => ({
                id: oi,
                nome: op.produto_investimento?.nome ?? "---",
                valor: valorCotasAReceber(op),
              }))}
              formatar={(v) => `R$ ${fmtNumber(v)}`}
            >
              <Text flex={1} textAlign="center" fontWeight={600} pr="24px">
                R${" "}
                {posicoes.length ? fmtNumber(valorCotasAReceber(p), 2) : "---"}
              </Text>
            </TooltipComparativo>
          </HStack>

          <Text textAlign="center" fontSize="xs">
            Cotas a receber
          </Text>
        </VStack>
      </CardBody>
      <CardFooter p="0 0 12px 0">
        <HStack justifyContent="center" w="100%">
          <Text flex={1} textAlign="center" fontSize="xs">
            Cotas
          </Text>
          {posicoes.length > 1 ? (
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
          ) : (
            <></>
          )}
        </HStack>
      </CardFooter>
    </Card>
  );
}
