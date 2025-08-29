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
import { Posicao } from "@/lib/types/leitor-carteiras-fundos/types";
import TooltipComparativo from "./TooltipComparativo";
import { fmtNumber } from "@/lib/util/string";
import { IoBarChartOutline } from "react-icons/io5";
import Seta from "./Seta";
import ContagemBolinhas from "./ContagemBolinhas";

export type PatrimonioLiquidoProps = {
  posicoes: Posicao[];
  focoPosicao: number;
  setFocoPosicao: (n: number) => void;
} & CardProps;

const extrairPL = (pos: Posicao) =>
  Number(pos.produto_investimento?.patrimonio_liquido) ?? 0;

export default function PatrimonioLiquido({
  posicoes,
  focoPosicao,
  setFocoPosicao,
  ...cardProps
}: PatrimonioLiquidoProps) {
  const p = posicoes[focoPosicao];
  const pl = p ? extrairPL(p) : 0;
  return (
    <Card {...cardProps}>
      <CardBody p={0}>
        <VStack pt="12px" h="100%" alignItems="stretch">
          <VStack alignItems="stretch" flex={1} justifyContent="center">
            <TooltipComparativo
              id={focoPosicao}
              valores={posicoes.map((op, oi) => ({
                id: oi,
                nome: op.produto_investimento?.nome ?? "---",
                valor: extrairPL(op),
              }))}
              formatar={(n) => `R$ ${fmtNumber(n)}`}
            >
              <HStack w="100%" justifyContent="center">
                <Icon
                  color={
                    {
                      [1]: "verde.main",
                      [0]: "cinza.main",
                      [-1]: "rosa.main",
                    }[Math.sign(pl)]
                  }
                  as={IoBarChartOutline}
                />
                <Text
                  fontWeight={600}
                  fontSize="2xl"
                  textAlign="center"
                  whiteSpace="nowrap"
                >
                  R${" "}
                  {posicoes.length
                    ? fmtNumber(
                        Number(p.produto_investimento?.patrimonio_liquido ?? 0),
                      )
                    : "---"}
                </Text>
              </HStack>
            </TooltipComparativo>
          </VStack>
        </VStack>
      </CardBody>
      <CardFooter p="4px 0 12px 0" position="relative">
        <HStack w="100%" justifyContent="center">
          <Text flex={1} textAlign="center" fontSize="xs">
            Patrimônio líquido
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
