import JSONText from "@/app/_components/misc/JSONText";
import { SugestaoBoleta } from "@/lib/types/api/iv/operacoes/processamento";
import { Text, VStack } from "@chakra-ui/react";

export type PassoRevisaoProps = {
  boletas: SugestaoBoleta[];
};

export default function PassoRevisao({ boletas }: PassoRevisaoProps) {
  return (
    <VStack alignItems="stretch" fontSize="sm">
      <Text fontSize="md">Resumo da importação:</Text>
      <Text>X linhas lidas</Text>
      <Text>X linhas aproveitadas</Text>
      <Text>Operações duplicadas ignoradas/consideradas</Text>
      <Text>X novas boletas</Text>
      <Text>X boletas corrigidas:</Text>
      <Text>- Boleta X</Text>
      <Text>- Boleta X</Text>
      <Text>- Boleta X</Text>
    </VStack>
  );
}
