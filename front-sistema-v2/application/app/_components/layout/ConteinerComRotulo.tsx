import { Box, HStack, StackProps, Text, VStack } from "@chakra-ui/react";
import Hint from "../texto/Hint";
import React from "react";
import { getColorHex } from "@/app/theme";

export type ConteinerComRotuloProps = {
  rotulo: string;
  lateral?: string;
  children?: React.ReactNode;
  icone?: React.ReactNode;
} & StackProps;

export default function ConteinerComRotulo({
  rotulo,
  children,
  icone,
  lateral = "azul_2.main",
  ...props
}: ConteinerComRotuloProps) {
  return (
    <VStack gap="6px" alignItems="stretch" {...props}>
      <Text>
        {icone} {rotulo}
      </Text>
      <HStack
        bgColor="white"
        flex={1}
        gap={0}
        borderRadius="8px"
        alignItems="stretch"
        boxShadow={"0 2px 4px 0" + getColorHex("cinza.main")}
      >
        {lateral && <Box w="8px" bgColor={lateral} borderLeftRadius="8px" />}
        <Box flex={1}>{children}</Box>
      </HStack>
    </VStack>
  );
}
