import { Box, Button, HStack, Text, VStack } from "@chakra-ui/react";
import React from "react";
import Link from "next/link";
import { ResultadoProcessamento } from "@/lib/types/api/iv/operacoes/processamento";

type Acao = {
  cor: string;
  texto: string;
  link: string;
};

export type AvisoProps = {
  alerta: ResultadoProcessamento;
};

export default function Aviso({ alerta }: AvisoProps) {
  const acoes: Acao[] = [];
  let texto: React.ReactNode = alerta.detalhes;

  return (
    <HStack borderRadius="8px" alignItems="stretch" m="4px 8px" bgColor="white">
      <Box
        borderLeftRadius="8px"
        w="6px"
        bgColor={alerta.status === "ERRO" ? "rosa.main" : "amarelo.main"}
      />
      <VStack flex={1} alignItems="stretch" p="4px 8px">
        <Text pt="8px" fontSize="xs" lineHeight={1.2}>
          Linha {alerta.linha}: {texto}
        </Text>
        <HStack justifyContent="flex-end">
          {acoes.map((a) => (
            <Link href={a.link} target="blank" rel="noopener noreferrer">
              <Button colorScheme={a.cor} size="xs">
                {a.texto}
              </Button>
            </Link>
          ))}
        </HStack>
      </VStack>
    </HStack>
  );
}
