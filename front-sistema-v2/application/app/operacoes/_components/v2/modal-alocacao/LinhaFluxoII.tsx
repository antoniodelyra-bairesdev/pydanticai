import { HStack, Text, Tooltip } from "@chakra-ui/react";
import Horario from "./Horario";
import React from "react";

type InformacoesLinha = {
  cor: string;
  texto: React.ReactNode;
  horario: string;
};

export type LinhaFluxoIIProps = {
  titulo: string;
  informacoes?: InformacoesLinha;
};

export default function LinhaFluxoII({
  titulo,
  informacoes,
}: LinhaFluxoIIProps) {
  return (
    <HStack justifyContent="space-between">
      <Text>{titulo}</Text>
      {informacoes ? (
        <HStack>
          <HStack
            borderRadius="4px"
            bgColor={informacoes.cor}
            alignItems="center"
            p="0 12px"
          >
            {typeof informacoes.texto === "string" ? (
              <Tooltip
                label={informacoes.texto}
                hasArrow
                borderRadius="8px"
                fontSize="xs"
              >
                <Text
                  w="144px"
                  textAlign="center"
                  overflow="hidden"
                  whiteSpace="nowrap"
                  textOverflow="ellipsis"
                >
                  {informacoes.texto}
                </Text>
              </Tooltip>
            ) : (
              informacoes.texto
            )}
          </HStack>
          <Horario horario={informacoes.horario} />
        </HStack>
      ) : (
        <Text color="cinza.500">Sem informações</Text>
      )}
    </HStack>
  );
}
