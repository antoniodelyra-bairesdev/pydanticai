import { getColorHex } from "@/app/theme";
import {
  Box,
  Divider,
  HStack,
  keyframes,
  Text,
  Tooltip,
  VStack,
} from "@chakra-ui/react";
import {
  coresStatus,
  DetalhesStatusAlocacao,
  StatusAlocacao,
} from "./boletas/BoletaComponent";

export type CarregamentoProps = {
  detalhes: DetalhesStatusAlocacao[];
};

const piscaCor = (inicial: string, final: string) => keyframes`
    0% { background-color: ${inicial}; }
    50% { background-color: ${final}; }
    100% { background-color: ${inicial}; }
`;

const statusCriticidade = {
  CONCLUIDO: 0,
  PENDENTE_EXTERNO_CADASTRADO: 1,
  PENDENTE_EXTERNO_NAO_CADASTRADO: 2,
  PENDENTE_VANGUARDA: 3,
  CANCELADO_OU_ERRO: 4,
};
const criticidadeStatus: Record<number, StatusAlocacao> = {
  0: "CONCLUIDO",
  1: "PENDENTE_EXTERNO_CADASTRADO",
  2: "PENDENTE_EXTERNO_NAO_CADASTRADO",
  3: "PENDENTE_VANGUARDA",
  4: "CANCELADO_OU_ERRO",
};

export default function CarregamentoBoleta({ detalhes }: CarregamentoProps) {
  const total = detalhes.length;
  let liq = 0;
  const diferentesStatus = detalhes.reduce(
    (map, sts) => {
      const crit = statusCriticidade[sts.status];
      if (crit === 0) {
        liq++;
      }
      const key = `${crit}-${sts.texto}`;
      map[key] ??= 0;
      map[key] += 1;
      return map;
    },
    {} as Record<string, number>,
  );

  return (
    <Tooltip
      hasArrow
      bgColor="azul_1.700"
      p="4px 8px"
      borderRadius="4px"
      label={
        <VStack fontWeight="bold" alignItems="stretch" gap={0}>
          {Object.keys(diferentesStatus)
            .sort()
            .map((k) => {
              const [crit, ...texto] = k.split("-");
              const qtd = diferentesStatus[k];
              const { txt } = coresStatus(criticidadeStatus[Number(crit)]);
              return (
                <HStack color={txt} justifyContent="space-between">
                  <Text>{texto}:</Text>
                  <Text>{qtd}</Text>
                </HStack>
              );
            })}
          <Divider m="4px 0" />
          <HStack color="white" justifyContent="space-between">
            <Text>Total:</Text>
            <Text>{total}</Text>
          </HStack>
        </VStack>
      }
      placement="top"
    >
      <HStack
        position="relative"
        overflow="hidden"
        gap={0}
        w="128px"
        h="18px"
        bgColor="cinza.main"
        borderRadius="4px"
        alignItems="stretch"
      >
        {Object.keys(diferentesStatus)
          .sort()
          .map((k) => {
            const [crit] = k.split("-");
            const qtd = diferentesStatus[k];
            const { txt, bg, anim } = coresStatus(
              criticidadeStatus[Number(crit)],
            );
            return (
              <Box
                opacity={0.6}
                w={`${(qtd / total) * 100}%`}
                bgColor={anim ? undefined : txt}
                animation={
                  anim
                    ? piscaCor(getColorHex(bg), getColorHex(txt)) +
                      " 1s linear infinite"
                    : undefined
                }
              />
            );
          })}
        <Text
          color={liq === total ? "white" : "black"}
          fontWeight={liq === total ? "bold" : "normal"}
          fontSize="xs"
          w="100%"
          position="absolute"
          textAlign="center"
        >
          {liq}/{total}
        </Text>
      </HStack>
    </Tooltip>
  );
}
