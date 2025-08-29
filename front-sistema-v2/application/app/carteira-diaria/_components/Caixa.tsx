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
import TooltipComparativo from "./TooltipComparativo";
import { fmtNumber } from "@/lib/util/string";
import { IoCashOutline } from "react-icons/io5";
import Seta from "./Seta";
import ContagemBolinhas from "./ContagemBolinhas";

export type CaixaProps = {
  posicoes: Posicao[];
  focoPosicao: number;
  setFocoPosicao: (n: number) => void;
} & CardProps;

const somarCaixa = (pos: Posicao) =>
  pos.produto_investimento?.financeiro.caixas.reduce(
    (soma, c) => soma + Number(c.valor_financeiro),
    0,
  ) ?? 0;

export default function Caixa({
  posicoes,
  focoPosicao,
  setFocoPosicao,
  ...cardProps
}: CaixaProps) {
  const p = posicoes[focoPosicao];
  const caixaAcumulado = p ? somarCaixa(p) : 0;
  return (
    <Card {...cardProps}>
      <CardBody p={0}>
        <VStack h="100%" pt="12px" alignItems="stretch">
          <VStack alignItems="stretch" flex={1} justifyContent="center">
            <TooltipComparativo
              id={focoPosicao}
              valores={posicoes.map((op, oi) => ({
                id: oi,
                nome: op.produto_investimento?.nome ?? "---",
                valor: somarCaixa(op),
              }))}
              formatar={(n) => `R$ ${fmtNumber(n)}`}
              detalhes={
                p?.produto_investimento?.financeiro.caixas.length ? (
                  <VStack alignItems="stretch">
                    {p.produto_investimento?.financeiro.caixas
                      .sort(
                        (c1, c2) =>
                          Number(c1.valor_financeiro) -
                          Number(c2.valor_financeiro),
                      )
                      .map((c) => (
                        <HStack justifyContent="space-between">
                          <Text textAlign="left">
                            {c.isin_instituicao_financeira.valor}
                          </Text>
                          <Text textAlign="right">
                            R$ {fmtNumber(Number(c.valor_financeiro))}
                          </Text>
                        </HStack>
                      ))}
                  </VStack>
                ) : undefined
              }
            >
              <HStack w="100%" justifyContent="center">
                <Icon
                  color={
                    {
                      [1]: "verde.main",
                      [0]: "cinza.main",
                      [-1]: "rosa.main",
                    }[Math.sign(caixaAcumulado)]
                  }
                  as={IoCashOutline}
                />
                <Text
                  fontWeight={600}
                  fontSize="2xl"
                  textAlign="center"
                  whiteSpace="nowrap"
                >
                  R$ {posicoes.length ? fmtNumber(caixaAcumulado) : "---"}
                </Text>
              </HStack>
            </TooltipComparativo>
          </VStack>
        </VStack>
      </CardBody>
      <CardFooter p="0 0 12px 0">
        <HStack justifyContent="center" w="100%">
          <Text flex={1} textAlign="center" fontSize="xs">
            Caixa
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
