import {
  Card,
  CardBody,
  CardHeader,
  Checkbox,
  Divider,
  HStack,
  Text,
} from "@chakra-ui/react";
import CopiarTexto from "./CopiarTexto";
import React from "react";

export type CardContaBancariaProps = {
  onValorChange: (v: string) => void;

  editando?: boolean;
  titulo: string;
  valor: string;
  icone?: React.ReactNode;
};

export default function CardContaBancaria({
  onValorChange,
  editando,
  titulo,
  valor,
  icone,
}: CardContaBancariaProps) {
  return (
    <Card minW="128px" overflow="hidden">
      <CardHeader p="4px 8px">
        <HStack alignItems="stretch">
          <HStack flex={1}>
            <Text>{titulo}</Text>
          </HStack>
          {icone}
        </HStack>
      </CardHeader>
      <Divider color="cinza.main" />
      <CardBody p={0}>
        <CopiarTexto
          editando={editando}
          valor={valor}
          onValorChange={onValorChange}
        />
      </CardBody>
    </Card>
  );
}
