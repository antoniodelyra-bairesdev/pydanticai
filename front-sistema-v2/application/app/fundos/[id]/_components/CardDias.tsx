"use client";

import Hint from "@/app/_components/texto/Hint";
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  CardProps,
  HStack,
  Input,
  Stack,
  StackProps,
  Switch,
  Text,
  VStack,
  useStatStyles,
} from "@chakra-ui/react";
import InputEditavel from "./InputEditavel";
import { useState } from "react";

export type CardDiasProps = {
  editando?: boolean;
  dias: number;
  onDiasChange: (d: number) => void;
  duMarcado: boolean;
  onDuMarcadoChange: (m: boolean) => void;
  textoLivre: string;
  onTextoLivreChange: (t: string) => void;
  titulo: string;
} & CardProps;

export default function CardDias({
  editando,
  titulo,
  textoLivre,
  onTextoLivreChange,
  duMarcado,
  onDuMarcadoChange,
  dias,
  onDiasChange,
  ...props
}: CardDiasProps) {
  return (
    <Card {...props}>
      <CardHeader p="4px 8px">
        <Text fontSize="xs">{titulo}</Text>
      </CardHeader>
      <CardBody p="4px 8px 8px 8px">
        <HStack
          flexWrap="wrap"
          color={editando ? "black" : "cinza.500"}
          gap="4px"
          fontSize="xs"
        >
          <Text>D + </Text>
          <Box w={editando ? "48px" : undefined} transition="all 0.5s">
            <InputEditavel
              valor={String(dias)}
              onValorChange={(v) => {
                const n = Number(v);
                onDiasChange(isNaN(n) ? 0 : n);
              }}
              flex={editando ? 1 : 0}
              editando={editando}
            />
          </Box>
          <HStack>
            <Text textAlign="center" as="span" w="72px">
              {editando
                ? "Dias úteis?"
                : duMarcado
                  ? "Dias úteis"
                  : "Dias corridos"}
            </Text>
            {editando && (
              <Switch
                isChecked={duMarcado}
                onChange={(ev) => onDuMarcadoChange(ev.currentTarget.checked)}
                size="sm"
                colorScheme="verde"
              />
            )}
          </HStack>
          <InputEditavel
            flex={1}
            valor={textoLivre}
            onValorChange={onTextoLivreChange}
            textoValorVazio=""
            placeholder="Texto livre"
            editando={editando}
          />
        </HStack>
      </CardBody>
    </Card>
  );
}
