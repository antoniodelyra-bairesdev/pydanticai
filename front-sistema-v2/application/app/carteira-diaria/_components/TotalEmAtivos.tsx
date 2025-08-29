import {
  Card,
  CardBody,
  CardProps,
  HStack,
  Text,
  VStack,
} from "@chakra-ui/react";
import TooltipComparativo from "./TooltipComparativo";
import { Posicao } from "@/lib/types/leitor-carteiras-fundos/types";
import { fmtNumber } from "@/lib/util/string";

export type TotalEmAtivosProps = {
  posicoes: Posicao[];
  focoPosicao: number;
} & CardProps;

const totalAtivos = (p: Posicao) =>
  Number(p.produto_investimento?.valor_ativos ?? 0);

export default function TotalEmAtivos({
  posicoes,
  focoPosicao,
  ...cardProps
}: TotalEmAtivosProps) {
  const p = posicoes[focoPosicao];
  const totalAtv = p ? totalAtivos(p) : 0;
  return (
    <Card {...cardProps}>
      <CardBody p="8px">
        <HStack alignItems="flex-start" justifyContent="space-between">
          <Text>Total em ativos:</Text>
          <VStack alignItems="stretch">
            <TooltipComparativo
              id={focoPosicao}
              valores={posicoes.map((op, oi) => ({
                id: oi,
                nome: op.produto_investimento?.nome ?? "---",
                valor: totalAtivos(op),
              }))}
              formatar={(n) => `R$ ${fmtNumber(n)}`}
            >
              <Text fontWeight={600}>
                R$ {posicoes.length ? fmtNumber(totalAtv) : "---"}
              </Text>
            </TooltipComparativo>
          </VStack>
        </HStack>
      </CardBody>
    </Card>
  );
}
